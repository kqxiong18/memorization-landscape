# Round 4 Review: "The Landscape of Memorization in LLMs: Mechanisms, Measurement, and Mitigation"

**Reviewer role:** Exceptionally strong main-track reviewer (NeurIPS / ICML / ICLR standards)
**Date:** May 2026
**Prior reviews consulted:** REVIEW_NeurIPS.md (Round 1), REVIEW_NeurIPS_v2.md (Round 2), Round 3 review and re-review from the current revision session
**Note:** This review assesses the paper in its current compiled state after all revisions to date. Items resolved in prior rounds are not re-litigated unless a new issue has been introduced.

---

## A. Summary

The paper proposes FMARD (Factor–Metric–Attack–Risk–Defense), a directed-dependency framework for organizing the LLM memorization literature. The central empirical claim is that statistical retention metrics (loss, Min-K%, ZLib) and operational extraction attacks (greedy exact match, ROUGE-L, probabilistic extraction) are weakly and Factor-dependently correlated: τ = 0.08 averaged across all configurations, varying from ~0.035 on literary prose to ~0.33 on structured text. The noise-attenuation alternative is now ruled out using the domain-dependent τ variation at moderate duplication (d ∈ {4,16,64}), with the d=256 sign inversion correctly demoted to a length-confound artifact. Tracked-change markup is now no-ops. The directed-dependency definition uses a modulation-based formulation. A SoK comparison table (Table I, Appendix) with an inline summary in §2 completes the differentiation argument. The paper is significantly improved over prior rounds.

---

## B. Strengths — Current Assessment

**B1. Correct falsifier for noise attenuation (new in this revision session).**
The domain-dependent τ variation at d ∈ {4,16,64} — where both metric and extraction families have genuine variance and length confounds are not yet dominant — is logically tight. A noise-attenuation model predicts a fixed attenuated positive correlation, not a qualitative difference between literary (τ ≈ 0.035) and structured text (τ ≈ 0.33). This is the paper's single strongest argument and is now correctly placed as the primary falsifier.

**B2. Sign-inversion correctly demoted.**
The §4.1 paragraph explicitly states that the d=256 sign inversion is "consistent with a noise-attenuation account of the length-adjusted signal and does not constitute independent evidence against construct distinctness." This is logically correct and avoids the circular contradiction present in prior drafts.

**B3. Attenuation formula properly hedged.**
The disattenuation formula is labeled as an approximation adapted from Pearson's correction, with an explicit note that the 0.48 convergent-validity figure does not satisfy the formula's assumptions. The estimate τ_true ≈ 0.12 is correctly labeled as an illustrative upper bound, not a formally derived value.

**B4. I.14 conclusion appropriately hedged.**
The aligned-vs-base conclusion now reads "RLHF preserves extractability (ΔEM = +0.0008) while weakening metric calibration," which is appropriately scoped to what the WikiText-103 experiment can establish.

**B5. SoK differentiation is now checkable.**
Table I provides a five-dimension structured comparison. The inline summary in §2 makes the differentiation argument visible in the main body without requiring a cross-reference. The Hartmann row uses "no quantitative link testing" rather than "no chain," which is both more accurate and harder to dispute.

**B6–B8 (prior strengths):** All original strengths (HUBBLE empirical grounding, actionable guidance, honest limitations) remain intact and are not degraded by the revision.

---

## C. Weaknesses — Current Assessment

### C1. τ Value Inconsistency Across Reporting Sites — **New, Critical**

Three different values are reported for what appears to be the same quantity (Loss vs. greedy EM at d=256):

- §4.3 text: "Loss and greedy extraction exhibit τ = −0.52"
- Conclusion: "varying from −0.53 to +0.42 across configurations"
- Figure 4 caption: "Loss vs. Sampling EM (blue) swings to τ ≈ −0.55"

Note: the figure caption says "Sampling EM" not "Greedy EM," which may explain −0.55 vs. −0.52, but the −0.52/−0.53 discrepancy for Loss vs. Greedy EM at d=256 is unresolved. Additionally, the upper bound of the range (+0.42) is reported only in the conclusion and never defined or attributed to a specific metric–attack pair anywhere in the main text — a reviewer cannot verify it.

**Required fix:** Reconcile −0.52 and −0.53; explicitly identify which metric–attack pair and duplication level yields +0.42 and −0.5x; ensure all three reporting sites agree.

### C2. Factor Taxonomy Internal Inconsistency — **New, Major**

