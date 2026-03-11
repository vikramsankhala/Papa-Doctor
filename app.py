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

from dotenv import load_dotenv
load_dotenv()

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
HOME_VISITS_FILE = os.path.join(DATA_DIR, "home_visits.json")
TASKS_SCHEDULE_FILE = os.path.join(DATA_DIR, "tasks_schedule.json")
NUTRITION_FILE = os.path.join(DATA_DIR, "nutrition_weekly.json")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.json")
TODO_FILE = os.path.join(DATA_DIR, "todo.json")


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


DEFAULT_RECOMMENDED_TASKS = [
    "Morning vitals (P, BP, SpO₂)",
    "Medications as per schedule",
    "Nebuliser (Asthalin + Budecort)",
    "Oral care (AM)",
    "Breakfast",
    "Bath / sponge bath",
    "Linen check / change if needed",
    "Room ventilation",
    "High-touch surface disinfection",
    "Bathroom disinfection",
    "Lunch",
    "Diaper changes as needed",
    "Oral care (PM)",
    "Dinner",
    "Evening vitals",
    "Medication log review",
]

DEFAULT_NUTRITION = {
    "Monday": {"breakfast": "Oats, milk, banana", "lunch": "Dal, rice, vegetables, roti", "dinner": "Soup, chapati, sabzi", "snacks": "Fruit, PROTEINEX"},
    "Tuesday": {"breakfast": "Idli, sambar, chutney", "lunch": "Rice, fish/egg curry, vegetables", "dinner": "Khichdi, yogurt", "snacks": "Biscuits, milk"},
    "Wednesday": {"breakfast": "Poha, tea", "lunch": "Roti, paneer, dal", "dinner": "Rice, dal, vegetable curry", "snacks": "Fruit, PROTEINEX"},
    "Thursday": {"breakfast": "Upma, coconut chutney", "lunch": "Rice, sambar, papad", "dinner": "Chapati, bhindi, dal", "snacks": "Nuts, banana"},
    "Friday": {"breakfast": "Dosa, sambar", "lunch": "Biryani/pulao, raita", "dinner": "Soup, roti, mixed vegetables", "snacks": "Fruit, PROTEINEX"},
    "Saturday": {"breakfast": "Paratha, yogurt", "lunch": "Dal, rice, aloo sabzi", "dinner": "Rice, fish curry, salad", "snacks": "Milk, biscuits"},
    "Sunday": {"breakfast": "Pancakes, honey, milk", "lunch": "Roti, chole, rice", "dinner": "Khichdi, papad, pickle", "snacks": "Fruit, PROTEINEX"},
}


def get_meals_for_date(d: date) -> dict:
    """Get meal schedule for a date from weekly nutrition chart."""
    nutrition = load_json(NUTRITION_FILE, DEFAULT_NUTRITION)
    day_name = d.strftime("%A")
    return nutrition.get(day_name, {})


def get_tasks_for_date(d: date) -> list:
    """Get task names for a date. Merges recommended + date-specific scheduled."""
    schedule = load_json(TASKS_SCHEDULE_FILE, {})
    date_str = d.isoformat()
    scheduled = schedule.get(date_str, [])
    base = DEFAULT_RECOMMENDED_TASKS.copy()
    for t in scheduled:
        if isinstance(t, dict):
            name = t.get("name", t.get("task", ""))
            if name and name not in base:
                base.append(name)
        else:
            if t not in base:
                base.append(t)
    return base


def get_checklist_for_date(d: date) -> dict:
    """Get checklist (tasks with completion) for a date."""
    checklist_data = load_json(CHECKLIST_LOG, [])
    date_str = d.isoformat()
    day_data = next((c for c in checklist_data if c.get("date") == date_str), {"date": date_str, "tasks": []})
    task_names = get_tasks_for_date(d)
    completed_map = {t["name"]: t.get("completed", False) for t in day_data.get("tasks", [])}
    tasks = [{"name": n, "completed": completed_map.get(n, False)} for n in task_names]
    if not day_data.get("tasks"):
        day_data["tasks"] = tasks
    return day_data


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


def get_assistant_context() -> str:
    """Build context about the CareAssist app and patient for the AI assistant."""
    vitals = load_json(VITALS_FILE, [])
    med_log = load_json(MEDICATION_LOG, [])
    visits = load_json(HOME_VISITS_FILE, [])
    latest_vitals = vitals[-1] if vitals else {}
    return f"""You are the AI Assistant for CareAssist, a virtual caretaking application for home care of Gopal Singh Sankhala, managed by Vikram Singh Sankhala with a medical attendant.

**Patient:** Mr. Gopal Singh Sankhala, 90 years old male
**Location:** 402, Florencia Apartments, Lane G, South Main Road, Koregaon Park, Pune, Maharashtra - 411001
**Doctor at Door:** https://doctoratdoor.co.in/ (home visit service)

**Current Prescriptions:**
- Nebuliser: Asthalin respules + Budecort respules
- Syp. Ascoril 1.5 × 10ml
- 10ml Tonul, Mucinac 600mg
- EMODEL DS lotion (apply locally)
- PROTEINEX Powder: 2 scoops/day

**Supplies:** Masks, hand gloves, Diapers Size 7, carry bags, dustbin for diaper disposal, camphor, extra virgin cold pressed coconut oil

**Care Context:**
- Stage 3/4 bed sores on both buttocks; wound cleaned with Normal Saline and Tincture of Iodine
- Respiratory: reduced air entry, bilateral crepits
- Latest vitals (if recorded): Pulse {latest_vitals.get('pulse', '—')}/min, BP {latest_vitals.get('bp_sys', '—')}/{latest_vitals.get('bp_dia', '—')} mmHg, SpO₂ {latest_vitals.get('spo2', '—')}%

**App Modules:** Dashboard, Home Visits, Medication & Treatment, Vitals & Monitoring, Image Analysis, Hygiene & Cleanliness, Bathroom Care, Equipment & Supplies, Disinfection & Pest Control, Technology Hygiene, General Surgery Care, Daily Checklist

**Your role:** Answer questions about caretaking, medications, hygiene, wound care, protocols, equipment, bathroom care, disinfection, pest control, or how to use this app. Be concise, practical, and supportive. Do not diagnose; recommend consulting a doctor for medical decisions. If asked about app features, explain how to use them."""


def chat_with_assistant(messages: list, api_key: str) -> str:
    """Send chat messages to Anthropic Claude and return response."""
    if not api_key:
        return "Please set ANTHROPIC_API_KEY in .env or in the Image Analysis API settings."
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=get_assistant_context(),
            messages=[{"role": m["role"], "content": m["content"]} for m in messages],
        )
        return response.content[0].text if response.content else ""
    except Exception as e:
        return f"Error: {str(e)}"


