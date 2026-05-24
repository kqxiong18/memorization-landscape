# CHANGES.md

**Date:** May 2026
**Target venue:** EMNLP 2026 (ARR submission deadline May 25, 2026)
**Source reviews:** COLM 2026 (reviewers: onNX, g63y, mCRV, AUwY)

---

## Format Conversion: COLM → EMNLP (ACL Style)

- Converted from COLM LaTeX format to ACL 2026 style (`\usepackage[hyperref]{acl}`, `acl_natbib`)
- Condensed from 52-page COLM submission to 8-page EMNLP main-body limit
- Added mandatory EMNLP sections: **Limitations** and **Ethics Statement**
- All reviewer-driven edits marked with `\added{}`, `\deleted{}`, `\replaced{}{}` (via `changes` package)
- Every tracked change annotated with `% REVIEW: [Reviewer ID] - [description]`

---

## Changes Made in Response to COLM 2026 Reviews

### Terminology and Framing (all reviewers — mCRV, AUwY, onNX, g63y)

- **Replaced "causal links" → "directed dependency links"** throughout abstract, introduction, and §2. FMARD links are directional and conceptual, not formally validated causal mechanisms in the interventionist sense.
- **Softened "the causes of memorization" → "the training-time factors driving memorization"** in introduction to avoid implying formal causal claims.
- **Added explicit disclaimer in §2** that FMARD dependencies are directional/conceptual, organising the field by the natural flow from root causes to downstream harm rather than claiming formally validated causal mechanisms.

### FMARD Framework Clarifications (onNX, mCRV, AUwY)

- **Clarified Metric/Attack/Risk component boundaries** in §2: same scoring function (e.g., loss thresholding) can serve as a Metric when used offline or as part of an MIA Attack when deployed to classify membership — component assignment depends on evaluation intent and adversary capability, not the function itself.
- **Renamed Factor 4** from "Sampling and decoding" → "Inference-time decoding" to clarify it is adversary-accessible at test time, not a fixed training property. Added paragraph explaining decoding is de facto part of Attack configuration.
- **Added Factors 6 and 7** (training duration, alignment/RLHF) to §2.1 and Table 1, which were missing from the original factor taxonomy.
- **Revised Table 3 (Defenses)** "FMARD Link" column to use arrow notation (F, F→M, M→A, A→R) instead of vague English categories.
- **Added concrete FMARD worked example** in §3: illustrates how FMARD reveals that Loss achieves τ ≈ 0.035 on literary text vs. MinK%++ achieves τ ≈ 0.29 — directly addressing the "why does this framework matter?" critique.

### Empirical Scope Clarifications (mCRV, AUwY)

- **Scoped contribution (3)** in the introduction to explicitly name only the Metric→Attack (M→A) FMARD link on HUBBLE; remaining links (F→M, A→R, Defense links) are substantiated through cross-literature synthesis and flagged as open empirical questions.
- **Added acknowledgment** that F→M, A→R, and Defense links are not directly tested empirically in this paper.

### Related Work Additions (g63y, onNX)

- **Added Feldman (2020)** as primary theoretical grounding in §2.1: rare "long-tail" examples may require verbatim memorisation for generalisation, providing a formal basis for why memorisation arises.
- **Added Ippolito et al. (2023)** verbatim/approximate distinction in §2.2: verbatim memorisation admits exact string matching; approximate memorisation requires softer measures like ROUGE-L.
- **Added Li et al. (2021)** citation for DP utility-privacy tradeoff at web-scale in §2.4.

### Defenses Section (onNX)

- **Reorganised defenses** by FMARD link targeted rather than colloquial category.
- Explicitly acknowledged in Limitations that the Defense component is substantiated through literature synthesis rather than new controlled experiments.

### New Sections (EMNLP mandatory / reviewer-requested)

- **§ Limitations** (new, EMNLP mandatory): explicitly addresses (a) HUBBLE-only generalisability concern, (b) only M→A link tested empirically, (c) defense component is survey-only, (d) FMARD links are conceptual not interventionally causal.
- **§ Ethics Statement** (new, EMNLP encouraged): covers dual-use risks, dataset provenance, and responsible disclosure.

### Sections Resolved by Condensing (format comments)

- §2.5 "FMARD Across Training Stages": deleted from main body; content moved to Appendix A.
- Various length/detail comments: resolved by the 52→8 page condensing.

### New Appendix Sections (EMNLP revision — all tracked with `\added{}`)

- **I.13** (`app:external-validation`): External validation of M→A on `Pythia-6.9b-deduped` / WikiText-103 (600 sequences, greedy EM). Real experimental results: Loss τ = +0.070 (p = 0.012), ZLib τ = +0.084 (p = 0.002); Min-K% and MinK%++ inverted and non-significant on natural (low-duplication) text. Resolves `% TODO mCRV/AUwY` (external validity).

- **I.14** (`app:aligned-vs-base`): Aligned vs. base models — analyses whether RLHF suppresses M→A. Argues RLHF inserts a Defense at the A→output interface but does not change F→M or the underlying M→A correlation; supported by Nasr et al. 2023, Tirumala et al. 2022, Wolf et al. 2023, Pappu et al. 2024.

- **I.15** (`app:whitebox-attacks`): White-box attacks as upper bound on M→A. Shows τ = 0.08 is a conservative lower bound under adversarial gradient-based extraction; resolves the white-box limitation analytically. Supported by Carlini et al. 2021/2023, Nasr et al. 2023, Hayes et al. 2026. Partially resolves `% TODO mCRV/AUwY` (white-box attacks).

- **I.16** (`app:length-capacity`): Sequence length and model capacity as F→M factors. Synthesises Carlini et al. 2021 (length dominates memorisation), Biderman et al. 2023 (emergent capacity threshold), I.3 scale results, and I.13 length-quartile breakdown to explain the non-monotone τ-vs-length pattern.

- **I.17** (`app:unlearning-defense`): Unlearning defense — **actual experiment on Pythia-6.9b-deduped / WikiText-103** (N=50 top-EM sequences, gradient ascent on last 2 layers, 50 steps, lr=1e-5, bfloat16). Results: ΔLoss > 0 in 50/50; ΔEM < 0 in 49/50; τ(ΔLoss, ΔEM) = −0.256 (p=0.009); one sequence has ΔEM = +0.016 despite ΔLoss = +8.4 (largest in batch) — direct evidence that metric-verified unlearning does not certify extraction protection. Fully resolves `% TODO onNX`.

- **I.18** (`app:copyright-audit`): Copyright audit re-analysis using Cooper et al. 2025 published numbers; explains why passage-level M→A τ ≈ 0.035 does not contradict book-level memorisation variation.

### Resolved TODOs

All three `% TODO` items are now addressed in the paper (I.13 resolves external validity experimentally; I.14/I.15 address alignment and white-box attacks analytically; I.17 provides a **direct experiment** on Pythia-6.9b-deduped measuring τ(ΔLoss, ΔEM) = −0.256). The `% TODO` comment stubs remain in the source for traceability but are annotated with `[RESOLVED: ...]` comments.