§2.1 states: "The literature identifies **six** primary factors (Table~\ref{tab:factors})" and then enumerates **seven** factors in the text body: (1) Data duplication, (2) Model capacity, (3) Sequence length, (4) Inference-time decoding, (5) Tokenization and content characteristics, (6) Training duration, (7) Alignment (RLHF). The table itself lists only **six** rows (Data duplication, Model capacity, Sequence length, Decoding method, Training duration, Alignment), omitting Factor 5 (Tokenization and content characteristics) entirely. This is an internal inconsistency: the text promises six, enumerates seven, and the table contains six, but not the same six as the text.

**Required fix:** Either (a) update the count to "seven" and add Factor 5 to the table, or (b) remove Factor 5 from the enumeration if it is intentionally secondary.

### C3. Forward-Reference Circularity in §4.1 Noise-Attenuation Argument — **New, Major**

The noise-attenuation paragraph in §4.1 (sec:metric-attack) invokes domain-specific τ values (τ ≈ 0.035 on Gutenberg; τ ≈ 0.33 on MMLU) to serve as the primary falsifier of noise attenuation, and directs the reader to "§\ref{sec:empirical}" for these values. But §4.1 is a subsection of §\ref{sec:empirical} — the cross-reference points to the enclosing section, which includes the very paragraph making the forward claim. The actual τ values appear in §4.3, three subsections later. A reader working linearly will not have seen these numbers when they encounter the falsification argument.

**Required fix:** Either (a) move the noise-attenuation paragraph to after §4.3, where the domain-specific τ values have been formally reported, or (b) forward-reference §\ref{sec:factor-confounding} instead of the parent section, and flag it clearly as a forward reference.

### C4. Kendall τ Variant Not Specified — **New, Major**

Greedy exact match is a binary outcome (0/1). When one variable is binary, Kendall τ has many ties, and Kendall's τ-a and τ-b give different values (τ-b applies a tie correction in the denominator; τ-a does not). The paper never specifies which variant is used. For the signed values reported (−0.52, 0.08, 0.33), the choice of τ-a vs. τ-b may produce materially different numbers, and the z-test formula also differs. This is a reproducibility issue.

**Required fix:** Specify "Kendall's τ-b" (the standard choice when ties are present) in the setup paragraph of §4.

### C5. 1B Scale Result May Reflect Floor Effect, Not Construct Independence — **New, Moderate**

§4.3 reports "At 1B parameters, cross-family τ ≈ 0.00 across all duplication levels." This is presented as evidence that Factor (scale) modulates the M→A link. However, at 1B, greedy exact match rates approach zero (Gutenberg: 0.000 at d=256 per HUBBLE results). A near-constant binary outcome produces undefined or degenerate rank correlation regardless of what the metric family does — τ ≈ 0.00 at 1B may reflect a floor effect in EM rather than genuine construct independence. The result is compatible with noise attenuation on a degenerate signal, not only with factor-modulated construct separation.

**Required fix:** Report the EM extraction rate at 1B. If EM rates are near-zero, acknowledge that "τ ≈ 0.00 at 1B" is consistent with a floor effect and does not independently support construct distinctness.

### C6. "Stronger Than a Mere Correlation" Claim is Unsupported — **Residual, Minor**

§2 states that a directed dependency link is "stronger than a mere correlation: the link encodes the logical direction in which the memorization pipeline flows." The directionality of F→M→A→R→D is imposed by construction (Factors are upstream by definition; Metrics precede Attacks in the measurement pipeline). No empirical test establishes that the direction cannot be reversed or that the link is asymmetric. The claim does not undermine the paper's argument but may draw objections from formal reviewers.

**Suggested fix:** Replace with "directional by construction: the upstream component shapes the operating range of the downstream one, though we do not claim this directionality has been empirically validated against its reverse."

### C7. Stale Preamble Comment — **Minor Presentation**

Lines 12–15 of the preamble read: "soul must load before microtype: the changes package loads soul internally, which redefines \\showhyphens." The `changes` package is no longer loaded in this version; the comment describes a constraint that no longer applies. This does not affect compilation but may confuse a collaborator auditing the preamble.

**Suggested fix:** Replace with: "soul must load before microtype: both are loaded explicitly, and soul redefines \\showhyphens, which microtype \\CheckCommands."

---

## D. Questions for Authors

**D1.** Table 1 lists six factors. The text enumerates seven. Which is authoritative? If Factor 5 (Tokenization and content characteristics) is intentionally absent from the table, what is the reason?

**D2.** The conclusion reports a range of −0.53 to +0.42 across configurations. What specific metric–attack pair and duplication level yields τ = +0.42? This value is not reported in the main text. If it is MinK%++ vs. Greedy EM at d=64, it should be cited with its provenance.

**D3.** For the YAGO experiment: at d=0 (zero duplication insertions), email extraction accuracy is reported at 0.655–0.684 under intro/name prefix. If sequences were inserted at d=0, the model was not exposed to them during training. Is the email extraction accuracy at d=0 measuring memorization or the model's ability to generate plausible emails from biographical context (a form of pattern completion)? How does the paper distinguish these two accounts?

