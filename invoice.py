
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from database import get_business_profile


def create_invoice_pdf(bill_id, customer_name, items, total,
                       bill_date=None):

    profile = get_business_profile()

    if not profile:
        raise ValueError(
            "Business profile not found. Complete pharmacy setup first."
        )

    company_name = profile.get("business_name") or "PHARMACY"
    owner_name = profile.get("owner_name") or ""
    address = profile.get("address") or ""
    phone = profile.get("phone") or ""
    email = profile.get("email") or ""
    gstin = profile.get("gstin") or ""
    prefix = profile.get("invoice_prefix") or "INV"

    invoice_number = "{}-{:05d}".format(prefix, bill_id)

    if bill_date is None:
        bill_date = datetime.now()

    if isinstance(bill_date, str):
        try:
            bill_date = datetime.strptime(
                bill_date, "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            bill_date = datetime.now()

    # Save PDFs in the project's bills folder.
    project_folder = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    bills_folder = os.path.join(project_folder, "bills")
    os.makedirs(bills_folder, exist_ok=True)

    filename = "Invoice_{}.pdf".format(invoice_number)
    pdf_path = os.path.join(bills_folder, filename)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    company_style = ParagraphStyle(
        "Company",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=27,
        textColor=colors.HexColor("#176B45"),
        alignment=TA_CENTER,
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64756B")
    )

    heading_style = ParagraphStyle(
        "InvoiceHeading",
        parent=styles["Heading2"],
        fontSize=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#176B45")
    )

    normal_style = ParagraphStyle(
        "NormalSmall",
        parent=styles["Normal"],
        fontSize=9,
        leading=13
    )

    story = []

    # Company header
    story.append(Paragraph(company_name.upper(), company_style))

    if owner_name:
        story.append(Paragraph(
            "Owner: {}".format(owner_name),
            subtitle_style
        ))

    if address:
        story.append(Paragraph(address, subtitle_style))

    contact = "Phone: {}".format(phone) if phone else ""

    if email:
        contact += " | Email: {}".format(email)

    if contact:
        story.append(Paragraph(contact, subtitle_style))

    if gstin:
        story.append(Paragraph(
            "GSTIN: {}".format(gstin),
            subtitle_style
        ))

    story.append(Spacer(1, 10))
    story.append(Paragraph("CASH / TAX INVOICE", heading_style))
    story.append(Spacer(1, 12))

    # Invoice details
    details = [
        [
            Paragraph(
                "<b>Invoice No:</b> {}".format(invoice_number),
                normal_style
            ),
            Paragraph(
                "<b>Date:</b> {}".format(
                    bill_date.strftime("%d-%m-%Y %I:%M %p")
                ),
                normal_style
            )
        ],
        [
            Paragraph(
                "<b>Customer:</b> {}".format(customer_name),
                normal_style
            ),
            Paragraph("<b>Payment:</b> Cash / Retail", normal_style)
        ]
    ]

    details_table = Table(
        details,
        colWidths=[85 * mm, 85 * mm]
    )

    details_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1),
         colors.HexColor("#F0F6F2")),
        ("BOX", (0, 0), (-1, -1), 0.6,
         colors.HexColor("#D6E5DB")),
        ("INNERGRID", (0, 0), (-1, -1), 0.4,
         colors.HexColor("#D6E5DB")),
        ("PADDING", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))

    story.append(details_table)
    story.append(Spacer(1, 18))

    # Medicine table
    table_data = [[
        "S.No.",
        "Medicine",
        "Batch",
        "Qty",
        "Rate (Rs.)",
        "Amount (Rs.)"
    ]]

    for index, item in enumerate(items, start=1):

        quantity = int(item["quantity"])
        price = float(item["price"])
        subtotal = quantity * price

        table_data.append([
            str(index),
            str(item["name"]),
            str(item.get("batch", "")),
            str(quantity),
            "{:.2f}".format(price),
            "{:.2f}".format(subtotal)
        ])

    medicine_table = Table(
        table_data,
        colWidths=[
            12 * mm,
            47 * mm,
            30 * mm,
            14 * mm,
            27 * mm,
            30 * mm
        ],
        repeatRows=1
    )

    medicine_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#176B45")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5,
         colors.HexColor("#D6E5DB")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#F4F8F5")
        ]),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 7)
    ]))

    story.append(medicine_table)
    story.append(Spacer(1, 18))

    # Grand total
    total_table = Table([
        ["GRAND TOTAL", "Rs. {:.2f}".format(float(total))]
    ], colWidths=[120 * mm, 40 * mm])

    total_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1),
         colors.HexColor("#E6F2E9")),
        ("TEXTCOLOR", (0, 0), (-1, -1),
         colors.HexColor("#176B45")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 13),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("BOX", (0, 0), (-1, -1), 0.8,
         colors.HexColor("#176B45")),
        ("PADDING", (0, 0), (-1, -1), 11)
    ]))

    story.append(total_table)
    story.append(Spacer(1, 35))

    story.append(Paragraph(
        "<b>Thank you for visiting us!</b>",
        ParagraphStyle(
            "Thanks",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=12,
            textColor=colors.HexColor("#176B45")
        )
    ))

    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "Computer-generated invoice. No signature required.",
        subtitle_style
    ))

    doc.build(story)

    return pdf_path
