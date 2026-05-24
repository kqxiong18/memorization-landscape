# NeurIPS Main-Track Review (Round 2): "The Landscape of Memorization in LLMs: Mechanisms, Measurement, and Mitigation"

**Reviewer role:** Exceptionally strong NeurIPS main-track reviewer  
**Date:** May 2026 (revised submission)  
**Prior review:** REVIEW_NeurIPS.md (Round 1)  
**Note:** This review assesses the revised paper against the same 13-dimension NeurIPS rubric. Each section notes whether the prior concern was resolved, partially resolved, or residual, and identifies new issues introduced by the revision.

---

## A. Summary of Revision

The revision addresses five of six prior concerns: it adds an operational definition of "directed dependency link" (§2), a structured SoK comparison table (Appendix Table I), a noise-attenuation rebuttal paragraph (§3.2), strengthened empirical-scope acknowledgments in the Contributions list and Limitations, and dataset-choice clarification notes in I.13 and I.14. A new Mistral-7B citation is added to the bibliography. The tracked-change markup (C6) remains in the document and is the only blocking presentation issue that persists.

---

## B. Strengths — Updated Assessment

All five original strengths remain. Three are further strengthened by the revision:

**B1 (correct problem).** Unchanged.

**B2 (HUBBLE empirical grounding).** The new noise-attenuation paragraph makes the sign-inversion argument explicit and quantified, strengthening the central empirical claim.

**B3 (actionable guidance).** Unchanged.

**B4 (honest limitations).** Significantly strengthened. The Limitations section now explicitly names all five FMARD links, distinguishes directly tested (M→A) from synthesis-supported (F→M, A→R, Defense links), and points to three specific appendix experiments as partial external evidence.

**B5 (appendix experiments).** The I.13 and I.14 dataset-choice notes add clarity about what these experiments do and do not establish, making the calibrated claims more credible.

**New strength B6:** The SoK comparison table (Table I, Appendix Related Work) is a genuine addition that was missing from the original submission. The five-dimension comparison — particularly the rows on Factor-dependent modulation and cross-study contradiction — makes FMARD's incremental contribution visible in a form that a reviewer can verify directly.

---

## C. Weaknesses — Updated Assessment

### C1. SoK differentiation — **Substantially Resolved; One Residual Issue**

**What changed:** Table I in the appendix provides the structured comparison that was missing. The §2 body now contains a pointer paragraph that includes the operational definition of "directed dependency link" and an explicit sentence directing readers to Table I. The Hartmann paragraph in Appendix Related Work now notes that Hartmann et al. "note that MIA and extraction attacks measure different things, but do not frame this as a modulated M→A link or provide empirical evidence that the two families rank sequences differently under controlled conditions."

**Residual issue:** The comparison table is placed entirely in the appendix with only a sentence pointer in the main body. For an EMNLP 8-page submission this is understandable, but a reviewer reading only the main body will not see the table and must follow a cross-reference. A condensed two-column summary row in §2 (e.g., one sentence listing what FMARD adds over Hartmann: "dependency chain + empirical M→A test + Factor-dependent modulation") would make the differentiation argument self-contained in the main text.

**Residual factual concern:** The table characterises Hartmann et al. 2023 as "Partial (definitions + implications, no chain)" on the first dimension. Hartmann et al. do discuss a flow from memorization mechanisms to implications across privacy, copyright, and auditing domains — a rudimentary chain. "Partial (no quantitative link testing)" would be both more accurate and harder to dispute.

**Assessment:** Concern substantially mitigated. Not yet fully resolved for a reviewer who reads only the main body, and one characterisation is debatable.

### C2. τ = 0.08 noise-attenuation interpretation — **Resolved; One Technical Caveat**

**What changed:** The new §3.2 paragraph computes an attenuation-corrected estimate τ_true ≈ 0.08/0.69 ≈ 0.12, then correctly notes this correction is bounded above (noise only dampens positive signal, cannot invert sign). The d=256 sign inversion (τ = −0.52) and below-chance tail overlap (0.077 < 0.10 random baseline) are offered as direct falsifiers of the noise account.

