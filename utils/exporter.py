import json
import io
import pandas as pd
import plotly.graph_objects as go
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, Image, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT


# ── Colour palette ─────────────────────────────────────────
C_DARK    = colors.HexColor("#1a1a1a")
C_MID     = colors.HexColor("#555553")
C_LIGHT   = colors.HexColor("#888780")
C_GREEN   = colors.HexColor("#1D9E75")
C_AMBER   = colors.HexColor("#EF9F27")
C_RED     = colors.HexColor("#E24B4A")
C_BLUE    = colors.HexColor("#185FA5")
C_PURPLE  = colors.HexColor("#534AB7")
C_BG      = colors.HexColor("#F8F8F6")
C_WHITE   = colors.white

# This module handles exporting the analysis results and portfolio data into PDF and JSON formats for reporting and sharing purposes.
def _styles():
    base = getSampleStyleSheet()
    return {
        "h1": ParagraphStyle("h1", fontSize=22, textColor=C_DARK,
                             spaceAfter=6, fontName="Helvetica-Bold"),
        "h2": ParagraphStyle("h2", fontSize=14, textColor=C_DARK,
                             spaceBefore=14, spaceAfter=5,
                             fontName="Helvetica-Bold"),
        "h3": ParagraphStyle("h3", fontSize=11, textColor=C_MID,
                             spaceBefore=8, spaceAfter=3,
                             fontName="Helvetica-Bold"),
        "body": ParagraphStyle("body", fontSize=10, textColor=C_DARK,
                               spaceAfter=4, leading=15,
                               fontName="Helvetica"),
        "small": ParagraphStyle("small", fontSize=8, textColor=C_LIGHT,
                                spaceAfter=2, fontName="Helvetica"),
        "caption": ParagraphStyle("caption", fontSize=8, textColor=C_MID,
                                  spaceAfter=6, alignment=TA_CENTER,
                                  fontName="Helvetica-Oblique"),
        "tag_green": ParagraphStyle("tag_green", fontSize=9,
                                    textColor=C_GREEN, fontName="Helvetica-Bold"),
        "tag_amber": ParagraphStyle("tag_amber", fontSize=9,
                                    textColor=C_AMBER, fontName="Helvetica-Bold"),
        "tag_red":   ParagraphStyle("tag_red", fontSize=9,
                                    textColor=C_RED, fontName="Helvetica-Bold"),
        "tag_blue":  ParagraphStyle("tag_blue", fontSize=9,
                                    textColor=C_BLUE, fontName="Helvetica-Bold"),
    }


def _fig_to_image(fig: go.Figure, width: int = 700, height: int = 380):
    img_bytes = fig.to_image(format="png", width=width, height=height, scale=2)
    return io.BytesIO(img_bytes)


