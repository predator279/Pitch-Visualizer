import streamlit as st
import requests
import io
import json
import time
from PIL import Image
from google import genai

# --- API KEYS ---
GEMINI_API_KEY = "AIzaSyByo79Aj8Ofg0JQNHBExHpuykGgJ9xSz0s"
HF_API_KEY = "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"

# --- CONFIGURATION ---
st.set_page_config(page_title="The Pitch Visualizer", page_icon="🖼️", layout="wide")

client = genai.Client(api_key=GEMINI_API_KEY)


def get_available_model():
    try:
        preferred = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-2.0-flash-exp", "gemini-1.5-pro"]
        available_models = [m.name for m in client.models.list()]
        clean_models = [m.replace("models/", "") for m in available_models]
        for model in preferred:
            if model in clean_models:
                return model
        return clean_models[0]
    except Exception as e:
        st.error(f"Failed to list models: {e}")
        return "gemini-1.5-flash"


HF_API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
hf_headers = {"Authorization": f"Bearer {HF_API_KEY}"}


def query_image_gen(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": "text, watermark, blurry, distorted face, bad hands, extra limbs, deformed, ugly, low quality, worst quality, cropped",
            "num_inference_steps": 35,
            "guidance_scale": 7.5,
            "width": 1024,
            "height": 576
        }
    }
    try:
        response = requests.post(HF_API_URL, headers=hf_headers, json=payload, timeout=90)
        if response.status_code == 503:
            st.info("Hugging Face model is warming up... waiting 20s.")
            time.sleep(20)
            return query_image_gen(prompt)
        elif response.status_code != 200:
            st.error(f"Image API Error: {response.text}")
            return None
        return response.content
    except Exception as e:
        st.error(f"Image request failed: {e}")
        return None


def get_consistent_storyboard(text_input, style_choice, model_name):
    style_keywords = {
        "Cinematic": "cinematic lighting, anamorphic lens, film grain, dramatic shadows, golden hour, shot on ARRI camera, movie still",
        "Digital Art": "digital art, concept art, artstation trending, sharp lines, vibrant colors, detailed illustration, 4k render",
        "Studio Ghibli": "studio ghibli style, soft watercolor, hand-drawn, warm pastel palette, dreamy atmosphere, miyazaki inspired",
        "Cyberpunk": "cyberpunk aesthetic, neon lights, rain-slicked streets, holographic displays, dark futuristic city, blade runner inspired",
        "Oil Painting": "oil painting, thick brushstrokes, renaissance lighting, rich textures, classical composition, museum quality art"
    }
    style_detail = style_keywords.get(style_choice, style_choice)

    prompt = f"""
    You are an expert AI image prompt engineer specializing in Stable Diffusion XL.
    Convert the story into 3 scenes with HIGHLY DETAILED image generation prompts.

    CRITICAL RULE — PRESERVE THE SCENE'S MEANING:
    The visual_prompt MUST visually depict exactly what the sentence is describing.
    If the sentence says "the team was drowning in paperwork", show that literal chaos.
    If the sentence says "an AI bot handled the workload", show a futuristic robot or glowing AI interface doing the work.
    If the sentence says "the team tripled their output", show celebration, energy, growth charts, success.
    Do NOT replace the core scene event with generic office imagery. The narrative action must be visible in the image.

    RULES FOR WRITING GREAT IMAGE PROMPTS:
    1. First, identify the KEY ACTION or EVENT in the sentence — make that the focal point of the image.
    2. Be extremely specific about: lighting, camera angle, environment, colors, mood, and composition.
    3. Use comma-separated descriptive keywords — NOT full sentences.
    4. Include subject details: age, clothing, expression, body language, position in frame.
    5. Include environment details: time of day, weather, background elements, depth of field.
    6. Always embed the Visual Anchor for character consistency.
    7. Each prompt should be 50-70 words of dense, specific visual keywords.

    STYLE TO USE: {style_detail}

    VISUAL ANCHOR INSTRUCTIONS:
    - Define the main character once: approximate age, hair color/style, clothing color and type.
    - Repeat these EXACT physical descriptors in every scene's prompt.

    Story: "{text_input}"

    Return ONLY valid JSON (no markdown, no backticks):
    {{
      "visual_anchor": "short character description for consistency",
      "scenes": [
        {{
          "segment": "original sentence from story",
          "visual_prompt": "dense SD keywords that faithfully depict what the sentence describes"
        }},
        {{
          "segment": "original sentence from story",
          "visual_prompt": "..."
        }},
        {{
          "segment": "original sentence from story",
          "visual_prompt": "..."
        }}
      ]
    }}

    EXAMPLE — sentence: "The team was overwhelmed by manual data entry"
    GOOD prompt: "exhausted young woman, mid-20s, brown ponytail, blue blazer, buried under towering stacks of paper files, frantic expression, hands typing on outdated keyboard, cluttered chaotic office, harsh fluorescent lighting, late night, overflowing inbox trays, desaturated blue tones, wide angle shot, shallow depth of field, cinematic lighting, film grain"
    BAD prompt: "a woman sits at an office desk working on a computer"

    EXAMPLE — sentence: "An AI bot automated 90% of the workload"
    GOOD prompt: "same woman, mid-20s, brown ponytail, blue blazer, watching in awe as a glowing holographic robot AI interface processes data streams, digital files flying and sorting automatically, futuristic blue glow, clean modern office, wide eyes, relieved expression, lens flare, dynamic angle, cinematic lighting, film grain"
    BAD prompt: "a robot in an office"
    """

    response = client.models.generate_content(model=model_name, contents=prompt)

    clean_text = response.text.strip()
    if "```json" in clean_text:
        clean_text = clean_text.split("```json")[1].split("```")[0].strip()
    elif "```" in clean_text:
        clean_text = clean_text.split("```")[1].split("```")[0].strip()

    return json.loads(clean_text)


