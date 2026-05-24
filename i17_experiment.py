#!/usr/bin/env python3
"""
I.17 Unlearning Defense Experiment: Does Metric Improvement Track Extraction?

Tests whether gradient-ascent approximate unlearning that increases Loss
(ΔLoss > 0) reliably reduces extraction success (ΔEM < 0).

Hypothesis: If M→A τ = 0.08, then Kendall τ(ΔLoss, ΔEM) across unlearned
sequences should be weak — metric-verified unlearning does not certify
extraction-level protection.

Method:
  Phase 1  Scan WikiText-103 for N_COLLECT sequences; measure baseline Loss + EM.
  Phase 2  Select top-N_TARGET by baseline EM (most extractable).
           Per sequence: restore checkpoint → gradient ascent on last N_LAYERS
           layers (N_STEPS steps) → re-measure Loss + EM → record ΔLoss, ΔEM.
  Analysis Kendall τ(ΔLoss, ΔEM); compare against baseline τ(Loss, EM).

Output: i17_results.json  +  i17_tau_summary.txt
"""

import json, gc, argparse
import numpy as np
import torch
from scipy.stats import kendalltau
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

# ── Config ─────────────────────────────────────────────────────────────────
MODEL          = "EleutherAI/pythia-6.9b-deduped"
N_COLLECT      = 600      # sequences to scan for baseline metrics
N_TARGET       = 50       # top-EM sequences to unlearn
MIN_TOKENS     = 80
MAX_TOKENS     = 300
PREFIX_FRAC    = 0.5
N_STEPS        = 50       # gradient-ascent steps per sequence
UNLEARN_LR     = 1e-5
N_LAYERS       = 2        # only update last N transformer layers
RESULTS_FILE   = "/home/ubuntu/i17b_results.json"
SUMMARY_FILE   = "/home/ubuntu/i17b_tau_summary.txt"

# ── Metric helpers ──────────────────────────────────────────────────────────
@torch.no_grad()
def get_token_logprobs(model, input_ids):
    out    = model(input_ids)
    logits = out.logits[0, :-1].float()
    labels = input_ids[0, 1:]
    lp     = torch.log_softmax(logits, dim=-1)
    return lp[range(len(labels)), labels].cpu().numpy()

def compute_loss(token_lp):
    return float(-token_lp.mean())

@torch.no_grad()
def greedy_em(model, tokenizer, input_ids, prefix_frac=PREFIX_FRAC):
    T          = input_ids.shape[1]
    prefix_len = max(10, int(T * prefix_frac))
    suffix_len = T - prefix_len
    if suffix_len < 5:
        return None
    prefix     = input_ids[:, :prefix_len]
    gen        = model.generate(prefix, max_new_tokens=suffix_len,
                                do_sample=False,
                                pad_token_id=tokenizer.eos_token_id)
    gen_suffix = gen[0, prefix_len:]
    gt_suffix  = input_ids[0, prefix_len:]
    n          = min(len(gen_suffix), len(gt_suffix))
    return float((gen_suffix[:n] == gt_suffix[:n]).float().mean().item())

# ── Checkpoint helpers ──────────────────────────────────────────────────────
def save_trainable_params(model):
    """Clone trainable parameter data to CPU."""
    return {name: p.data.clone().cpu()
            for name, p in model.named_parameters() if p.requires_grad}

def restore_trainable_params(model, saved):
    """Copy saved CPU tensors back to their GPU parameters."""
    for name, p in model.named_parameters():
        if name in saved:
            p.data.copy_(saved[name].to(p.device))

def freeze_except_last_n(model, n):
    """Freeze all parameters except the last n GPT-NeoX transformer layers."""
    for p in model.parameters():
        p.requires_grad = False
    total = len(model.gpt_neox.layers)
    for i in range(total - n, total):
        for p in model.gpt_neox.layers[i].parameters():
            p.requires_grad = True

