import streamlit as st
from fpdf import FPDF
from PIL import Image, ImageOps
import os

st.title("Return Parcel Evident)")

# Inputs
brand = st.text_input("Brand")
platform = st.text_input("Platform")
order_id = st.text_input("Order ID")
tracking = st.text_input("Tracking Number")
sku = st.text_input("SKU")
reason = st.selectbox("Reason", ["Damage", "Wrong Item"])
remark = st.text_area("Remark")

def highlighted_title(text):
    st.markdown(
        f'<div style="background-color:#ffff44; color:#222; font-weight:bold; padding:2px 8px; border-radius:3px; display:inline-block; margin-bottom:4px;">{text}</div>',
        unsafe_allow_html=True
    )

# Highlighted UI titles for visual alert
highlighted_title("Received Parcel Condition Photo")
parcel_photo = st.file_uploader("Drag and drop file here", type=["jpg", "jpeg", "png"], key="parcel_photo")

highlighted_title("AWB/Tracking Detail Photo")
awb_photo = st.file_uploader("Drag and drop file here", type=["jpg", "jpeg", "png"], key="awb_photo")

highlighted_title("Product Condition Photo 1")
product_photo_1 = st.file_uploader("Drag and drop file here", type=["jpg", "jpeg", "png"], key="product_photo_1")

highlighted_title("Product Condition Photo 2")
product_photo_2 = st.file_uploader("Drag and drop file here", type=["jpg", "jpeg", "png"], key="product_photo_2")

def save_temp_image(uploaded_file, name, max_dim=500):
    if uploaded_file:
        img = Image.open(uploaded_file)
        img = ImageOps.exif_transpose(img)
        img.thumbnail((max_dim, max_dim))  # Resize for fitting
        img_path = f"temp_{name}.png"
        img.save(img_path)
        return img_path
    return None

if st.button("Generate PDF"):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()

    # Plain PDF (no highlight)
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 14, "Order Issue Report", ln=1, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Brand: {brand}   Platform: {platform}", ln=1)
    pdf.cell(0, 6, f"Order ID: {order_id}", ln=1)
    pdf.cell(0, 6, f"Tracking: {tracking}   SKU: {sku}", ln=1)
    pdf.cell(0, 6, f"Reason: {reason}", ln=1)
    pdf.cell(0, 6, f"Remark: {remark}", ln=1)
    pdf.ln(2)

    # Image grid setup (2 columns x 2 rows)
    img_width = 65  # mm
    img_height = 50 # mm
    margin_x = 20
    margin_y = pdf.get_y() + 3
    col_spacing = 90
    row_spacing = 60

    photos = [
        (parcel_photo, "Received Parcel Condition"),
        (awb_photo, "AWB/Tracking Detail"),
        (product_photo_1, "Product Condition Photo 1"),
        (product_photo_2, "Product Condition Photo 2"),
    ]

    temp_files = []
    for i, (photo, caption) in enumerate(photos):
        if photo:
            img_path = save_temp_image(photo, i)
            temp_files.append(img_path)
            # Position calculation (2x2 grid)
            col = i % 2
            row = i // 2
            x = margin_x + col * col_spacing
            y = margin_y + row * row_spacing
            pdf.image(img_path, x=x, y=y, w=img_width, h=img_height)
            pdf.set_xy(x, y + img_height + 2)
            pdf.set_font("Arial", "B", 10)
            pdf.cell(img_width, 7, caption, align="C")
            pdf.set_font("Arial", "", 10)

    # Export PDF file name according to order_id
    pdf_filename = f"{order_id if order_id else 'order_issue_report'}.pdf"
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    st.download_button(f"Download PDF ({pdf_filename})", data=pdf_bytes, file_name=pdf_filename, mime="application/pdf")

    # Clean up temp files
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
        except Exception:
            pass
