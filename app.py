import streamlit as st
from rembg import remove
from PIL import Image, ImageEnhance, ImageOps
import io
import qrcode
import cv2
import numpy as np

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
    
    /* Input Fields */
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input,
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
    
    /* Buttons */
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
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/10061/10061839.png", width=70)
    st.title("Shafin's Tools")
    st.markdown("---")
    
    selected_tool = st.radio(
        "টুলস মেনু:",
        [
            "📸 ফটো মেকার (পেপার সেভার)",
            "🔄 ইমেজ কনভার্টার",
            "✨ ফটো রিস্টোরার (AI)",
            "📱 QR কোড জেনারেটর"
        ]
    )
    st.markdown("---")
    st.caption("Auto-Fill Paper Saving Mode")

# ==========================================
# TOOL 1: PHOTO MAKER (SMART AUTO FILL)
# ==========================================
if selected_tool == "📸 ফটো মেকার (পেপার সেভার)":
    st.header("📸 স্টুডিও মাস্টার (স্মার্ট গ্রিড)")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        uploaded_file = st.file_uploader("ছবি আপলোড করুন", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            st.markdown("### সেটিংস")
            
            size_mode = st.radio("সাইজ:", ["পাসপোর্ট (40x50 mm)", "স্ট্যাম্প (20x25 mm)"], horizontal=True)
            bg_color = st.color_picker("ব্যাকগ্রাউন্ড:", "#3b82f6")
            
            # Smart Copy Input
            st.info("💡 টিপস: পেপার ভরাতে চাইলে কপি সংখ্যা বাড়িয়ে দিন।")
            num_copies = st.number_input("কয় কপি লাগবে?", 1, 100, 30) # Default increased
            
            add_border = st.checkbox("বর্ডার ও কাটার দাগ?", value=True)
            
            # Gap Control (New)
            gap_size = st.slider("ছবির মাঝখানের গ্যাপ (Gap)", 0, 50, 10)
            
            with st.expander("অ্যাডভান্সড এডিটিং"):
                brightness = st.slider("উজ্জ্বলতা", 0.5, 2.0, 1.1)
                contrast = st.slider("কন্ট্রাস্ট", 0.5, 2.0, 1.1)
                zoom = st.slider("জুম", 0.8, 1.5, 1.0)
                move_y = st.slider("উপরে-নিচে সরান", -100, 100, 0)

    with col2:
        if uploaded_file:
            if st.button("🚀 পেজ সাজান (Generate)"):
                with st.spinner("AI পেজ সাজাচ্ছে..."):
                    try:
                        # 1. Image Processing
                        img = Image.open(uploaded_file)
                        no_bg = remove(img)
                        enhancer = ImageEnhance.Brightness(no_bg)
                        img = enhancer.enhance(brightness)
                        enhancer = ImageEnhance.Contrast(img)
                        img = enhancer.enhance(contrast)
                        
                        # 2. Target Size Calculation (300 DPI)
                        if size_mode == "পাসপোর্ট (40x50 mm)":
                            target_w, target_h = 472, 590 
                        else:
                            target_w, target_h = 236, 295 
                        
                        # 3. Create Individual Photo
                        canvas = Image.new("RGBA", (target_w, target_h), bg_color)
                        scale = (target_w / img.width) * zoom
                        nw, nh = int(img.width * scale), int(img.height * scale)
                        img = img.resize((nw, nh), Image.LANCZOS)
                        
                        x = (target_w - nw) // 2
                        y = (target_h - nh) + move_y
                        canvas.paste(img, (x, y), img)
                        
                        if add_border:
                            canvas = ImageOps.expand(canvas, border=3, fill='white')
                            canvas = ImageOps.expand(canvas, border=1, fill='#cccccc')
                            
                        final_photo = canvas.convert("RGB")
                        st.image(final_photo, caption=f"সিঙ্গেল কপি ({size_mode})", width=120)
                        
                        # 4. SMART GRID LOGIC (Paper Saver)
                        # A4 Size: 2480 x 3508 pixels
                        sheet_w, sheet_h = 2480, 3508
                        sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
                        
                        # Starting Position (Minimal Margins)
                        margin_top = 50   # Only 50px from top
                        margin_left = 50  # Only 50px from left
                        
                        current_x = margin_left
                        current_y = margin_top
                        
                        photos_placed = 0
                        
                        for i in range(num_copies):
                            # Check if photo fits in current row
                            if current_x + final_photo.width > sheet_w:
                                # Move to next row
                                current_x = margin_left
                                current_y += final_photo.height + gap_size
                            
                            # Check if photo fits in page height
                            if current_y + final_photo.height > sheet_h:
                                st.warning(f"⚠️ পেজ ভরে গেছে! মাত্র {photos_placed} টি ছবি আটানো সম্ভব হয়েছে।")
                                break
                            
                            # Paste Photo
                            sheet.paste(final_photo, (current_x, current_y))
                            
                            # Move X for next photo
                            current_x += final_photo.width + gap_size
                            photos_placed += 1
                                
                        st.image(sheet, caption=f"A4 প্রিন্ট প্রিভিউ ({photos_placed} কপি)", use_column_width=True)
                        
                        # Download
                        buf = io.BytesIO()
                        sheet.save(buf, format="JPEG", quality=95)
                        st.download_button(f"📥 ডাউনলোড প্রিন্ট ফাইল", buf.getvalue(), "paper_saver_print.jpg", "image/jpeg")
                        
                    except Exception as e: st.error(str(e))

# ==========================================
# TOOL 2: IMAGE CONVERTER
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
# TOOL 3: PHOTO RESTORER
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
# TOOL 4: QR CODE
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
