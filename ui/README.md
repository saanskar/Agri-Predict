# 🌾 AgriPredict Pro — Merged Frontend

**Final Year Capstone Project**  
AI-powered crop recommendation system combining a FastAPI ML backend (V1) with a premium multi-page Streamlit dashboard (V2).

---

## 📁 Project Structure

```
agripredict_merged/
│
├── app.py                          ← Streamlit entry point + sidebar nav
├── styles.py                       ← Full CSS (dark glassmorphism theme)
├── charts.py                       ← All Plotly chart functions
├── utils.py                        ← API client, session state, helpers
├── requirements.txt
│
├── pages/
│   ├── dashboard.py                ← Home: KPIs, soil gauge, overview
│   ├── predict.py                  ← Core: soil form → API → results
│   ├── weather.py                  ← Live weather cards + session trend
│   ├── soil.py                     ← NPK + pH detail, tips, update form
│   ├── history.py                  ← Session prediction log + CSV export
│   └── about.py                    ← Project info, tech stack, API ref
│
└── components/
    ├── geolocation.py              ← V1 browser GPS component (unchanged)
    └── geolocation_frontend/
        └── index.html              ← V1 component HTML (unchanged)
```

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) set a custom backend URL
export AGRIPREDICT_API_BASE_URL=https://agri-predict-v4em.onrender.com

# 3. Run
streamlit run app.py
```

The backend is already deployed at `https://agri-predict-v4em.onrender.com`.  
No backend changes needed — the V1 FastAPI server is used as-is.

---

## 🔌 Backend API Contract (V1 — unchanged)

**POST** `/recommendations`

```json
// Request
{
  "location": { "lat": 20.5, "lon": 78.9 },
  "soil":     { "n": 90, "p": 42, "k": 43, "ph": 6.5 },
  "top_k":    5
}

// Response
{
  "weather": {
    "temperature_c": 25.3,
    "relative_humidity_pct": 72.0,
    "rainfall_mm": 0.0
  },
  "recommendations": [
    { "crop": "rice",   "probability": 0.87 },
    { "crop": "maize",  "probability": 0.10 }
  ]
}
```

**GET** `/health` → `200 OK`

---

## ✅ Merge Rules Applied

| Rule | Status |
|------|--------|
| 1. V1 backend untouched | ✅ `components/geolocation.py` ported verbatim; API contract preserved |
| 2. V2 frontend design | ✅ All pages, CSS, charts from V2 |
| 3. Real values only | ✅ Zero simulated data; all KPIs from session_state |
| 4. Every page works | ✅ 6 pages with empty-state fallbacks |
| 5. Modular code | ✅ `utils` / `charts` / `styles` / `pages` / `components` separated |
| 6. Mobile responsive | ✅ CSS breakpoints at 768 px and 480 px |
| 7. Error handling | ✅ `APIError` / `NetworkError` with user-friendly guidance |
| 8. Submission ready | ✅ Clean imports, docstrings, README |

---

## 🌐 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AGRIPREDICT_API_BASE_URL` | `https://agri-predict-v4em.onrender.com` | Backend base URL |

---

## 📦 Pages Summary

| Page | Description |
|------|-------------|
| **Dashboard** | 6 live KPI cards + soil gauge + last prediction chart |
| **Predict Crop** | Soil form + GPS + API call + ranked results + charts |
| **Weather Analytics** | Live weather cards + session trend (real readings) |
| **Soil Health** | NPK bars, pH scale, nutrient status, fertiliser tips |
| **History** | Session prediction log, trend chart, CSV export |
| **About** | Project overview, ML architecture, tech stack, API ref |
