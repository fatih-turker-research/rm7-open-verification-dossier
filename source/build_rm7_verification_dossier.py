from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "rebuild" / "RM7_OPEN_VERIFICATION_DOSSIER.pdf"

NAVY = colors.HexColor("#14283D")
TEAL = colors.HexColor("#167D7F")
PALE = colors.HexColor("#EAF3F3")
PALE_RED = colors.HexColor("#FCEDEC")
GRAY = colors.HexColor("#5B6570")
LIGHT_GRAY = colors.HexColor("#E4E8EB")


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=25,
        textColor=NAVY,
        alignment=TA_LEFT,
        spaceAfter=5 * mm,
    )
)
styles.add(
    ParagraphStyle(
        name="Subtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=GRAY,
        spaceAfter=5 * mm,
    )
)
styles.add(
    ParagraphStyle(
        name="Section",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=NAVY,
        spaceBefore=5 * mm,
        spaceAfter=2.5 * mm,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        name="Subsection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        textColor=TEAL,
        spaceBefore=3 * mm,
        spaceAfter=1.5 * mm,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        name="BodyX",
        parent=styles["BodyText"],
        fontName="Times-Roman",
        fontSize=10.2,
        leading=14.2,
        textColor=colors.HexColor("#20262B"),
        spaceAfter=2.4 * mm,
        alignment=TA_LEFT,
    )
)
styles.add(
    ParagraphStyle(
        name="Small",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.6,
        leading=11.5,
        textColor=GRAY,
        spaceAfter=1.5 * mm,
    )
)
styles.add(
    ParagraphStyle(
        name="TableHeader",
        parent=styles["Small"],
        fontName="Helvetica-Bold",
        textColor=colors.white,
        spaceAfter=0,
    )
)
styles.add(
    ParagraphStyle(
        name="Equation",
        parent=styles["BodyText"],
        fontName="Courier",
        fontSize=9.2,
        leading=12.5,
        alignment=TA_CENTER,
        textColor=NAVY,
        spaceBefore=1.5 * mm,
        spaceAfter=2.5 * mm,
    )
)
styles.add(
    ParagraphStyle(
        name="BoxText",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.2,
        leading=12.4,
        textColor=NAVY,
    )
)
styles.add(
    ParagraphStyle(
        name="BulletX",
        parent=styles["BodyText"],
        fontName="Times-Roman",
        fontSize=10,
        leading=13.6,
        leftIndent=5 * mm,
        firstLineIndent=-3.5 * mm,
        bulletIndent=1.5 * mm,
        spaceAfter=1.4 * mm,
    )
)


def p(text: str, style: str = "BodyX") -> Paragraph:
    return Paragraph(text, styles[style])


def bullet(text: str) -> Paragraph:
    return Paragraph(text, styles["BulletX"], bulletText="-")


def status_box(text: str, warning: bool = False) -> Table:
    table = Table([[p(text, "BoxText")]], colWidths=[166 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALE_RED if warning else PALE),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#C75B55") if warning else TEAL),
                ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
            ]
        )
    )
    return table


def footer(canvas, doc) -> None:
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(LIGHT_GRAY)
    canvas.line(22 * mm, 16 * mm, width - 22 * mm, 16 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GRAY)
    canvas.drawString(22 * mm, 10.5 * mm, "AI-assisted RM(7) open verification dossier - version 1")
    canvas.drawRightString(width - 22 * mm, 10.5 * mm, f"Page {doc.page}")
    canvas.restoreState()


doc = BaseDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    leftMargin=22 * mm,
    rightMargin=22 * mm,
    topMargin=20 * mm,
    bottomMargin=21 * mm,
    title="Open verification dossier for a degree-50 RM(7) pullback",
    author="No human mathematical authorship claimed",
    subject="Unverified AI-assisted computations and a dependency-separated candidate genus-8 conclusion",
)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
doc.addPageTemplates(PageTemplate(id="all", frames=[frame], onPage=footer))

