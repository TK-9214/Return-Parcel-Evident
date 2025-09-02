import streamlit as st
from fpdf import FPDF
from PIL import Image, ImageOps
import io
import os

st.title("Order Issue PDF Generator (Landscape, Auto-Rotate Photos)")

# User input fields
brand = st.text_input("Brand")
platform = st.text_input("Platform")
order_id = st.text_input("Order ID")
tracking = st.text_input("Tracking Number")
sku = st.text_input("SKU")
reason = st.selectbox("Reason", ["Damage", "Wrong Item"])

# Image upload fields
parcel_photo = st.file_uploader("Received Parcel Condition Photo", type=["jpg", "jpeg", "png"])
awb_photo = st.file_uploader("AWB/Tracking Detail Photo", type=["jpg", "jpeg", "png"])
product_photo_1 = st.file_uploader("Product Condition Photo 1", type=["jpg", "jpeg", "png"])
product_photo_2 = st.file_uploader("Product Condition Photo 2", type=["jpg", "jpeg", "png"])

def save_temp_image(uploaded_file, name):
    if uploaded_file:
        img = Image.open(uploaded_file)
        # Auto-correct orientation based on EXIF
        img = ImageOps.exif_transpose(img)
        img_path = f"temp_{name}.png"
        img.save(img_path)
        return img_path
    return None

if st.button("Generate PDF"):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Order Issue Report", ln=1, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Brand: {brand}   Platform: {platform}", ln=1)
    pdf.cell(0, 8, f"Order ID: {order_id}", ln=1)
    pdf.cell(0, 8, f"Tracking: {tracking}   SKU: {sku}", ln=1)
    pdf.cell(0, 8, f"Reason: {reason}", ln=1)
    pdf.ln(4)

    # Image layout: 2 rows x 2 columns
    img_width = 80
    img_height = 60
    x_positions = [10, 110]
    y_positions = [pdf.get_y(), pdf.get_y() + img_height + 15]

    photos = [
        (parcel_photo, "Received Parcel Condition"),
        (awb_photo, "AWB/Tracking Detail"),
        (product_photo_1, "Product Condition Photo 1"),
        (product_photo_2, "Product Condition Photo 2"),
    ]

    coords = [(x, y) for y in y_positions for x in x_positions]

    temp_files = []

    for idx, (photo, caption) in enumerate(photos):
        if photo:
            img_path = save_temp_image(photo, idx)
            temp_files.append(img_path)
            x, y = coords[idx]
            pdf.image(img_path, x=x, y=y, w=img_width, h=img_height)
            pdf.set_xy(x, y + img_height)
            pdf.set_font("Arial", "I", 10)
            pdf.cell(img_width, 8, caption, align="C")
    
    # Export PDF file name according to order_id (fall back to generic if empty)
    pdf_filename = f"{order_id if order_id else 'order_issue_report'}.pdf"
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    st.download_button(f"Download PDF ({pdf_filename})", data=pdf_bytes, file_name=pdf_filename, mime="application/pdf")

    # Clean up temporary images
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
        except Exception:
            pass
