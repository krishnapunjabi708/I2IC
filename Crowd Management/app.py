import streamlit as st
import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split


def train_and_save_model(file_path, model_name):
    df = pd.read_csv(file_path)
    label_encoder = LabelEncoder()
    df['Day'] = label_encoder.fit_transform(df['Day'])

    #split the data
    X = df[['Day', 'Slot_No']]
    y = df['Number_of_People']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    #Random Forest model
    model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    # Saved tge model
    with open(f"{model_name}_model.pkl", "wb") as f:
        pickle.dump((model, label_encoder), f)


train_and_save_model("canteen_footfall_6months.csv", "canteen1")
train_and_save_model("canteen2_footfall.csv", "canteen2")
train_and_save_model("canteen3_footfall.csv", "canteen3")



#UI
# st.title("Canteen Crowd Prediction and Recommendation")
# canteen_capacities = {
#     "Canteen 1": 120,
#     "Canteen 2": 50,
#     "Canteen 3": 300,
# }
# time_slots = {
#     1: "12:00 PM - 12:10 PM",
#     2: "12:10 PM - 12:20 PM",
#     3: "12:20 PM - 12:30 PM",
#     4: "12:30 PM - 12:40 PM",
#     5: "12:40 PM - 12:50 PM",
#     6: "12:50 PM - 1:00 PM",
#     7: "1:00 PM - 1:10 PM",
#     8: "1:10 PM - 1:20 PM",
#     9: "1:20 PM - 1:30 PM",
#     10: "1:30 PM - 1:40 PM",
#     11: "1:40 PM - 1:50 PM",
#     12: "1:50 PM - 2:00 PM",

# }

# input_day = st.selectbox("Select Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

# selected_time_slot = st.selectbox("Select Time Slot", list(time_slots.values()))

# slot_no = list(time_slots.keys())[list(time_slots.values()).index(selected_time_slot)]

# predictions = {}
# free_spaces = {}

# for canteen_name in canteen_capacities.keys():
#     model_file = f"{canteen_name.lower().replace(' ', '')}_model.pkl"
#     with open(model_file, "rb") as f:
#         saved_data = pickle.load(f) 
#         model, label_encoder = saved_data  

#     encoded_day = label_encoder.transform([input_day])[0]

#     predicted_crowd = model.predict([[encoded_day, slot_no]])[0]
#     predictions[canteen_name] = predicted_crowd

    
#     capacity = canteen_capacities[canteen_name]
#     free_space = capacity - predicted_crowd
#     free_spaces[canteen_name] = free_space

# st.subheader("Predictions and Free Spaces")
# for canteen_name, predicted_crowd in predictions.items():
#     st.write(f"{canteen_name}: Predicted crowd = {int(predicted_crowd)}, Free space = {int(free_spaces[canteen_name])}")


# ranked_canteens = sorted(free_spaces.items(), key=lambda x: x[1], reverse=True)


# st.subheader("Recommendations")
# for i, (canteen_name, free_space) in enumerate(ranked_canteens):
#     if free_space > 0:
#         st.write(f"{i + 1}. {canteen_name} has {int(free_space)} free seats available.")
#     else:
#         st.write(f"{i + 1}. {canteen_name} is full (no free seats).")

# total_capacity = sum(canteen_capacities.values())
# total_predicted_crowd = sum(predictions.values())

# st.subheader("Overall Statistics")
# st.write(f"Total capacity of all canteens: {total_capacity}")
# st.write(f"Total predicted crowd across all canteens: {int(total_predicted_crowd)}")

from flask import Flask, render_template, request
import pickle

app = Flask(__name__)

canteen_capacities = {
    "Canteen 1": 120,
    "Canteen 2": 50,
    "Canteen 3": 300,
}

time_slots = {
    1: "12:00 PM - 12:10 PM",
    2: "12:10 PM - 12:20 PM",
    3: "12:20 PM - 12:30 PM",
    4: "12:30 PM - 12:40 PM",
    5: "12:40 PM - 12:50 PM",
    6: "12:50 PM - 1:00 PM",
    7: "1:00 PM - 1:10 PM",
    8: "1:10 PM - 1:20 PM",
    9: "1:20 PM - 1:30 PM",
    10: "1:30 PM - 1:40 PM",
    11: "1:40 PM - 1:50 PM",
    12: "1:50 PM - 2:00 PM",
}

