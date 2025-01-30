import streamlit as st
import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

# Load the dataset
file_path = "canteen_footfall_6months.csv"
df = pd.read_csv(file_path)

# Encode categorical day column
label_encoder = LabelEncoder()
df['Day'] = label_encoder.fit_transform(df['Day'])

# Train-test split
X = df[['Day', 'Slot_No']]
y = df['Number_of_People']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train different regression models
models = {
    "Random Forest": RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42),
    "Linear Regression": LinearRegression(),
    "Support Vector Regression": SVR(kernel='rbf', C=100, gamma=0.1)
}

best_model = None
best_r2 = float('-inf')
model_scores = {}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred_test = model.predict(X_test)
    r2 = r2_score(y_test, y_pred_test)
    model_scores[name] = r2
    if r2 > best_r2:
        best_r2 = r2
        best_model = model

# Save the best trained model
with open("canteen_model.pkl", "wb") as f:
    pickle.dump((best_model, label_encoder), f)

# Streamlit UI
st.title("Canteen Crowd Prediction")

# Display R-squared values for all models
for model_name, r2_value in model_scores.items():
    st.write(f"{model_name} Test R-squared value: {r2_value:.2f}")

st.write(f"Best Model Selected: {max(model_scores, key=model_scores.get)}")

# User input
input_day = st.selectbox("Select Day", label_encoder.classes_)
input_slot = st.slider("Select Time Slot", min_value=int(df['Slot_No'].min()), max_value=int(df['Slot_No'].max()))

# Predict
if st.button("Predict Crowd"):
    encoded_day = label_encoder.transform([input_day])[0]
    prediction = best_model.predict([[encoded_day, input_slot]])[0]
    st.write(f"Predicted crowd: {int(prediction)} people")