**This is the strongest new addition in the revision.** The argument is logically sound and uses only numbers already in the paper.

**Technical caveat:** The disattenuation formula τ_true = τ_obs / √(r_M · r_A) is borrowed from Pearson's formula for correcting for attenuation. Kendall τ does not have the same algebraic disattenuation properties as Pearson r — the formula is an approximation at best. A technical reviewer may object. The main argument (sign inversion rules out pure-noise account) is valid independently of the formula; the quantitative estimate of τ_true ≈ 0.12 is illustrative rather than formally derived. The paper should add a footnote acknowledging this.

**Assessment:** Conceptually resolved. The sign-inversion argument is clean and persuasive. The quantitative formula should be hedged.

### C3. Empirical scope — **Substantially Addressed; Structural Gap Remains**

**What changed:** Contribution (3) now lists F→M, A→R, Defense→F, and Defense→M→A explicitly as links not directly tested, with named appendix experiments as partial external evidence. The Limitations section opens with a `\replaced{}` paragraph that explicitly states "only the M→A link directly, out of five links in the FMARD chain."

**Residual structural gap:** The gap itself is not closed by this revision — F→M, A→R, and Defense links are still not tested under controlled conditions. This is acknowledged clearly, which is the right move for an honest paper, but it remains a genuine limitation at NeurIPS standards. The acknowledgment language is appropriate.

**Assessment:** The claim is now well-calibrated to the evidence. The underlying gap remains but is no longer overclaimed.

### C4. HUBBLE generalizability — **Partially Addressed**

**What changed:** I.13 "Dataset choice note" explains that The Pile validation split is non-member data, clarifying this is an M→A correlation experiment rather than MIA. The I.14 note acknowledges WikiText-103 is in Mistral's training mix (hence in-distribution) but that membership cannot be certified without access to the original training corpus.

**Residual issue:** The I.14 note adds honesty but also highlights a gap: the comparison between base and aligned models is performed on text that is in-distribution but not confirmed training data. This means the baseline metric values (loss, Min-K%) are those of a model that may be generating these sequences based on general Wikipedia-style text understanding rather than verbatim memorization. The ΔEM = +0.0008 result is therefore measuring whether RLHF suppresses *in-distribution generation*, not necessarily *memorized-content extraction*. The note acknowledges this limitation, but the interpretation of the I.14 result in the main body (§app:aligned-vs-base) does not fully update to reflect it — the text still concludes "RLHF does not reduce underlying extractability," which is a stronger claim than what WikiText-103 (without confirmed membership) supports.

**Assessment:** Substantially improved in transparency. The main text conclusion in I.14 should be hedged one degree further to reflect the non-certified membership caveat.

### C5. Framework definition precision — **Resolved; One Logical Issue**

**What changed:** The new §2 operational definition states that a directed dependency link X→Y asserts: (1) X is a necessary precondition for Y to have any signal (removing X makes Y degenerate), and (2) properties of X modulate the strength or character of Y.

**New logical issue introduced:** Condition (1) — "X is a necessary precondition for Y to have any signal" — is too strong and is not satisfied by any FMARD link in the paper. Specifically:
- Removing Factors does not make Metrics degenerate: Metrics (loss, Min-K%) have non-zero values on any text, including text with d=0 in HUBBLE.
- Removing Metrics does not make Attacks degenerate: extraction attacks succeed or fail independently of whether anyone computes a metric score.
- The d=0 condition in HUBBLE already demonstrates that Metrics have signal even when the Factor (duplication) is absent.

Condition (1) should be revised to: "X is a significant predictor of Y's magnitude or direction across the empirically relevant range" — or dropped in favour of the modulation claim alone (Condition 2), which is accurate and supported. The current formulation introduces a claim the paper does not and cannot support.

**Assessment:** The addition of a definition is the right move. The definition needs correction on Condition (1).

### C6. Changes-package markup in PDF — **Not Addressed**

`\added{}`, `\deleted{}`, and `\replaced{}{}` still render in the document. This is still the single most urgent pre-submission fix.