# ── Main ────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_collect", type=int, default=N_COLLECT)
    parser.add_argument("--n_target",  type=int, default=N_TARGET)
    args = parser.parse_args()

    print(f"Loading tokenizer/model: {MODEL}")
    tok   = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, torch_dtype=torch.float16, device_map="auto"
    )
    model.eval()
    print("Model loaded.\n")

    freeze_except_last_n(model, N_LAYERS)
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Trainable params: {n_trainable:,}  (last {N_LAYERS} layers)\n")

    print("Saving trainable-layer checkpoint …")
    checkpoint = save_trainable_params(model)
    print(f"Checkpoint: {len(checkpoint)} tensors, "
          f"{sum(v.numel() for v in checkpoint.values())/1e6:.1f}M params\n")

    # ── Phase 1: baseline scan ────────────────────────────────────────────────
    print(f"Phase 1: scanning {args.n_collect} WikiText-103 sequences for baseline …")
    ds = load_dataset("Salesforce/wikitext", "wikitext-103-raw-v1",
                      split="train", streaming=True)
    baseline, seen = [], 0
    for sample in ds:
        if seen >= args.n_collect:
            break
        text = sample.get("text", "")
        if not text or len(text.split()) < 30:
            continue
        enc = tok(text, return_tensors="pt",
                  max_length=MAX_TOKENS, truncation=True).to(model.device)
        ids = enc["input_ids"]
        if ids.shape[1] < MIN_TOKENS:
            continue
        try:
            tok_lp = get_token_logprobs(model, ids)
            loss   = compute_loss(tok_lp)
            em     = greedy_em(model, tok, ids)
        except Exception as ex:
            print(f"  skip ({ex})")
            continue
        if em is None:
            continue
        baseline.append({"text": text, "loss": loss, "em": em,
                         "seq_len": int(ids.shape[1])})
        seen += 1
        if seen % 50 == 0:
            print(f"  {seen}/{args.n_collect}  last em={em:.3f} loss={loss:.3f}")

    print(f"Baseline collected: {len(baseline)} seqs\n")

    # Select top-N_TARGET by baseline EM
    baseline.sort(key=lambda x: x["em"], reverse=True)
    targets = baseline[:args.n_target]
    print(f"Selected {len(targets)} targets  "
          f"(EM range {targets[-1]['em']:.3f}–{targets[0]['em']:.3f})\n")

    # ── Phase 2: per-sequence gradient-ascent unlearning ─────────────────────
    print(f"Phase 2: unlearning ({N_STEPS} steps, lr={UNLEARN_LR}) …")
    results = []
    for idx, rec in enumerate(targets):
        restore_trainable_params(model, checkpoint)
        model.train()

        enc = tok(rec["text"], return_tensors="pt",
                  max_length=MAX_TOKENS, truncation=True).to(model.device)
        ids = enc["input_ids"]

        opt = torch.optim.AdamW(
            [p for p in model.parameters() if p.requires_grad],
            lr=UNLEARN_LR
        )
        for _ in range(N_STEPS):
            opt.zero_grad()
            out = model(ids, labels=ids)
            (-out.loss).backward()   # gradient ASCENT
            torch.nn.utils.clip_grad_norm_(
                [p for p in model.parameters() if p.requires_grad], max_norm=1.0
            )
            opt.step()

        model.eval()
        try:
            tok_lp_new = get_token_logprobs(model, ids)
            loss_new   = compute_loss(tok_lp_new)
            em_new     = greedy_em(model, tok, ids)
        except Exception as ex:
            print(f"  [{idx+1}] eval error: {ex}")
            continue
        if em_new is None:
            continue

        dl = loss_new - rec["loss"]
        de = em_new   - rec["em"]
        results.append({
            "baseline_loss": rec["loss"], "baseline_em": rec["em"],
            "post_loss":     loss_new,    "post_em":     em_new,
            "delta_loss":    dl,          "delta_em":    de,
            "seq_len":       rec["seq_len"]
        })
        print(f"  [{idx+1:2d}/{len(targets)}]  "
              f"ΔLoss={dl:+.3f}  ΔEM={de:+.3f}  "
              f"(base loss={rec['loss']:.3f} em={rec['em']:.3f} → "
              f"post loss={loss_new:.3f} em={em_new:.3f})")

        gc.collect(); torch.cuda.empty_cache()

    print(f"\nCompleted {len(results)} unlearning experiments.\n")
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)

    # ── Analysis ──────────────────────────────────────────────────────────────
    dl_arr = np.array([r["delta_loss"]    for r in results])
    de_arr = np.array([r["delta_em"]      for r in results])
    bl_arr = np.array([r["baseline_loss"] for r in results])
    be_arr = np.array([r["baseline_em"]   for r in results])

    tau_base,  _         = kendalltau(bl_arr, be_arr)
    tau_delta, pval_delta = kendalltau(dl_arr, de_arr)

    n_loss_up = int((dl_arr > 0).sum())
    n_em_down = int((de_arr < 0).sum())
    n_both    = int(((dl_arr > 0) & (de_arr < 0)).sum())

    lines = [
        "=== I.17 Unlearning Defense: ΔLoss vs. ΔEM (Pythia-6.9b-deduped) ===\n",
        f"  n={len(results)}  steps={N_STEPS}  lr={UNLEARN_LR}  layers={N_LAYERS}\n",
        f"  Baseline τ(Loss, EM):          τ = {tau_base:+.3f}",
        f"  Unlearning τ(ΔLoss, ΔEM):      τ = {tau_delta:+.3f}  (p = {pval_delta:.4f})\n",
        f"  Mean ΔLoss:  {dl_arr.mean():+.3f}  (>0 in {n_loss_up}/{len(results)})",
        f"  Mean ΔEM:    {de_arr.mean():+.3f}  (<0 in {n_em_down}/{len(results)})",
        f"  Both ΔLoss>0 and ΔEM<0 (unlearn 'success'): {n_both}/{len(results)}",
    ]
    summary = "\n".join(lines)
    with open(SUMMARY_FILE, "w") as f:
        f.write(summary)
    for line in lines:
        print(line)
    print(f"\nSaved summary → {SUMMARY_FILE}")
    print(f"Saved raw results → {RESULTS_FILE}")

if __name__ == "__main__":
    main()