# Sidebar navigation
st.sidebar.markdown("## 🏥 CareAssist")
st.sidebar.markdown("**Patient:** Gopal Singh Sankhala  \n**Caregiver:** Vikram Singh Sankhala")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    [
        "📊 Dashboard",
        "🤖 AI Assistant",
        "🏠 Home Visits",
        "💊 Medication & Treatment",
        "🩺 Vitals & Monitoring",
        "📷 Image Analysis",
        "🧹 Hygiene & Cleanliness",
        "🚿 Bathroom Care",
        "🔧 Equipment & Supplies",
        "🛒 Care Equipment Guide",
        "🦠 Disinfection & Pest Control",
        "📱 Technology Hygiene",
        "🏥 General Surgery Care",
        "🩹 Skin, Wound & Physiotherapy",
        "📅 Daily Tasks & Schedule",
        "📋 Daily ToDo",
        "🍽️ Nutrition Chart",
        "🥗 Nutrition & Supplements",
        "🍳 English Breakfast Guide",
        "📦 Inventory",
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

    inv = load_json(INVENTORY_FILE, {"medicines": [], "supplements": [], "food": []})
    low_stock = []
    for cat, items in inv.items():
        for item in items:
            cur, mon = float(item.get("current_stock", 0)), float(item.get("monthly_requirement", 1))
            if mon > 0 and (cur / mon) < 0.4:
                low_stock.append(item.get("name", "?"))
    if low_stock:
        st.markdown("### ⚠️ Re-order alerts")
        st.warning("Low stock (<40%): " + ", ".join(low_stock))

    todo_today = load_json(TODO_FILE, {}).get(today, [])
    todo_done = sum(1 for t in todo_today if t.get("status") == "completed")
    if todo_today:
        st.markdown("### 📋 Today's ToDo")
        st.caption(f"{todo_done} of {len(todo_today)} completed")

    st.markdown("### Today's meals")
    meals = get_meals_for_date(date.today())
    if meals:
        st.markdown(f"**Breakfast:** {meals.get('breakfast', '—')} | **Lunch:** {meals.get('lunch', '—')} | **Dinner:** {meals.get('dinner', '—')}")
    
    st.markdown("---")
    st.info("Use the sidebar to navigate to specific modules: Daily Tasks & Schedule, Nutrition Chart, Inventory, and more.")

# ==================== AI ASSISTANT ====================
elif page == "🤖 AI Assistant":
    st.subheader("🤖 AI Assistant")
    st.markdown("Ask anything about caretaking, medications, protocols, wound care, or how to use this app.")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.warning("Set ANTHROPIC_API_KEY in .env to use the AI Assistant.")

    if prompt := st.chat_input("Ask a question about care, medications, or this app..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chat_with_assistant(st.session_state.chat_messages, api_key)
            st.markdown(response)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})

    if st.session_state.chat_messages:
        st.markdown("---")
        if st.button("Clear chat"):
            st.session_state.chat_messages = []
            st.rerun()

# ==================== HOME VISITS ====================
elif page == "🏠 Home Visits":
    st.subheader("🏠 Home Visits")
    st.markdown("## [Doctor at Door](https://doctoratdoor.co.in/) — Doctor Home Visit Log Book")

    # Default visits if none stored
    default_visits = [
        {
            "date": "2026-03-08",
            "date_display": "8th March, 2026",
            "arrived_on": "8/3/2026",
            "ended_at": "1 PM",
            "patient_name": "Mr. Gopalsingh Sankhala",
            "location": "402, Florencia Apartments, Lane G, South Main Road. Before Archana Meadows, Koregaon Park, Pune, Maharashtra - 411001",
            "examination": {
                "age_sex": "90 years old male c̄ (with)...",
                "temp": "N (Normal)",
                "pulse": "88/min",
                "rr": "16/min",
                "bp": "140/80 mm Hg",
                "spo2": "93%",
            },
            "wound_notes": "Stage 3/4 bed sores on both the buttocks. Wound cleaned with Normal Saline and Tincture of Iodine.",
        }
    ]

    visits = load_json(HOME_VISITS_FILE, default_visits)

    for i, v in enumerate(reversed(visits)):
        with st.expander(f"**Visit — {v.get('date_display', v.get('date', ''))}** (Arrived: {v.get('arrived_on', '')}, Ended: {v.get('ended_at', '')})", expanded=(i == 0)):
            st.markdown(f"**Date:** {v.get('arrived_on', '')} *(arrived on)*  \n**Ended at:** {v.get('ended_at', '')}")
            st.markdown(f"**{v.get('date_display', v.get('date', ''))}**")
            st.markdown(f"**Patient Name:** {v.get('patient_name', '')}")
            st.markdown(f"**Location:** {v.get('location', '')}")
            st.markdown("**Examination & Provisional Diagram:**")
            ex = v.get("examination", {})
            st.markdown(f"- {ex.get('age_sex', '')}")
            st.markdown(f"- Temp: **{ex.get('temp', '')}**")
            st.markdown(f"- Pulse: **{ex.get('pulse', '')}**")
            st.markdown(f"- RR: **{ex.get('rr', '')}**")
            st.markdown(f"- B.P.: **{ex.get('bp', '')}**")
            st.markdown(f"- SpO₂: **{ex.get('spo2', '')}**")
            st.markdown("**Wound Notes:**")
            st.markdown(f"- {v.get('wound_notes', '')}")

    with st.expander("➕ Add New Home Visit", expanded=False):
        with st.form("home_visit_form"):
            col1, col2 = st.columns(2)
            with col1:
                visit_date = st.date_input("Visit Date", value=date.today())
                arrived = st.text_input("Arrived on (e.g. 8/3/2026)", value=f"{date.today().day}/{date.today().month}/{date.today().year}")
                ended = st.text_input("Ended at (e.g. 1 PM)", "1 PM")
            with col2:
                patient = st.text_input("Patient Name", "Mr. Gopalsingh Sankhala")
                location = st.text_area("Location", "402, Florencia Apartments, Lane G, South Main Road. Before Archana Meadows, Koregaon Park, Pune, Maharashtra - 411001")
            st.markdown("**Examination**")
            v1, v2, v3 = st.columns(3)
            with v1:
                temp = st.text_input("Temp", "N (Normal)")
                pulse = st.text_input("Pulse", "88/min")
            with v2:
                rr = st.text_input("RR", "16/min")
                bp = st.text_input("B.P.", "140/80 mm Hg")
            with v3:
                spo2 = st.text_input("SpO₂", "93%")
                age_sex = st.text_input("Age/Sex", "90 years old male c̄ (with)...")
            wound_notes = st.text_area("Wound Notes", "Stage 3/4 bed sores on both the buttocks. Wound cleaned with Normal Saline and Tincture of Iodine.")
            if st.form_submit_button("Save Visit"):
                visits = load_json(HOME_VISITS_FILE, default_visits)
                visits.append({
                    "date": visit_date.isoformat(),
                    "date_display": f"{visit_date.day} {visit_date.strftime('%B')}, {visit_date.year}",
                    "arrived_on": arrived,
                    "ended_at": ended,
                    "patient_name": patient,
                    "location": location,
                    "examination": {"age_sex": age_sex, "temp": temp, "pulse": pulse, "rr": rr, "bp": bp, "spo2": spo2},
                    "wound_notes": wound_notes,
                })
                save_json(HOME_VISITS_FILE, visits)
                st.success("Visit saved.")
                st.rerun()

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