story = []
story.append(p("Open verification dossier for a degree-50 RM(7) pullback", "DocTitle"))
story.append(
    p(
        "AI-assisted candidate computations for exceptional fibres, geometric integrality, projective monodromy, and genus 8",
        "Subtitle",
    )
)
story.append(
    status_box(
        "<b>Public verification dossier - not a research publication.</b> The repository uploader has stated that they cannot independently defend all mathematical derivations in this document. Core research direction, derivations, code, checks, and drafting were produced with substantial OpenAI Codex assistance. No subject-matter expert has validated the candidate conclusions. This document is not peer reviewed, must not be cited as establishing a theorem, does not solve the (3,5,7) signature or the Beal conjecture, and is not a prize submission.",
        warning=True,
    )
)
story.append(Spacer(1, 4 * mm))
story.append(p("Abstract", "Section"))
story.append(
    p(
        "This dossier records a reproducible computational candidate concerning the positive genus-two Frey family associated with a hypothetical primitive solution of A^3 + B^5 = C^7. The released scripts report that the pullback of a hash-pinned inert level-7 Hilbert modular polynomial to the Gundlach line 5U = 9V^2 has a primitive equation of degree 50 in X, degree 100 in V, and 4,752 nonzero terms. Machine-generated Newton and residual-polynomial calculations report the boundary fibres, while a dependency-sensitive argument suggests geometric integrality and, subject to named source inputs and the correctness of a third-party coefficient database, genus 8. These are candidates for expert checking, not established results. No rational-point enumeration, Diophantine solution, or Beal solution is claimed."
    )
)
story.append(p("Claim classification", "Subsection"))
classification = [
    [p("Item", "TableHeader"), p("Status", "TableHeader"), p("Meaning", "TableHeader")],
    [p("Pinned pullback and boundary fibres", "Small"), p("MACHINE-CHECKED CANDIDATE", "Small"), p("Exact finite algebra reproduced by AI-generated implementations; no expert audit", "Small")],
    [p("Geometric integrality", "Small"), p("UNVERIFIED CANDIDATE", "Small"), p("Argument uses arithmetic irreducibility and a rational infinity place", "Small")],
    [p("Genus 8 for the modular pullback", "Small"), p("DEPENDENT CANDIDATE", "Small"), p("Uses named source theorems and an unregenerated coefficient database", "Small")],
    [p("Complete K-rational point list", "Small"), p("OPEN", "Small"), p("No effective enumeration or height bound is proved", "Small")],
    [p("Independent human validation", "Small"), p("NOT PERFORMED", "Small"), p("The public release asks qualified readers to reproduce and review the work", "Small")],
]
table = Table(classification, colWidths=[52 * mm, 29 * mm, 85 * mm], repeatRows=1)
table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.35, LIGHT_GRAY),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
        ]
    )
)
story.append(table)

story.append(PageBreak())
story.append(p("1. Diophantine and modular setup", "Section"))
story.append(
    p(
        "Let K = Q(sqrt(5)). In Branch I of the current (3,5,7) reduction, a hypothetical primitive positive solution satisfies 30 | C and 7 does not divide AB. Under (a,b,c,p) = (B,-C,A,7), the positive Frey family is"
    )
)
story.append(p("C_t:  y^2 = 5x^6 - 12x^5 + 10t x^3 + t^2,     t = -B^5/A^3.", "Equation"))
story.append(
    p(
        "Exact transvectant and invariant calculations map this family to the discriminant-5 Gundlach surface by"
    )
)
story.append(p("5U = 9V^2,     V = 375t/(t-1).", "Equation"))
story.append(p("For a Branch-I solution this gives the two perfect-power ratios", "BodyX"))
story.append(p("V/375 = B^5/C^7,     1 - V/375 = A^3/C^7.", "Equation"))
story.append(
    p(
        "The first published inert level-7 equation pulls back to a monic P(X,V) of degree 50 in X. The canonical primitive numerator F(X,V) in Z[X,V] has bidegree (50,100), 4,752 nonzero terms, and canonical hash"
    )
)
story.append(p("C8BEB2665A88AC2F8F3172ACE30087ECFA707FCFA45F5363973F9D8CA29C54CC", "Equation"))
story.append(
    p(
        "Two good split fibres have factor degrees 25+25 and 1+7+7+7+7+7+7+7. Their subset-degree intersections are only 0 and 50, proving irreducibility over Q(V) and K(V), conditional on the pinned source representing the intended modular polynomial."
    )
)

