import joblib
import pandas as pd
from sklearn.metrics import accuracy_score
import json

# Load model
model = joblib.load("../../artifacts/random_forest.joblib")

# Load preprocessor
preprocessor = joblib.load("../../artifacts/preprocessor.joblib")

# Load labels list
with open("../../artifacts/labels.json") as f:
    labels = json.load(f)

# Create mapping (IMPORTANT FIX)
label_map = {label: idx for idx, label in enumerate(labels)}

# Load dataset
df = pd.read_csv("../Crop_recommendation.csv")

# Features & label
X = df[['N','P','K','temperature','humidity','ph','rainfall']]
y = df['label']

# Convert labels to numeric
y_encoded = y.map(label_map)

# Apply preprocessing
X_processed = preprocessor.transform(X)

# Predict
y_pred = model.predict(X_processed)

# Accuracy
accuracy = accuracy_score(y_encoded, y_pred)

print("Model Accuracy:", accuracy)