# ==================== CARE EQUIPMENT GUIDE ====================
elif page == "🛒 Care Equipment Guide":
    st.subheader("🛒 Care Equipment Guide")
    st.markdown("Recommended equipment for home care, with detailed use instructions and purchase links.")

    st.markdown("---")
    st.markdown("## 1. Posey Transfer Belt — Safe Patient Transfers & Walking Support")

    st.markdown("""
    [**TIDI Posey Transfer Belt (6537Q)** — Extra-Wide Soft Nylon](https://www.amazon.in/Posey-Extra-Wide-Therapists-Caregivers-6537Q/dp/B00LWVQ3WA)

    A medical-grade transfer and gait belt designed for nurses, therapists, and home care caregivers. Essential for safe patient transfers and fall prevention.
    """)

    with st.expander("**What it is & when to use**", expanded=True):
        st.markdown("""
        The Posey Transfer Belt is a **waist belt with multiple handles** that caregivers grip to safely assist patients during:
        - **Transfers:** Bed ↔ wheelchair, wheelchair ↔ toilet, chair ↔ standing
        - **Walking (gait training):** Supporting balance and stability
        - **Standing:** Helping patient rise from seated position

        **Ideal for:** Elderly patients, fall-risk individuals, post-surgery recovery, mobility-limited patients, home care settings.
        """)

    with st.expander("**Key features**"):
        feat_df = pd.DataFrame({
            "Feature": [
                "Quick-release buckle",
                "6 grab handles",
                "Extra-wide 4\" nylon webbing",
                "Rear support band",
                "Waist size range",
                "Machine washable",
            ],
            "Benefit": [
                "Facilitates full transfers; easy to put on/remove",
                "Multiple grasping points from any side or angle",
                "Strong, supportive; reduces caregiver back strain",
                "Additional stability and fall prevention",
                "28\" to 52\" (71–132 cm) — adjustable",
                "Hygienic; easy to clean",
            ],
        })
        st.dataframe(feat_df, use_container_width=True, hide_index=True)

    with st.expander("**How to use — step-by-step**"):
        st.markdown("""
        1. **Position the patient** seated on bed, chair, or wheelchair.
        2. **Wrap the belt** around the patient's waist, over clothing. Ensure it sits at waist level, not on ribs or hips.
        3. **Secure the buckle** — snap closed. Belt should be snug but allow 2 fingers between belt and body.
        4. **For standing/transfer:** Stand facing the patient. Grasp 2 handles (one on each side) or use rear handles. Use your legs, not your back, to lift.
        5. **For walking:** Walk beside or behind, holding handles. Match the patient's pace.
        6. **Release:** Use quick-release buckle when transfer is complete.
        """)

    with st.expander("**Care & maintenance**"):
        st.markdown("""
        - **Clean:** Machine wash in cold water; air dry. Do not bleach.
        - **Inspect:** Check stitching and buckle before each use.
        - **Storage:** Keep dry; avoid direct sunlight.
        """)

    st.markdown("[🛒 View on Amazon.in](https://www.amazon.in/Posey-Extra-Wide-Therapists-Caregivers-6537Q/dp/B00LWVQ3WA)")

    st.markdown("---")
    st.markdown("## 2. Hero Eco Med Reclining Commode Wheelchair MHL-1006")

    st.markdown("""
    [**Hero Eco Med Reclining Commode Wheelchair MHL-1006**](https://www.amazon.in/dp/B0BCQMP2G9)

    A foldable wheelchair with 180° reclining, built-in commode, and headrest. Designed for patients who need mobility support and toileting assistance at home.
    """)

    with st.expander("**What it is & when to use**", expanded=True):
        st.markdown("""
        A **multi-function wheelchair** that combines:
        - **Wheelchair** — for mobility indoors and short distances
        - **Recliner** — 180° recline to supine (bed-like) position
        - **Commode** — U-cut seat with removable, cleanable pan for toileting

        **Ideal for:** Bed-bound or limited-mobility patients, those who need toileting without bed transfer, post-surgery, elderly care at home.
        """)

    with st.expander("**Key specifications**"):
        spec_df = pd.DataFrame({
            "Specification": [
                "Reclining",
                "Weight capacity",
                "Commode",
                "Wheels",
                "Foldable",
                "Dimensions",
                "Weight",
            ],
            "Details": [
                "180° recline — supine position, optimized center of gravity",
                "100 kg",
                "U-cut seat, microbe-resistant pan with lid, removable & cleanable",
                "24\" rear spoke wheels; 8\" solid PP front wheels",
                "Yes — portable, doubles as normal wheelchair",
                "114D × 65.5W × 118H cm",
                "24.9 kg",
            ],
        })
        st.dataframe(spec_df, use_container_width=True, hide_index=True)

    with st.expander("**Key features**"):
        st.markdown("""
        - **Removable headrest** with neck support
        - **Calf support** and detachable footrests
        - **Antibacterial upholstery** — strong, flexible, easy to clean
        - **Chrome-plated** frame — durable, ergonomic design
        """)

    with st.expander("**How to use — step-by-step**"):
        st.markdown("""
        **As wheelchair:**
        1. Unfold and lock in place. Ensure brakes are released for movement.
        2. Assist patient into seat. Adjust footrests.
        3. Use rear handles to push. Apply brakes when stationary.

        **As commode:**
        1. Position over toilet or place pan beneath U-cut seat.
        2. Ensure pan is securely in place with lid removed.
        3. After use, remove pan, empty, clean with disinfectant. Replace lid.

        **As recliner:**
        1. Use recline lever/mechanism to tilt back.
        2. Support patient's head with headrest. Adjust calf support.
        3. Return to upright slowly when done.
        """)

    with st.expander("**Care & maintenance**"):
        st.markdown("""
        - **Commode pan:** Empty promptly. Clean with disinfectant (e.g. bleach 0.1%). Rinse and dry.
        - **Upholstery:** Wipe with damp cloth and mild detergent. Avoid harsh chemicals.
        - **Wheels:** Check for debris. Lubricate axles if needed.
        - **Frame:** Wipe down regularly. Check all locks and mechanisms.
        """)

    st.markdown("[🛒 View on Amazon.in](https://www.amazon.in/dp/B0BCQMP2G9)")

    st.markdown("---")
    st.caption("*Product details and pricing may change. Verify on Amazon before purchase.*")

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