story.append(p("2. Exact exceptional fibres", "Section"))
fibre_data = [
    [p("Base value", "TableHeader"), p("Normalization", "TableHeader"), p("Cycle type", "TableHeader"), p("Different", "TableHeader")],
    [p("V = 0", "Small"), p("10 geometric points, each e = 5", "Small"), p("5^10", "Small"), p("40", "Small")],
    [p("Q_36(V) = 0", "Small"), p("49 finite and 1 projective unramified branch", "Small"), p("1^50", "Small"), p("0", "Small")],
    [p("V = 375", "Small"), p("2 unramified and 16 branches of e = 3", "Small"), p("1^2 3^16", "Small"), p("32", "Small")],
    [p("V = infinity", "Small"), p("7 branches of e = 7 and 1 rational e = 1 branch", "Small"), p("1 7^7", "Small"), p("42", "Small")],
]
table = Table(fibre_data, colWidths=[31 * mm, 83 * mm, 30 * mm, 22 * mm], repeatRows=1)
table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F8F9")]),
            ("GRID", (0, 0), (-1, -1), 0.35, LIGHT_GRAY),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (2, 1), (-1, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 2.2 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2.2 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
        ]
    )
)
story.append(table)
story.append(p("At V = 0", "Subsection"))
story.append(
    p(
        "Primitive specialization is H_10(X)^5. Independent factor-degree witnesses modulo 11 and 13 have subset-degree intersection {0,10}, so H_10 is irreducible over Q. Translation at its closed point yields a primitive Newton edge from (0,1) to (5,0); geometrically there are ten tame e = 5 points, contributing 10(5-1) = 40."
    )
)
story.append(p("At the denominator divisor", "Subsection"))
story.append(
    p(
        "The coefficient valuations are 0 for X^0 through X^49 and 2 for X^50. The finite degree-49 residual polynomial is square-free, and the projective chart has one smooth branch with X of pole order 2. All 50 branches are unramified."
    )
)
story.append(p("At V = 375", "Subsection"))
story.append(
    p(
        "The fibre factors with degree/multiplicity pattern 1^2, 4^6, 8^3. Local Newton polygons give two e = 1 branches and sixteen e = 3 branches. The normalized different is 32. The power-basis discriminant order is 58; the difference 26 equals twice the local index defect 13."
    )
)
story.append(
    KeepTogether(
        [
            p("At V = infinity", "Subsection"),
            p(
                "After w = 1/V and projective rescaling, the Newton vertices are (0,0), (49,14), (50,28). The length-49 edge gives seven e = 7 branches. The width-one edge gives a rational unramified branch with leading value"
            ),
            p("3^26 / (5^7 * 281^2).", "Equation"),
        ]
    )
)

story.append(p("3. Candidate geometric-integrality argument", "Section"))
story.append(
    status_box(
        "<b>Candidate proposition (unverified; relative to the pinned source).</b> The normalization of the degree-50 pullback is geometrically integral over Q."
    )
)
story.append(Spacer(1, 3 * mm))
story.append(
    p(
        "Proposed argument. Arithmetic irreducibility makes L a field. The width-one infinity edge gives a place of L whose residue field is reported to be exactly Q. Let k_0 be the algebraic closure of Q inside L. Reduction at that place would embed k_0 into Q, hence k_0 = Q. In characteristic zero, L/Q would therefore be regular, so the associated normal curve would remain integral after base change to an algebraic closure of Q. This reasoning has not been independently checked by a human expert."
    )
)
story.append(
    p(
        "If correct, this would close the earlier generic geometric-component caveat. It would not imply that any particular fibre lacks a K-rational point."
    )
)

