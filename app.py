import streamlit as st
from rembg import remove
from PIL import Image, ImageEnhance, ImageOps
import io

# 1. Page Config
st.set_page_config(page_title="Studio Master AI", page_icon="📸", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    div.stButton > button { width: 100%; background-color: #2563eb; color: white; border-radius: 8px; font-weight: bold; padding: 10px; }
    div.stButton > button:hover { background-color: #1d4ed8; }
    </style>
""", unsafe_allow_html=True)

st.title("📸 স্টুডিও মাস্টার AI")
st.write("আপনার ছবিকে প্রফেশনাল ল্যাবের মতো এডিট এবং প্রিন্ট লেআউট তৈরি করুন।")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🎛 এডিটিং প্যানেল")
    
    # Upload
    uploaded_file = st.file_uploader("ছবি আপলোড করুন", type=["jpg", "png", "jpeg"])
    
    st.divider()
    
    # 1. Background Color
    bg_color = st.color_picker("ব্যাকগ্রাউন্ড কালার:", "#3b82f6")
    
    # 2. Adjustments
    st.subheader("💡 কালার ও লাইট")
    brightness = st.slider("উজ্জ্বলতা (Brightness)", 0.5, 2.0, 1.2, 0.1) # Default 1.2 (slightly bright)
    contrast = st.slider("কন্ট্রাস্ট (Contrast)", 0.5, 2.0, 1.1, 0.1)
    
    # 3. Size & Position
    st.subheader("📐 পজিশন ও সাইজ")
    zoom_level = st.slider("জুম (Zoom)", 0.5, 2.0, 1.0, 0.05)
    move_y = st.slider("উপরে-নিচে সরান (Y)", -100, 100, 0, 5)
    
    # 4. Border
    add_border = st.checkbox("সাদা বর্ডার দিন?", value=True)

# --- MAIN LOGIC ---

if uploaded_file:
    # Load Original
    original_image = Image.open(uploaded_file)
    
    if st.button("🚀 ছবি প্রসেস করুন"):
        with st.spinner("AI স্টুডিও কাজ করছে..."):
            try:
                # STEP 1: Remove Background
                no_bg_image = remove(original_image)
                
                # STEP 2: Enhance Image (Light & Contrast)
                # Brightness
                enhancer = ImageEnhance.Brightness(no_bg_image)
                enhanced_img = enhancer.enhance(brightness)
                # Contrast
                enhancer = ImageEnhance.Contrast(enhanced_img)
                enhanced_img = enhancer.enhance(contrast)
                
                # STEP 3: Create Canvas (Passport Size High Res)
                target_size = (600, 750) # 4:5 Ratio
                final_canvas = Image.new("RGBA", target_size, bg_color)
                
                # STEP 4: Smart Resize & Zoom Logic
                # Fit width to canvas
                base_width = target_size[0]
                w_percent = (base_width / float(enhanced_img.size[0]))
                h_size = int((float(enhanced_img.size[1]) * float(w_percent)))
                
                # Apply Zoom
                new_w = int(base_width * zoom_level)
                new_h = int(h_size * zoom_level)
                
                person_resized = enhanced_img.resize((new_w, new_h), Image.LANCZOS)
                
                # Calculate Center Position
                x_pos = (target_size[0] - new_w) // 2
                # Align Bottom usually, but add Y offset
                y_pos = (target_size[1] - new_h) + move_y
                
                # Fix: If zoomed out, center vertically
                if new_h < target_size[1]:
                     y_pos = ((target_size[1] - new_h) // 2) + move_y
                
                # Paste Person
                final_canvas.paste(person_resized, (x_pos, y_pos), person_resized)
                
                # Add Border (Optional)
                if add_border:
                    final_canvas = ImageOps.expand(final_canvas, border=10, fill='white')
                    # Resize back to target after border adds pixels
                    final_canvas = final_canvas.resize(target_size, Image.LANCZOS)

                # Convert to RGB for display/download
                passport_photo = final_canvas.convert("RGB")
                
                # --- DISPLAY SINGLE PHOTO ---
                col1, col2 = st.columns(2)
                with col1:
                    st.image(passport_photo, caption="পাসপোর্ট সাইজ", use_column_width=True)
                
                # --- CREATE PRINT SHEET (4R Size - 4 Copies) ---
                with col2:
                    st.write("🖨 **প্রিন্ট লেআউট (4R)**")
                    # 4R size in pixels at 300 DPI is approx 1200x1800
                    sheet_w, sheet_h = 1200, 1800
                    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
                    
                    # Resize passport photo to fit 4 on a sheet
                    # A gap of 50px
                    photo_w_print = 500
                    photo_h_print = 625
                    photo_for_sheet = passport_photo.resize((photo_w_print, photo_h_print))
                    
                    # Grid positions (2x2)
                    positions = [
                        (70, 100), (630, 100),  # Row 1
                        (70, 800), (630, 800)   # Row 2
                    ]
                    
                    for pos in positions:
                        sheet.paste(photo_for_sheet, pos)
                    
                    st.image(sheet, caption="৪ কপি (প্রিন্ট ফাইল)", use_column_width=True)

                # --- DOWNLOAD BUTTONS ---
                st.divider()
                st.subheader("📥 ডাউনলোড অপশন")
                
                c1, c2 = st.columns(2)
                
                # Download Single
                buf1 = io.BytesIO()
                passport_photo.save(buf1, format="JPEG", quality=100)
                c1.download_button("পাসপোর্ট ছবি (১টি)", buf1.getvalue(), "passport_single.jpg", "image/jpeg")
                
                # Download Sheet
                buf2 = io.BytesIO()
                sheet.save(buf2, format="JPEG", quality=100)
                c2.download_button("প্রিন্ট ফাইল (৪টি - 4R)", buf2.getvalue(), "passport_sheet_4R.jpg", "image/jpeg")
                
            except Exception as e:
                st.error(f"Something went wrong: {e}")

else:
    st.info("👈 কাজ শুরু করতে বাম পাশের সাইডবার থেকে ছবি আপলোড করুন।")
