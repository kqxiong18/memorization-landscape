# NeurIPS Main-Track Review: "The Landscape of Memorization in LLMs: Mechanisms, Measurement, and Mitigation"

**Reviewer role:** Exceptionally strong NeurIPS main-track reviewer  
**Date:** May 2026  
**Note:** This review applies NeurIPS standards (higher bar than EMNLP) to an EMNLP 2026 submission. Scores and recommendations are calibrated for the NeurIPS context.

---

## A. Summary

The paper proposes FMARD (Factor–Metric–Attack–Risk–Defense), a framework that organizes the memorization-in-LLMs literature through directed dependency links rather than descriptive categories. The central empirical claim is that statistical retention metrics (loss, Min-K%, ZLib) and operational extraction attacks (greedy exact match, ROUGE-L, probabilistic extraction) are weakly correlated (Kendall τ = 0.08, p < 10⁻⁴) when evaluated jointly on 21,000 sequences from the HUBBLE controlled benchmark (Llama-3, 1B and 8B, duplication levels d ∈ {0,1,4,16,64,256}). The paper characterizes three failure modes—link mismatch, factor confounding, and cross-link interference—and argues that FMARD explains why different studies reach contradictory conclusions about the same model families. Practical threat-model-driven evaluation guidelines are derived for copyright, PII, and regulatory compliance use cases. Appendices add external validation on Pythia-6.9b-deduped/WikiText-103, an alignment (RLHF) experiment on Mistral-7B, and an unlearning defense experiment.

---

## B. Strengths

**B1. Correct and important problem statement.**  
The field genuinely suffers from the fragmentation the paper describes. Duan et al. 2024 and Nasr et al. 2023 do reach opposite conclusions about Pythia-class models, and this is a real source of confusion for practitioners. Naming the failure modes explicitly (link mismatch, factor confounding, cross-link interference) is a substantive contribution that improves on prior cataloguing work.

**B2. HUBBLE-backed empirical grounding.**  
The use of HUBBLE provides something rare: ground-truth membership, calibrated duplication, and a controlled architecture. The sign inversion at d=256 (τ = −0.52, Loss vs. Greedy EM) is a clean, surprising result that would be invisible without the controlled setup. The factor-confounding analysis (sequence length driving the inversion via τ(Loss, length) = +0.78 and τ(EM, length) = −0.47) is a good example of FMARD-guided diagnosis.

**B3. Actionable practical guidance.**  
The threat-model-driven section (§5) translates abstract framework claims into concrete protocol differences. Practitioners who currently use perplexity for copyright audits will find the τ ≈ 0.035 figure on literary text directly useful.

**B4. Honest limitation disclosure.**  
The paper explicitly names: (a) single architecture scope, (b) only M→A link tested empirically, (c) defenses validated through synthesis not experiment, (d) directional/conceptual rather than interventionally causal links. This level of transparency is appropriate and appreciated.

**B5. Appendix experiments add credibility.**  
The external validation on Pythia-6.9b-deduped (I.13: Loss τ = +0.070, p = 0.012; ZLib τ = +0.084, p = 0.002), the RLHF experiment (I.14: ΔEM = +0.0008, confirming RLHF does not suppress extractability), and the unlearning defense experiment (I.17: τ(ΔLoss, ΔEM) = −0.256, p = 0.0088) are methodologically careful and directly address the limitations named in the main body.

---

## C. Weaknesses

**C1. Differentiation from prior SoK papers is insufficient. [Critical]**  
Hartmann et al. 2023 ("SoK: Memorization in General-Purpose Large Language Models") and Meeus et al. 2025 ("SoK: Memorization in Foundation Models") are both systematization-of-knowledge papers covering overlapping terrain. The paper cites both but does not provide a structured comparison showing what FMARD adds beyond these works. Specifically:

- Hartmann et al. already distinguish extraction attacks from membership inference attacks and note they measure different phenomena.
- Meeus et al. already show that WikiMIA AUC inflation is explained by distribution shift—a direct instance of what the paper calls "factor confounding."

Without an explicit comparison table or paragraph-level differentiator, a reviewer familiar with these prior works cannot easily assess the incremental contribution of the FMARD naming and framing.

**C2. τ = 0.08 alternative interpretation is not ruled out. [Critical]**  
The paper interprets τ = 0.08 as evidence that metrics and attacks "target different properties." But a simpler interpretation is that both families are individually noisy measurements of the same underlying latent memorization, and their cross-family correlation is attenuated by measurement noise (i.e., τ = 0.08 ≈ ρ_true × √(reliability_A × reliability_B) under a noise attenuation model). The paper does not rule out this alternative: if intra-family τ = 0.48 for metrics and τ = 0.99 for extraction metrics, then the geometric mean ≈ 0.69, and τ_cross = 0.08/0.69 ≈ 0.12 corrected for attenuation—still low, but the gap between "low cross-family correlation due to different constructs" and "low cross-family correlation due to mutual noise with shared underlying signal" is not addressed. The d=256 sign inversion is good evidence against the pure-noise interpretation, but this argument is not made explicitly.