# ==================== SKIN, WOUND & PHYSIOTHERAPY ====================
elif page == "🩹 Skin, Wound & Physiotherapy":
    st.subheader("🩹 Skin Care, Disinfectants, Wounds, Necrosis, Surgery & Physiotherapy")
    st.markdown("Comprehensive guidance for skin health, wound management, and rehabilitation. *Follow doctor's orders for all wound and surgical care.*")

    st.markdown("---")
    st.markdown("## 1. Skin Care")

    with st.expander("**Daily skin care for bed-bound / elderly**", expanded=True):
        st.markdown("""
        - **Cleansing:** Gentle wash with mild soap; pat dry. Avoid harsh scrubbing.
        - **Moisturising:** Apply moisturiser (e.g. coconut oil, prescribed lotions) after bath to prevent dryness and cracking.
        - **Pressure areas:** Inspect sacrum, heels, hips, elbows daily for redness or breakdown.
        - **Repositioning:** Change position every 2 hours to reduce pressure.
        - **Barrier creams:** Use zinc oxide or prescribed barrier cream in diaper area to prevent rash.
        - **EMODEL DS lotion:** Apply locally as per prescription.
        """)

    with st.expander("**Skin health tips**"):
        st.markdown("""
        - **Hydration:** Adequate fluids; dry skin is common in elderly.
        - **Nutrition:** Protein, Vitamin C, zinc support skin healing.
        - **Avoid friction:** Use soft bedding; avoid dragging when repositioning.
        - **Sun:** Limited exposure; use sunscreen if outdoors.
        """)

    st.markdown("---")
    st.markdown("## 2. Disinfectants for Wounds & Skin")

    disinf_df = pd.DataFrame({
        "Agent": ["Normal saline", "Povidone-iodine (Betadine)", "Chlorhexidine", "Hydrogen peroxide", "Sodium hypochlorite (Dakin's)"],
        "Use": ["Routine wound irrigation", "Antiseptic for wound cleaning", "Skin antisepsis before procedure", "Limited — can damage tissue", "Infected wounds (diluted)"],
        "Notes": ["Safest for irrigation; no tissue damage", "Tincture of Iodine used in wound care", "0.05% for wound; avoid eyes", "Use sparingly; delays healing", "0.025–0.5%; doctor-directed"],
    })
    st.dataframe(disinf_df, use_container_width=True, hide_index=True)

    st.markdown("""
    **For wound cleaning (as per Doctor at Door notes):** Normal Saline and Tincture of Iodine.
    - **Normal saline:** Flush wound gently to remove debris.
    - **Tincture of Iodine:** Apply as directed; effective antiseptic.
    """)

    st.markdown("---")
    st.markdown("## 3. Wound Care")

    with st.expander("**Wound types & stages (pressure ulcers / bed sores)**"):
        stage_df = pd.DataFrame({
            "Stage": ["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Unstageable"],
            "Description": ["Intact skin, non-blanchable redness", "Partial thickness; blister or shallow open", "Full thickness; visible fat", "Full thickness; bone/tendon exposed", "Slough or eschar obscures depth"],
        })
        st.dataframe(stage_df, use_container_width=True, hide_index=True)
        st.caption("Current care context: Stage 3/4 bed sores on both buttocks.")

    with st.expander("**General wound care steps**"):
        st.markdown("""
        1. **Hand hygiene** — wash hands; use gloves.
        2. **Remove old dressing** — discard in sealed bag.
        3. **Clean wound** — normal saline; gentle irrigation. Pat surrounding skin dry.
        4. **Apply antiseptic** — as per doctor (e.g. Tincture of Iodine).
        5. **Apply dressing** — sterile gauze, foam, or as prescribed.
        6. **Secure** — tape or bandage. Do not wrap too tightly.
        7. **Wash hands** after removing gloves.
        """)

    with st.expander("**Signs of infection — call doctor**"):
        st.markdown("""
        - Increased redness, warmth, swelling
        - Pus or foul-smelling discharge
        - Fever, chills
        - Increased pain
        - Wound not healing or getting larger
        """)

    st.markdown("---")
    st.markdown("## 4. Necrosis")

    st.markdown("""
    **Necrosis** = death of body tissue due to lack of blood supply, infection, or injury.

    **Types relevant to wound care:**
    - **Dry necrosis (eschar):** Black, dry, hard tissue. Do not remove yourself — requires medical debridement.
    - **Wet necrosis:** Moist, discoloured tissue; infection risk. Needs doctor evaluation.
    - **Slough:** Yellow/white dead tissue on wound surface. May be removed by doctor or trained nurse.

    **Action:** Report any black, grey, or spreading dead tissue to the doctor immediately. Do not attempt to debride at home.
    """)

    st.markdown("---")
    st.markdown("## 5. Surgery & Post-Surgical Skin Care")

    with st.expander("**Pre-surgery skin prep**"):
        st.markdown("""
        - Skin cleaned with antiseptic (chlorhexidine or povidone-iodine) as per hospital protocol.
        - Shaving may be done; avoid nicks.
        """)

    with st.expander("**Post-surgery wound care**"):
        st.markdown("""
        - Keep dressing dry and clean.
        - Change as per doctor's schedule.
        - Watch for signs of infection.
        - Support healing with good nutrition (protein, Vitamin C, zinc).
        """)

    with st.expander("**Surgical site care at home**"):
        st.markdown("""
        - Wash hands before touching dressing.
        - Do not remove staples/sutures yourself.
        - Report bleeding, opening, or discharge.
        """)

    st.markdown("---")
    st.markdown("## 6. Physiotherapy")

    with st.expander("**Goals in elderly / bed-bound care**", expanded=True):
        st.markdown("""
        - **Maintain joint mobility** — passive/active range of motion.
        - **Prevent contractures** — gentle stretching.
        - **Improve circulation** — leg exercises, positioning.
        - **Support breathing** — deep breathing, incentive spirometry if advised.
        - **Safe mobility** — transfer practice, gait training with support.
        """)

    with st.expander("**Simple exercises (as tolerated)**"):
        st.markdown("""
        - **Ankle pumps:** Point toes up/down; 10× each foot, several times daily.
        - **Knee bends:** Gently bend and straighten knees (if able).
        - **Arm raises:** Raise arms overhead; lower slowly.
        - **Deep breathing:** Inhale slowly, hold 2–3 sec, exhale. 5–10×, 2–3× daily.
        - **Seated leg lifts:** If sitting, lift one leg at a time, hold, lower.
        """)

    with st.expander("**When to involve a physiotherapist**"):
        st.markdown("""
        - After surgery or hospitalisation
        - Significant weakness or mobility loss
        - Risk of falls
        - Breathing difficulties
        - Contractures or stiffness
        - Doctor recommends PT
        """)

    with st.expander("**Transfer belt (Posey) for physiotherapy**"):
        st.markdown("""
        The [Posey Transfer Belt](https://www.amazon.in/Posey-Extra-Wide-Therapists-Caregivers-6537Q/dp/B00LWVQ3WA) supports safe standing, walking, and transfers during physiotherapy. See Care Equipment Guide for use instructions.
        """)

    st.markdown("---")
    st.caption("*This guide is for reference. All wound, necrosis, and surgical care must follow the treating doctor's instructions.*")

# ==================== DAILY TASKS & SCHEDULE ====================
elif page == "📅 Daily Tasks & Schedule":
    st.subheader("📅 Daily Tasks & Schedule")
    today = date.today()

    col_cal, col_tasks = st.columns([1, 2])
    with col_cal:
        selected_date = st.date_input("Select date", value=today, key="task_calendar")
        st.markdown("---")
        st.markdown("### 🍽️ Meal schedule")
        meals = get_meals_for_date(selected_date)
        if meals:
            st.markdown(f"**Breakfast:** {meals.get('breakfast', '—')}")
            st.markdown(f"**Lunch:** {meals.get('lunch', '—')}")
            st.markdown(f"**Dinner:** {meals.get('dinner', '—')}")
            st.markdown(f"**Snacks:** {meals.get('snacks', '—')}")
        else:
            st.info("Edit Nutrition Chart to set meals for this day.")

        with st.expander("➕ Schedule a task for this day"):
            new_task = st.text_input("Task name", placeholder="e.g. Doctor visit")
            if st.button("Add to schedule"):
                if new_task.strip():
                    schedule = load_json(TASKS_SCHEDULE_FILE, {})
                    date_str = selected_date.isoformat()
                    day_tasks = schedule.get(date_str, [])
                    day_tasks.append({"name": new_task.strip(), "added": datetime.now().isoformat()})
                    schedule[date_str] = day_tasks
                    save_json(TASKS_SCHEDULE_FILE, schedule)
                    st.success("Task scheduled.")
                    st.rerun()

    with col_tasks:
        st.markdown(f"### Tasks for {selected_date.strftime('%A, %d %B %Y')}")
        day_data = get_checklist_for_date(selected_date)
        tasks = day_data["tasks"]
        updated = False
        for i, t in enumerate(tasks):
            new_val = st.checkbox(t["name"], value=t.get("completed", False), key=f"task_{selected_date}_{i}")
            if new_val != t.get("completed"):
                tasks[i]["completed"] = new_val
                updated = True

        if updated or st.button("Save checklist", key="save_tasks"):
            checklist_data = load_json(CHECKLIST_LOG, [])
            day_data["tasks"] = tasks
            other = [c for c in checklist_data if c.get("date") != selected_date.isoformat()]
            other.append(day_data)
            save_json(CHECKLIST_LOG, other)
            st.success("Checklist saved.")
            st.rerun()

        completed = sum(1 for t in tasks if t.get("completed"))
        st.progress(completed / len(tasks) if tasks else 0)
        st.caption(f"{completed} of {len(tasks)} tasks completed")

