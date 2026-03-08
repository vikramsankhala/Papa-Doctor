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
        "🦠 Disinfection & Pest Control",
        "📱 Technology Hygiene",
        "🏥 General Surgery Care",
        "📅 Daily Tasks & Schedule",
        "📋 Daily ToDo",
        "🍽️ Nutrition Chart",
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