**C3. Empirical scope covers only one FMARD link. [Major]**  
Only the M→A link is tested directly. F→M is tested only indirectly (the AUC vs. negative-control establishes metrics detect something, not that factors causally determine it within the framework). A→R is untested (the paper cites prior work). Defense links are synthesis-only. For a framework paper claiming to organize an entire research area, the empirical coverage is narrow. The Limitations section acknowledges this, but acknowledgment alone does not resolve the gap for NeurIPS standards.

**C4. HUBBLE generalizability is unclear. [Major]**  
HUBBLE inserts sequences into a model trained on a controlled corpus at known duplication counts. Real-world pre-trained models (GPT-4, LLaMA-3, Mistral) have organic memorization distributions without ground-truth duplication labels. The external validation (I.13) uses WikiText-103 which has its own biases (high-quality, encyclopedic text; not PII or copyright-sensitive content). The claim that FMARD-guided evaluation applies across real deployments rests on thin evidence beyond these appendix results.

**C5. Framework definition lacks formal precision. [Minor]**  
FMARD is presented descriptively. The "directed dependency link" terminology is claimed to be more rigorous than prior taxonomies, but the dependencies are never formally defined (e.g., as probabilistic graphical model edges, partial orderings, or functional relationships). Given the explicit disclaimer that these are "directional and conceptual, not interventionally causal," the word "dependency" in the name may mislead readers into expecting more formal guarantees than the paper provides.

**C6. Changes-package markup renders in the PDF. [Presentation—Urgent]**  
The paper uses `\added{}`, `\deleted{}`, `\replaced{}{}` from the LaTeX `changes` package, which renders colored boxes and strikethrough text showing prior reviewer comments in the submitted PDF. This is a serious presentation problem: it exposes the review history, creates a confusing reading experience, and fails basic double-blind hygiene. This must be removed before any submission by commenting out or replacing the `changes` package with a no-op definition. This is not a scientific weakness but it is the single most urgent revision needed.

---

## D. Questions for Authors

1. **D1.** Can you provide a structured differentiator (table or paragraph) comparing FMARD against Hartmann 2023 and Meeus 2025 at the level of: (a) coverage of the F→M→A→R→D chain, (b) empirical grounding, (c) which failure modes each identifies? Without this, the incremental contribution is difficult to assess.

2. **D2.** For the τ = 0.08 finding: can you address the measurement noise / attenuation alternative interpretation? Specifically, what is the estimated true-score correlation after correcting for intra-family reliability, and does it meaningfully differ from 0.08?

3. **D3.** The I.13 external validation uses WikiText-103 (encyclopedic, low-duplication text). Is there a reason not to use The Pile validation set (which Pythia-6.9b-deduped was trained on) for a more faithful membership inference test? If The Pile was unavailable, please clarify why.

4. **D4.** The RLHF experiment (I.14) uses WikiText-103 for a base Mistral-7B model. WikiText-103 is not in Mistral's training set and is not aligned content. How does this choice affect the interpretation? Would the result change if sequences known to be in the training data were used?

5. **D5.** Table 3 (Defenses) still uses `\replaced{}{}` markup showing both the old and new column header simultaneously. This affects readability independent of the changes package issue. What was the original column header, and why was it changed?

---

## E. Novelty Assessment

**Novelty: Moderate.**  
The FMARD naming and the three failure modes (link mismatch, factor confounding, cross-link interference) are new organizational contributions. The HUBBLE empirical study is new. The sign inversion result and the field-level PII granularity finding are new. However, the core insight—that loss-based metrics and extraction attacks measure different things—has been noted informally by Nasr et al. 2023, Duan et al. 2024, and implicitly by Meeus et al. 2025. FMARD formalizes and names this insight but the naming is the primary novelty, not a discovery. This is a legitimate contribution at the right venue (EMNLP, ACL) but is below the novelty bar typically expected at NeurIPS.

---

## F. Technical Soundness Assessment

**Soundness: Good, with caveats.**  
The Kendall τ computation is standard. The use of HUBBLE's ground-truth membership enables valid within-study inferences. The sign inversion analysis (attributing −0.52 to sequence length as common cause) is sound and well-supported. The unlearning experiment (I.17) is small (n=50) but the finding (one failure case: ΔEM = +0.016 despite the largest ΔLoss = +8.4) is interesting and not cherry-picked (reported per the paper's disclosed protocol). The main concern is the narrow scope (see C3) and the HUBBLE-specific generalization (see C4), not errors in the reported analyses.

---

## G. Significance Assessment

**Significance: Moderate-to-high for the practitioner community.**  
The practical guidance sections (§4.1, §5) translate directly into better evaluation protocols. The finding that loss does not predict extraction on literary text (τ ≈ 0.035) is precisely the kind of actionable negative result that prevents wasted evaluation effort. For the NeurIPS ML theory and systems audience, the significance is lower because the paper does not advance our formal understanding of why the gap exists or how large it can be in principle.

---

## H. Presentation Assessment

**Writing: Clear and well-organized.** The three-section structure (framework → cross-literature analysis → controlled empirical study) is logical. Claims are hedged appropriately. The abstract accurately represents the paper's scope. Section 4 (Controlled Empirical Study) is well-written and the FMARD-diagnosis framing of each result is consistently applied.