**D4.** Which variant of Kendall τ is used throughout — τ-a, τ-b, or τ-c? When one variable is binary (greedy EM), τ-b is standard. For the z-test significance computation, which standard error formula was applied?

---

## E. Novelty Assessment — Current

**Novelty: Moderate-to-Good.**

The paper's core novelty claim is now well-supported: FMARD is the only work to (a) model F→M→A→R→D as a dependency chain, (b) empirically test whether M→A link strength varies by Factor configuration, and (c) demonstrate qualitative domain-dependent τ variation under controlled conditions. Claims (a)–(c) are substantiated. Table I makes (a) checkable by comparison.

The updated abstract correctly frames the Factor-dependent pattern (0.035 vs. 0.33 by domain) as "the central finding" rather than the mean τ = 0.08. This is the right emphasis — the pattern is what is novel, not the mean.

Residual novelty concern: the domain variation partially reflects differences in base extraction rates rather than purely the M→A relationship, as the paper itself acknowledges in §4.3. The caveat is present but is a factual limitation on how strongly the 0.035/0.33 contrast can be attributed to the Metric→Attack relationship per se.

---

## F. Technical Soundness — Current

**Soundness: Good, with three specific residual concerns.**

The noise-attenuation argument is now the paper's strongest technical passage and is logically sound. The domain-dependent falsifier works: a single-construct noise model predicts a factor-independent attenuated positive correlation, not a qualitative sign change by content domain. The below-chance tail overlap provides additional convergent evidence.

**Remaining soundness concerns:**
1. τ value inconsistency (C1) introduces numerical unreliability; the −0.52/−0.53 discrepancy must be resolved before publication.
2. Kendall τ variant unspecified (C4) creates a reproducibility gap: the exact numbers depend on tie correction.
3. 1B floor-effect confound (C5) is a genuine technical limitation that should be disclosed.

---

## G. Significance — Current

**Significance: Moderate-to-high for the practitioner community; moderate for the NeurIPS/ICML theoretical audience.**

The threat-model-driven table (§5) is clean and directly actionable. The PII field-granularity finding (virtually all biographies are "mixed" at d ≤ 4; per-field τ < 0.12) is the paper's most practically consequential result and is well-supported. The unlearning gap (metric-verified unlearning does not certify extraction protection; I.17) is directly relevant to compliance practitioners.

For a theoretical audience, the paper does not advance formal understanding of why the M→A gap exists or bound its magnitude in principle. The HUBBLE setting (synthetic insertions, single architecture) limits generalization to the organic memorization distribution of production models.

---

## H. Presentation — Current

**Writing:** No regressions from the revision. The noise-attenuation paragraph reads well. The §5 table is cleaner than the prior prose form.

**Numerical consistency:** The τ = −0.52/−0.53/−0.55 inconsistency and the +0.42 upper bound without provenance are the most significant presentation problems in the current version.

**Factor table:** The six/seven discrepancy will catch reviewer attention.

**Stale comment in preamble:** Minor; does not affect the compiled output.

**Minor:** Lines ~218–244 (the merged §2 operational-definition paragraph) are dense — three distinct claims (directional nature, operational definition, component boundary) appear in one long paragraph. For an 8-page submission this is understandable, but a reader skimming for the definition will have difficulty locating it.

---

## I. Comparison to Related Work — Current

Table I now makes the comparison explicit and checkable. The five-dimension structure is appropriate. The Hartmann row uses "no quantitative link testing" — accurate and defensible. No new concerns here.

---

## J. Decision Recommendation

| Venue | Score | Label | Change from Round 2 |
|---|---|---|---|
| **NeurIPS** | **6** | Borderline accept | Unchanged |
| **ICML** | **6** | Borderline accept | — |
| **ICLR** | **5** | Borderline reject | — |
| **COLM 2026** | **7** | Accept | +1 from Round 1 |
| **EMNLP 2026** | **4** (Accept) | Accept | Unchanged |

**Reasoning for NeurIPS/ICML remaining at 6:**

The blocking markup issue (Round 1 C6) is resolved. The definition issue (Round 2 D-new-2) is resolved. The noise-attenuation argument (Round 2 C2, Round 3 §3.2 fix) is now the paper's strongest passage. The remaining obstacles to a 7 are:

1. The τ numerical inconsistency (C1) is a factual error that a reviewer checking numbers will flag as disqualifying until resolved.
2. The factor taxonomy discrepancy (C2) signals that the framework description was not fully reconciled after the Round 1 additions of Factors 6 and 7.
3. The τ variant (C4) and 1B floor-effect (C5) are methodological gaps that a technical reviewer will ask about.

