import streamlit as st
from PIL import Image, ImageOps
from openai import OpenAI
import io
import base64

st.set_page_config(page_title="TruckBrick 🛻🧱", layout="wide")

st.sidebar.title("Settings")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if not api_key:
    st.warning("Enter your OpenAI key to start!")
    st.stop()

client = OpenAI(api_key=api_key)

st.title("🛻 TruckBrick: Photo → Lego/Mould King Truck")
st.write("Snap or upload a truck photo → get build instructions + parts list.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Your Truck Photo")
    photo = st.camera_input("Take a photo") or st.file_uploader("Or upload", type=["jpg", "jpeg", "png"])
    
    if photo:
        img = Image.open(photo)
        img = ImageOps.exif_transpose(img)
        st.image(img, caption="Your Truck", use_column_width=True)
        
        if st.button("Generate Build", type="primary"):
            with st.spinner("Analyzing truck + generating build... ~30-60 sec"):
                # Encode image
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # Vision: Describe truck
                vision_resp = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert in trucks and Lego/Mould King Technic design."},
                        {"role": "user", "content": [
                            {"type": "text", "text": "Describe this truck precisely: year/model, body style, colors, key features (cab, bed, wheels, exhaust, lights, etc), overall proportions for scaling a brick model."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                        ]}
                    ],
                    max_tokens=500
                )
                truck_desc = vision_resp.choices[0].message.content
                
                # Build instructions
                build_prompt = f"""
                Master Mould King / Lego Technic truck designer.
                Create full build guide for a model inspired by this truck:
                {truck_desc}
                
                Target: 800-1500 pieces.
                
                Output in markdown:
                ## Model Overview
                - Name: ...
                - Approx total pieces: ...
                - Scale: ...
                - Approx dimensions: ...
                - Key features: ...
                
                ## Parts List (most used first)
                Format: NUMBERx Part Name - Color (e.g. 45x Technic Beam 11L - Black)
                Top 15-20 parts.
                
                ## Step-by-Step Instructions
                15-25 clear numbered steps.
                
                ## Build Tips
                Color matching, optional motorization, pitfalls.
                """
                
                build_resp = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": build_prompt}],
                    max_tokens=1800
                )
                instructions = build_resp.choices[0].message.content
                
                # Display results
                st.markdown(instructions)
                
                # DALL-E image (optional - add if you want visual)
                # image_prompt = f"Photorealistic Lego Technic model of {truck_desc}"
                # img_resp = client.images.generate(prompt=image_prompt, model="dall-e-3", n=1, size="1024x1024")
                # st.image(img_resp.data[0].url, caption="AI Render")

with col2:
    st.subheader("Build Preview")
    st.info("Results appear here after generation.")