def _metric_table(metrics: list[tuple]) -> Table:
    data = [[Paragraph(f"<b>{v}</b>", ParagraphStyle(
                "mv", fontSize=16, textColor=C_DARK,
                fontName="Helvetica-Bold", alignment=TA_CENTER)),
             Paragraph(label, ParagraphStyle(
                "ml", fontSize=8, textColor=C_MID,
                fontName="Helvetica", alignment=TA_CENTER))]
            for v, label in metrics]

    col_data = list(zip(*[data[i:i+4] for i in range(0, len(data), 4)][0]))
    t = Table([col_data[0], col_data[1]], colWidths=[4.2*cm]*4)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_BG),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_BG]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
        ("ROUNDEDCORNERS", [4]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    return t


def to_pdf(analysis: dict, df: pd.DataFrame, figures: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="Portfolio Rationalization Report",
    )
    s = _styles()
    story = []

    # ── Cover header ───────────────────────────────────────
    story.append(Paragraph("LeanIX GenAI Portfolio Analyzer", s["h1"]))
    story.append(Paragraph("Application Portfolio Rationalization Report",
                            ParagraphStyle("sub", fontSize=13, textColor=C_MID,
                                           fontName="Helvetica", spaceAfter=4)))
    story.append(Paragraph("Powered by Claude · Anthropic",
                            ParagraphStyle("pow", fontSize=9, textColor=C_LIGHT,
                                           fontName="Helvetica", spaceAfter=8)))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor("#e0e0e0"), spaceAfter=12))

    # ── Executive summary ──────────────────────────────────
    story.append(Paragraph("Executive Summary", s["h2"]))
    summary = analysis.get("executive_summary", "")
    story.append(Paragraph(summary, s["body"]))

    saving = analysis.get("total_potential_saving_usd", 0)
    if saving:
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f"<b>Total identified saving opportunity: ${saving:,} / year</b>",
            ParagraphStyle("saving", fontSize=11, textColor=C_GREEN,
                           fontName="Helvetica-Bold", spaceAfter=4)
        ))

    story.append(Spacer(1, 10))

    # ── Portfolio metrics ──────────────────────────────────
    story.append(Paragraph("Portfolio Overview", s["h2"]))
    total_cost = int(df["annual_cost_usd"].sum())
    high_debt  = int((df["tech_debt_score"] >= 7).sum())
    retire_c   = int(df["lifecycle_stage"].isin(["End of Life","Phase Out"]).sum())
    metrics = [
        (str(len(df)),        "Total applications"),
        (f"${total_cost:,}",  "Annual spend"),
        (str(high_debt),      "High tech debt (≥7)"),
        (str(retire_c),       "Retire candidates"),
    ]
    story.append(_metric_table(metrics))
    story.append(Spacer(1, 14))

    # ── Charts ─────────────────────────────────────────────
    story.append(Paragraph("Portfolio Analytics", s["h2"]))

    if "scatter" in figures:
        img = _fig_to_image(figures["scatter"], width=720, height=420)
        story.append(Image(img, width=17*cm, height=10*cm))
        story.append(Paragraph(
            "Bubble size = annual cost  ·  Colour = recommended action",
            s["caption"]))
        story.append(Spacer(1, 8))

    if "lifecycle" in figures and "cost" in figures:
        lc_img   = _fig_to_image(figures["lifecycle"], width=360, height=260)
        cost_img = _fig_to_image(figures["cost"],      width=360, height=260)
        row = Table(
            [[Image(lc_img, width=8.2*cm, height=6.2*cm),
              Image(cost_img, width=8.2*cm, height=6.2*cm)]],
            colWidths=[8.5*cm, 8.5*cm]
        )
        story.append(row)
        story.append(Spacer(1, 8))

    if "heatmap" in figures:
        img = _fig_to_image(figures["heatmap"], width=720, height=380)
        story.append(Image(img, width=17*cm, height=9*cm))
        story.append(Paragraph(
            "Red ≥7  ·  Amber 5–6  ·  Green <5", s["caption"]))

    story.append(Spacer(1, 14))

    # ── Retire ─────────────────────────────────────────────
    retire_list = analysis.get("retire", [])
    if retire_list:
        story.append(Paragraph("Retirement Candidates", s["h2"]))
        story.append(Paragraph(
            "Applications recommended for decommissioning based on low "
            "business value, high technical debt, or end-of-life status.",
            s["body"]))
        story.append(Spacer(1, 6))

        for item in retire_list:
            if not isinstance(item, dict):
                continue
            saving_amt = item.get("estimated_saving_usd", 0)
            urgency    = item.get("urgency", "")
            urgency_color = (C_RED if urgency == "immediate"
                             else C_AMBER if urgency == "6-months" else C_MID)
            block = KeepTogether([
                Table([[
                    Paragraph(f"<b>{item.get('app_name','')}</b>",
                              ParagraphStyle("an", fontSize=11, textColor=C_DARK,
                                             fontName="Helvetica-Bold")),
                    Paragraph(f"Save ${saving_amt:,}/yr",
                              ParagraphStyle("sv", fontSize=10, textColor=C_GREEN,
                                             fontName="Helvetica-Bold",
                                             alignment=TA_RIGHT)),
                ]], colWidths=[11*cm, 5.7*cm],
                style=TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE")])),
                Paragraph(item.get("reason", ""), s["body"]),
                Paragraph(f"Urgency: {urgency}",
                          ParagraphStyle("urg", fontSize=9,
                                         textColor=urgency_color,
                                         fontName="Helvetica-Bold",
                                         spaceAfter=8)),
                HRFlowable(width="100%", thickness=0.5,
                           color=colors.HexColor("#eeeeee"), spaceAfter=6),
            ])
            story.append(block)

    # ── Modernize ──────────────────────────────────────────
    modernize_list = analysis.get("modernize", [])
    if modernize_list:
        story.append(Paragraph("Modernization Priorities", s["h2"]))
        story.append(Paragraph(
            "High-value applications with significant technical debt that "
            "cannot be retired — require re-platforming or refactoring.",
            s["body"]))
        story.append(Spacer(1, 6))

        priority_color = {"high": C_RED, "medium": C_AMBER, "low": C_GREEN}
        for item in modernize_list:
            if not isinstance(item, dict):
                continue
            priority = item.get("priority", "medium")
            pc = priority_color.get(priority, C_MID)
            block = KeepTogether([
                Table([[
                    Paragraph(f"<b>{item.get('app_name','')}</b>",
                              ParagraphStyle("an2", fontSize=11, textColor=C_DARK,
                                             fontName="Helvetica-Bold")),
                    Paragraph(f"{priority.upper()} priority",
                              ParagraphStyle("pr", fontSize=9, textColor=pc,
                                             fontName="Helvetica-Bold",
                                             alignment=TA_RIGHT)),
                ]], colWidths=[11*cm, 5.7*cm],
                style=TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE")])),
                Paragraph(item.get("reason", ""), s["body"]),
                Paragraph(
                    f"<b>Approach:</b> {item.get('recommended_approach','')}",
                    ParagraphStyle("ap", fontSize=9, textColor=C_BLUE,
                                   fontName="Helvetica", spaceAfter=8)),
                HRFlowable(width="100%", thickness=0.5,
                           color=colors.HexColor("#eeeeee"), spaceAfter=6),
            ])
            story.append(block)

    # ── Key risks ──────────────────────────────────────────
    risks = analysis.get("key_risks", [])
    if risks:
        story.append(Paragraph("Key Risks", s["h2"]))
        for risk in risks:
            if not isinstance(risk, dict):
                continue
            affected = ", ".join(risk.get("affected_apps", []))
            story.append(KeepTogether([
                Paragraph(f"<b>{risk.get('risk','')}</b>",
                          ParagraphStyle("rk", fontSize=10, textColor=C_RED,
                                         fontName="Helvetica-Bold", spaceAfter=2)),
                Paragraph(f"Affected: {affected}", s["small"]),
                Paragraph(f"Mitigation: {risk.get('mitigation','')}", s["body"]),
                HRFlowable(width="100%", thickness=0.5,
                           color=colors.HexColor("#eeeeee"), spaceAfter=4),
            ]))

    # ── Quick wins ─────────────────────────────────────────
    qws = analysis.get("quick_wins", [])
    if qws:
        story.append(Paragraph("Quick Wins", s["h2"]))
        for qw in qws:
            if isinstance(qw, str):
                story.append(Paragraph(f"• {qw}", s["body"]))

    # ── Footer ─────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#e0e0e0"), spaceAfter=6))
    story.append(Paragraph(
        "Generated by LeanIX GenAI Portfolio Analyzer · Powered by Anthropic Claude · "
        "github.com/suduat/leanix-genai-analyzer",
        ParagraphStyle("footer", fontSize=7, textColor=C_LIGHT,
                       fontName="Helvetica", alignment=TA_CENTER)
    ))

    doc.build(story)
    return buf.getvalue()


def to_json(analysis: dict, df: pd.DataFrame) -> str:
    export = {
        "report": analysis,
        "portfolio_stats": {
            "total_apps": len(df),
            "total_annual_cost_usd": int(df["annual_cost_usd"].sum()),
            "high_debt_apps": int((df["tech_debt_score"] >= 7).sum()),
            "retire_candidates": int(
                df["lifecycle_stage"].isin(["End of Life","Phase Out"]).sum()
            ),
            "quadrant_breakdown": df["rationalization_quadrant"]
                                    .value_counts().to_dict(),
            "hosting_cost_breakdown": df.groupby("hosting_type")["annual_cost_usd"]
                                        .sum().astype(int).to_dict(),
        },
        "applications": df[[
            "app_name", "business_capability", "lifecycle_stage",
            "tech_debt_score", "business_value_score", "annual_cost_usd",
            "hosting_type", "age_years", "rationalization_quadrant", "risk_score"
        ]].to_dict(orient="records"),
    }
    return json.dumps(export, indent=2, default=str)