# CareAssist — Virtual Caretaking Assistant

A comprehensive virtual assistant for daily treatment and record-keeping of **Gopal Singh Sankhala**, managed by **Vikram Singh Sankhala** with the support of a medical attendant.

## Features

| Module | Description |
|--------|-------------|
| **Dashboard** | Daily overview, latest vitals, checklist progress |
| **Medication & Treatment** | Prescription tracking, medication logging, nebuliser care |
| **Vitals & Monitoring** | Record and view pulse, BP, SpO₂, respiratory notes |
| **Hygiene & Cleanliness** | Daily hygiene protocols, hand hygiene, linen care |
| **Bathroom Care** | Disinfection protocols, diaper care, disinfectant guidance |
| **Equipment & Supplies** | Nebuliser care, BP monitor, supplies checklist |
| **Disinfection & Pest Control** | Disinfection schedule, pest prevention |
| **Technology Hygiene** | Device sanitization, data backup |
| **General Surgery Care** | Wound care, post-surgery monitoring, when to call doctor |
| **Image Analysis** | Upload photos for AI analysis (wound, skin, medication, hygiene) via OpenAI/Claude/Gemini |
| **Daily Checklist** | Task list for caregiver and attendant |

## Deploy on Render.com via GitHub

### 1. Push to GitHub

```bash
cd "c:\Users\I762844\Documents\Doctor"
git init
git add .
git commit -m "Initial CareAssist deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/careassist.git
git push -u origin main
```

> **Note:** Create a new repository on [GitHub](https://github.com/new) named `careassist` (or your choice) first, then use its URL above.

### 2. Deploy on Render

1. Go to [Render.com](https://render.com) and sign up (free).
2. Click **New** → **Web Service**.
3. Connect your GitHub account and select the `careassist` repository.
4. Configure:
   - **Name:** `careassist` (or any name)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
5. Click **Create Web Service**.

6. **Image Analysis (optional):** To enable AI image analysis, add environment variables in Render Dashboard → Environment:
   - `OPENAI_API_KEY` (for GPT-4o), or
   - `ANTHROPIC_API_KEY` (for Claude 3), or
   - `GOOGLE_API_KEY` (for Gemini)

Render will build and deploy. Your app will be available at `https://careassist.onrender.com` (or your chosen subdomain).

### 3. Optional: Use render.yaml

If your repo has `render.yaml`, Render can auto-detect it. When creating a new service, choose **Apply render.yaml** and it will use the configuration from the file.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Data Storage

- Vitals, medication logs, and checklist data are stored in the `data/` folder as JSON files.
- On Render’s free tier, the filesystem is ephemeral, so data resets on redeploy. For persistent storage, consider adding a database (e.g. SQLite with a persistent disk, or a cloud DB).

## Patient & Caregiver

- **Patient:** Gopal Singh Sankhala  
- **Primary Caregiver:** Vikram Singh Sankhala  
- **Support:** Medical attendant (doctor, nurse, caretaker functions)

---

*CareAssist v1.0 — Built for comprehensive home care*
