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
# 2. PREMIUM DARK THEME
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    section[data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .stTextInput > div > div > input, .stNumberInput > div > div > input, .stSelectbox > div > div > div {
        background-color: #0E1117; color: white; border: 1px solid #30363d;
    }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label, .stRadio label, .stCheckbox label {
        color: #e6edf3 !important;
    }
    div.stButton > button {
        width: 100%; background: linear-gradient(90deg, #238636 0%, #2ea043 100%);
        color: white; border: none; padding: 12px; font-weight: bold; border-radius: 6px;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #2ea043 0%, #3fb950 100%);
    }
    h1, h2, h3 { color: #58a6ff !important; }
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
        ["📸 ফটো মেকার (লাইভ মুভ)", "🔄 ইমেজ কনভার্টার", "✨ ফটো রিস্টোরার (AI)", "📱 QR কোড জেনারেটর"]
    )
    st.markdown("---")

# ==========================================
# SESSION STATE SETUP (For Live Moving)
# ==========================================
if 'processed_photo' not in st.session_state:
    st.session_state.processed_photo = None

# ==========================================
# TOOL 1: PHOTO MAKER (LIVE MOVE)
# ==========================================
if selected_tool == "📸 ফটো মেকার (লাইভ মুভ)":
    st.header("📸 স্টুডিও মাস্টার (লাইভ মুভমেন্ট)")
    
    # 1. Upload & Initial Settings
    col_upload, col_settings = st.columns([1, 2])
    
    with col_upload:
        uploaded_file = st.file_uploader("প্রথমে ছবি আপলোড করুন", type=["jpg", "png", "jpeg"])
        
        if uploaded_file:
            st.info("১. প্রথমে নিচের বাটন চেপে ছবি রেডি করুন।")
            size_mode = st.radio("সাইজ:", ["পাসপোর্ট (40x50 mm)", "স্ট্যাম্প (20x25 mm)"])
            bg_color = st.color_picker("ব্যাকগ্রাউন্ড:", "#3b82f6")
            
            # Additional AI Settings
            with st.expander("AI সেটিংস (উজ্জ্বলতা/জুম)"):
                brightness = st.slider("উজ্জ্বলতা", 0.5, 2.0, 1.1)
                contrast = st.slider("কন্ট্রাস্ট", 0.5, 2.0, 1.1)
                zoom = st.slider("জুম (Zoom)", 0.8, 1.5, 1.0)
                move_y_frame = st.slider("ফ্রেমের ভেতরে সরান", -100, 100, 0)
                add_border = st.checkbox("বর্ডার দিন?", value=True)

            # PROCESS BUTTON
            if st.button("⚙️ ছবি রেডি করুন (Process)"):
                with st.spinner("AI কাজ করছে..."):
                    try:
                        img = Image.open(uploaded_file)
                        no_bg = remove(img)
                        enhancer = ImageEnhance.Brightness(no_bg)
                        img = enhancer.enhance(brightness)
                        enhancer = ImageEnhance.Contrast(img)
                        img = enhancer.enhance(contrast)
                        
                        # Size Logic
                        if size_mode == "পাসপোর্ট (40x50 mm)":
                            target_w, target_h = 472, 590 
                        else:
                            target_w, target_h = 236, 295 
                        
                        canvas = Image.new("RGBA", (target_w, target_h), bg_color)
                        scale = (target_w / img.width) * zoom
                        nw, nh = int(img.width * scale), int(img.height * scale)
                        img = img.resize((nw, nh), Image.LANCZOS)
                        
                        x = (target_w - nw) // 2
                        y = (target_h - nh) + move_y_frame
                        canvas.paste(img, (x, y), img)
                        
                        if add_border:
                            canvas = ImageOps.expand(canvas, border=4, fill='white')
                            canvas = ImageOps.expand(canvas, border=1, fill='#cccccc')
                        
                        # Save to Session State (Memory)
                        st.session_state.processed_photo = canvas.convert("RGB")
                        st.session_state.photo_size = size_mode
                        st.success("ছবি রেডি! এখন ডানপাশে মুভ করুন 👉")
                        
                    except Exception as e: st.error(str(e))

    # 2. Live Moving Area (Right Side)
    with col_settings:
        if st.session_state.processed_photo is not None:
            st.markdown("### ২. ছবি সাজান (কাটা কাগজের জন্য)")
            
            # --- LIVE SLIDERS ---
            c1, c2, c3 = st.columns(3)
            with c1:
                # X Axis Move
                pos_x = st.slider("ডানে-বামে সরান (X)", 0, 2200, 50, step=10)
            with c2:
                # Y Axis Move
                pos_y = st.slider("উপরে-নিচে সরান (Y)", 0, 3000, 50, step=10)
            with c3:
                # Copy Count
                copies = st.slider("কয় কপি?", 1, 50, 4)
            
            gap = st.slider("ছবির মাঝখানের গ্যাপ", 0, 100, 30)

            # --- REAL-TIME GENERATION ---
            # This part runs instantly whenever a slider moves
            final_photo = st.session_state.processed_photo
            sheet = Image.new("RGB", (2480, 3508), "white")
            
            current_x = pos_x
            current_y = pos_y
            
            for i in range(copies):
                # Bounds check
                if current_x + final_photo.width > 2480:
                    current_x = pos_x # Reset X to start position
                    current_y += final_photo.height + gap # New Line
                
                if current_y + final_photo.height > 3508:
                    break # Stop if page ends
                
                sheet.paste(final_photo, (current_x, current_y))
                current_x += final_photo.width + gap

            # Display Result
            st.image(sheet, caption="A4 প্রিন্ট প্রিভিউ (লাইভ)", use_column_width=True)
            
            # Download
            buf = io.BytesIO()
            sheet.save(buf, format="JPEG", quality=95)
            st.download_button(f"📥 ডাউনলোড প্রিন্ট ফাইল", buf.getvalue(), "print_ready.jpg", "image/jpeg")
            
            if st.button("❌ নতুন ছবি নিন (Clear)"):
                st.session_state.processed_photo = None
                st.rerun()

        else:
            st.info("👈 বাম পাশ থেকে ছবি আপলোড করে 'ছবি রেডি করুন' বাটনে চাপ দিন।")
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/PDF_file_icon.svg/1200px-PDF_file_icon.svg.png", width=100, caption="Waiting...") # Placeholder

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