**Reasoning for COLM 2026 reaching 7:**

COLM accepts survey/systematization papers with a lower empirical-scope bar than NeurIPS. The SoK contribution, the honest limitations, and the domain-dependent M→A finding are a strong fit. The residual issues (τ inconsistency, factor table) are fixable before camera-ready and do not undermine the core argument.

**Reasoning for ICLR at 5 rather than 6:**

ICLR reviewers weight architectural and theoretical novelty more than NeurIPS. The paper is explicitly a systematization/evaluation paper with no new model, training procedure, or theoretical result. The empirical scope (one architecture, one FMARD link directly tested) is narrow by ICLR standards. The venue fit is poor regardless of execution quality.

---

## K. Required Revisions Before Submission

| Priority | Item | Section |
|---|---|---|
| **[Critical]** | Reconcile τ = −0.52 (§4.3), −0.53 (Conclusion), −0.55 (Fig. 4 caption) for Loss vs. EM at d=256. Report the single authoritative value consistently. | C1 |
| **[Critical]** | Identify and report the metric–attack pair and duplication level that yields τ = +0.42 (Conclusion τ range upper bound). | C1 |
| **[Major]** | Fix factor taxonomy: update "six primary factors" to "seven" and add Factor 5 (Tokenization) to Table 1; or remove Factor 5 from the enumeration and explain its absence. | C2 |
| **[Major]** | Move or re-anchor the noise-attenuation paragraph: it invokes τ values (0.035, 0.33) reported three subsections later. Either place the paragraph after §4.3, or forward-reference §\ref{sec:factor-confounding} explicitly. | C3 |
| **[Major]** | Specify "Kendall's τ-b" in the setup paragraph and confirm that the z-test uses the τ-b standard error formula. | C4 |
| **[Major]** | Report EM extraction rates at 1B (or their near-zero nature) and acknowledge that τ ≈ 0.00 at 1B may reflect a floor effect, not construct independence. | C5 |
| **[Moderate]** | Revise "stronger than a mere correlation" to a defensible formulation. | C6 |
| **[Moderate]** | Address YAGO d=0 email extraction (0.655–0.684): distinguish memorization from pattern completion from biographical context. | D3 |
| **[Minor]** | Fix stale preamble comment (changes package no longer loaded; comment describes old constraint). | C7 |
| **[Minor]** | Add 95% confidence intervals to the primary τ values (n=143 per cell at d=256; SE ≈ 0.084, CI width ≈ ±0.16). | — |

---

## L. Summary of Top Strengths

1. **Domain-dependent τ variation as noise-attenuation falsifier** (τ ≈ 0.035 on Gutenberg vs. τ ≈ 0.33 on MMLU at moderate duplication) is the cleanest empirical argument in the paper and is now correctly positioned as the central finding.
2. **Limitations section** is among the most specific and honest in the memorization literature — every unvalidated link is named, and three appendix experiments are offered as partial external evidence.
3. **SoK comparison (Table I + inline §2 summary)** makes FMARD's incremental contribution directly checkable. The five-dimension structure is appropriate and the Hartmann characterization is now defensible.

---

## M. Summary of Top Weaknesses

1. **τ numerical inconsistency** (−0.52/−0.53/−0.55 for what appears to be the same quantity; +0.42 upper bound without provenance) is a factual reliability problem that will cause rejection at NeurIPS without correction.
2. **Factor taxonomy discrepancy** (text says "six," enumerates seven, table has six different rows) signals incomplete reconciliation after the Round 1 taxonomy expansion — a reviewer auditing §2.1 will catch it.
3. **Methodological underspecification** (τ-a vs. τ-b for binary EM outcome; 1B floor effect not disclosed) are reproducibility and soundness gaps that technical reviewers will flag.

---

## N. Final Note on Venue

The strongest target remains **EMNLP 2026**. After fixing the [Critical] and [Major] items above, the paper should receive an Accept. The controlled empirical contribution (domain-dependent M→A correlation, PII field-granularity finding, unlearning I.17 experiment) is well-calibrated to an NLP evaluation audience, and the practical guidance is directly relevant to EMNLP practitioners.

For **NeurIPS or ICML**, fixing the same items would move the score from 6 to 7 (accept), but the path to acceptance depends on how the area chair weights a systematization paper with one directly tested link. The 8-page condensed format works well for EMNLP but leaves some architecture and methodology details in appendices that NeurIPS reviewers would expect in the main body.

**COLM 2026** is an excellent fit: the SoK framing, the evaluation methodology focus, and the controlled benchmark setting align with COLM's scope, and the score would reach 7–8 after the critical revisions.