---

## D. New Issues Introduced by the Revision

### D-new-1. Attenuation formula applicability (§3.2)

As noted in C2: the Spearman-Brown / Pearson disattenuation formula is applied to Kendall τ without justification. Add a footnote: "The disattenuation formula is adapted from Pearson's correction and is an approximation for rank correlations; we use it as an illustrative upper bound, not a formally derived estimate."

### D-new-2. Condition (1) in the "directed dependency link" definition (§2)

As noted in C5: "necessary precondition" is not supported by any FMARD link. Revise to a modulation-based formulation or remove Condition (1) entirely.

### D-new-3. I.14 conclusion hedging (Appendix I.14)

The empirical paragraph concludes "RLHF alignment does not reduce underlying extractability." The I.14 dataset note acknowledges the sequences may not be confirmed training members. These two statements are in tension. The conclusion should read: "RLHF does not suppress in-distribution greedy generation; under confirmed training-member probing, extractability suppression may differ."

### D-new-4. Main-body accessibility of Table I

The SoK comparison table lives in the appendix. Given that C1 was a "critical" concern in Round 1, the differentiation argument should be visible in the main body without requiring a cross-reference. Even a two-sentence inline summary in §2 — "Unlike Hartmann et al. (2023) and Meeus et al. (2025), who catalog components descriptively, FMARD models them as a dependency chain and empirically tests whether link strength is Factor-modulated (see Table I, Appendix)" — would substantially improve this.

---

## E. Novelty Assessment — Updated

The addition of Table I and the noise-attenuation argument makes the novelty more legible. The core novelty claim is now: FMARD is the only work to (a) model F→M→A→R→D as a dependency chain, (b) empirically test whether M→A link strength varies by Factor configuration, and (c) show that the sign of the M→A correlation can invert across Factor settings.

Claims (a)–(c) are substantiated by the evidence in the paper. The table makes (a) checkable. The sign inversion makes (c) compelling.

**Revised novelty assessment: Moderate-to-Good.** The core insight remains an organization of known facts, but the empirical characterization of M→A as a Factor-modulated, sign-invertible link is a genuinely new empirical finding, not merely a re-labeling.

---

## F. Technical Soundness — Updated

The noise-attenuation paragraph strengthens the empirical soundness of §3.2. The dataset-choice notes in I.13 and I.14 are honest about scope. The d=256 sign inversion argument (τ = −0.52 as direct falsifier of noise-attenuation) is clean.

**Remaining soundness issue:** Condition (1) of the directed-dependency definition is not satisfied by the paper's own data (Metrics have signal at d=0). This is an internal inconsistency that should be fixed before submission.

**Overall: Good.**

---

## G. Significance — Updated

Unchanged: Moderate-to-high for practitioners; moderate for NeurIPS theoretical audience. The I.14 experiment adds practical significance (RLHF does not suppress EM) but its interpretation is somewhat undermined by the non-certified membership caveat.

---

## H. Presentation — Updated

**Main body writing:** No regressions from the revision. The noise-attenuation paragraph reads well and is well-placed. The operational definition paragraph in §2 is clear but needs Condition (1) revised.

**Table I:** Well-structured. The characterization of Hartmann 2023 as "no chain" should be revised to "no quantitative link testing."

**Still-blocking issue:** `changes` package markup (C6). Remove before submission.

**Minor new presentation issue:** §2 now has three consecutive `\added{}` paragraphs (conceptual/directional claim, operational definition, component boundary note). These read somewhat fragmented. Consider merging the first two into a single paragraph.

---

## I. Comparison to Related Work — Updated

Table I (Appendix) now makes this comparison explicit and reviewable. The five-row structure covers the most important differentiating dimensions. The comparison is fair to Satvaty 2024 and largely fair to Meeus 2025; the Hartmann 2023 characterization needs minor revision (see C1 residual).

---

## J. Decision Recommendation — Updated

**Recommended score (NeurIPS scale): 6 — Borderline accept**  
**Confidence: 4 — Confident**  
**Change from Round 1: +1 (from 5 to 6)**