**Critical presentation issue:** The tracked-change markup (C6) must be removed before submission. It is currently the most visible problem in the paper.

**Minor presentation issues:**
- Tables 1, 3, and 4 risk overflow in ACL two-column layout; the use of `\footnotesize` and explicit `p{}` widths should be verified by compiling locally.
- Figure placement at `[!ht]` in a 2-column ACL document may produce unexpected float positioning; verify in the compiled output.
- Section 2.5 ("FMARD Across Training Stages") is conditionally excluded via `\iffalse...\fi`; this LaTeX technique is fine but may confuse reviewers who read the source.

---

## I. Comparison to Related Work

| Paper | Scope | Failure modes identified | Empirical grounding |
|---|---|---|---|
| Hartmann et al. 2023 (SoK) | Full taxonomy by implication type | Implicit (no framework) | Survey only |
| Satvaty et al. 2024 | Survey by topic | None | Survey only |
| Meeus et al. 2025 (SoK) | Attack vectors + benchmark critique | Distribution shift in WikiMIA | Benchmark reanalysis |
| **This paper (FMARD)** | Directed dependency chain | 3 named failure modes | HUBBLE + appendix experiments |

FMARD is the only work among these to (a) formally decompose F→M→A→R→D as a dependency chain and (b) test the M→A link empirically under controlled factor variation. However, the above comparison should appear in the paper itself to make the differentiation visible to reviewers.

---

## J. Decision Recommendation

**Recommended score (NeurIPS scale):** 5 — Borderline reject  
**Confidence:** 4 — Confident  

**Reasoning:** The paper makes a real contribution: FMARD names and organizes a set of failure modes that the field has been encountering informally, and the HUBBLE empirical study provides clean, controlled evidence for the central M→A disconnect claim. The three appendix experiments (I.13, I.14, I.17) add credibility and address the most important external validity concerns. However, for NeurIPS:

1. The differentiation from Hartmann 2023 and Meeus 2025 is not adequately argued; a reviewer familiar with those papers will struggle to identify the incremental contribution beyond naming.
2. The empirical scope (one link out of five, one model architecture) is narrow for a framework paper claiming to organize an entire research area.
3. The tracked-change markup in the PDF is a submission-blocking presentation problem.

**Recommendation for EMNLP:** The paper is a strong fit for EMNLP at a score of 6 (weak accept / borderline accept). The contributions are appropriate in scope for an NLP venue, the practical guidance is directly relevant to the EMNLP audience, and the controlled empirical study is a genuine asset. The tracked-change markup must be removed before submission.

---

## K. Required Revisions Before Submission

1. **[Blocking]** Remove `changes` package tracked-change markup. Replace with final text or use no-op macro definitions. This applies to all `\added{}`, `\deleted{}`, and `\replaced{}{}` calls throughout the document.

2. **[Blocking]** Add a structured comparison to Hartmann 2023 and Meeus 2025 (ideally a table in §2 or §3 showing what FMARD adds beyond each). Without this, reviewers familiar with the prior SoK literature will assign the paper a low novelty score.

3. **[Major]** Address the noise attenuation interpretation of τ = 0.08 in §3.2. The sign inversion at d=256 already provides good evidence, but the argument needs to be made explicitly.

4. **[Major]** In I.14, clarify whether WikiText-103 sequences are known/unknown to Mistral-7B-v0.1. The base model's relationship to this evaluation corpus is not established, weakening the alignment comparison.

5. **[Minor]** Compile the final PDF and verify Table 1, 3, 4 do not overflow. Verify Figures 2–5 appear at their citation locations (not drifted to end of section or page).

6. **[Minor]** Add a brief note in §2 clarifying what "directed dependency link" means operationally—is it a correlation, a partial order, a causal assumption? The disclaimer that links are "conceptual not causal" is good, but the word "dependency" still implies more than what is claimed.

---

## L. Summary of Top Strengths

1. Clean controlled experiment (HUBBLE) with genuine signal: the d=256 sign inversion and the 7.7% vs. 10% expected top-decile overlap are surprising, reproducible, and directly support the central claim.
2. Honest, specific limitation section that names exactly which links are not empirically validated.
3. Appendix experiments (I.13, I.14, I.17) are methodologically careful and directly answer the main objections a reviewer would raise.

## M. Summary of Top Weaknesses

1. Insufficient differentiation from Hartmann 2023 and Meeus 2025: both already note the metric/attack distinction informally, and without an explicit comparison the incremental contribution is unclear.
2. Only one of five FMARD links (M→A) is directly tested; for a framework paper this is a significant empirical gap.
3. τ = 0.08 alternative interpretation (measurement noise attenuation rather than conceptually distinct constructs) is not formally ruled out.

## N. Final Note on Venue

This paper is best positioned at EMNLP 2026 or ACL 2026. At NeurIPS, the novelty-per-page bar is higher and the audience is less familiar with the specific benchmarks (HUBBLE, WikiMIA) and threat models (copyright, GDPR) that motivate the work. After the changes in K1–K4 above, the paper should have a good chance of acceptance at EMNLP.
