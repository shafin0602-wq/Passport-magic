import streamlit as st
from rembg import remove
from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageFont, ImageFilter
import io
import datetime
import qrcode
import cv2
import numpy as np
from pypdf import PdfWriter

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Shafin's Tools", page_icon="⚡", layout="wide")

# ==========================================
# 2. PREMIUM DARK THEME (CSS)
# ==========================================
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Sidebar Background */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Input Fields (Dark Mode Fix) */
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: #0E1117;
        color: white;
        border: 1px solid #30363d;
    }
    
    /* Text Color Fixes */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label,
    .stRadio label, .stCheckbox label {
        color: #e6edf3 !important;
    }
    
    /* Buttons - Pro Green/Blue Gradient */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #238636 0%, #2ea043 100%);
        color: white;
        border: none;
        padding: 12px;
        font-weight: bold;
        border-radius: 6px;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #2ea043 0%, #3fb950 100%);
        box-shadow: 0 4px 12px rgba(46, 160, 67, 0.4);
        transform: translateY(-2px);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #58a6ff !important;
    }
    
    /* Divider */
    hr {
        border-color: #30363d;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #161b22;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================

def bangla_date_converter(eng_date):
    bangla_months = ["বৈশাখ", "জ্যৈষ্ঠ", "আষাঢ়", "শ্রাবণ", "ভাদ্র", "আশ্বিন", "কার্তিক", "অগ্রহায়ু", "পৌষ", "মাঘ", "ফাল্গুন", "চৈত্র"]
    day, month, year = eng_date.day, eng_date.month, eng_date.year
    
    if month > 4 or (month == 4 and day >= 14): bangla_year = year - 593
    else: bangla_year = year - 594
    
    if month == 4 and day >= 14: idx = 0
    elif month == 5 and day < 15: idx = 0
    elif month == 5: idx = 1
    elif month == 6 and day < 15: idx = 1
    elif month == 6: idx = 2
    elif month == 7 and day < 16: idx = 2
    elif month == 7: idx = 3
    elif month == 8 and day < 16: idx = 3
    elif month == 8: idx = 4
    elif month == 9 and day < 16: idx = 4
    elif month == 9: idx = 5
    elif month == 10 and day < 16: idx = 5
    elif month == 10: idx = 6
    elif month == 11 and day < 15: idx = 6
    elif month == 11: idx = 7
    elif month == 12 and day < 15: idx = 7
    elif month == 12: idx = 8
    elif month == 1 and day < 14: idx = 8
    elif month == 1: idx = 9
    elif month == 2 and day < 13: idx = 9
    elif month == 2: idx = 10
    elif month == 3 and day < 15: idx = 10
    elif month == 3: idx = 11
    else: idx = 11
    
    return f"{day}ই {bangla_months[idx]}, {bangla_year} বঙ্গাব্দ"

def convert_to_bangla_digits(number):
    eng, ban = "0123456789", "০১২৩৪৫৬৭৮৯"
    return str(number).translate(str(number).maketrans(eng, ban))

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/10061/10061839.png", width=70)
    st.title("Shafin's Tools")
    st.markdown("---")
    
    selected_tool = st.radio(
        "টুলস মেনু:",
        [
            "📸 পাসপোর্ট ফটো মেকার",
            "📑 স্মার্ট ডকুমেন্ট স্ক্যানার",
            "🆔 NID/ফর্ম ফিলার",
            "📂 PDF জয়েনার (Merge)",
            "🔄 ইমেজ কনভার্টার",
            "✨ ফটো রিস্টোরার (AI)",
            "📅 বয়স ক্যালকুলেটর",
            "🗓️ বাংলা তারিখ কনভার্টার",
            "📱 QR কোড জেনারেটর"
        ]
    )
    st.markdown("---")
    st.caption("All-in-One Digital Center")

# ==========================================
# TOOL 1: PASSPORT PHOTO MAKER
# ==========================================
if selected_tool == "📸 পাসপোর্ট ফটো মেকার":
    st.header("📸 পাসপোর্ট স্টুডিও প্রো")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        uploaded_file = st.file_uploader("ছবি আপলোড করুন", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            st.markdown("### সেটিংস")
            bg_color = st.color_picker("ব্যাকগ্রাউন্ড:", "#3b82f6")
            num_copies = st.number_input("A4 পেজে কয় কপি?", 1, 25, 4)
            add_border = st.checkbox("বর্ডার ও কাটার দাগ?", value=True)
            
            with st.expander("অ্যাডভান্সড এডিটিং"):
                brightness = st.slider("উজ্জ্বলতা", 0.5, 2.0, 1.1)
                contrast = st.slider("কন্ট্রাস্ট", 0.5, 2.0, 1.1)
                zoom = st.slider("জুম", 0.8, 1.5, 1.0)
                move_y = st.slider("উপরে-নিচে সরান", -100, 100, 0)

    with col2:
        if uploaded_file:
            if st.button("🚀 ছবি তৈরি করুন"):
                with st.spinner("AI কাজ করছে..."):
                    try:
                        # 1. Process Image
                        img = Image.open(uploaded_file)
                        no_bg = remove(img)
                        enhancer = ImageEnhance.Brightness(no_bg)
                        img = enhancer.enhance(brightness)
                        enhancer = ImageEnhance.Contrast(img)
                        img = enhancer.enhance(contrast)
                        
                        # 2. Canvas Logic
                        target_w, target_h = 472, 590
                        canvas = Image.new("RGBA", (target_w, target_h), bg_color)
                        
                        scale = (target_w / img.width) * zoom
                        nw, nh = int(img.width * scale), int(img.height * scale)
                        img = img.resize((nw, nh), Image.LANCZOS)
                        
                        x = (target_w - nw) // 2
                        y = (target_h - nh) + move_y
                        canvas.paste(img, (x, y), img)
                        
                        if add_border:
                            canvas = ImageOps.expand(canvas, border=5, fill='white')
                            canvas = ImageOps.expand(canvas, border=1, fill='#cccccc')
                            
                        passport = canvas.convert("RGB")
                        
                        # 3. Create A4 Sheet
                        sheet = Image.new("RGB", (2480, 3508), "white")
                        cols, rows, gap = 4, 6, 50
                        margin_left = (2480 - ((cols*passport.width) + (cols-1)*gap)) // 2
                        
                        count = 0
                        for r in range(rows):
                            for c in range(cols):
                                if count >= num_copies: break
                                x_off = margin_left + c*(passport.width+gap)
                                y_off = 150 + r*(passport.height+gap)
                                sheet.paste(passport, (x_off, y_off))
                                count += 1
                                
                        st.image(sheet, caption="A4 প্রিন্ট প্রিভিউ", use_column_width=True)
                        
                        buf = io.BytesIO()
                        sheet.save(buf, format="JPEG", quality=95)
                        st.download_button("📥 ডাউনলোড প্রিন্ট ফাইল", buf.getvalue(), "passport_print.jpg", "image/jpeg")
                    except Exception as e: st.error(str(e))

# ==========================================
# TOOL 2: SMART DOCUMENT SCANNER
# ==========================================
elif selected_tool == "📑 স্মার্ট ডকুমেন্ট স্ক্যানার":
    st.header("📑 স্মার্ট স্ক্যানার (CamScanner)")
    st.write("বাজে কোয়ালিটির ডকুমেন্টের ছবিকে পরিষ্কার স্ক্যান কপিতে রূপান্তর করুন।")
    
    doc_file = st.file_uploader("ডকুমেন্টের ছবি দিন", type=["jpg", "png"])
    
    if doc_file:
        file_bytes = np.asarray(bytearray(doc_file.read()), dtype=np.uint8)
        opencv_image = cv2.imdecode(file_bytes, 1)
        st.image(opencv_image, channels="BGR", caption="অরিজিনাল", width=300)
        
        filter_mode = st.radio("ফিল্টার:", ["ম্যাজিক কালার", "সাদা-কালো (B&W)", "পরিষ্কার (Clear)"], horizontal=True)
        
        if st.button("✨ স্ক্যান করুন"):
            processed = opencv_image.copy()
            if filter_mode == "সাদা-কালো (B&W)":
                gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
                processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                final_pil = Image.fromarray(processed)
            elif filter_mode == "ম্যাজিক কালার":
                processed = cv2.convertScaleAbs(processed, alpha=1.2, beta=10)
                hsv = cv2.cvtColor(processed, cv2.COLOR_BGR2HSV)
                hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], 1.2)
                processed = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                final_pil = Image.fromarray(cv2.cvtColor(processed, cv2.COLOR_BGR2RGB))
            else:
                processed = cv2.convertScaleAbs(processed, alpha=1.1, beta=5)
                final_pil = Image.fromarray(cv2.cvtColor(processed, cv2.COLOR_BGR2RGB))

            st.image(final_pil, caption="ফাইনাল স্ক্যান", use_column_width=True)
            buf = io.BytesIO()
            final_pil.save(buf, format="JPEG", quality=95)
            st.download_button("📥 ডাউনলোড স্ক্যান কপি", buf.getvalue(), "scanned_doc.jpg", "image/jpeg")

