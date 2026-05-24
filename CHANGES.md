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

### Pending (marked % TODO in source)

- `% TODO mCRV/AUwY`: Replicate M→A correlation analysis on a non-HUBBLE model (e.g., LLaMA-3-8B-base on Pile) to establish external validity.
- `% TODO mCRV/AUwY`: Extend empirical evaluation to soft-prompt (white-box) attacks to test whether M→A τ changes under a stronger adversary.
- `% TODO onNX`: Add controlled defense experiment within HUBBLE setup (apply DP-SGD and unlearning; measure whether M→A τ changes).