story.append(p("4. Dependent cover identification and candidate genus", "Section"))
story.append(
    p(
        "Pacetti--Villagra Torcomian construct the generic genus-two Jacobian with an integral O_K-action and endomorphism algebra K. Its canonical principal polarization and positivity of Rosati make that action self-adjoint. Because 7 is inert in K, J[7] is a rank-two F_49-module and its lines form a degree-50 finite etale cover over the smooth locus. Scalar twists vanish projectively."
    )
)
story.append(bullet("At t = 0, the exact boundary type is 5^10; the abstract nonsplit order-5 action reproduces it."))
story.append(bullet("At t = infinity, the exact boundary type is 1^2 3^16; the abstract split order-3 action reproduces it."))
story.append(bullet("At t = 1, the exact boundary type is 1 7^7; an abstract nontrivial characteristic-7 unipotent reproduces it."))
story.append(p("R = 10(5-1) + 16(3-1) + 7(7-1) = 114.", "Equation"))
story.append(p("2g-2 = -2*50 + 114 = 14,     so g = 8.", "Equation"))
story.append(
    p(
        "The proposed identification reads Milio--Robert Propositions 4.3 and 4.11, the symmetric case of Theorem 4.15, and Proposition B.5 as identifying their Gundlach polynomial with the product over the 50 RM-stable kernels and as providing the generic function-field statement. After restriction to the Frey line, the argument proposes that the polynomial field injects into the 50-dimensional line algebra by evaluating the target J2 invariant, and that equal dimensions make this an isomorphism. If this reading, the absence of interior ramification, the boundary calculations, and the pinned database are all correct, Riemann--Hurwitz gives g = 8. Every part of this conclusion remains a dependent candidate until specialist review."
    )
)

story.append(p("5. Cross-checks and a discarded genus calculation", "Section"))
story.append(
    p(
        "Two separately implemented but AI-generated programs enumerate the 50 projective points and reproduce only the projective cycle types and numerical Riemann--Hurwitz value g = 8. A source-linked verifier obtains the boundary different from F. This is implementation diversity, not independent human verification, and none of these checks proves the pinned-cover identification or branch-locus completeness."
    )
)
story.append(
    p(
        "Modulo 1009, the large squared-discriminant factor consists of 4,501 ordinary nodes, and V = 375 has delta invariant 13, giving 4522 - 4501 - 13 = 8. This is only finite-field consistency evidence, not a characteristic-zero node-lifting proof. The raw values 4522 and 4509 count nonnormal plane singularities as ramification and are invalid."
    )
)

story.append(p("6. Branch-I local audit", "Section"))
story.append(
    p(
        "For every prime p not dividing 15, the two unit perfect-power ratios are residue-surjective onto every V other than 0 and 375. Complete source-linked scans at p = 11, 29, 31 yield exact necessary restrictions, but no global exclusion."
    )
)
story.append(
    p(
        "More importantly, the steep width-one edge at infinity has leading coefficients"
    )
)
story.append(p("L_49 = -3^86 * 5^7,     L_50 = 3^60 * 5^14 * 281^2.", "Equation"))
story.append(
    p(
        "If v_q(V) = -7c and q does not divide 3*5*281, Hensel's lemma gives a simple Q_q-root of the first Phi_7 equation. Hence the already forced primes 2, 7, 19, 71, 79, 89, 131 do not produce a contradiction through Phi_7 alone. The companion invariant or a genuine global point argument is necessary."
    )
)