# --- SESSION STATE INIT ---
if 'gemini_model' not in st.session_state:
    with st.spinner("Checking available Gemini models..."):
        st.session_state.gemini_model = get_available_model()

if 'scenes' not in st.session_state:
    st.session_state.scenes = []
if 'images' not in st.session_state:
    st.session_state.images = []
if 'visual_anchor' not in st.session_state:
    st.session_state.visual_anchor = ""
if 'current_slide' not in st.session_state:
    st.session_state.current_slide = 0


# --- UI ---
st.title("🖼️ The Pitch Visualizer")
st.markdown("Transform your narrative into a visual storyboard.")

st.sidebar.success(f"Using Model: {st.session_state.gemini_model}")
style = st.sidebar.selectbox("Art Style", ["Cinematic", "Digital Art", "Studio Ghibli", "Cyberpunk", "Oil Painting"])
user_text = st.text_area("Paste your story (3-5 sentences):", height=150)

if st.button("Generate Storyboard", type="primary"):
    if not user_text:
        st.warning("Please enter text.")
    else:
        try:
            # Reset state
            st.session_state.scenes = []
            st.session_state.images = []
            st.session_state.current_slide = 0

            with st.spinner("Gemini is engineering your scene prompts..."):
                data = get_consistent_storyboard(user_text, style, st.session_state.gemini_model)
                st.session_state.scenes = data.get("scenes", [])
                st.session_state.visual_anchor = data.get("visual_anchor", "")

            # Generate all images and store as bytes
            for i, scene in enumerate(st.session_state.scenes):
                with st.spinner(f"Generating image {i + 1} of {len(st.session_state.scenes)}..."):
                    final_prompt = f"{scene['visual_prompt']}, masterpiece, best quality, ultra detailed, 8k"
                    img_bytes = query_image_gen(final_prompt)
                    st.session_state.images.append(img_bytes)

            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")


# --- SLIDESHOW VIEW ---
if st.session_state.scenes and st.session_state.images:

    st.divider()
    st.info(f"🎨 **Visual Anchor:** {st.session_state.visual_anchor}")
    st.divider()

    total = len(st.session_state.scenes)
    idx = st.session_state.current_slide

    # Slide counter
    st.markdown(
        f"<h4 style='text-align:center; color:gray;'>Scene {idx + 1} of {total}</h4>",
        unsafe_allow_html=True
    )

    # --- Image ---
    img_bytes = st.session_state.images[idx]
    if img_bytes:
        image = Image.open(io.BytesIO(img_bytes))
        # Center the image with padding
        _, img_col, _ = st.columns([0.5, 9, 0.5])
        with img_col:
            st.image(image, use_container_width=True)
    else:
        st.warning("Image could not be generated for this scene.")

    # --- Caption ---
    st.markdown(
        f"<p style='text-align:center; font-size:18px; padding: 12px 40px;'>"
        f"💬 {st.session_state.scenes[idx]['segment']}"
        f"</p>",
        unsafe_allow_html=True
    )

    # --- Image Prompt Dropdown ---
    _, drop_col, _ = st.columns([1, 4, 1])
    with drop_col:
        with st.expander("🔍 View Image Prompt"):
            st.caption(st.session_state.scenes[idx]['visual_prompt'])

    st.write("")  # spacing

    # --- Navigation Arrows ---
    left_col, mid_col, right_col = st.columns([1, 3, 1])

    with left_col:
        if st.button("⬅️ Prev", disabled=(idx == 0), use_container_width=True):
            st.session_state.current_slide -= 1
            st.rerun()

    with mid_col:
        # Dot indicators
        dots = ""
        for d in range(total):
            if d == idx:
                dots += "🔵 "
            else:
                dots += "⚪ "
        st.markdown(
            f"<p style='text-align:center; font-size:20px; padding-top:6px;'>{dots}</p>",
            unsafe_allow_html=True
        )

    with right_col:
        if st.button("Next ➡️", disabled=(idx == total - 1), use_container_width=True):
            st.session_state.current_slide += 1
            st.rerun()