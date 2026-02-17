import streamlit as st
from rembg import remove
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import io
import qrcode
import cv2
import numpy as np

# ==========================================
# 1. PAGE CONFIGURATION & THEME
# ==========================================
st.set_page_config(page_title="Shafin's Tools Pro", page_icon="⚡", layout="wide")

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
        color: white; border: none; padding: 12px; font-weight: bold; border-radius: 6px; transition: all 0.3s ease;
    }
    div.stButton > button:hover { background: linear-gradient(90deg, #2ea043 0%, #3fb950 100%); transform: translateY(-2px); }
    h1, h2, h3 { color: #58a6ff !important; }
    .streamlit-expanderHeader { background-color: #161b22; color: white; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/10061/10061839.png", width=70)
    st.title("Shafin's Tools")
    st.markdown("---")
    selected_tool = st.radio("টুলস মেনু:", ["📸 ফটো মেকার (Pro)", "🔄 ইমেজ কনভার্টার", "✨ ফটো রিস্টোরার (AI)", "📱 QR কোড জেনারেটর"])
    st.markdown("---")

# Session State for Photo Maker
if 'base_image' not in st.session_state:
    st.session_state.base_image = None

# ==========================================
# TOOL 1: PHOTO MAKER PRO (Beauty + Mixed)
# ==========================================
if selected_tool == "📸 ফটো মেকার (Pro)":
    st.header("📸 স্টুডিও মাস্টার প্রো (Beauty & Mixed)")
    
    col_upload, col_generate = st.columns([1, 2])
    
    # --- LEFT COLUMN: PROCESSING & BEAUTY ---
    with col_upload:
        uploaded_file = st.file_uploader("১. ছবি আপলোড করুন", type=["jpg", "png", "jpeg"])
        
        if uploaded_file:
            st.markdown("### এডিটিং প্যানেল")
            bg_color = st.color_picker("ব্যাকগ্রাউন্ড কালার:", "#3b82f6")
            
            with st.expander("✨ বিউটি ও কালার সেটিংস", expanded=True):
                # NEW: Beauty Slider
                smoothness = st.slider("ফেস স্মুথ (Beauty)", 0, 50, 0, help="মুখের দাগ দূর করতে এবং উজ্জ্বল করতে বাড়ান।")
                brightness = st.slider("উজ্জ্বলতা", 0.5, 1.5, 1.0)
                contrast = st.slider("কন্ট্রাস্ট", 0.5, 1.5, 1.0)
            
            if st.button("⚙️ ছবি প্রসেস করুন (Process)"):
                with st.spinner("AI কাজ করছে (Beauty & BG)..."):
                    try:
                        img = Image.open(uploaded_file)
                        
                        # 1. Background Remove
                        no_bg = remove(img)
                        
                        # 2. Beauty Enhancement (OpenCV Bilateral Filter)
                        if smoothness > 0:
                            # Convert PIL RGBA to OpenCV BGR
                            cv_img = cv2.cvtColor(np.array(no_bg.convert('RGB')), cv2.COLOR_RGB2BGR)
                            # Apply smoothing (sigma values depend on slider)
                            sigma = smoothness 
                            smooth_img = cv2.bilateralFilter(cv_img, d=9, sigmaColor=sigma*2, sigmaSpace=sigma)
                            # Convert back to PIL
                            no_bg = Image.fromarray(cv2.cvtColor(smooth_img, cv2.COLOR_BGR2RGB))

                        # 3. Brightness/Contrast
                        enhancer = ImageEnhance.Brightness(no_bg)
                        img = enhancer.enhance(brightness)
                        enhancer = ImageEnhance.Contrast(img)
                        img = enhancer.enhance(contrast)

                        # Save processed base image to session
                        st.session_state.base_image = img
                        st.success("ছবি রেডি! এখন ডানপাশে লেআউট তৈরি করুন। 👉")
                        
                    except Exception as e: st.error(f"Error: {e}")

    # --- RIGHT COLUMN: LAYOUT & GENERATION ---
    with col_generate:
        if st.session_state.base_image is not None:
            st.markdown("### ২. পেজ লেআউট তৈরি করুন")
            
            tab1, tab2 = st.tabs(["🔲 সিঙ্গেল সাইজ (লাইভ মুভ)", "🔀 মিক্সড (পাসপোর্ট + স্ট্যাম্প)"])
            
            # --- TAB 1: SINGLE SIZE LIVE MOVE (Existing Feature) ---
            with tab1:
                size_mode = st.radio("সাইজ সিলেক্ট করুন:", ["পাসপোর্ট (40x50 mm)", "স্ট্যাম্প (20x25 mm)"], horizontal=True)
                
                c1, c2, c3 = st.columns(3)
                with c1: pos_x = st.slider("ডানে-বামে (X)", 0, 2200, 50)
                with c2: pos_y = st.slider("উপরে-নিচে (Y)", 0, 3000, 50)
                with c3: copies = st.slider("কপি সংখ্যা", 1, 50, 4)
                
                with st.expander("পজিশন ও বর্ডার সেটিংস"):
                    zoom = st.slider("জুম (Zoom)", 0.8, 1.5, 1.0)
                    move_y_frame = st.slider("ফ্রেমের ভেতরে সরান", -100, 100, 0)
                    gap = st.slider("গ্যাপ", 0, 100, 30)
                    add_border = st.checkbox("বর্ডার দিন?", value=True, key="border_single")

                # Generate Single Photo Func
                def get_single_photo(target_w, target_h, border=True):
                    canvas = Image.new("RGBA", (target_w, target_h), bg_color)
                    img_base = st.session_state.base_image
                    scale = (target_w / img_base.width) * zoom
                    nw, nh = int(img_base.width * scale), int(img_base.height * scale)
                    img_resized = img_base.resize((nw, nh), Image.LANCZOS)
                    x = (target_w - nw) // 2
                    y = (target_h - nh) + move_y_frame
                    canvas.paste(img_resized, (x, y), img_resized)
                    if border:
                        canvas = ImageOps.expand(canvas, border=4, fill='white')
                        canvas = ImageOps.expand(canvas, border=1, fill='#cccccc')
                    return canvas.convert("RGB")

                # Live Generation logic
                if size_mode == "পাসপোর্ট (40x50 mm)": tw, th = 472, 590
                else: tw, th = 236, 295
                
                final_photo = get_single_photo(tw, th, add_border)
                
                sheet = Image.new("RGB", (2480, 3508), "white")
                curr_x, curr_y = pos_x, pos_y
                for _ in range(copies):
                    if curr_x + final_photo.width > 2480:
                        curr_x = pos_x
                        curr_y += final_photo.height + gap
                    if curr_y + final_photo.height > 3508: break
                    sheet.paste(final_photo, (curr_x, curr_y))
                    curr_x += final_photo.width + gap
                
                st.image(sheet, caption="লাইভ প্রিভিউ", use_column_width=True)
                buf = io.BytesIO()
                sheet.save(buf, format="JPEG", quality=95)
                st.download_button("📥 ডাউনলোড (সিঙ্গেল)", buf.getvalue(), "single_layout.jpg", "image/jpeg")

            # --- TAB 2: MIXED LAYOUT (NEW FEATURE) ---
            with tab2:
                st.info("একই পেজে পাসপোর্ট এবং স্ট্যাম্প ছবি একসাথে সাজান।")
                c_p, c_s = st.columns(2)
                with c_p: num_pass = st.number_input("পাসপোর্ট কপি:", min_value=0, value=4)
                with c_s: num_stamp = st.number_input("স্ট্যাম্প কপি:", min_value=0, value=8)
                
                mix_border = st.checkbox("বর্ডার দিন?", value=True, key="border_mix")
                mix_gap = st.slider("গ্যাপ (Mixed)", 10, 50, 20)

                if st.button("🔀 মিক্সড পেজ তৈরি করুন"):
                    # Generate base photos for both sizes (using default center focus)
                    img_base = st.session_state.base_image
                    
                    def create_sized_photo(tw, th):
                        cvs = Image.new("RGBA", (tw, th), bg_color)
                        scale = tw / img_base.width
                        nw, nh = int(img_base.width * scale), int(img_base.height * scale)
                        img_r = img_base.resize((nw, nh), Image.LANCZOS)
                        cvs.paste(img_r, ((tw-nw)//2, th-nh), img_r) # Align bottom
                        if mix_border:
                             cvs = ImageOps.expand(cvs, border=3, fill='white')
                             cvs = ImageOps.expand(cvs, border=1, fill='#cccccc')
                        return cvs.convert("RGB")

                    pass_img = create_sized_photo(472, 590)
                    stamp_img = create_sized_photo(236, 295)

                    # Create A4 Sheet
                    sheet_mix = Image.new("RGB", (2480, 3508), "white")
                    
                    # Place Passports first
                    cx, cy = 100, 100 # Start margins
                    p_count = 0
                    for _ in range(num_pass):
                        if cx + pass_img.width > 2480:
                            cx = 100
                            cy += pass_img.height + mix_gap
                        if cy + pass_img.height > 3508: break
                        sheet_mix.paste(pass_img, (cx, cy))
                        cx += pass_img.width + mix_gap
                        p_count += 1
                    
                    # Place Stamps starting from next row
                    if num_stamp > 0:
                        cx = 100
                        if p_count > 0: cy += pass_img.height + mix_gap * 2 # Move to new row area
                        
                        for _ in range(num_stamp):
                            if cx + stamp_img.width > 2480:
                                cx = 100
                                cy += stamp_img.height + mix_gap
                            if cy + stamp_img.height > 3508: break
                            sheet_mix.paste(stamp_img, (cx, cy))
                            cx += stamp_img.width + mix_gap

                    st.image(sheet_mix, caption="মিক্সড লেআউট প্রিভিউ", use_column_width=True)
                    buf_m = io.BytesIO()
                    sheet_mix.save(buf_m, format="JPEG", quality=95)
                    st.download_button("📥 ডাউনলোড (মিক্সড)", buf_m.getvalue(), "mixed_layout.jpg", "image/jpeg", type="primary")

        else:
            st.info("👈 প্রথমে বাম পাশ থেকে ছবি আপলোড করে প্রসেস করুন।")

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