# ==================== DAILY TODO ====================
elif page == "📋 Daily ToDo":
    st.subheader("📋 Daily ToDo Checklist")
    st.markdown("Add tasks with notes, track status, and set reminders. *Reminders are shown when you open this page.*")

    today = date.today()
    todo_data = load_json(TODO_FILE, {})
    selected_date = st.date_input("Date", value=today, key="todo_date")
    date_str = selected_date.isoformat()
    items = todo_data.get(date_str, [])

    now = datetime.now()
    reminders_today = [i for i in items if i.get("reminder") and i.get("status") != "completed"]
    reminders_today.sort(key=lambda x: x.get("reminder", ""))

    if reminders_today:
        st.markdown("### ⏰ Reminders")
        for r in reminders_today:
            st.info(f"**{r.get('reminder', '')}** — {r.get('title', '')}")
        st.markdown("---")

    st.markdown("### ToDo list")
    if not items:
        st.caption("No items yet. Add one below.")
    else:
        for i, item in enumerate(items):
            with st.container():
                col_chk, col_content, col_status, col_del = st.columns([0.4, 3, 1.5, 0.4])
                with col_chk:
                    is_done = item.get("status") == "completed"
                    new_done = st.checkbox("", value=is_done, key=f"todo_done_{date_str}_{i}")
                with col_content:
                    title = item.get("title", "")
                    notes = item.get("notes", "")
                    reminder = item.get("reminder", "")
                    st.markdown(f"**{title}**" + (f" — *Reminder: {reminder}*" if reminder else ""))
                    if notes:
                        st.caption(notes)
                with col_status:
                    status = st.selectbox(
                        "Status",
                        ["pending", "in_progress", "completed"],
                        index=["pending", "in_progress", "completed"].index(item.get("status", "pending")),
                        key=f"todo_status_{date_str}_{i}",
                        format_func=lambda x: {"pending": "Pending", "in_progress": "In Progress", "completed": "Completed"}[x],
                    )
                with col_del:
                    if st.button("🗑️", key=f"todo_del_{date_str}_{i}", help="Delete"):
                        items.pop(i)
                        todo_data[date_str] = items
                        save_json(TODO_FILE, todo_data)
                        st.rerun()
                new_status = "completed" if new_done else (status if status != "completed" else "pending")
                if new_status != item.get("status"):
                    item["status"] = new_status
                    item["updated"] = now.isoformat()
                    todo_data[date_str] = items
                    save_json(TODO_FILE, todo_data)
                    st.rerun()

    st.markdown("---")
    with st.expander("➕ Add ToDo"):
        with st.form("add_todo"):
            t_title = st.text_input("Title", placeholder="e.g. Call pharmacy")
            t_notes = st.text_area("Notes", placeholder="Optional details...")
            t_reminder = st.text_input("Reminder time (e.g. 09:00, 2:30 PM)", placeholder="09:00")
            if st.form_submit_button("Add"):
                if t_title.strip():
                    items.append({
                        "title": t_title.strip(),
                        "notes": t_notes.strip(),
                        "status": "pending",
                        "reminder": t_reminder.strip() or None,
                        "created": now.isoformat(),
                    })
                    todo_data[date_str] = items
                    save_json(TODO_FILE, todo_data)
                    st.success("ToDo added.")
                    st.rerun()
                else:
                    st.error("Enter a title.")

    completed = sum(1 for i in items if i.get("status") == "completed")
    st.progress(completed / len(items) if items else 0)
    st.caption(f"{completed} of {len(items)} completed")

# ==================== NUTRITION CHART ====================
elif page == "🍽️ Nutrition Chart":
    st.subheader("🍽️ Weekly Nutrition Chart")
    st.markdown("Set meal schedules for each day of the week. Shown on Daily Tasks & Schedule and Dashboard.")

    nutrition = load_json(NUTRITION_FILE, DEFAULT_NUTRITION)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for day in days:
        with st.expander(f"**{day}**", expanded=False):
            day_meals = nutrition.get(day, {})
            with st.form(f"nutrition_{day}"):
                b = st.text_input("Breakfast", value=day_meals.get("breakfast", ""), key=f"b_{day}")
                l = st.text_input("Lunch", value=day_meals.get("lunch", ""), key=f"l_{day}")
                d = st.text_input("Dinner", value=day_meals.get("dinner", ""), key=f"d_{day}")
                s = st.text_input("Snacks", value=day_meals.get("snacks", ""), key=f"s_{day}")
                if st.form_submit_button("Save"):
                    nutrition[day] = {"breakfast": b, "lunch": l, "dinner": d, "snacks": s}
                    save_json(NUTRITION_FILE, nutrition)
                    st.success(f"{day} saved.")
                    st.rerun()

