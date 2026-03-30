# AgriPredict

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.39%2B-FF4B4B?logo=streamlit&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-enabled-261230?logo=ruff&logoColor=white)
![Mypy](https://img.shields.io/badge/mypy-strict-2A6DB2)
![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)
![Cost of Development](https://img.shields.io/badge/Cost_of_Development-%245-brightgreen)

AgriPredict is a hybrid machine-learning crop recommendation system combining **Random Forest**, **XGBoost**, and a small **Neural Network**. It takes manual soil inputs (NPK + pH), enriches them with live weather by location (Open-Meteo), and returns crop recommendations via a backend API and farmer-friendly UI.

## Quick start (local)

### Prerequisites

- Python 3.11+

### Setup

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### Train models (creates local artifacts)

```bash
python -m ml.train
```

### Run API

```bash
uvicorn backend.app.main:app --reload
```

### Run UI

```bash
streamlit run ui/app.py
```

### Run checks

```bash
ruff format --check .
ruff check .
mypy backend ml ui scripts
pytest --cov
python scripts/check_design_guards.py
```

## GitHub Actions

CI runs the same checks on every push/PR.

