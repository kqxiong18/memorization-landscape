#!/usr/bin/env python3
"""
I.14 Aligned vs. Base: Does RLHF Suppress M→A?

Compares Kendall τ(Metric, Greedy EM) between a base model and its
RLHF-aligned counterpart on neutral WikiText-103 text.

If RLHF only inserts a Defense at the A→output interface (leaving
F→M and M→A intact), τ should be similar for both models on neutral text.

Models: mistralai/Mistral-7B-v0.1 (base) vs mistralai/Mistral-7B-Instruct-v0.3
Dataset: WikiText-103 train split (same protocol as I.13)
Output: i14_results.json + i14_tau_summary.txt
"""

import json, zlib, gc, argparse
import numpy as np
import torch
from scipy.stats import kendalltau
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

# ── Config ────────────────────────────────────────────────────────────────────
BASE_MODEL    = "mistralai/Mistral-7B-v0.1"
ALIGNED_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
N_SEQ         = 300
MIN_TOKENS    = 100
MAX_TOKENS    = 400
PREFIX_FRAC   = 0.5
MINK_K        = 0.2
RESULTS_FILE  = "/home/ubuntu/i14_results.json"
SUMMARY_FILE  = "/home/ubuntu/i14_tau_summary.txt"

# ── Metric helpers ─────────────────────────────────────────────────────────────
@torch.no_grad()
def get_token_logprobs(model, input_ids):
    out    = model(input_ids)
    logits = out.logits[0, :-1].float()
    labels = input_ids[0, 1:]
    lp     = torch.log_softmax(logits, dim=-1)
    return lp[range(len(labels)), labels].cpu().numpy()

def compute_loss(token_lp):
    return float(-token_lp.mean())

def compute_mink(token_lp, k=MINK_K):
    n_k = max(1, int(len(token_lp) * k))
    return float(np.sort(token_lp)[:n_k].mean())

def compute_zlib(token_lp, text):
    loss = float(-token_lp.mean())
    z    = len(zlib.compress(text.encode("utf-8"))) / max(1, len(text.encode("utf-8")))
    return loss / max(z, 1e-8)

@torch.no_grad()
def greedy_em(model, tokenizer, input_ids, prefix_frac=PREFIX_FRAC):
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

# ── Per-model evaluation ───────────────────────────────────────────────────────
def evaluate_model(model_name, texts):
    print(f"\nLoading {model_name} …")
    tok   = AutoTokenizer.from_pretrained(model_name)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map="auto"
    )
    model.eval()
    print("Model loaded.\n")

    results = []
    for i, text in enumerate(texts):
        enc = tok(text, return_tensors="pt",
                  max_length=MAX_TOKENS, truncation=True).to(model.device)
        ids = enc["input_ids"]
        try:
            tok_lp = get_token_logprobs(model, ids)
            loss   = compute_loss(tok_lp)
            mink   = compute_mink(tok_lp)
            zlibsc = compute_zlib(tok_lp, text)
            em     = greedy_em(model, tok, ids)
        except Exception as ex:
            print(f"  [{i+1}] skip: {ex}")
            results.append(None)
            continue
        if em is None:
            results.append(None)
            continue
        results.append(dict(loss=loss, mink=mink, zlib=zlibsc,
                            greedy_em=em, seq_len=int(ids.shape[1])))
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(texts)}  em={em:.3f}  loss={loss:.3f}")

    del model
    gc.collect()
    torch.cuda.empty_cache()
    return results

# ── τ summary helper ───────────────────────────────────────────────────────────
def tau_lines(label, results):
    valid = [r for r in results if r is not None]
    ems   = np.array([r["greedy_em"] for r in valid])
    lines = []
    for name, key, negate in [
        ("Loss",   "loss", True),
        ("Min-K%", "mink", True),
        ("ZLib",   "zlib", True),
    ]:
        vals     = -np.array([r[key] for r in valid]) if negate else np.array([r[key] for r in valid])
        tau, pval = kendalltau(vals, ems)
        lines.append(f"  {label}  {name:<8} τ = {tau:+.3f}  (p = {pval:.4f})  n={len(valid)}")
    return lines

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=N_SEQ)
    args = parser.parse_args()

    # Collect texts using base model tokenizer (just for length filtering)
    print("Streaming WikiText-103 …")
    ds      = load_dataset("Salesforce/wikitext", "wikitext-103-raw-v1",
                           split="train", streaming=True)
    tok_tmp = AutoTokenizer.from_pretrained(BASE_MODEL)
    texts, seen = [], 0
    for sample in ds:
        if seen >= args.n:
            break
        text = sample.get("text", "")
        if not text or len(text.split()) < 50:
            continue
        enc = tok_tmp(text, return_tensors="pt",
                      max_length=MAX_TOKENS, truncation=True)
        if enc["input_ids"].shape[1] < MIN_TOKENS:
            continue
        texts.append(text)
        seen += 1
    del tok_tmp
    print(f"Collected {len(texts)} texts.\n")

    # Evaluate both models sequentially to avoid OOM
    base_res    = evaluate_model(BASE_MODEL,    texts)
    aligned_res = evaluate_model(ALIGNED_MODEL, texts)

    # Keep only paired successes
    paired = [(b, a) for b, a in zip(base_res, aligned_res)
              if b is not None and a is not None]
    base_paired    = [p[0] for p in paired]
    aligned_paired = [p[1] for p in paired]
    print(f"\nPaired sequences: {len(paired)}")

    # ── Summary ───────────────────────────────────────────────────────────────
    lines = [
        "=== I.14 Aligned vs. Base: M→A Kendall τ (WikiText-103) ===\n",
        f"  Base model:    {BASE_MODEL}",
        f"  Aligned model: {ALIGNED_MODEL}",
        f"  n (paired):    {len(paired)}\n",
    ]
    lines += tau_lines("[Base   ]", base_paired)
    lines.append("")
    lines += tau_lines("[Aligned]", aligned_paired)

    base_em    = np.array([r["greedy_em"] for r in base_paired])
    aligned_em = np.array([r["greedy_em"] for r in aligned_paired])
    lines += [
        f"\n  Mean Greedy EM — Base:         {base_em.mean():.4f}",
        f"  Mean Greedy EM — Aligned:      {aligned_em.mean():.4f}",
        f"  Mean ΔEM (aligned − base):     {(aligned_em - base_em).mean():+.4f}",
    ]

    summary = "\n".join(lines)
    with open(SUMMARY_FILE, "w") as f:
        f.write(summary)
    with open(RESULTS_FILE, "w") as f:
        json.dump({"base": base_paired, "aligned": aligned_paired}, f, indent=2)
    for line in lines:
        print(line)
    print(f"\nSaved summary → {SUMMARY_FILE}")
    print(f"Saved results  → {RESULTS_FILE}")

if __name__ == "__main__":
    main()