# ==========================================
# TOOL 3: NID/FORM FILLER
# ==========================================
elif selected_tool == "🆔 NID/ফর্ম ফিলার":
    st.header("🆔 অটোমেটিক ফর্ম ফিলার")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("নাম (Name)")
        father = st.text_input("পিতার নাম")
        dob = st.text_input("জন্ম তারিখ")
        id_no = st.text_input("ID Number")
    
    with col2:
        st.info("কার্ড প্রিভিউ")
        if st.button("কার্ড জেনারেট করুন"):
            card = Image.new("RGB", (600, 380), "#f0fdf4")
            draw = ImageDraw.Draw(card)
            draw.rectangle([(10, 10), (590, 370)], outline="#16a34a", width=4)
            draw.text((220, 30), "National ID Card", fill="#16a34a")
            try: font = ImageFont.load_default()
            except: font = ImageFont.load_default()

            draw.text((50, 80), f"Name: {name}", fill="black", font=font)
            draw.text((50, 120), f"Father: {father}", fill="black", font=font)
            draw.text((50, 160), f"DOB: {dob}", fill="red", font=font)
            draw.text((50, 200), f"ID NO: {id_no}", fill="blue", font=font)
            draw.rectangle([(450, 80), (550, 200)], outline="black")
            draw.text((470, 130), "Photo", fill="gray")
            
            st.image(card)
            buf = io.BytesIO()
            card.save(buf, format="JPEG")
            st.download_button("📥 ডাউনলোড কার্ড", buf.getvalue(), "id_card.jpg", "image/jpeg")

