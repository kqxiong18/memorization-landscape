#!/usr/bin/env python3
"""
I.13 External Validation: M→A correlation on Pythia-6.9b-deduped.
Replicates the HUBBLE M→A analysis on a real pre-trained model without
controlled duplication levels. Uses Pythia-6.9b-deduped (open, ungated)
on The Pile validation split as member sequences.

Output: i13_results.json  +  i13_tau_summary.txt
"""

import json, zlib, gc, argparse
import numpy as np
import torch
from scipy.stats import kendalltau
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

# ── Config ────────────────────────────────────────────────────────────────────
MODEL        = "EleutherAI/pythia-6.9b-deduped"
N_SEQ        = 600          # sequences to evaluate (trim to those with valid EM)
MIN_TOKENS   = 100
MAX_TOKENS   = 400
PREFIX_FRAC  = 0.5          # fraction of tokens used as extraction prefix
MINK_K       = 0.2          # Min-K% percentile
RESULTS_FILE = "i13_results.json"
SUMMARY_FILE = "i13_tau_summary.txt"

# ── Metric helpers ─────────────────────────────────────────────────────────────
@torch.no_grad()
def get_token_logprobs(model, input_ids):
    """Return per-token log-probs (shape T-1) for input_ids."""
    out = model(input_ids)
    logits = out.logits[0, :-1]                          # (T-1, V)
    labels = input_ids[0, 1:]                            # (T-1,)
    lp = torch.log_softmax(logits.float(), dim=-1)
    return lp[range(len(labels)), labels].cpu().numpy()  # (T-1,)

def compute_loss(token_lp):
    return float(-token_lp.mean())

def compute_mink(token_lp, k=MINK_K):
    n_k = max(1, int(len(token_lp) * k))
    return float(np.sort(token_lp)[:n_k].mean())

def compute_minkpp(model, input_ids, k=MINK_K):
    """MinK%++: normalize each token log-prob by vocab mean/std at that pos."""
    with torch.no_grad():
        out  = model(input_ids)
        logits = out.logits[0, :-1].float()              # (T-1, V)
    labels = input_ids[0, 1:]
    lp     = torch.log_softmax(logits, dim=-1)
    tok_lp = lp[range(len(labels)), labels]              # (T-1,)
    mu     = lp.mean(dim=-1)
    sigma  = lp.std(dim=-1).clamp(min=1e-8)
    norm   = ((tok_lp - mu) / sigma).cpu().numpy()
    n_k    = max(1, int(len(norm) * k))
    return float(np.sort(norm)[:n_k].mean())

def compute_zlib(token_lp, text):
    loss = float(-token_lp.mean())
    z    = len(zlib.compress(text.encode("utf-8"))) / max(1, len(text.encode("utf-8")))
    return loss / max(z, 1e-8)

@torch.no_grad()
def greedy_em(model, tokenizer, input_ids, prefix_frac=PREFIX_FRAC):
    """Prefix-extraction exact-match rate."""
    T          = input_ids.shape[1]
    prefix_len = max(10, int(T * prefix_frac))
    suffix_len = T - prefix_len
    if suffix_len < 10:
        return None
    prefix = input_ids[:, :prefix_len]
    gen    = model.generate(prefix, max_new_tokens=suffix_len,
                            do_sample=False, pad_token_id=tokenizer.eos_token_id)
    gen_suffix = gen[0, prefix_len:]
    gt_suffix  = input_ids[0, prefix_len:]
    n = min(len(gen_suffix), len(gt_suffix))
    return float((gen_suffix[:n] == gt_suffix[:n]).float().mean().item())

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=N_SEQ)
    args = parser.parse_args()

    print(f"Loading tokenizer/model: {MODEL}")
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, torch_dtype=torch.float16, device_map="auto"
    )
    model.eval()
    print("Model loaded.\n")

    # Load The Pile validation split (streaming avoids full download)
    print("Streaming The Pile validation split …")
    try:
        pile = load_dataset("EleutherAI/pile", split="validation", streaming=True)
    except Exception as e:
        print(f"Pile unavailable ({e}); falling back to wikitext-103 train split.")
        pile = load_dataset("wikitext", "wikitext-103-raw-v1",
                            split="train", streaming=True)

    results, seen = [], 0
    for sample in pile:
        if seen >= args.n:
            break
        text = sample.get("text", sample.get("text", ""))
        if not text or len(text.split()) < 50:
            continue

        enc = tok(text, return_tensors="pt",
                  max_length=MAX_TOKENS, truncation=True).to(model.device)
        ids = enc["input_ids"]
        T   = ids.shape[1]
        if T < MIN_TOKENS:
            continue

        try:
            tok_lp  = get_token_logprobs(model, ids)
            loss    = compute_loss(tok_lp)
            mink    = compute_mink(tok_lp)
            minkpp  = compute_minkpp(model, ids)
            zlibsc  = compute_zlib(tok_lp, text)
            em      = greedy_em(model, tok, ids)
        except Exception as ex:
            print(f"  skip (error: {ex})")
            continue

        if em is None:
            continue

        results.append(dict(loss=loss, mink=mink, minkpp=minkpp,
                            zlib=zlibsc, greedy_em=em, seq_len=int(T)))
        seen += 1
        if seen % 50 == 0:
            print(f"  {seen}/{args.n}  last em={em:.3f}  loss={loss:.3f}")

        # free cache periodically
        if seen % 100 == 0:
            gc.collect(); torch.cuda.empty_cache()

    print(f"\nCollected {len(results)} valid sequences.")
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)

    # ── Compute Kendall τ ──────────────────────────────────────────────────────
    arr = {k: np.array([r[k] for r in results]) for k in results[0]}
    ems = arr["greedy_em"]

    lines = ["=== I.13 External Validation: M→A Kendall τ (Pythia-6.9b-deduped) ===\n"]
    for name, metric, negate in [
        ("Loss",    arr["loss"],   True),   # higher loss → less memorized
        ("Min-K%",  arr["mink"],   True),   # more negative → less memorized
        ("MinK%++", arr["minkpp"], True),
        ("ZLib",    arr["zlib"],   True),
    ]:
        vals = -metric if negate else metric
        tau, pval = kendalltau(vals, ems)
        line = f"  {name:<10} vs Greedy EM:  τ = {tau:+.3f}  (p = {pval:.4f})"
        print(line); lines.append(line)

    # seq-length stratified
    lines.append("\nStratified by sequence length quartile:")
    qtiles = np.percentile(arr["seq_len"], [25, 50, 75])
    for i, (lo, hi) in enumerate(zip(
            [0, qtiles[0], qtiles[1], qtiles[2]],
            [qtiles[0], qtiles[1], qtiles[2], 9999])):
        mask = (arr["seq_len"] >= lo) & (arr["seq_len"] < hi)
        if mask.sum() < 10:
            continue
        tau, _ = kendalltau(-arr["loss"][mask], ems[mask])
        line = f"  Q{i+1} (len {int(lo)}–{int(hi)}, n={mask.sum()}): Loss τ = {tau:+.3f}"
        print(line); lines.append(line)

    summary = "\n".join(lines)
    with open(SUMMARY_FILE, "w") as f:
        f.write(summary)
    print(f"\nSaved summary → {SUMMARY_FILE}")
    print(f"Saved raw results → {RESULTS_FILE}")

if __name__ == "__main__":
    main()
