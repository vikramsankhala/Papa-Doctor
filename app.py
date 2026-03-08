"""
CareAssist — Virtual Caretaking Assistant
For: Gopal Singh Sankhala
Primary Caregiver: Vikram Singh Sankhala
"""

import streamlit as st
from datetime import datetime, date, timedelta
import pandas as pd
import json
import os
import base64

# Page config
st.set_page_config(
    page_title="CareAssist — Gopal Singh Sankhala",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional medical theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'DM Sans', sans-serif;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    .main-header {
        background: linear-gradient(90deg, #0f766e 0%, #14b8a6 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 14px rgba(15, 118, 110, 0.3);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 1.8rem;
    }
    
    .main-header p {
        margin: 0.3rem 0 0 0;
        opacity: 0.95;
    }
    
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
        border-left: 4px solid #14b8a6;
    }
    
    .card-warning {
        border-left-color: #f59e0b;
    }
    
    .card-critical {
        border-left-color: #ef4444;
    }
    
    .checklist-item {
        padding: 0.6rem 0;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .section-title {
        color: #0f766e;
        font-weight: 700;
        margin: 1.5rem 0 0.8rem 0;
        font-size: 1.2rem;
    }
    
    .protocol-box {
        background: #ecfdf5;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        border: 1px solid #a7f3d0;
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0f766e;
    }
</style>
""", unsafe_allow_html=True)

# Data file path
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
VITALS_FILE = os.path.join(DATA_DIR, "vitals.json")
MEDICATION_LOG = os.path.join(DATA_DIR, "medication_log.json")
CHECKLIST_LOG = os.path.join(DATA_DIR, "checklist_log.json")


def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def analyze_image_with_llm(image_bytes: bytes, prompt: str, provider: str, api_key: str, mime: str = "image/jpeg") -> str:
    """Analyze image using selected LLM Vision API."""
    b64 = base64.b64encode(image_bytes).decode("utf-8")

    if provider == "OpenAI (GPT-4o)":
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                        ],
                    }
                ],
                max_tokens=1024,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"Error: {str(e)}"

    elif provider == "Anthropic (Claude 3)":
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "source": {"type": "base64", "media_type": mime, "data": b64}},
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            )
            return response.content[0].text if response.content else ""
        except Exception as e:
            return f"Error: {str(e)}"

    elif provider == "Google (Gemini)":
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            img_part = {"mime_type": mime, "data": image_bytes}
            response = model.generate_content([prompt, img_part])
            return response.text or ""
        except Exception as e:
            return f"Error: {str(e)}"

    return "Unsupported provider."


# Sidebar navigation
st.sidebar.markdown("## 🏥 CareAssist")
st.sidebar.markdown("**Patient:** Gopal Singh Sankhala  \n**Caregiver:** Vikram Singh Sankhala")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    [
        "📊 Dashboard",
        "💊 Medication & Treatment",
        "🩺 Vitals & Monitoring",
        "📷 Image Analysis",
        "🧹 Hygiene & Cleanliness",
        "🚿 Bathroom Care",
        "🔧 Equipment & Supplies",
        "🦠 Disinfection & Pest Control",
        "📱 Technology Hygiene",
        "🏥 General Surgery Care",
        "✅ Daily Checklist",
    ],
    label_visibility="collapsed"
)

# Header
st.markdown("""
<div class="main-header">
    <h1>CareAssist — Virtual Caretaking Assistant</h1>
    <p>Comprehensive care support for Gopal Singh Sankhala • Managed by Vikram Singh Sankhala with medical attendant</p>
</div>
""", unsafe_allow_html=True)

# ==================== DASHBOARD ====================
if page == "📊 Dashboard":
    st.subheader("📊 Daily Overview")
    
    vitals_data = load_json(VITALS_FILE, [])
    med_log = load_json(MEDICATION_LOG, [])
    checklist_data = load_json(CHECKLIST_LOG, [])
    
    today = date.today().isoformat()
    today_vitals = [v for v in vitals_data if v.get("date") == today]
    today_meds = [m for m in med_log if m.get("date") == today]
    today_checklist = [c for c in checklist_data if c.get("date") == today]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Vitals Recorded Today", len(today_vitals), "entries")
    with col2:
        st.metric("Medications Logged", len(today_meds), "entries")
    with col3:
        completed = sum(1 for c in today_checklist if c.get("completed", False))
        st.metric("Checklist Progress", f"{completed}/{len(today_checklist) if today_checklist else 0}", "tasks")
    with col4:
        st.metric("Date", datetime.now().strftime("%d %b %Y"), "")
    
    if today_vitals:
        latest = today_vitals[-1]
        st.markdown("### Latest Vitals")
        v1, v2, v3, v4 = st.columns(4)
        v1.metric("Pulse", f"{latest.get('pulse', '—')}/min", "")
        v2.metric("BP", f"{latest.get('bp_sys', '—')}/{latest.get('bp_dia', '—')} mmHg", "")
        v3.metric("SpO₂", f"{latest.get('spo2', '—')}%", "")
        v4.metric("Time", latest.get("time", "—"), "")
    
    st.markdown("---")
    st.info("Use the sidebar to navigate to specific modules: Medication, Vitals, Hygiene, Bathroom Care, Equipment, Disinfection, Technology, Surgery Care, and Daily Checklist.")

# ==================== MEDICATION & TREATMENT ====================
elif page == "💊 Medication & Treatment":
    st.subheader("💊 Medication & Treatment Management")
    
    st.markdown("""
    <div class="card">
        <div class="section-title">Current Prescription (from records)</div>
        <ul>
            <li><strong>Nebuliser:</strong> Asthalin respules — 5, Budecort respules — 5</li>
            <li><strong>Syp. Ascoril:</strong> 1.5 × 10ml — Start to End (Tick: 10)</li>
            <li><strong>10ml Tonul</strong></li>
            <li><strong>Mucinac:</strong> 600mg</li>
            <li><strong>EMODEL DS lotion:</strong> Apply locally</li>
            <li><strong>PROTEINEX Powder:</strong> 2 scoops/day</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📝 Log Medication Administration", expanded=True):
        med_name = st.text_input("Medication name")
        dose = st.text_input("Dose / quantity")
        time_given = st.time_input("Time given", value=datetime.now().time())
        notes = st.text_area("Notes (e.g., any reaction, skipped)")
        if st.button("Log Medication"):
            log = load_json(MEDICATION_LOG, [])
            log.append({
                "date": date.today().isoformat(),
                "time": time_given.strftime("%H:%M"),
                "medication": med_name,
                "dose": dose,
                "notes": notes,
            })
            save_json(MEDICATION_LOG, log)
            st.success("Medication logged.")
    
    st.markdown("### Medication Best Practices")
    st.markdown("""
    - **Storage:** Keep medications in a cool, dry place away from sunlight. Check expiry dates weekly.
    - **Hand hygiene:** Wash hands before handling medications. Use gloves if handling topical medications.
    - **Timing:** Administer at the same time each day when possible. Set reminders.
    - **Nebuliser:** Clean mask and chamber after each use. Replace filters as per manufacturer.
    - **Document:** Always log administration time and any adverse effects.
    """)

# ==================== VITALS & MONITORING ====================
elif page == "🩺 Vitals & Monitoring":
    st.subheader("🩺 Vitals & Monitoring")
    
    with st.form("vitals_form"):
        col1, col2 = st.columns(2)
        with col1:
            pulse = st.number_input("Pulse (per min)", min_value=40, max_value=200, value=90)
            bp_sys = st.number_input("BP Systolic (mmHg)", min_value=60, max_value=250, value=140)
            spo2 = st.number_input("SpO₂ (%)", min_value=70, max_value=100, value=95)
        with col2:
            bp_dia = st.number_input("BP Diastolic (mmHg)", min_value=40, max_value=150, value=90)
            resp_rate = st.number_input("Respiratory rate (optional)", min_value=0, max_value=60, value=0)
            notes = st.text_area("Clinical notes (e.g., crepits, AE)")
        
        if st.form_submit_button("Record Vitals"):
            vitals = load_json(VITALS_FILE, [])
            vitals.append({
                "date": date.today().isoformat(),
                "time": datetime.now().strftime("%H:%M"),
                "pulse": pulse,
                "bp_sys": bp_sys,
                "bp_dia": bp_dia,
                "spo2": spo2,
                "resp_rate": resp_rate if resp_rate else None,
                "notes": notes,
            })
            save_json(VITALS_FILE, vitals)
            st.success("Vitals recorded.")
    
    vitals_data = load_json(VITALS_FILE, [])
    if vitals_data:
        df = pd.DataFrame(vitals_data)
        st.dataframe(df.tail(20), use_container_width=True, hide_index=True)
    
    st.markdown("### Monitoring Guidelines")
    st.markdown("""
    - **Pulse:** Normal 60–100/min. Report if &lt;50 or &gt;120.
    - **BP:** Target &lt;140/90. Report sustained elevation.
    - **SpO₂:** Maintain ≥94% on room air. Report if &lt;92%.
    - **Respiratory:** Note any crepits, wheeze, or distress.
    """)

# ==================== IMAGE ANALYSIS ====================
elif page == "📷 Image Analysis":
    st.subheader("📷 Image Upload & Analysis")
    st.markdown("Upload a photo (e.g., wound, skin, medication, equipment) for AI-assisted analysis. **Not a substitute for medical advice.**")

    with st.expander("⚙️ API Configuration", expanded=False):
        provider = st.selectbox(
            "LLM Provider",
            ["Anthropic (Claude 3)", "OpenAI (GPT-4o)", "Google (Gemini)"],
            help="Choose your vision-capable LLM. API key is read from env or entered below.",
        )
        api_key = st.text_input(
            "API Key",
            type="password",
            placeholder="sk-... or leave blank to use env var",
            help="OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY. Prefer env vars on Render.",
        )
        env_map = {
            "OpenAI (GPT-4o)": "OPENAI_API_KEY",
            "Anthropic (Claude 3)": "ANTHROPIC_API_KEY",
            "Google (Gemini)": "GOOGLE_API_KEY",
        }
        if not api_key:
            api_key = os.environ.get(env_map[provider], "")

    prompt_options = {
        "Care-focused (wound, skin, general)": """You are a care assistant. Analyze this image in the context of home care for an elderly patient. Describe what you see clearly and objectively. If it appears to be a wound, skin condition, or medical concern: note any visible signs (redness, swelling, discharge, etc.) and suggest when to seek medical attention. Be concise and practical. Do not diagnose; recommend consulting a doctor for any concerns.""",
        "Medication / equipment": """Analyze this image. If it shows medications, equipment, or supplies: identify items, check for labels/expiry if visible, and note any storage or safety concerns. Be concise.""",
        "Room / hygiene": """Analyze this image for cleanliness and hygiene in a care setting. Note any areas of concern (clutter, spills, surfaces) and suggest improvements.""",
        "Custom prompt": None,
    }
    prompt_choice = st.selectbox("Analysis type", list(prompt_options.keys()))
    if prompt_choice == "Custom prompt":
        custom_prompt = st.text_area("Enter your analysis prompt")
        prompt = custom_prompt or "Describe this image in detail."
    else:
        prompt = prompt_options[prompt_choice]

    uploaded = st.file_uploader(
        "Upload image",
        type=["jpg", "jpeg", "png", "webp"],
        help="Camera photos, screenshots, or scans. Max 20MB.",
    )

    if uploaded and prompt:
        image_bytes = uploaded.read()
        mime = uploaded.type or "image/jpeg"
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(image_bytes, caption="Uploaded image", use_container_width=True)
        with col2:
            if st.button("Analyze with LLM", type="primary"):
                if not api_key:
                    st.error("Please set an API key (in env or above) for the selected provider.")
                else:
                    with st.spinner("Analyzing..."):
                        result = analyze_image_with_llm(
                            image_bytes, prompt, provider, api_key, mime
                        )
                    st.markdown("### Analysis")
                    st.markdown(result)

    st.markdown("---")
    st.caption("Use cases: wound progress photos, skin condition checks, medication identification, room hygiene review. Always consult a healthcare provider for medical decisions.")

# ==================== HYGIENE & CLEANLINESS ====================
elif page == "🧹 Hygiene & Cleanliness":
    st.subheader("🧹 Hygiene & Cleanliness")
    
    st.markdown("""
    <div class="section-title">Daily Hygiene Protocol</div>
    <div class="protocol-box">
        <strong>Hand hygiene (caregiver & attendant):</strong> Wash with soap and water for 20 seconds before and after care. Use alcohol-based sanitizer (60%+) between washes.
    </div>
    <div class="protocol-box">
        <strong>Patient hygiene:</strong> Daily bath or sponge bath. Oral care twice daily. Nail trimming weekly. Hair wash as needed.
    </div>
    <div class="protocol-box">
        <strong>Linen:</strong> Change bed linens at least twice weekly; daily if soiled. Wash at 60°C+ with detergent.
    </div>
    <div class="protocol-box">
        <strong>Room:</strong> Daily dusting, mopping with disinfectant. Ventilate room 2–3 times daily for 10–15 minutes.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### High-Touch Surface Cleaning (2× daily)")
    st.markdown("""
    - Bed rails, remote controls, call bell
    - Door handles, light switches
    - Table surfaces, phone
    - Nebuliser mask and tubing
    """)

# ==================== BATHROOM CARE ====================
elif page == "🚿 Bathroom Care":
    st.subheader("🚿 Bathroom Care — Highest Standard")
    
    st.markdown("""
    <div class="card">
        <div class="section-title">Bathroom Disinfection Protocol</div>
        <ol>
            <li><strong>Daily:</strong> Wipe all surfaces (toilet seat, flush handle, taps, sink, grab rails) with hospital-grade disinfectant (e.g., sodium hypochlorite 0.1% or quaternary ammonium).</li>
            <li><strong>Floor:</strong> Mop with disinfectant solution. Use separate mop for bathroom.</li>
            <li><strong>Toilet bowl:</strong> Clean with toilet cleaner and brush. Disinfect handle.</li>
            <li><strong>After each use (if applicable):</strong> Wipe seat with disinfectant wipe.</li>
        </ol>
    </div>
    <div class="card">
        <div class="section-title">Diaper & Incontinence Care</div>
        <ul>
            <li>Change promptly when soiled. Use Size 7 as per prescription.</li>
            <li>Dispose in sealed bags; use dedicated dustbin with lid.</li>
            <li>Clean perineal area with gentle wipe; apply barrier cream (e.g., zinc oxide) to prevent rash.</li>
            <li>Wash hands thoroughly after each change.</li>
        </ul>
    </div>
    <div class="card">
        <div class="section-title">Recommended Disinfectants</div>
        <ul>
            <li><strong>Bleach (sodium hypochlorite):</strong> 0.1% for general surfaces (1 part 5% bleach : 50 parts water)</li>
            <li><strong>Dettol / Lysol:</strong> As per label for bathroom</li>
            <li><strong>Quaternary ammonium:</strong> Hospital-grade for high-touch areas</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ==================== EQUIPMENT & SUPPLIES ====================
elif page == "🔧 Equipment & Supplies":
    st.subheader("🔧 Equipment & Supplies")
    
    st.markdown("""
    <div class="card">
        <div class="section-title">Current Supplies (from records)</div>
        <ul>
            <li>1 packet Mask</li>
            <li>Hand gloves — 1 packet</li>
            <li>Diapers — Size 7</li>
            <li>Carry bags and Dustbin for diaper disposal</li>
            <li>Camphor and Extra Virgin cold pressed coconut oil</li>
        </ul>
    </div>
    <div class="card">
        <div class="section-title">Nebuliser Care</div>
        <ul>
            <li>Clean mask and chamber with warm soapy water after each use; air dry.</li>
            <li>Replace mask every 2–4 weeks or if damaged.</li>
            <li>Replace filter as per manufacturer (typically every 6 months).</li>
        </ul>
    </div>
    <div class="card">
        <div class="section-title">Equipment Checklist</div>
        <ul>
            <li>BP monitor: Calibrate annually; check batteries.</li>
            <li>Pulse oximeter: Clean sensor with alcohol wipe; replace if inaccurate.</li>
            <li>Thermometer: Disinfect after each use.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ==================== DISINFECTION & PEST CONTROL ====================
elif page == "🦠 Disinfection & Pest Control":
    st.subheader("🦠 Disinfection & Pest Control")
    
    st.markdown("""
    <div class="card">
        <div class="section-title">Disinfection Schedule</div>
        <table style="width:100%; border-collapse: collapse;">
        <tr><th>Area</th><th>Frequency</th><th>Agent</th></tr>
        <tr><td>Patient room</td><td>Daily</td><td>Disinfectant mop, surface wipe</td></tr>
        <tr><td>Bathroom</td><td>Daily + after use</td><td>Bleach 0.1% / quaternary ammonium</td></tr>
        <tr><td>Kitchen</td><td>Daily</td><td>Disinfectant</td></tr>
        <tr><td>Common areas</td><td>2×/week</td><td>Disinfectant</td></tr>
        </table>
    </div>
    <div class="card">
        <div class="section-title">Pest Control</div>
        <ul>
            <li><strong>Prevention:</strong> No food left uncovered. Seal garbage. Fix leaks. Seal cracks.</li>
            <li><strong>Monthly:</strong> Professional pest control if in pest-prone area.</li>
            <li><strong>Safe products:</strong> Use pest control that is safe for elderly/medical conditions. Ventilate after use.</li>
            <li><strong>Mosquitoes:</strong> Nets, repellents, eliminate stagnant water.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ==================== TECHNOLOGY HYGIENE ====================
elif page == "📱 Technology Hygiene":
    st.subheader("📱 Technology Hygiene")
    
    st.markdown("""
    <div class="card">
        <div class="section-title">Device Sanitization</div>
        <ul>
            <li><strong>Phones, tablets, remotes:</strong> Wipe daily with 70% isopropyl alcohol or disinfectant wipes. Avoid excess moisture.</li>
            <li><strong>BP monitor, pulse oximeter:</strong> Wipe cuffs and sensors after each use.</li>
            <li><strong>Nebuliser:</strong> Clean mask, chamber, tubing as per equipment protocol.</li>
            <li><strong>Call bell / emergency device:</strong> Wipe daily; ensure within reach.</li>
        </ul>
    </div>
    <div class="card">
        <div class="section-title">Data & Records</div>
        <ul>
            <li>Back up vitals and medication logs regularly.</li>
            <li>Share records with doctor during visits.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ==================== GENERAL SURGERY CARE ====================
elif page == "🏥 General Surgery Care":
    st.subheader("🏥 General Surgery & Wound Care")
    
    st.markdown("""
    <div class="card">
        <div class="section-title">Wound Care Basics</div>
        <ul>
            <li><strong>Hand hygiene:</strong> Wash hands; use gloves before touching wound.</li>
            <li><strong>Dressing change:</strong> As per doctor's schedule. Use sterile technique.</li>
            <li><strong>Signs of infection:</strong> Redness, swelling, pus, fever, increased pain — report immediately.</li>
        </ul>
    </div>
    <div class="card">
        <div class="section-title">Post-Surgery Monitoring</div>
        <ul>
            <li>Monitor vitals more frequently as advised.</li>
            <li>Watch for bleeding, dehiscence, or unusual discharge.</li>
            <li>Ensure adequate nutrition and hydration for healing.</li>
        </ul>
    </div>
    <div class="card">
        <div class="section-title">When to Call Doctor</div>
        <ul>
            <li>Fever &gt;38°C</li>
            <li>Worsening breathing or SpO₂ &lt;92%</li>
            <li>Severe pain, confusion, fall</li>
            <li>Signs of wound infection</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ==================== DAILY CHECKLIST ====================
elif page == "✅ Daily Checklist":
    st.subheader("✅ Daily Care Checklist")
    
    default_tasks = [
        ("Morning vitals (P, BP, SpO₂)", False),
        ("Medications as per schedule", False),
        ("Nebuliser (Asthalin + Budecort)", False),
        ("Oral care (AM)", False),
        ("Bath / sponge bath", False),
        ("Linen check / change if needed", False),
        ("Room ventilation", False),
        ("High-touch surface disinfection", False),
        ("Bathroom disinfection", False),
        ("Diaper changes as needed", False),
        ("Oral care (PM)", False),
        ("Evening vitals", False),
        ("Medication log review", False),
    ]
    
    today = date.today().isoformat()
    checklist_data = load_json(CHECKLIST_LOG, [])
    today_data = next((c for c in checklist_data if c.get("date") == today), {"date": today, "tasks": []})
    
    if not today_data.get("tasks"):
        today_data["tasks"] = [{"name": n, "completed": d} for n, d in default_tasks]
    
    tasks = today_data["tasks"]
    updated = False
    
    for i, t in enumerate(tasks):
        new_val = st.checkbox(t["name"], value=t.get("completed", False), key=f"task_{i}")
        if new_val != t.get("completed"):
            tasks[i]["completed"] = new_val
            updated = True
    
    if updated or st.button("Save Checklist"):
        other = [c for c in checklist_data if c.get("date") != today]
        other.append(today_data)
        save_json(CHECKLIST_LOG, other)
        st.success("Checklist saved.")
    
    completed = sum(1 for t in tasks if t.get("completed"))
    st.progress(completed / len(tasks) if tasks else 0)
    st.caption(f"{completed} of {len(tasks)} tasks completed today")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("CareAssist v1.0 • For Gopal Singh Sankhala")
