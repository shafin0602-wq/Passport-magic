import streamlit as st
from rembg import remove
from PIL import Image, ImageEnhance, ImageOps
import io

# 1. Page Config
st.set_page_config(page_title="Studio Master Pro (A4)", page_icon="📸", layout="wide")

# Custom CSS for better UI
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; padding: 12px; background: linear-gradient(45deg, #2563eb, #1d4ed8); border: none; }
    .stButton>button:hover { background: linear-gradient(45deg, #1d4ed8, #1e40af); box-shadow: 0 4px 12px rgba(37,99,235,0.2); }
    /* Improve slider visibility */
    .stSlider > div > div > div > div { background-color: #2563eb; }
    </style>
""", unsafe_allow_html=True)

st.title("📸 স্টুডিও মাস্টার প্রো (স্মার্ট ফিক্স)")
st.write("উন্নত ব্যাকগ্রাউন্ড রিমুভ এবং স্মার্ট সাইজিং সহ A4 প্রিন্ট মেকার।")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🎛 এডিটিং প্যানেল")
    st.info("💡 টিপস: ব্যাকগ্রাউন্ডে সমস্যা হলে 'উজ্জ্বলতা' ও 'কন্ট্রাস্ট' বাড়িয়ে দেখুন।")
    
    # Upload
    uploaded_file = st.file_uploader("ছবি আপলোড করুন (ভালো আলোর ছবি দিন)", type=["jpg", "png", "jpeg"])
    
    st.divider()
    
    # 1. Print Settings
    st.subheader("🖨️ প্রিন্ট সেটিংস")
    num_copies = st.number_input("কয় কপি ছবি লাগবে?", min_value=1, max_value=25, value=4, step=1)
    
    st.divider()

    # 2. Background Color
    bg_color = st.color_picker("ব্যাকগ্রাউন্ড কালার:", "#3b82f6")
    
    # 3. Adjustments (Crucial for fixing bad BG removal)
    st.subheader("💡 কালার ও লাইট (ব্যাকগ্রাউন্ড ফিক্স)")
    brightness = st.slider("উজ্জ্বলতা (Brightness)", 0.8, 1.5, 1.1, 0.05, help="ব্যাকগ্রাউন্ডের ময়লা লুকাতে এটি বাড়ান।")
    contrast = st.slider("কন্ট্রাস্ট (Contrast)", 0.8, 1.5, 1.1, 0.05, help="ছবি শার্প করতে এটি বাড়ান।")
    
    # 4. Size & Position (Crucial for framing)
    st.subheader("📐 পজিশন ও সাইজ (ম্যানুয়াল)")
    zoom_level = st.slider("জুম (Zoom) - ছোট/বড় করুন", 0.8, 1.5, 1.0, 0.02)
    move_y = st.slider("উপরে-নিচে সরান (Move Y)", -150, 150, 0, 5, help="মাথা কেটে গেলে নিচে নামান।")
    
    # 5. Border
    add_border = st.checkbox("সাদা বর্ডার ও কাটার দাগ?", value=True)

# --- MAIN LOGIC ---

if uploaded_file:
    # Layout Columns
    col1, col2 = st.columns([2, 3])
    
    # Load Original
    original_image = Image.open(uploaded_file)
    
    # Process Button
    if st.sidebar.button("🚀 ছবি তৈরি করুন (Start Processing)"):
        with st.spinner("AI স্টুডিও কাজ করছে... একটু ধৈর্য ধরুন..."):
            try:
                # --- STEP 1: ADVANCED IMAGE PROCESSING ---
                # Remove Background
                no_bg_image = remove(original_image)
                
                # Enhance (Apply sliders)
                enhancer = ImageEnhance.Brightness(no_bg_image)
                enhanced_img = enhancer.enhance(brightness)
                enhancer = ImageEnhance.Contrast(enhanced_img)
                enhanced_img = enhancer.enhance(contrast)
                
                # --- STEP 2: SMART SIZING LOGIC (IMPROVED) ---
                # Canvas Target: Passport Size (40mm x 50mm @ 300 DPI)
                target_w, target_h = 472, 590
                final_canvas = Image.new("RGBA", (target_w, target_h), bg_color)
                
                # Smart Fill Logic:
                # Instead of fitting INSIDE, we try to FILL the width to make it look professional.
                # Calculate scale needed to match target width
                scale_factor = target_w / enhanced_img.width
                
                # Apply user zoom on top of smart scale
                final_scale = scale_factor * zoom_level
                
                new_w = int(enhanced_img.width * final_scale)
                new_h = int(enhanced_img.height * final_scale)
                
                # High-quality resize
                person_resized = enhanced_img.resize((new_w, new_h), Image.LANCZOS)
                
                # Positioning Logic (Anchor Bottom Center)
                # Center horizontally
                x_pos = (target_w - new_w) // 2
                
                # Align near bottom (Standard passport look)
                # Default position: Bottom of person aligns with bottom of frame
                default_y_pos = target_h - new_h
                
                # Apply user manual movement (move_y)
                # If move_y is positive, move down. Negative, move up.
                final_y_pos = default_y_pos + move_y
                
                # Paste person onto canvas
                final_canvas.paste(person_resized, (x_pos, final_y_pos), person_resized)
                
                # Crop any overflow (if zoomed in too much)
                final_canvas = final_canvas.crop((0, 0, target_w, target_h))
                
                # --- STEP 3: BORDER ---
                if add_border:
                    # Inner white border
                    final_canvas = ImageOps.expand(final_canvas, border=6, fill='white')
                    # Outer gray cutting line
                    final_canvas = ImageOps.expand(final_canvas, border=1, fill='#cccccc')

                passport_photo = final_canvas.convert("RGB")
                
                # --- DISPLAY SINGLE PHOTO (Left Column) ---
                with col1:
                    st.subheader("👁‍🗨 একক প্রিভিউ")
                    st.image(passport_photo, caption="পাসপোর্ট সাইজ (চেক করুন)", width=300)
                    st.info("👆 ফ্রেম ঠিক না থাকলে বাম পাশের 'জুম' এবং 'সরান' স্লাইডার ব্যবহার করুন।")
                    
                    # Single Download
                    buf1 = io.BytesIO()
                    passport_photo.save(buf1, format="JPEG", quality=95)
                    st.download_button("⬇️ ডাউনলোড (১টি ছবি)", buf1.getvalue(), "single_passport.jpg", "image/jpeg")

                # --- CREATE A4 SHEET (Right Column) ---
                with col2:
                    st.subheader(f"📄 A4 প্রিন্ট প্রিভিউ ({num_copies} কপি)")
                    
                    # A4 Settings (300 DPI)
                    sheet_w, sheet_h = 2480, 3508
                    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
                    
                    photo_w = passport_photo.width
                    photo_h = passport_photo.height
                    
                    # Grid Layout
                    cols = 4
                    rows = 6
                    gap = 50 # Gap between photos for cutting
                    
                    # Centering grid on A4
                    grid_total_w = (cols * photo_w) + ((cols - 1) * gap)
                    margin_left = (sheet_w - grid_total_w) // 2
                    margin_top = 150 # Top margin for printer grip
                    
                    count = 0
                    for r in range(rows):
                        for c in range(cols):
                            if count >= num_copies: break
                            
                            x = margin_left + (c * (photo_w + gap))
                            y = margin_top + (r * (photo_h + gap))
                            sheet.paste(passport_photo, (x, y))
                            count += 1
                        if count >= num_copies: break
                    
                    # Show A4 Preview
                    st.image(sheet, caption="A4 পেপার প্রিন্ট লেআউট", use_column_width=True)
                    
                    # A4 Download
                    buf2 = io.BytesIO()
                    sheet.save(buf2, format="JPEG", quality=95)
                    st.download_button(f"🖨️ ডাউনলোড প্রিন্ট ফাইল ({num_copies} কপি)", buf2.getvalue(), "print_file_A4.jpg", "image/jpeg", type="primary")
                
            except Exception as e:
                st.error(f"একটি সমস্যা হয়েছে: {e}")
                st.warning("টিপস: অন্য একটি ছবি দিয়ে চেষ্টা করুন অথবা পেজটি রিফ্রেশ দিন।")
else:
    st.info("👈 কাজ শুরু করতে বাম পাশ থেকে একটি স্পষ্ট ছবি আপলোড করুন এবং 'ছবি তৈরি করুন' বাটনে ক্লিক করুন।")
