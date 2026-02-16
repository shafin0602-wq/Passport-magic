import streamlit as st
from rembg import remove
from PIL import Image, ImageEnhance, ImageOps
import io
import datetime

# 1. Page Configuration
st.set_page_config(page_title="IT Lancer Clone Tools", page_icon="🛠️", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    div.stButton > button { width: 100%; background-color: #2563eb; color: white; border-radius: 5px; padding: 10px; }
    div.stButton > button:hover { background-color: #1d4ed8; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🛠️ ডিজিটাল সেবা টুলস")
    selected_tool = st.radio(
        "টুল সিলেক্ট করুন:",
        ["📸 পাসপোর্ট ফটো মেকার", "✍️ ডিজিটাল স্বাক্ষর (300x80)", "🆔 NID/কার্ড প্রিন্ট সেটআপ", "📉 ইমেজ সাইজ কমান (KB)"]
    )
    st.divider()
    st.write("Developed with Python")

# ==========================================
# TOOL 1: PASSPORT PHOTO MAKER (Previous Code)
# ==========================================
if selected_tool == "📸 পাসপোর্ট ফটো মেকার":
    st.header("📸 পাসপোর্ট স্টুডিও প্রো")
    col1, col2 = st.columns([1, 2])
    with col1:
        uploaded_file = st.file_uploader("ছবি দিন", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            num_copies = st.number_input("কয় কপি?", 1, 25, 4)
            bg_color = st.color_picker("ব্যাকগ্রাউন্ড:", "#3b82f6")
            brightness = st.slider("উজ্জ্বলতা", 0.5, 2.0, 1.1)
            contrast = st.slider("কন্ট্রাস্ট", 0.5, 2.0, 1.1)
            zoom_level = st.slider("জুম", 0.8, 1.5, 1.0)
            move_y = st.slider("সরান (Y)", -100, 100, 0)
            add_border = st.checkbox("বর্ডার?", value=True)

    with col2:
        if uploaded_file:
            if st.button("🚀 প্রসেস করুন"):
                with st.spinner("কাজ চলছে..."):
                    try:
                        img = Image.open(uploaded_file)
                        no_bg = remove(img)
                        enhancer = ImageEnhance.Brightness(no_bg)
                        img = enhancer.enhance(brightness)
                        enhancer = ImageEnhance.Contrast(img)
                        img = enhancer.enhance(contrast)
                        
                        target_w, target_h = 472, 590
                        canvas = Image.new("RGBA", (target_w, target_h), bg_color)
                        
                        scale = (target_w / img.width) * zoom_level
                        nw, nh = int(img.width * scale), int(img.height * scale)
                        img = img.resize((nw, nh), Image.LANCZOS)
                        
                        x = (target_w - nw) // 2
                        y = (target_h - nh) + move_y
                        canvas.paste(img, (x, y), img)
                        
                        if add_border:
                            canvas = ImageOps.expand(canvas, border=5, fill='white')
                            canvas = ImageOps.expand(canvas, border=1, fill='#cccccc')

                        passport = canvas.convert("RGB")
                        st.image(passport, caption="প্রিভিউ", width=150)
                        
                        # A4 Grid
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
                        
                        buf = io.BytesIO()
                        sheet.save(buf, format="JPEG", quality=95)
                        st.download_button(f"📥 ডাউনলোড প্রিন্ট ফাইল ({num_copies} কপি)", buf.getvalue(), "passport_print.jpg", "image/jpeg")
                    except Exception as e: st.error(str(e))

# ==========================================
# TOOL 2: SIGNATURE RESIZER (NEW - Seen in Video)
# ==========================================
elif selected_tool == "✍️ ডিজিটাল স্বাক্ষর (300x80)":
    st.header("✍️ ডিজিটাল স্বাক্ষর রিসাইজার")
    st.info("সরকারি চাকরির আবেদনের জন্য অটোমেটিক ৩০০x৮০ পিক্সেল সাইজ তৈরি করুন।")
    
    sig_file = st.file_uploader("স্বাক্ষরের ছবি আপলোড করুন", type=["jpg", "png"])
    
    if sig_file:
        original_sig = Image.open(sig_file)
        st.image(original_sig, caption="আপনার আপলোড করা স্বাক্ষর", width=300)
        
        remove_bg_sig = st.checkbox("ব্যাকগ্রাউন্ড রিমুভ করব? (সাদা কাগজের জন্য)", value=True)
        
        if st.button("✂️ রিসাইজ করুন"):
            with st.spinner("রিসাইজ হচ্ছে..."):
                if remove_bg_sig:
                    processed_sig = remove(original_sig)
                else:
                    processed_sig = original_sig
                
                # Resize to standard 300x80
                final_sig = processed_sig.resize((300, 80), Image.LANCZOS)
                
                # If transparent, make white background (optional, mostly needed for JPEG)
                bg_sig = Image.new("RGB", (300, 80), "white")
                if final_sig.mode == 'RGBA':
                    bg_sig.paste(final_sig, (0, 0), final_sig)
                else:
                    bg_sig = final_sig.convert("RGB")
                
                st.success("স্বাক্ষর রেডি!")
                st.image(bg_sig, caption="৩০০ x ৮০ পিক্সেল")
                
                buf_sig = io.BytesIO()
                bg_sig.save(buf_sig, format="JPEG", quality=100)
                st.download_button("📥 ডাউনলোড সিগনেচার", buf_sig.getvalue(), "signature_300x80.jpg", "image/jpeg")

# ==========================================
# TOOL 3: NID/CARD PRINT SETUP (NEW - Seen in Video)
# ==========================================
elif selected_tool == "🆔 NID/কার্ড প্রিন্ট সেটআপ":
    st.header("🆔 স্মার্ট আইডি কার্ড প্রিন্ট সেটআপ")
    st.write("এনআইডি বা আইডি কার্ডের সামনের ও পেছনের ছবি আপলোড করুন, এক পেজে প্রিন্ট করার জন্য সাজিয়ে দিব।")
    
    col_front, col_back = st.columns(2)
    with col_front:
        front_img = st.file_uploader("সামনের অংশ (Front)", type=["jpg", "png"])
    with col_back:
        back_img = st.file_uploader("পেছনের অংশ (Back)", type=["jpg", "png"])
        
    if front_img and back_img:
        if st.button("🖨️ কার্ড তৈরি করুন"):
            img_f = Image.open(front_img)
            img_b = Image.open(back_img)
            
            # Resize logic to standard ID card ratio (approx 3.375 x 2.125 inches)
            # In pixels at 300 DPI: ~1012 x 638
            card_w, card_h = 1012, 638
            img_f = img_f.resize((card_w, card_h))
            img_b = img_b.resize((card_w, card_h))
            
            # Create A4 Sheet
            a4_w, a4_h = 2480, 3508
            sheet_card = Image.new("RGB", (a4_w, a4_h), "white")
            
            # Paste Logic (Top center)
            start_y = 200
            center_x = (a4_w - card_w) // 2
            
            # Front
            sheet_card.paste(img_f, (center_x, start_y))
            # Back (Below front with gap)
            sheet_card.paste(img_b, (center_x, start_y + card_h + 50))
            
            # Draw Border (Optional visualization of cut lines could be added)
            
            st.image(sheet_card, caption="প্রিন্ট প্রিভিউ (অংশবিশেষ)", width=400)
            
            buf_card = io.BytesIO()
            sheet_card.save(buf_card, format="JPEG", quality=95)
            st.download_button("📥 ডাউনলোড প্রিন্ট ফাইল (A4)", buf_card.getvalue(), "nid_print_file.jpg", "image/jpeg")

# ==========================================
# TOOL 4: IMAGE COMPRESSOR
# ==========================================
elif selected_tool == "📉 ইমেজ সাইজ কমান (KB)":
    st.header("📉 ইমেজ কম্প্রেসার")
    img_comp = st.file_uploader("ছবি দিন", type=["jpg", "png"])
    if img_comp:
        image = Image.open(img_comp)
        target = st.slider("টার্গেট সাইজ (KB)", 20, 500, 100)
        if st.button("কম্প্রেস করুন"):
            out = io.BytesIO()
            q = 95
            img_fmt = image.format if image.format else 'JPEG'
            image.save(out, format=img_fmt, quality=q)
            while out.tell() > target*1024 and q>10:
                out = io.BytesIO()
                q -= 5
                image.save(out, format=img_fmt, quality=q)
            st.success(f"নতুন সাইজ: {out.tell()/1024:.1f} KB")
            st.download_button("ডাউনলোড", out.getvalue(), "compressed."+img_fmt.lower())