story.append(p("7. Conditional consequence and open problem", "Section"))
story.append(
    status_box(
        "<b>Candidate implication.</b> If the named external inputs, pinned coefficient source, cover identification, and ramification analysis are correct, the relevant first modular equation defines a geometrically integral genus-8 curve, and Faltings' theorem would imply that its K-rational points are finite.<br/><br/><b>What is not established.</b> No independent expert validation, complete point list, effective height bound, companion-invariant test, orientation/descent theorem, Branch-I contradiction, (3,5,7) theorem, or full Beal proof has been obtained."
    )
)
story.append(Spacer(1, 3 * mm))
story.append(p("The next decisive work package is:", "BodyX"))
for item in [
    "Reconstruct and hash-pin the companion Psi_7 data with an independent implementation.",
    "Test the width-one infinity branch for cusp, admissibility, and RM orientation.",
    "Build a practical smooth projective genus-8 model over K with explicit birational maps.",
    "Obtain a rigorous Jacobian rank bound and run a complete Chabauty, covering, or Mordell--Weil sieve.",
    "Impose both perfect-power ratios and every Frey-specific descent condition on the complete K-point list.",
]:
    story.append(bullet(item))

story.append(p("8. Reproducibility, provenance, and authorship boundary", "Section"))
story.append(
    p(
        "The release includes compact certificates, a one-command manifest verifier, normal and optimized execution modes, exact source hashes, and separate reports for exceptional fibres, cover identification, monodromy, and local points. The third-party 42 MB database is hash-pinned but not redistributed because no explicit redistribution licence was found."
    )
)
story.append(
    p(
        "No human mathematical authorship is claimed for this dossier. GitHub user ftrspor directed and authorized its public release and has expressly stated that they cannot independently defend the mathematical derivations. OpenAI Codex was used substantively between 24 July and 2 August 2026 for research-direction selection, literature synthesis, mathematical derivation, code generation, execution planning, checking, and drafting. The uploader's acceptance of responsibility for posting does not convert these candidate conclusions into verified human research. For that reason this artifact is released only as an open request for verification, not submitted to a journal, arXiv, Zenodo, the AMS, or the Beal Prize Committee."
    )
)

story.append(p("Questions for independent reviewers", "Subsection"))
for item in [
    "Does the pinned third-party coefficient archive represent the intended inert level-7 Hilbert modular polynomial, and can its interpolation be regenerated independently?",
    "Are the Newton-polygon, residual-polynomial, normalization, and projective-infinity calculations complete at every exceptional fibre?",
    "Is the proposed function-field bridge to the 50-sheet RM-stable line cover valid after restriction to the Frey line?",
    "Is the assertion of no additional interior ramification justified by the cited results and hypotheses?",
    "If all preceding items hold, does the stated Riemann--Hurwitz computation establish genus 8 for the normalization?",
]:
    story.append(bullet(item))

story.append(Spacer(1, 5 * mm))
story.append(p("References", "Section"))
refs = [
    "A. Pacetti and L. Villagra Torcomian, On the generalized Fermat equation of signature (5,p,3), arXiv:2512.17845v1 (2025), especially Sections 2.1, 2.2 and 7.1.",
    "E. Milio and D. Robert, Modular polynomials on Hilbert surfaces, Journal of Number Theory 216 (2020), 403-459, especially Propositions 4.3, 4.11, B.5 and Theorem 4.15, DOI 10.1016/j.jnt.2020.04.014.",
    "American Mathematical Society, Procedures for Determination of an Award of the Beal Prize, Council Attachment W (current procedure checked 2 August 2026).",
]
for ref in refs:
    story.append(bullet(ref))

story.append(Spacer(1, 3 * mm))
story.append(
    p(
        "Status disclosure: this is an AI-assisted, unverified public verification dossier. It is not peer reviewed, has no DOI, claims no human mathematical authorship, and must not be cited as proof of any theorem or of the Beal conjecture.",
        "Small",
    )
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
doc.build(story)
print(OUTPUT)