@app.route("/", methods=["GET", "POST"])
def index():
    predictions = {}
    free_spaces = {}
    ranked_canteens = []
    total_capacity = sum(canteen_capacities.values())
    total_predicted_crowd = 0

    if request.method == "POST":
        input_day = request.form.get("day")
        selected_time_slot = request.form.get("time_slot")
        slot_no = list(time_slots.keys())[list(time_slots.values()).index(selected_time_slot)]

        for canteen_name in canteen_capacities.keys():
            model_file = f"{canteen_name.lower().replace(' ', '')}_model.pkl"
            with open(model_file, "rb") as f:
                saved_data = pickle.load(f)
                model, label_encoder = saved_data

            encoded_day = label_encoder.transform([input_day])[0]
            predicted_crowd = model.predict([[encoded_day, slot_no]])[0]
            predictions[canteen_name] = predicted_crowd

            capacity = canteen_capacities[canteen_name]
            free_space = capacity - predicted_crowd
            free_spaces[canteen_name] = free_space

        ranked_canteens = sorted(free_spaces.items(), key=lambda x: x[1], reverse=True)
        total_predicted_crowd = sum(predictions.values())

    return render_template(
        "index.html",
        time_slots=time_slots,
        predictions=predictions,
        free_spaces=free_spaces,
        ranked_canteens=ranked_canteens,
        total_capacity=total_capacity,
        total_predicted_crowd=total_predicted_crowd,
    )




from flask import Flask, render_template, request
import pickle

app = Flask(__name__)

canteen_capacities = {
    "Canteen 1": 120,
    "Canteen 2": 50,
    "Canteen 3": 300,
}

time_slots = {
    1: "12:00 PM - 12:10 PM",
    2: "12:10 PM - 12:20 PM",
    3: "12:20 PM - 12:30 PM",
    4: "12:30 PM - 12:40 PM",
    5: "12:40 PM - 12:50 PM",
    6: "12:50 PM - 1:00 PM",
    7: "1:00 PM - 1:10 PM",
    8: "1:10 PM - 1:20 PM",
    9: "1:20 PM - 1:30 PM",
    10: "1:30 PM - 1:40 PM",
    11: "1:40 PM - 1:50 PM",
    12: "1:50 PM - 2:00 PM",
}

@app.route("/", methods=["GET", "POST"])
def index():
    predictions = {}
    free_spaces = {}
    ranked_canteens = []
    total_capacity = sum(canteen_capacities.values())
    total_predicted_crowd = 0

    if request.method == "POST":
        input_day = request.form.get("day")
        selected_time_slot = request.form.get("time_slot")
        slot_no = list(time_slots.keys())[list(time_slots.values()).index(selected_time_slot)]

        for canteen_name in canteen_capacities.keys():
            model_file = f"{canteen_name.lower().replace(' ', '')}_model.pkl"
            with open(model_file, "rb") as f:
                saved_data = pickle.load(f)
                model, label_encoder = saved_data

            encoded_day = label_encoder.transform([input_day])[0]
            predicted_crowd = model.predict([[encoded_day, slot_no]])[0]
            predictions[canteen_name] = predicted_crowd

            capacity = canteen_capacities[canteen_name]
            free_space = capacity - predicted_crowd
            free_spaces[canteen_name] = free_space

        ranked_canteens = sorted(free_spaces.items(), key=lambda x: x[1], reverse=True)
        total_predicted_crowd = sum(predictions.values())

    return render_template(
        "index.html",
        time_slots=time_slots,
        predictions=predictions,
        free_spaces=free_spaces,
        ranked_canteens=ranked_canteens,
        total_capacity=total_capacity,
        total_predicted_crowd=total_predicted_crowd,
        enumerate=enumerate,  # Pass the enumerate function to the template
    )


if __name__ == "__main__":
    app.run(debug=True)
