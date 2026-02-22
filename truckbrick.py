import streamlit as st
from PIL import Image, ImageOps
import openai
import io
import base64
from datetime import datetime

st.set_page_config(page_title="TruckBrick 🛻🧱", layout="wide")

st.sidebar.title("Settings")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if not api_key:
    st.warning("Enter your OpenAI key to start!")
    st.stop()
openai.api_key = api_key

st.title("🛻 TruckBrick: Photo → Lego/Mould King Truck")
st.write("Snap or upload a truck photo → get build instructions + parts list.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Your Truck Photo")
    photo = st.camera_input("Take a photo") or st.file_uploader("Or upload", type= )
    if photo:
        img = Image.open(photo)
        img = ImageOps.exif_transpose(img)
        st.image(img, caption="Your Truck")

        if st.button("Generate Build", type="primary"):
            with st.spinner("Building..."):
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()

                desc_resp = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Expert truck & Lego/Mould King designer."},
                        {"role": "user", "content": [
                            {"type": "text", "text": "Describe this truck: type, color, features, proportions for brick model."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                        ]}
                    ]
                )
                truck