# ==========================================
# TOOL 4: PDF MERGER
# ==========================================
elif selected_tool == "📂 PDF জয়েনার (Merge)":
    st.header("📂 PDF ও ইমেজ জয়েনার")
    st.write("একাধিক PDF বা ছবি একসাথে জোড়া দিয়ে একটি ফাইল বানান।")
    
    uploaded_files = st.file_uploader("ফাইল দিন (PDF/Image)", 
                                      type=["pdf", "jpg", "png"], 
                                      accept_multiple_files=True)
    
    if uploaded_files and st.button("🔗 ফাইল জোড়া লাগান"):
        merger = PdfWriter()
        try:
            for file in uploaded_files:
                if file.type in ["image/jpeg", "image/png", "image/jpg"]:
                    img = Image.open(file)
                    img_pdf = io.BytesIO()
                    img = img.convert('RGB')
                    img.save(img_pdf, format="PDF")
                    merger.append(img_pdf)
                else:
                    merger.append(file)
            
            output_pdf = io.BytesIO()
            merger.write(output_pdf)
            st.success("✅ ফাইল জোড়া লাগানো হয়েছে!")
            st.download_button("📥 ডাউনলোড মার্জড PDF", output_pdf.getvalue(), "merged.pdf", "application/pdf")
        except Exception as e: st.error(str(e))

