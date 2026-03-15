# Pitch-Visualizer
Transform text pitches into AI-generated visual storyboards using Gemini and Stable Diffusion. https://pitch-visualizer.streamlit.app/

# 🖼️ The Pitch Visualizer

The Pitch Visualizer is an AI-powered storytelling tool that transforms a short narrative into a visual storyboard.

Users input a short story or pitch, and the system automatically:

1. Breaks the story into scenes using a Large Language Model (Gemini).
2. Generates detailed image prompts using prompt engineering.
3. Creates visual scenes using Stable Diffusion XL.
4. Displays them as a cinematic slideshow.

This allows users to quickly convert text pitches into visual narratives.

---

# 🚀 Features

• Converts text stories into visual scenes
• Uses **Gemini LLM** for scene breakdown and prompt generation
• Uses **Stable Diffusion XL** for high-quality image generation
• Maintains **visual consistency** across scenes using a visual anchor
• Supports multiple artistic styles:

* Cinematic
* Digital Art
* Studio Ghibli
* Cyberpunk
* Oil Painting

• Interactive slideshow interface built with **Streamlit**

---

# 🧠 System Architecture

The system works in three main stages:

### 1️⃣ Scene Extraction (LLM)

The Gemini model receives the user's story and converts it into **three narrative scenes**.

Each scene contains:

* The original text segment
* A detailed visual prompt optimized for Stable Diffusion

---

### 2️⃣ Prompt Engineering

The system uses structured prompt instructions to guide the LLM to produce high-quality prompts.

The prompt instructs the model to include:

• Subject details (age, clothing, expression)
• Environment details (lighting, background, time of day)
• Camera style (wide angle, cinematic lighting)
• Artistic style keywords
• Scene action based on the story sentence

The system also creates a **Visual Anchor**, which describes the main character and ensures visual consistency across scenes.

---

### 3️⃣ Image Generation

Each visual prompt is sent to:

Stable Diffusion XL via HuggingFace Inference API.

The system generates images with parameters optimized for quality:

* 1024 × 576 resolution
* 35 inference steps
* Guidance scale: 7.5

Negative prompts remove artifacts such as:

* Watermarks
* Distorted faces
* Extra limbs
* Low-quality outputs

---

# 🖥️ Application Interface

The application is built with **Streamlit** and provides:

• Story input area
• Art style selector
• Automatic storyboard generation
• Slideshow navigation between scenes
• Ability to inspect the generated prompts

---

# ⚙️ Setup Instructions

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/pitch-visualizer.git
cd pitch-visualizer
```

---

## 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3️⃣ Add API Keys

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key
HF_API_KEY=your_huggingface_api_key
```

You can copy the template:

```bash
cp .env.example .env
```

---

## 4️⃣ Run the Application

```bash
streamlit run app.py
```

The app will open in your browser.

---

# 🔑 API Services Used

### Google Gemini

Used for:

* Story segmentation
* Prompt generation
* Scene structure creation

### HuggingFace Inference API

Used for:

* Stable Diffusion XL image generation

---

# 📐 Design Choices

### Scene-Based Storyboarding

Instead of generating a single image, the system divides the narrative into scenes to better represent the progression of a story.

### Visual Anchor

To maintain character consistency across images, the system generates a **visual anchor** describing the main character and injects it into every prompt.

### Dense Prompt Strategy

The prompt engineering strategy forces the LLM to produce prompts using **dense visual keywords instead of sentences**, improving diffusion model results.

### Negative Prompting

Negative prompts remove common diffusion artifacts such as distorted hands or watermarks.

---

# 🛠️ Tech Stack

Python
Streamlit
Google Gemini API
Stable Diffusion XL
HuggingFace Inference API
Pillow

---

# 📌 Example Workflow

User Input:

```
Our small team was drowning in paperwork.
Then an AI system automated most of the workload.
Soon productivity skyrocketed and the office was full of energy.
```

Output:

Scene 1 → Overworked team buried in documents
Scene 2 → AI system processing data automatically
Scene 3 → Happy team celebrating productivity growth

---

# 📷 Future Improvements

• Video storyboard export
• Character persistence across scenes
• Support for longer narratives
• Multi-character scene generation

---

# 👨‍💻 Author

Manish Gaikwad