**Reasoning for upgrade:**  
- C1 (SoK differentiation): Substantially addressed by Table I. This was the primary reason for the Round 1 reject recommendation.
- C2 (noise attenuation): Cleanly resolved; the sign-inversion argument is the strongest new addition.
- C3 (empirical scope): Acknowledged precisely in Limitations. The claim is now well-calibrated.
- C5 (definition): Addressed, though Condition (1) needs correction.

**Reasons the score does not reach 7 (accept):**  
1. Table I is in the appendix, not the main body. A reviewer reading the 8-page main body cannot directly verify the SoK differentiation claim without a cross-reference.
2. Condition (1) of the directed-dependency definition is not supported by the paper's own data, introducing an internal inconsistency.
3. The I.14 conclusion ("RLHF does not reduce underlying extractability") overreaches relative to the non-certified membership caveat added by the dataset note.
4. C6 (tracked-change markup) blocks final submission.

**Score at EMNLP: 7 (accept)** — these residual issues are not fatal at EMNLP standards; the paper makes a clear contribution, is honest about scope, and the empirical results are sound.

---

## K. Required Revisions Before Submission — Updated

| Priority | Item | Status |
|---|---|---|
| **[Blocking]** | Remove `changes` package markup (C6) | Not addressed |
| **[Major]** | Revise Condition (1) of directed-dependency definition: "necessary precondition" is empirically false; replace with modulation-based formulation | New issue (D-new-2) |
| **[Major]** | Add footnote to §3.2 attenuation formula: "adapted from Pearson correction; an approximation for rank correlations" | New issue (D-new-1) |
| **[Major]** | Revise I.14 main conclusion: hedge "RLHF does not reduce extractability" → "does not suppress in-distribution greedy generation; confirmed-member test remains open" | New issue (D-new-3) |
| **[Moderate]** | Add 1–2 sentence inline SoK differentiation summary in §2 main body (not just appendix pointer) | D-new-4 |
| **[Minor]** | Revise Table I Hartmann row: "no chain" → "no quantitative link testing" | C1 residual |
| **[Minor]** | Merge the three consecutive `\added{}` paragraphs in §2 into one or two | H presentation |

---

## L. Resolved Items from Round 1

| Round 1 item | Resolution |
|---|---|
| C1: Insufficient SoK differentiation | **Substantially resolved** — Table I added; §2 pointer added; Hartmann paragraph explicitly notes what prior work did not do |
| C2: τ=0.08 noise-attenuation interpretation | **Resolved** — §3.2 paragraph computes τ_true ≈ 0.12 and rules it out via sign inversion |
| C3: Empirical scope | **Substantially addressed** — Limitations explicitly names all five links and their evidential status |
| C4: HUBBLE generalizability | **Partially addressed** — I.13 and I.14 notes add transparency about what the external experiments establish |
| C5: Framework definition precision | **Addressed with issues** — definition added but Condition (1) is logically problematic |
| D3: I.13 dataset choice | **Resolved** — "Dataset choice note" clarifies The Pile validation is non-member; purpose is M→A correlation, not MIA |
| D4: I.14 WikiText-103/Mistral | **Addressed** — new note acknowledges Wikipedia in Mistral's training mix but non-certified membership |

---

## M. Summary

**What is now convincing:**  
The paper's central empirical claim — that M→A is a weak, sign-invertible, Factor-modulated correlation — is well-supported and the noise-attenuation alternative is persuasively ruled out. The SoK comparison table makes the incremental contribution legible. The Limitations section is now among the most honest and specific in the recent memorization literature.

**What still requires revision:**  
The directed-dependency definition's Condition (1) is an internal inconsistency that should be corrected. The I.14 conclusion overreaches its evidential basis. The tracked-change markup must be stripped before any submission. The SoK table should be summarised in one sentence in the main body.

**Venue recommendation:** Accept at EMNLP 2026 after addressing the [Blocking] and [Major] items above. For NeurIPS, additional empirical work on at least one other FMARD link (F→M under a non-HUBBLE setting, or A→R) would strengthen the case for acceptance above 6.