# ==========================================
# TOOL 5: IMAGE CONVERTER
# ==========================================
elif selected_tool == "🔄 ইমেজ কনভার্টার":
    st.header("🔄 ইমেজ ফরম্যাট কনভার্টার")
    img_file = st.file_uploader("ছবি দিন", type=["png", "jpg", "jpeg", "webp"])
    target_format = st.selectbox("কোন ফরম্যাটে নিবেন?", ["JPEG", "PNG", "PDF", "WEBP"])
    
    if img_file and st.button("🔄 কনভার্ট করুন"):
        image = Image.open(img_file)
        if image.mode in ("RGBA", "P") and target_format == "JPEG":
            image = image.convert("RGB")
            
        buf = io.BytesIO()
        if target_format == "JPEG":
            image.save(buf, format="JPEG", quality=100)
            mime, ext = "image/jpeg", "jpg"
        elif target_format == "PNG":
            image.save(buf, format="PNG")
            mime, ext = "image/png", "png"
        elif target_format == "PDF":
            image.save(buf, format="PDF")
            mime, ext = "application/pdf", "pdf"
        elif target_format == "WEBP":
            image.save(buf, format="WEBP")
            mime, ext = "image/webp", "webp"
            
        st.success("কনভার্ট সম্পন্ন!")
        st.download_button(f"📥 ডাউনলোড {target_format}", buf.getvalue(), f"converted.{ext}", mime)

# ==========================================
# TOOL 6: PHOTO RESTORER
# ==========================================
elif selected_tool == "✨ ফটো রিস্টোরার (AI)":
    st.header("✨ ফটো এনহ্যান্সার")
    uploaded_file = st.file_uploader("নষ্ট ছবি দিন", type=["jpg", "png"])
    if uploaded_file:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        st.image(img, channels="BGR", caption="আগের ছবি", width=300)
        
        mode = st.radio("মোড:", ["শার্পনেস", "কালার ফিক্স", "নয়েজ রিমুভ"], horizontal=True)
        if st.button("✨ ফিক্স করুন"):
            processed = img.copy()
            if mode == "শার্পনেস":
                kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
                processed = cv2.filter2D(processed, -1, kernel)
            elif mode == "কালার ফিক্স":
                img_yuv = cv2.cvtColor(processed, cv2.COLOR_BGR2YUV)
                img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
                processed = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
            elif mode == "নয়েজ রিমুভ":
                processed = cv2.fastNlMeansDenoisingColored(processed, None, 10, 10, 7, 21)

            final_pil = Image.fromarray(cv2.cvtColor(processed, cv2.COLOR_BGR2RGB))
            st.image(final_pil, caption="ফিক্স করা ছবি", width=300)
            buf = io.BytesIO()
            final_pil.save(buf, format="JPEG")
            st.download_button("📥 ডাউনলোড", buf.getvalue(), "restored.jpg", "image/jpeg")

# ==========================================
# TOOL 7: AGE CALCULATOR
# ==========================================
elif selected_tool == "📅 বয়স ক্যালকুলেটর":
    st.header("📅 বয়স ক্যালকুলেটর")
    col1, col2 = st.columns(2)
    with col1: dob = st.date_input("জন্ম তারিখ", datetime.date(2000, 1, 1))
    with col2: target = st.date_input("হিসাবের তারিখ", datetime.date.today())
        
    if st.button("হিসাব করুন"):
        delta = target - dob
        years = delta.days // 365
        remaining_days = delta.days % 365
        months = remaining_days // 30
        days = remaining_days % 30
        st.success(f"বয়স: {years} বছর, {months} মাস, {days} দিন (প্রায়)")

# ==========================================
# TOOL 8: BANGLA DATE
# ==========================================
elif selected_tool == "🗓️ বাংলা তারিখ কনভার্টার":
    st.header("🗓️ বাংলা তারিখ কনভার্টার")
    eng_date = st.date_input("ইংরেজি তারিখ সিলেক্ট করুন")
    if st.button("কনভার্ট করুন"):
        st.success(f"বাংলা তারিখ: {convert_to_bangla_digits(bangla_date_converter(eng_date))}")

# ==========================================
# TOOL 9: QR CODE
# ==========================================
elif selected_tool == "📱 QR কোড জেনারেটর":
    st.header("📱 QR কোড মেকার")
    data = st.text_input("লিংক বা টেক্সট লিখুন")
    color = st.color_picker("QR রং", "#000000")
    if data and st.button("জেনারেট করুন"):
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=color, back_color="white")
        st.image(img.get_image(), width=250)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button("📥 ডাউনলোড", buf.getvalue(), "qrcode.png", "image/png")
