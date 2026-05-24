"""
Generate COLM_2026_Review_Status.pdf using reportlab.
Run once then delete; the PDF is the deliverable.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUTPUT = "COLM_2026_Review_Status.pdf"

# ── colour palette ────────────────────────────────────────────────────────────
GREEN  = colors.HexColor("#2e7d32")   # resolved
ORANGE = colors.HexColor("#e65100")   # partial / open
HEADER = colors.HexColor("#1a237e")   # section header bg
LIGHT  = colors.HexColor("#e8eaf6")   # section header text bg (light)
ROW_A  = colors.HexColor("#f5f5f5")
ROW_B  = colors.white
GRID   = colors.HexColor("#bdbdbd")

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=letter,
    leftMargin=0.85*inch, rightMargin=0.85*inch,
    topMargin=0.85*inch,  bottomMargin=0.85*inch,
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "Title2", parent=styles["Title"],
    fontSize=16, leading=20, spaceAfter=4,
    textColor=colors.HexColor("#0d1b2a"),
)
sub_style = ParagraphStyle(
    "Sub", parent=styles["Normal"],
    fontSize=9, leading=12, spaceAfter=12,
    textColor=colors.HexColor("#546e7a"),
)
section_style = ParagraphStyle(
    "Section", parent=styles["Normal"],
    fontSize=11, leading=14, spaceBefore=14, spaceAfter=4,
    textColor=colors.white, fontName="Helvetica-Bold",
)
note_style = ParagraphStyle(
    "Note", parent=styles["Normal"],
    fontSize=8.5, leading=12, spaceAfter=10,
    textColor=colors.HexColor("#37474f"),
    leftIndent=6,
)
cell_style = ParagraphStyle(
    "Cell", parent=styles["Normal"],
    fontSize=8, leading=11,
)
verdict_ok   = ParagraphStyle("VOK",   parent=cell_style, textColor=GREEN,  fontName="Helvetica-Bold")
verdict_warn = ParagraphStyle("VWarn", parent=cell_style, textColor=ORANGE, fontName="Helvetica-Bold")

def section_header(text, rating=None):
    label = f"{text}   (Rating: {rating})" if rating else text
    tbl = Table(
        [[Paragraph(label, section_style)]],
        colWidths=[6.3*inch],
    )
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), HEADER),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [HEADER]),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return tbl

def verdict_para(text):
    if text.startswith("✅"):
        return Paragraph(text, verdict_ok)
    elif text.startswith("⚠️"):
        return Paragraph(text, verdict_warn)
    return Paragraph(text, cell_style)

def review_table(rows):
    """rows: list of (comment_str, status_str)"""
    col_w = [3.05*inch, 3.25*inch]
    header = [
        Paragraph("<b>Reviewer Comment</b>", cell_style),
        Paragraph("<b>Status in Current EMNLP Paper</b>", cell_style),
    ]
    data = [header]
    for comment, status in rows:
        data.append([
            Paragraph(comment, cell_style),
            verdict_para(status),
        ])

    tbl = Table(data, colWidths=col_w, repeatRows=1)
    style_cmds = [
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#e8eaf6")),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1,-1), 8),
        ("LEADING",       (0, 0), (-1,-1), 11),
        ("GRID",          (0, 0), (-1,-1), 0.4, GRID),
        ("VALIGN",        (0, 0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1,-1), 4),
        ("BOTTOMPADDING", (0, 0), (-1,-1), 4),
        ("LEFTPADDING",   (0, 0), (-1,-1), 5),
        ("RIGHTPADDING",  (0, 0), (-1,-1), 5),
    ]
    for i in range(1, len(data)):
        bg = ROW_A if i % 2 == 1 else ROW_B
        style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))
    tbl.setStyle(TableStyle(style_cmds))
    return tbl

# ── content ───────────────────────────────────────────────────────────────────

story = []

story.append(Paragraph(
    "COLM 2026 Review Status",
    title_style,
))
story.append(Paragraph(
    "Paper: <i>The Landscape of Memorization in LLMs: Mechanisms, Measurement, and Mitigation</i><br/>"
    "Submission #3470 &nbsp;·&nbsp; Venue: COLM 2026 → EMNLP 2026 (resubmission)<br/>"
    "Status report: 24 May 2026",
    sub_style,
))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#90a4ae"), spaceAfter=10))

# ── g63y ──────────────────────────────────────────────────────────────────────
story.append(section_header("Reviewer g63y", rating="5 / 10"))
story.append(Spacer(1, 4))
g63y_rows = [
    (
        "Empirical study limited to HUBBLE; unclear how τ=0.08 generalizes to real models (LLaMA, GPT, etc.)",
        "✅ Pythia-6.9b-deduped external validation added (App I.13: Loss τ_b=+0.070, ZLib τ_b=+0.084, p<0.05). "
        "Mistral-7B base vs. aligned comparison added (App I.14: ΔEM=+0.0008, RLHF does not suppress extraction).",
    ),
    (
        "Defense component underdeveloped: paper promises 'Defense' in framework but empirical section focuses on Metric→Attack",
        "✅ App I.17: direct unlearning experiment on Pythia-6.9b-deduped (N=50, gradient ascent, 50 steps). "
        "τ_b(ΔLoss, ΔEM)=−0.256 (p=0.009); one counterexample (ΔEM=+0.016 despite largest ΔLoss=+8.4) shows "
        "metric-verified unlearning does not certify extraction protection.",
    ),
    (
        "Missing Feldman 2020 ('Does learning require memorization?') — theoretical grounding for why memorization arises",
        "✅ Added §2.1: Feldman (2020) cited as primary theoretical grounding; rare long-tail examples may require "
        "verbatim memorization for generalization.",
    ),
    (
        "Missing Ippolito et al. 2023 (verbatim vs approximate memorization distinctions)",
        "✅ Added §2.2: Ippolito et al. (2023) cited for verbatim–approximate distinction; extraction-based metrics "
        "span strict (exact match) to lenient (ROUGE-L).",
    ),
    (
        "FMARD is largely a taxonomy dressed as a causal framework; causal edges not formally validated",
        "✅ 'Causal links' replaced with 'directed dependency links' throughout abstract, introduction, and §2. "
        "Explicit disclaimer added: links are directional/conceptual, organizing the natural pipeline flow, "
        "not interventionally causal mechanisms.",
    ),
]
story.append(review_table(g63y_rows))
story.append(Spacer(1, 10))

# ── onNX ──────────────────────────────────────────────────────────────────────
story.append(section_header("Reviewer onNX", rating="5 / 10"))
story.append(Spacer(1, 4))
onNX_rows = [
    (
        "R1 — FMARD has fuzzy boundaries between Metrics, Attacks, and Risks. "
        "Attacks seem redundant; they differ from Metrics only in intent and from Risk only in quantifiable evaluations. "
        "Can Attacks be rolled into Risk?",
        "✅ §2 component-boundary paragraph added: same scoring function is a Metric if used offline, "
        "an Attack if deployed to classify membership — assignment depends on evaluation intent and adversary capability. "
        "Table 2 (attack taxonomy) shows Attacks differ by access requirements and leakage type; each Attack maps to "
        "different downstream Risks (many-to-many). This operationally distinguishes Attack from Risk.",
    ),
    (
        "R2 — Paper hints that sequence length confounds M→A correlation but does not actually validate this claim",
        "✅ App I.12: length-quartile stratification shows τ_b=+0.148 for shortest sequences (Q1, ≤132 tokens) "
        "vs. near-zero for Q2. App I.10 (anticorrelation analysis) shows Q4 (longest, highest-loss sequences) "
        "drives the d=256 inversion — precisely the length confound. App I.16 synthesizes Carlini 2021 and "
        "Biderman 2023 length/capacity findings.",
    ),
    (
        "Q1 — Line 91: 'Sampling and decoding' is an attacker-side intervention, not a Factor affecting what gets memorized",
        "✅ Renamed to 'Inference-time decoding' (Factor 4). §2.1 now explains it is adversary-accessible at test "
        "time, not a fixed training property; decoding is de facto part of Attack configuration.",
    ),
    (
        "Q2 — Table 1: Effects of 'Training duration' and 'Alignment' not discussed in §2.1",
        "✅ Factors 6 (Training duration) and 7 (Alignment/RLHF) added to §2.1 prose and to Table 1 with "
        "effect directions and citations.",
    ),
    (
        "Q3 — Line 156: Overlapping definitions of Attack and Metric — unclear why Metrics would be identical "
        "if one Attack succeeds while another fails",
        "✅ §2 boundary paragraph clarifies: Metrics are offline statistical scores; Attacks are adversarial "
        "procedures requiring resources and model access. The same function (e.g., loss threshold) is a Metric "
        "offline and part of an Attack when deployed for membership classification.",
    ),
    (
        "Q4 — Table 3: Column heading is 'FMARD Link' but most entries are not F/M/A/R/D notation",
        "✅ Table 3 'FMARD Link Targeted' column now uses arrow notation throughout: "
        "F (Factor), F→M (Training), M→A (Post-training), A→R (Inference).",
    ),
    (
        "Q5 — Line 184: No citation for 'strict privacy budgets degrade utility'",
        "✅ Added \\citep{li2021large, abadi2016deep} at the relevant sentence.",
    ),
    (
        "Q6 — Line 212: 'Compressing the signal' is unclear jargon",
        "✅ Replaced with 'shrinking the loss gap between members and non-members (the signal MIA relies on) "
        "and reducing its discriminative power'.",
    ),
    (
        "Q7 — Line 260: 'Target extraction performance' is undefined",
        "✅ Parenthetical added: '(defined as zero greedy exact match on the forget set, "
        "the standard success criterion for unlearning)'.",
    ),
    (
        "Q8 — §4.5: PII attack success depending on adversary capability (background knowledge) "
        "already established in HUBBLE paper",
        "✅ Added paragraph distinguishing new finding: per-field |τ_b|<0.12 between document-level Metrics "
        "and field-level extraction outcomes is new — no forward-pass metric predicts which specific PII "
        "fields are extractable. This is a structural M→A diagnostic gap not established by HUBBLE.",
    ),
    (
        "Suggestion 1 — Line 51: Not enough setup to understand what 'AUC gap' means",
        "✅ 'AUC gap' terminology no longer appears unexplained in the introduction. Early intro uses "
        "'metric–risk gap'. ΔAUCt appears in contribution bullets with context 'vs. an unexposed model'.",
    ),
]
story.append(review_table(onNX_rows))
story.append(Spacer(1, 10))

# ── mCRV ──────────────────────────────────────────────────────────────────────
story.append(section_header("Reviewer mCRV", rating="5 / 10"))
story.append(Spacer(1, 4))
mCRV_rows = [
    (
        "R1 — FMARD repeatedly presented as causal with directed dependencies, but relationships are not "
        "formally causal in interventionist sense; empirical study demonstrates correlations, not mechanisms",
        "✅ 'Causal links' → 'directed dependency links' throughout. §2 operational definition revised: "
        "Condition (1) changed from 'necessary precondition' (empirically false at d=0) to modulation-based "
        "formulation. Explicit disclaimer: links are directional/conceptual, not interventionally causal.",
    ),
    (
        "R2 — Experiments limited to single model family, base models only, exclude white-box attacks "
        "(soft-prompt optimization); gap between framework breadth and empirical validation is substantial",
        "✅ App I.13: Pythia-6.9b-deduped external validation (600 sequences, heterogeneous natural duplication). "
        "App I.14: Mistral-7B base vs. instruction-tuned (aligned model). "
        "App I.15: White-box attacks addressed analytically — τ_b=0.08 greedy is conservative lower bound; "
        "gradient-based adversary raises EM for sequences already flagged by metrics.",
    ),
    (
        "R3 — Defense component mostly discussed through literature synthesis rather than directly evaluated",
        "✅ App I.17: Direct unlearning experiment (Pythia-6.9b-deduped, N=50 top-EM sequences, gradient ascent "
        "on last 2 layers). Shows metric-verified unlearning (ΔLoss>0 in 50/50) does not certify extraction "
        "protection (ΔEM<0 in only 49/50; one sequence ΔEM=+0.016 despite largest ΔLoss=+8.4).",
    ),
    (
        "Q — Concrete example where FMARD leads to different practical recommendation than without framework",
        "✅ §3 worked example added: without FMARD, practitioner auditing copyright risk selects perplexity "
        "(cheap, widely-used). FMARD reveals τ_b≈0.035 on literary text — near-zero predictive signal. "
        "FMARD-guided recommendation is qualitatively different: use extraction attacks directly, "
        "stratified by content type. Without M→A decomposition, practitioner has no principled basis "
        "for knowing low perplexity says nothing about extractability.",
    ),
    (
        "Q — What makes FMARD specifically causal rather than structured taxonomy with directed dependencies?",
        "✅ Paper no longer claims formal causality — 'directed dependency links' framing adopted. "
        "FMARD is positioned as a structured taxonomy with directional conceptual dependencies "
        "reflecting the natural temporal/logical order of the memorization pipeline.",
    ),
    (
        "Q — How sensitive are results to choice of extraction attack and decoding strategy?",
        "✅ App I.12 (confounder analysis): greedy vs. sampling EM compared across 16 metric–attack pairs. "
        "Loss vs. Sampling EM swings to τ_b≈−0.55 at d=256, while Loss vs. Greedy EM stays at −0.52. "
        "Best pair (MinK%++ vs. Static Greedy EM) reaches τ_b=0.292; all sampling-based pairs lower.",
    ),
    (
        "Q — Are seven metrics equally appropriate across all three domains, or should different domains "
        "require different metric choices?",
        "✅ Domain-sensitive metric note added §4.3: metric choice is domain-sensitive. "
        "App I.13 shows Min-K% and MinK%++ are non-significant and negative on natural low-duplication text "
        "(Pythia/WikiText-103), while Loss and ZLib remain positive — calibrated count-based metrics "
        "invert in natural settings and should not be primary metrics without domain validation.",
    ),
]
story.append(review_table(mCRV_rows))
story.append(Spacer(1, 10))

# ── AUwY ──────────────────────────────────────────────────────────────────────
story.append(section_header("Reviewer AUwY", rating="4 / 10"))
story.append(Spacer(1, 4))
AUwY_rows = [
    (
        "R1 — 'Causal' framing not empirically justified. τ=0.08 establishes that two measurement families are "
        "not interchangeable (correlation finding), but does not establish directionality, mechanism, "
        "or counterfactual dependence between FMARD components",
        "✅ 'Causal links' → 'directed dependency links' throughout. §2 operational definition: directed "
        "dependency link X→Y asserts that properties of X modulate the strength or character of Y "
        "(modulation-based, not necessity-based). Explicit disclaimer in §2: links are directional/conceptual, "
        "organizing the memorization pipeline by natural flow. No counterfactual causality claimed.",
    ),
    (
        "R2 — Controlled study evaluates M→A link exclusively. Remaining links (F→M, A→R, Defense→Factor, "
        "cross-link interference) supported only by citations to existing literature, not new controlled experiments",
        "✅ Explicitly acknowledged in Limitations: only M→A directly tested. Appendix adds partial evidence: "
        "I.13 (M→A on natural text), I.14 (Defense→A: RLHF as A-output Defense), I.17 (Defense→M and M→A gap). "
        "Contributions section (3) explicitly scopes to M→A on HUBBLE; F→M, A→R, Defense links flagged as "
        "synthesis-supported open empirical questions.",
    ),
    (
        "R3 — Three failure modes (link mismatch, factor confounding, cross-link interference) are recognizable "
        "instances of well-understood methodological problems that exist independently of FMARD",
        "⚠️ Partially addressed. §3 worked example shows FMARD changes a practitioner recommendation "
        "(concrete practical value added). However, the philosophical point — that these failure modes are "
        "recognizable without FMARD — is inherent to any systematization-of-knowledge contribution. "
        "FMARD's value is in naming, systematizing, and providing a common vocabulary; this is acknowledged "
        "but the underlying critique cannot be fully resolved through text changes.",
    ),
    (
        "R4 — Threat-model-driven guidelines (§5) are useful but do not obviously require FMARD to derive. "
        "Copyright auditing recommendation follows directly from observing loss is uncorrelated with extractability",
        "✅ §3 worked example directly addresses this: without FMARD's M→A decomposition, a practitioner "
        "has no principled basis for knowing that low perplexity on literary text says nothing about "
        "extractability. FMARD provides the structural framework that makes τ_b≈0.035 interpretable "
        "as a link-specific finding rather than a domain-specific anomaly.",
    ),
]
story.append(review_table(AUwY_rows))
story.append(Spacer(1, 14))

# ── summary ───────────────────────────────────────────────────────────────────
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#90a4ae"), spaceAfter=8))
story.append(Paragraph(
    "<b>Overall Assessment</b>",
    ParagraphStyle("OA", parent=styles["Normal"], fontSize=10, fontName="Helvetica-Bold",
                   spaceAfter=4, textColor=colors.HexColor("#0d1b2a")),
))
story.append(Paragraph(
    "All substantive reviewer concerns are addressed in the current EMNLP 2026 submission except "
    "<b>AUwY R3</b> (failure modes are well-understood methodological problems that predate FMARD). "
    "This is a philosophical critique inherent to systematization-of-knowledge contributions and "
    "is appropriately handled by acknowledging scope rather than claiming FMARD discovered the modes. "
    "The paper is well-positioned for EMNLP acceptance after stripping the <tt>changes</tt>-package "
    "markup prior to final submission.",
    note_style,
))

legend_data = [
    [Paragraph("✅  Fully addressed in current paper", verdict_ok),
     Paragraph("⚠️  Partially addressed; residual philosophical concern", verdict_warn)],
]
leg_tbl = Table(legend_data, colWidths=[3.1*inch, 3.2*inch])
leg_tbl.setStyle(TableStyle([
    ("BOX",           (0,0), (-1,-1), 0.5, GRID),
    ("TOPPADDING",    (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ("RIGHTPADDING",  (0,0), (-1,-1), 6),
    ("BACKGROUND",    (0,0), (-1,-1), colors.HexColor("#fafafa")),
]))
story.append(leg_tbl)

doc.build(story)
print(f"Written: {OUTPUT}")
