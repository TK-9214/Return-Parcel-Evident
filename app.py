import streamlit as st
from fpdf import FPDF
from PIL import Image, ImageOps
import os

st.title("Order Issue PDF Generator (Full Landscape Page)")

# Inputs
brand = st.text_input("Brand")
platform = st.text_input("Platform")
order_id = st.text_input("Order ID")
tracking = st.text_input("Tracking Number")
sku = st.text_input("SKU")
reason = st.selectbox("Reason", ["Damage", "Wrong Item"])

parcel_photo = st.file_uploader("Received Parcel Condition Photo", type=["jpg", "jpeg", "png"])
awb_photo = st.file_uploader("AWB/Tracking Detail Photo", type=["jpg", "jpeg", "png"])
product_photo_1 = st.file_uploader("Product Condition Photo 1", type=["jpg", "jpeg", "png"])
product_photo_2 = st.file_uploader("Product Condition Photo 2", type=["jpg", "jpeg", "png"])

def save_temp_image(uploaded_file, name, max_dim=800):
    if uploaded_file:
        img = Image.open(uploaded_file)
        img = ImageOps.exif_transpose(img)
        img.thumbnail((max_dim, max_dim))
        img_path = f"temp_{name}.png"
        img.save(img_path)
        return img_path
    return None

if st.button("Generate PDF"):
    # A4 landscape size: 297mm x 210mm
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()

    # Top info
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 14, "Order Issue Report", ln=1, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.set_xy(20, 22)
    pdf.multi_cell(0, 8, f"Brand: {brand}     Platform: {platform}\nOrder ID: {order_id}\nTracking: {tracking}     SKU: {sku}\nReason: {reason}")

    # Image grid setup
    img_width = 90  # Wider for fuller page
    img_height = 65
    x_start = 25
    y_start = 60
    x_gap = img_width + 18
    y_gap = img_height + 20

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
            col = i % 2
            row = i // 2
            x = x_start + col * x_gap
            y = y_start + row * y_gap
            pdf.image(img_path, x=x, y=y, w=img_width, h=img_height)
            pdf.set_xy(x, y + img_height + 2)
            pdf.set_font("Arial", "I", 11)
            pdf.cell(img_width, 8, caption, align="C")

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
