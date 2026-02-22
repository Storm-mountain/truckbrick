import streamlit as st
from PIL import Image, ImageOps
import openai
import io
import base64
from datetime import datetime

# Set page config
st.set_page_config(page_title="TruckBrick 🛻🧱", page_icon="🛻", layout="wide")

# Sidebar
st.sidebar.title("🚀 TruckBrick Settings")
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="platform.openai.com")
style = st.sidebar.selectbox("Style", ["Mould King (Technic Trucks)", "Lego Technic"], index=0)

scale_options = {
    "Small (desk model)": {"label": "Small (desk model)", "pieces": 500, "scale": "1:25–1:30", "desc": "~30–40 cm long, quick build"},
    "Medium (shelf display)": {"label": "Medium (shelf display)", "pieces": 1200, "scale": "1:17–1:20", "desc": "~45–60 cm long, good detail"},
    "Large (detailed beast)": {"label": "Large (detailed beast)", "pieces": 2500, "scale": "1:12–1:14", "desc": "~70+ cm long, complex functions"},
    "Custom": {"label": "Custom", "pieces": None, "scale": "custom", "desc": "Set your own piece target"}
}
selected_scale = st.sidebar.selectbox("Scale", list(scale_options.keys()), index=1)

if scale_options[selected_scale]["pieces"] is None:
    target_pieces = st.sidebar.number_input("Target Piece Count", min_value=300, max_value=5000, value=1200, step=100)
else:
    target_pieces = scale_options[selected_scale]["pieces"]

scale_info = scale_options[selected_scale]
st.sidebar.info(f"**{scale_info['label']}** — ≈ {target_pieces} pieces, {scale_info['scale']} scale, {scale_info['desc']}")

if not openai_api_key:
    st.sidebar.warning("Enter your OpenAI key to build!")
    st.stop()

openai.api_key = openai_api_key

# Main UI
st.title("🛻 TruckBrick: Photo → Mould King / Lego Truck Builder")
st.markdown("**Upload a truck photo → Get custom build + step-by-step instructions.** Clarksville truck fans unite! 🏎️")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Your Truck Photo")
    camera_input = st.camera_input("Take photo")
    uploaded_file = st.file_uploader("Or upload", type=["jpg", "jpeg", "png"])
    
    if camera_input or uploaded_file:
        image = Image.open(camera_input) if camera_input else Image.open(uploaded_file)
        image = ImageOps.exif_transpose(image)
        st.image(image, caption="Your Truck", use_column_width=True)
        
        if st.button("🔨 Generate Build", type="primary"):
            with st.spinner("Analyzing truck + designing build... ~30–50 sec"):
                # Encode image
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # Vision: Describe truck
                vision_resp = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Expert in trucks and Lego/Mould King Technic design."},
                        {"role": "user", "content": [
                            {"type": "text", "text": f"Detail this truck: type (pickup/semi/etc), color, features (cab, bed, wheels, etc), overall proportions for scaling a brick model."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                        ]}
                    ],
                    max_tokens=500
                )
                truck_desc = vision_resp.choices[0].message.content
                
                # Build instructions prompt with scale
                scale_text = f"approximately {scale_info['scale']} scale" if scale_info["scale"] != "custom" else f"around {target_pieces} pieces total"
                build_prompt = f"""
                Master Mould King / Lego Technic truck designer.
                Create full build guide for a {style} model inspired by:
                {truck_desc}
                
                Target: {target_pieces} pieces (±20%), {scale_text}.
                
                Exact output format:
                1. **Model Overview**: Cool name, total pieces approx, scale, approx dimensions (length/width/height in cm), key features.
                2. **Main Parts List** — top 15 types (e.g. '45x Technic Beam 11L - Black', '8x Large Wheel').
                3. **Step-by-Step Instructions** — 18–30 clear steps like official manuals ('Step 5: Attach 4x 15L beams to form chassis rails...').
                4. **Build Tips**: Color matching, optional motorization/PF, common pitfalls.
                
                Realistic with standard parts; fun and buildable.
                """
                
                build_resp = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": build_prompt}],
                    max_tokens=1800
                )
                instructions = build_resp.choices[0].message.content
                
                # Lego-style image
                image_prompt = f"Photorealistic Mould King / Lego Technic model of {truck_desc}, built to {scale_text}, on workbench, detailed, vibrant, exploded view optional."
                img_resp = openai.Image.create(
                    model="dall-e-3",
                    prompt=image_prompt,
                    n=1,
                    size="1024x1024"
                )
                lego_image_url = img_resp['data'][0]['url']
                
                # Save to session
                st.session_state.update({
                    'truck_desc': truck_desc,
                    'instructions': instructions,
                    'lego_image_url': lego_image_url,
                    'image': image,
                    'scale_selected': selected_scale
                })

with col2:
    if 'instructions' in st.session_state:
        st.subheader(f"Your {st.session_state.scale_selected} Scale Build")
        
        st.image(st.session_state.lego_image_url, caption="AI Render of Your Scaled Model")
        
        tab1, tab2 = st.tabs(["📋 Full Instructions", "🧱 Parts & Tips"])
        
        with tab1:
            st.markdown(st.session_state.instructions)
            txt_data = st.session_state.instructions.encode()
            st.download_button(
                "📄 Download Instructions (TXT)",
                data=txt_data,
                file_name=f"truckbrick_{datetime.now().strftime('%Y%m%d')}_{st.session_state.scale_selected}.txt",
                mime="text/plain"
            )
        
        with tab2:
            st.info("**Parts sourcing**: BrickLink.com (Lego authentic) or AliExpress/Temu (Mould King clones – search 'Technic truck parts').")
            st.caption("Tip: Start with chassis/beams first – that's where scale really shows.")

st.markdown("---")
st.caption("TruckBrick MVP v2 • Built for Robert in Clarksville, TN • Want Flutter mobile version, LDraw export, or more scales? Just say!")