# ==================== NUTRITION & SUPPLEMENTS ====================
elif page == "🥗 Nutrition & Supplements":
    st.subheader("🥗 Nutritional Requirements & Natural Supplements")
    st.markdown("Guidance for elderly care. *Always consult a doctor or dietitian before adding supplements.*")

    st.markdown("---")
    st.markdown("### 📋 Daily Nutritional Requirements (Elderly 70+ years)")

    req_df = pd.DataFrame({
        "Nutrient": [
            "Protein", "Calcium", "Vitamin D", "Vitamin B12", "Iron", "Zinc",
            "Vitamin C", "Omega-3", "Fibre", "Fluids",
        ],
        "Daily need (approx.)": [
            "1.0–1.2 g/kg body weight", "1200 mg", "800–1000 IU", "2.4 mcg", "8 mg (men)", "11 mg (men)",
            "75–90 mg", "1.1–1.6 g", "21–30 g", "1.5–2 L",
        ],
        "Role": [
            "Muscle, wound healing, immunity", "Bones, teeth", "Calcium absorption, bones", "Nerves, blood", "Oxygen, energy", "Immunity, wound healing",
            "Immunity, wound healing", "Heart, brain, anti-inflammatory", "Digestion, gut health", "Hydration, kidney function",
        ],
    })
    st.dataframe(req_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 🥛 Protein — Priority for Wound Healing & Muscle")

    st.markdown("""
    **Why it matters:** Protein is essential for wound healing (e.g. bed sores), maintaining muscle mass, and immunity. Elderly often need more than younger adults.

    **Food sources:** Dal, paneer, eggs, fish, chicken, milk, yogurt, nuts, PROTEINEX (as prescribed).

    **Current prescription:** PROTEINEX Powder — 2 scoops/day.
    """)

    st.markdown("---")
    st.markdown("### 💊 Natural Supplements — Common for Elderly Care")

    with st.expander("**Vitamin D**"):
        st.markdown("""
        - **Why:** Poor absorption with age; limited sun exposure; supports bones, immunity, mood.
        - **Sources:** Sunlight (15–20 min), fatty fish, fortified milk, eggs.
        - **Supplement:** Often 600–1000 IU/day; doctor may prescribe higher if deficient.
        """)

    with st.expander("**Vitamin B12**"):
        st.markdown("""
        - **Why:** Absorption decreases with age; supports nerves and red blood cells.
        - **Sources:** Fish, eggs, dairy, fortified cereals.
        - **Supplement:** Sublingual or injection if deficient (common in elderly).
        """)

    with st.expander("**Calcium**"):
        st.markdown("""
        - **Why:** Bone health; often low in elderly.
        - **Sources:** Milk, yogurt, paneer, ragi, leafy greens, fish with bones.
        - **Note:** Take with Vitamin D for absorption.
        """)

    with st.expander("**Omega-3 (fish oil)**"):
        st.markdown("""
        - **Why:** Heart, brain, anti-inflammatory.
        - **Sources:** Fatty fish (salmon, mackerel), walnuts, flaxseed, chia.
        - **Supplement:** 250–500 mg EPA+DHA; check with doctor if on blood thinners.
        """)

    with st.expander("**Zinc**"):
        st.markdown("""
        - **Why:** Wound healing, immunity, taste.
        - **Sources:** Legumes, nuts, seeds, whole grains, dairy.
        - **Supplement:** 8–11 mg; high doses can affect copper absorption.
        """)

    with st.expander("**Probiotics**"):
        st.markdown("""
        - **Why:** Gut health, immunity, digestion.
        - **Sources:** Yogurt, buttermilk, fermented foods (idli, dosa batter).
        - **Supplement:** Lactobacillus, Bifidobacterium; choose strains suited to elderly.
        """)

    with st.expander("**Turmeric / Curcumin**"):
        st.markdown("""
        - **Why:** Anti-inflammatory; may support joints and general wellness.
        - **Sources:** Turmeric in cooking, haldi milk.
        - **Note:** Can interact with blood thinners; discuss with doctor.
        """)

    with st.expander("**Ashwagandha**"):
        st.markdown("""
        - **Why:** Traditionally used for stress, sleep, energy.
        - **Note:** May affect thyroid, blood sugar, blood pressure; consult doctor before use.
        """)

    st.markdown("---")
    st.markdown("## 📅 Weekly Food Plan")

    st.markdown("""
    A practical meal plan aligned with nutritional requirements for elderly care. Focus: **protein** (wound healing), **calcium**, **Vitamin C**, **zinc**, **probiotics**, **omega-3**. Adjust textures (soft, mashed) and portion sizes as needed.
    """)

    plan_df = pd.DataFrame({
        "Meal": ["Early morning", "Breakfast", "Mid-morning", "Lunch", "Evening", "Dinner", "Before bed"],
        "Time": ["6:30–7:00", "8:00–8:30", "10:30–11:00", "12:30–1:00", "4:00–4:30", "7:00–7:30", "9:00–9:30"],
        "Purpose": ["Hydration, gentle start", "Main meal, protein", "Snack, energy", "Main meal, balanced", "Light snack", "Lighter main", "Sleep support"],
    })
    st.dataframe(plan_df, use_container_width=True, hide_index=True)

    st.markdown("### Sample daily template")
    st.markdown("""
    | Meal | Options (rotate) |
    | --- | --- |
    | **Early morning** | Warm water + lemon, or haldi milk (turmeric), or green tea |
    | **Breakfast** | Oats/porridge + milk + banana + **PROTEINEX 1 scoop** • OR Idli/dosa + sambar + chutney • OR Poha + peanuts + lemon • OR Upma + coconut |
    | **Mid-morning** | Fruit (papaya, banana, apple) • OR Buttermilk • OR Handful of nuts (almonds, walnuts) |
    | **Lunch** | Dal + rice + sabzi + roti + curd • OR Fish/egg curry + rice + vegetables • OR Khichdi + papad + pickle |
    | **Evening** | Milk + biscuits • OR Fruit • OR **PROTEINEX 1 scoop** with milk • OR Sprouted salad |
    | **Dinner** | Light: Soup + chapati + vegetable • OR Khichdi + yogurt • OR Rice + dal + steamed vegetables |
    | **Before bed** | Warm milk (optional) |
    """)

    st.markdown("### Weekly rotation — protein & key nutrients")

    week_plan = pd.DataFrame({
        "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "Protein focus": ["Dal, paneer", "Egg, fish", "Chicken, legumes", "Paneer, dal", "Fish, egg", "Legumes, yogurt", "Mixed — khichdi"],
        "Calcium": ["Milk, curd, paneer", "Milk, fish", "Curd, ragi", "Paneer, milk", "Fish, curd", "Yogurt, milk", "Curd, milk"],
        "Vitamin C": ["Lemon, tomato, papaya", "Orange, capsicum", "Amla, leafy greens", "Tomato, guava", "Lemon, broccoli", "Papaya, tomato", "Lemon, vegetables"],
        "Probiotics": ["Curd", "Buttermilk", "Curd", "Buttermilk", "Curd", "Yogurt, fermented", "Curd"],
    })
    st.dataframe(week_plan, use_container_width=True, hide_index=True)

    st.markdown("### Sample weekly menu (detailed)")

    with st.expander("**Monday**"):
        st.markdown("""
        - **Breakfast:** Oats cooked in milk, banana, PROTEINEX 1 scoop
        - **Lunch:** Moong dal, rice, bhindi sabzi, roti, curd
        - **Dinner:** Vegetable soup, chapati, paneer bhurji
        """)

    with st.expander("**Tuesday**"):
        st.markdown("""
        - **Breakfast:** 2 idli, sambar, coconut chutney
        - **Lunch:** Fish curry (or egg curry), rice, mixed vegetables, buttermilk
        - **Dinner:** Khichdi, papad, curd
        """)

    with st.expander("**Wednesday**"):
        st.markdown("""
        - **Breakfast:** Poha with peanuts, lemon, PROTEINEX 1 scoop
        - **Lunch:** Chole, rice, roti, raita, salad
        - **Dinner:** Dal, rice, palak sabzi, curd
        """)

    with st.expander("**Thursday**"):
        st.markdown("""
        - **Breakfast:** Upma, coconut chutney
        - **Lunch:** Paneer curry, dal, rice, roti, buttermilk
        - **Dinner:** Vegetable pulao, raita
        """)

    with st.expander("**Friday**"):
        st.markdown("""
        - **Breakfast:** Dosa, sambar, chutney
        - **Lunch:** Egg curry (or chicken), rice, beans sabzi, curd
        - **Dinner:** Soup, chapati, dal
        """)

    with st.expander("**Saturday**"):
        st.markdown("""
        - **Breakfast:** Paratha with yogurt, PROTEINEX 1 scoop
        - **Lunch:** Rajma, rice, roti, cucumber raita
        - **Dinner:** Khichdi, papad, pickle
        """)

    with st.expander("**Sunday**"):
        st.markdown("""
        - **Breakfast:** Pancakes or bread with egg, milk
        - **Lunch:** Roti, chole, rice, mixed vegetables, curd
        - **Dinner:** Light khichdi, yogurt
        """)

    st.markdown("### Tips for this food plan")
    st.markdown("""
    - **PROTEINEX:** 2 scoops/day — split (1 at breakfast, 1 at evening) or as advised.
    - **Texture:** Soft, well-cooked, mashed if needed. Avoid hard, dry, or choking-risk foods.
    - **Portions:** Smaller, more frequent meals if appetite is low.
    - **Hydration:** Water, buttermilk, soups, milk — aim 1.5–2 L.
    - **Omega-3:** Include fish 2–3×/week; walnuts in snacks.
    - **Sync with Nutrition Chart:** Use the Nutrition Chart page to set your preferred weekly meals.
    """)

    st.markdown("---")
    st.markdown("### ⚠️ Important Notes")

    st.markdown("""
    - **Consult a doctor or dietitian** before starting any supplement.
    - **Drug interactions:** Supplements can interact with medications (e.g. blood thinners, diabetes drugs).
    - **Quality:** Choose reputable brands; avoid unregulated products.
    - **Food first:** Prioritise a balanced diet; supplements complement, not replace, food.
    - **Track in Inventory:** Log supplements in the Inventory section for stock and re-order alerts.
    """)

    st.markdown("---")
    st.markdown("### 📌 For This Care Context")

    st.markdown("""
    Given respiratory support needs and wound care (bed sores):
    - **Protein:** Ensure adequate intake (PROTEINEX + dietary sources) for wound healing.
    - **Vitamin C & Zinc:** Support tissue repair.
    - **Vitamin D:** Often deficient; consider testing and supplementation if advised.
    - **Hydration:** Adequate fluids; monitor if on fluid restrictions.
    """)

# ==================== ENGLISH BREAKFAST GUIDE ====================
elif page == "🍳 English Breakfast Guide":
    st.subheader("🍳 The Indian Guide to English Breakfast")
    st.markdown("""
    *Master every technique from boiling to frying. Step-by-step instructions, Indian substitutions & pro tips.*  
    Adapted from **English Breakfast for Indians** — a comprehensive guide for Indian cooks.
    """)

    st.markdown("### 📺 Watch & Learn — YouTube Tutorials")
    yt_cols = st.columns(2)
    with yt_cols[0]:
        st.markdown("""
        - [Full English Breakfast 🥓🍳](https://www.youtube.com/watch?v=ZEJNpx9aYFI)
        - [Basics with Babish — Full English](https://www.youtube.com/watch?v=n2POMVVED1A)
        - [A Proper Full English Breakfast](https://www.youtube.com/watch?v=P-WNLRsLlvE)
        """)
    with yt_cols[1]:
        st.markdown("""
        - [Gordon Ramsay — Perfect Scrambled Eggs](https://www.youtube.com/watch?v=quNIZN6yAQo)
        - [How to Make Breakfast Like a Brit](https://www.youtube.com/watch?v=rmieAqTG1wI)
        """)

    st.markdown("---")
    st.markdown("### 🍽️ What is a Full English Breakfast?")
    st.markdown("""
    A traditional **Full English** (or "Fry-Up") typically includes:
    - Back bacon or streaky bacon
    - Fried or scrambled eggs
    - Pork sausages
    - Grilled tomatoes
    - Baked beans
    - Toast with butter
    - Sautéed mushrooms
    - Black pudding (optional)
    - Hash browns (modern versions)
    """)
    st.info("💡 Many ingredients have easy Indian substitutes — noted throughout this guide.")

    st.markdown("---")
    st.markdown("### 🕐 Cooking Timeline (Visualization)")
    timeline_df = pd.DataFrame({
        "Time": ["T-25 min", "T-15 min", "T-12 min", "T-10 min", "T-8 min", "T-6 min", "T-5 min", "T-4 min", "T-3 min", "T-0"],
        "Item": ["Sausages", "Hash browns", "Tomatoes", "Bacon", "Mushrooms", "Beans", "Tomatoes flip", "Toast", "Eggs", "Plate & serve"],
        "Action": ["Start grilling", "Oven/pan", "Grill cut-side down", "Pan fry", "Sauté", "Warm on low", "Flip cut-side up", "Start toasting", "Cook last", "Serve immediately"],
    })
    st.dataframe(timeline_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 📖 Part 1: Cooking Techniques")

    with st.expander("**Chapter 1: Boiling** — Eggs & More", expanded=True):
        st.markdown("""
        **What is Boiling?** Heating a liquid to 100°C and submerging food to cook.

        **Types** | **Use**
        --- | ---
        Full rolling boil | Pasta, potatoes, hard-boiled eggs
        Gentle simmer (85–95°C) | Poached eggs, sauces, soups
        Blanching | Quick dip, then ice water — preserves vegetable colour

        **Perfect Soft Boiled Egg:**
        1. Remove eggs from fridge 10 min before cooking
        2. Bring water to full rolling boil
        3. Gently lower eggs, reduce to simmer
        4. **4 min** = runny yolk | **5 min** = jammy yolk | **7 min** = medium | **10–12 min** = hard
        5. Transfer to ice water 1 min, then peel
        """)
        boil_df = pd.DataFrame({
            "Type": ["Soft Boiled", "Medium Boiled", "Hard Boiled"],
            "Time": ["4–5 mins", "7 mins", "10–12 mins"],
            "Yolk": ["Runny, liquid", "Jammy, semi-set", "Fully set, firm"],
            "Serve With": ["Toast soldiers", "Salads, toast", "Egg mayo, sandwiches"],
        })
        st.dataframe(boil_df, use_container_width=True, hide_index=True)
        st.caption("Tip: Add salt or vinegar to water to prevent cracking. Use room-temperature eggs.")

    with st.expander("**Chapter 2: Frying** — Eggs, Bacon, Hash Browns"):
        st.markdown("""
        **Types:** Shallow frying (most common) | Deep frying | Dry frying (no oil — bacon fat releases)

        **Fats:** Butter (eggs) | Ghee (Indian substitute) | Vegetable oil | Bacon fat (traditional)

        **Fried Egg Styles:**
        - **Sunny Side Up:** One side only, yolk runny, cover 30 sec to set white
        - **Over Easy:** Flip briefly, yolk runny
        - **Over Hard:** Both sides until yolk firm
        - **Basted:** Spoon hot butter over yolk continuously

        **Tip:** Low-to-medium heat. High heat = rubbery white, burnt edges. Ghee adds nutty aroma.
        """)

    with st.expander("**Chapter 3: Scrambling** — English Method"):
        st.markdown("""
        **English vs American:** English = low heat, patience, creamy curds. American = high heat, drier.

        **Ingredients (Serves 2):**
        | Ingredient | Quantity | Notes |
        | --- | --- | --- |
        | Eggs | 4 large | Room temperature |
        | Butter | 30g | Substitute: ghee |
        | Milk or cream | 2 tbsp | Full-fat |
        | Salt | To taste | Add after cooking |
        | White pepper | Pinch | Or black pepper |
        | Chives | Optional | Spring onion greens work |

        **Steps:**
        1. Beat eggs, milk, pepper — do not over-beat
        2. Melt butter in pan on LOW heat
        3. Pour eggs, wait 20–30 sec
        4. Drag S-shapes with spatula, fold gently
        5. Move pan off heat every few seconds
        6. Remove when slightly underdone — residual heat finishes
        7. Season with salt only at the end
        8. Serve on hot buttered toast

        **Indian twist:** Add turmeric + finely chopped green chilli.
        """)

    with st.expander("**Chapter 4: Sautéing** — Mushrooms"):
        st.markdown("""
        **Key:** Mushrooms must go into a HOT pan. Cold pan = grey, watery mushrooms.

        **Ingredients (Serves 2):**
        | Ingredient | Quantity | Notes |
        | --- | --- | --- |
        | Button mushrooms | 200g | Or cremini |
        | Butter | 20g | Ghee or olive oil |
        | Garlic | 2 cloves, minced | Optional |
        | Thyme | 2 sprigs | Dried: half quantity |
        | Parsley | For garnish | Coriander works |

        **Steps:**
        1. Wipe mushrooms with damp cloth — do not wash
        2. Slice thickly (5mm)
        3. Heat pan MEDIUM-HIGH until very hot
        4. Add butter, foam, then mushrooms in SINGLE LAYER
        5. Do not stir for 2 min — let sear
        6. Toss once, 60–90 sec more
        7. Add garlic, thyme, 1 min
        8. Season, finish with butter knob
        """)

    st.markdown("---")
    st.markdown("### 🍳 Part 2: Full Recipe & Ingredients")

    with st.expander("**Complete Ingredients List** (Serves 4)"):
        full_df = pd.DataFrame({
            "Ingredient": [
                "Back bacon or streaky bacon", "Pork sausages", "Eggs", "Button mushrooms",
                "Large tomatoes", "Baked beans (tinned)", "Thick white bread", "Butter",
                "Vegetable oil", "Optional: black pudding", "Optional: hash browns",
            ],
            "Quantity": ["4–6 rashers", "4", "4", "150g", "2 halved", "1 tin 400g", "4 slices", "50g", "2 tbsp", "2 slices", "4 pieces"],
            "Indian Substitute": [
                "Chicken bacon (Licious)", "Chicken/turkey sausages", "—", "—",
                "—", "Heinz (imported) or homemade", "—", "Amul salted butter", "—",
                "Spiced beetroot slices", "—",
            ],
        })
        st.dataframe(full_df, use_container_width=True, hide_index=True)

    with st.expander("**Vegetarian Adaptations**"):
        veg_df = pd.DataFrame({
            "Original": ["Pork/chicken bacon", "Pork sausages", "Black pudding", "Baked beans", "Butter"],
            "Vegetarian Substitute": ["Smoked paneer strips", "Vegetable soya sausages", "Spiced beetroot slices", "Rajma in tomato sauce", "Vegan butter or ghee"],
        })
        st.dataframe(veg_df, use_container_width=True, hide_index=True)

        st.markdown("**Paneer Bacon (Marinated):**")
        st.markdown("""
        | Ingredient | Quantity |
        | --- | --- |
        | Paneer | 200g, thin strips 4mm |
        | Soy sauce | 2 tbsp |
        | Smoked paprika | 1 tsp |
        | Maple syrup/honey | 1 tsp |
        | Garlic powder | ½ tsp |
        | Oil | 1 tbsp |
        """)

    with st.expander("**HP Sauce (Homemade Brown Sauce)**"):
        st.markdown("""
        | Ingredient | Quantity |
        | --- | --- |
        | Tamarind paste | 3 tbsp |
        | Date paste/jaggery | 2 tbsp |
        | Malt vinegar | 2 tbsp |
        | Soy sauce | 1 tbsp |
        | Worcestershire sauce | 1 tsp |
        | Tomato ketchup | 3 tbsp |
        | Mixed spice powder | ½ tsp |
        | Salt | To taste |

        Combine, simmer 3–4 min until thickened. Cool, store in jar. Keeps 2 weeks.
        """)

    st.markdown("---")
    st.markdown("### 🛠️ Troubleshooting")

    with st.expander("Common Problems & Solutions"):
        prob_df = pd.DataFrame({
            "Item": ["Eggs", "Bacon", "Mushrooms", "Toast", "Sausages"],
            "Problem": [
                "Eggs spread in pan", "Bacon burnt & curling", "Grey, watery mushrooms", "Pale inside, burnt edges", "Brown outside, raw inside",
            ],
            "Solution": [
                "Use fresh eggs only",
                "Reduce heat; score fat edge",
                "Pan not hot enough; cook in batches",
                "Move grill further away",
                "Reduce heat; cook slower; prick 4–5 times",
            ],
        })
        st.dataframe(prob_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 📚 Glossary")
    gloss_df = pd.DataFrame({
        "Term": ["Fry-up", "Rasher", "Back bacon", "Streaky bacon", "Black pudding", "Basted egg", "Soldiers", "Hash browns", "HP Sauce", "Full works"],
        "Meaning": [
            "British slang for Full English",
            "Single slice of bacon",
            "From back loin — leaner",
            "From belly — fattier, crispier",
            "Sausage from pork blood, oats",
            "Egg with hot butter spooned over",
            "Toast fingers for dipping",
            "Grated fried potato cakes",
            "Britain's iconic brown sauce",
            "Complete Full English",
        ],
    })
    st.dataframe(gloss_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 📖 Make-Ahead")
    st.markdown("""
    - **Hash browns:** Bake, cool, refrigerate. Reheat 10 min at 200°C.
    - **Beans:** Homemade batch, refrigerate 3–4 days.
    - **HP Sauce:** Homemade jar, 2 weeks.
    - **Paneer bacon:** Marinate overnight.
    - **Sausages:** Grill ahead, keep warm 100°C oven up to 30 min.
    """)

    st.markdown("---")
    st.success("**Happy cooking!** — From your kitchen to the British countryside. Experiment with ghee, green chilli, cumin. The recipe is yours to make.")

# ==================== INVENTORY ====================
elif page == "📦 Inventory":
    st.subheader("📦 Medicines, Supplements & Food Inventory")
    st.markdown("Track stock levels. **Re-order alert** when stock falls below 40% of monthly requirement.")

    REORDER_THRESHOLD = 0.4
    inventory = load_json(INVENTORY_FILE, {"medicines": [], "supplements": [], "food": []})

    for category, label in [("medicines", "💊 Medicines"), ("supplements", "💊 Supplements"), ("food", "🍎 Food")]:
        st.markdown(f"### {label}")
        items = inventory.get(category, [])
        alerts = []
        for i, item in enumerate(items):
            name = item.get("name", "?")
            current = float(item.get("current_stock", 0))
            monthly = float(item.get("monthly_requirement", 1))
            unit = item.get("unit", "units")
            pct = (current / monthly * 100) if monthly > 0 else 0
            if pct < 40:
                alerts.append(f"**{name}**: {current} {unit} ({pct:.0f}% of monthly) — re-order needed")

        if alerts:
            for a in alerts:
                st.error(a)

        df = pd.DataFrame(items) if items else pd.DataFrame(columns=["name", "current_stock", "monthly_requirement", "unit"])
        if not df.empty:
            st.dataframe(df[["name", "current_stock", "monthly_requirement", "unit"]], use_container_width=True, hide_index=True)

        with st.expander(f"Add/Update {category}"):
            with st.form(f"inv_{category}"):
                in_name = st.text_input("Item name", key=f"inv_name_{category}")
                in_current = st.number_input("Current stock", min_value=0.0, value=0.0, key=f"inv_cur_{category}")
                in_monthly = st.number_input("Monthly requirement", min_value=0.1, value=1.0, key=f"inv_mon_{category}")
                in_unit = st.text_input("Unit (e.g. strips, bottles, kg)", value="units", key=f"inv_unit_{category}")
                if st.form_submit_button("Add/Update"):
                    if not in_name.strip():
                        st.error("Enter item name.")
                    else:
                        existing = next((x for x in items if x.get("name", "").lower() == in_name.strip().lower()), None)
                        if existing:
                            existing["current_stock"] = in_current
                            existing["monthly_requirement"] = in_monthly
                            existing["unit"] = in_unit
                        else:
                            items.append({"name": in_name.strip(), "current_stock": in_current, "monthly_requirement": in_monthly, "unit": in_unit})
                        inventory[category] = items
                        save_json(INVENTORY_FILE, inventory)
                        st.success("Updated.")
                        st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("CareAssist v1.0 • For Gopal Singh Sankhala")
