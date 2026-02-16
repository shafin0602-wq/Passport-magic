import streamlit as st
from rembg import remove
from PIL import Image
import io

st.set_page_config(page_title="Magic Passport Maker", layout="centered")

st.title("📸 ফ্রি আনলিমিটেড পাসপোর্ট মেকার")
st.write("যেকোনো ছবি আপলোড করুন, অটোমেটিক ব্যাকগ্রাউন্ড রিমুভ হয়ে পাসপোর্ট সাইজ হয়ে যাবে।")

# 1. Upload
uploaded_file = st.file_uploader("ছবি দিন (JPG/PNG)", type=["jpg", "jpeg", "png"])

# 2. Settings
col1, col2 = st.columns(2)
with col1:
    size_type = st.radio("সাইজ:", ["পাসপোর্ট (40x50 mm)", "স্ট্যাম্প (20x25 mm)"])
with col2:
    bg_color = st.color_picker("ব্যাকগ্রাউন্ড কালার:", "#3b82f6") # Blue Default

if uploaded_file is not None:
    st.image(uploaded_file, caption="অরিজিনাল ছবি", width=200)
    
    if st.button("🚀 প্রসেস শুরু করুন (Start)"):
        with st.spinner("AI কাজ করছে... ৫-১০ সেকেন্ড সময় দিন..."):
            try:
                # Load Image
                input_img = Image.open(uploaded_file)

                # A. Remove Background (Server Side - Powerful)
                output = remove(input_img)

                # B. Prepare Canvas
                if size_type == "পাসপোর্ট (40x50 mm)":
                    target = (600, 750)
                else:
                    target = (300, 375)
                
                # C. Create Background
                final_img = Image.new("RGBA", target, bg_color)
                
                # D. Smart Fit Logic
                img_ratio = output.width / output.height
                target_ratio = target[0] / target[1]
                
                if img_ratio > target_ratio:
                    # Width is bigger
                    new_h = int(target[0] / img_ratio)
                    output = output.resize((target[0], new_h), Image.LANCZOS)
                else:
                    # Height is bigger (Normal portrait)
                    new_w = int(target[0] * 0.90) # 90% width fill
                    new_h = int(new_w / img_ratio)
                    output = output.resize((new_w, new_h), Image.LANCZOS)
                
                # Align Bottom Center
                pos_x = (target[0] - output.width) // 2
                pos_y = target[1] - output.height
                
                # Paste
                final_img.paste(output, (pos_x, pos_y), output)
                
                # Convert to JPG for download
                rgb_im = final_img.convert('RGB')
                
                # Display Result
                st.success("কাজ শেষ! নিচে দেখুন 👇")
                st.image(rgb_im, caption="ফাইনাল পাসপোর্ট ছবি", width=300)
                
                # Download Button
                buf = io.BytesIO()
                rgb_im.save(buf, format="JPEG", quality=100)
                byte_im = buf.getvalue()
                
                st.download_button(
                    label="📥 ছবি ডাউনলোড করুন",
                    data=byte_im,
                    file_name="passport_photo.jpg",
                    mime="image/jpeg"
                )

            except Exception as e:
                st.error("সমস্যা হয়েছে। অন্য ছবি দিয়ে চেষ্টা করুন।")
