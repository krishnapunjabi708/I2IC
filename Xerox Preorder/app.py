from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import json
import qrcode
from io import BytesIO
import base64
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"
ADMIN_PASSWORD = "admin123"

# Configure upload folder
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

from flask import send_from_directory


# Add to the top with other functions
def load_settings():
    try:
        with open("settings.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"accepting_orders": True}

def save_settings(settings):
    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=2)


# Route to serve uploaded files
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)    

# Load Xerox options from JSON
def load_xerox_options():
    with open("xerox_options.json", "r") as f:
        return json.load(f)

# Load orders from JSON
def load_orders():
    try:
        with open("orders.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save orders to JSON
def save_orders(orders):
    with open("orders.json", "w") as f:
        json.dump(orders, f, indent=2)

# @app.route("/")
# def home():
#     # Check for notifications in the session
#     notification = session.pop("notification", None)
#     xerox_options = load_xerox_options()
#     return render_template("xerox_menu.html", xerox_options=xerox_options, notification=notification)

@app.route("/")
def home():
    settings = load_settings()
    if not settings["accepting_orders"]:
        return render_template("orders_paused.html")  # Create this template

    notification = session.pop("notification", None)
    xerox_options = load_xerox_options()
    return render_template("xerox_menu.html", xerox_options=xerox_options, notification=notification)

@app.route("/toggle-orders", methods=["POST"])
def toggle_orders():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin"))
    
    settings = load_settings()
    settings["accepting_orders"] = not settings["accepting_orders"]
    save_settings(settings)
    return redirect(url_for("admin_dashboard"))

@app.route("/order", methods=["POST"])
def place_order():

    student_id = request.form.get("student_id")
    xerox_type = request.form.get("xerox_type")
    num_copies = int(request.form.get("num_copies", 1))

    settings = load_settings()
    if not settings["accepting_orders"]:
        flash("Orders are currently paused. Please try again later.")
        return redirect(url_for("home"))

    # Handle file upload
    if "document" not in request.files:
        return "No file uploaded!", 400

    file = request.files["document"]
    if file.filename == "":
        return "No file selected!", 400

    # Save the file
    filename = f"{student_id}_{datetime.now().timestamp()}_{file.filename}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    xerox_options = load_xerox_options()
    orders = load_orders()

    selected_option = next((option for option in xerox_options if option["type"] == xerox_type), None)

    if not selected_option:
        return "Invalid Xerox type selected!", 400

    price_per_copy = selected_option["price"]
    total_amount = price_per_copy * num_copies

    order = {
        "id": str(datetime.now().timestamp()),
        "student_id": student_id,
        "xerox_type": xerox_type,
        "num_copies": num_copies,
        "total": total_amount,
        "status": "pending_payment",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "document": filename  # Store the filename in the order
    }
    orders.append(order)
    save_orders(orders)

    return redirect(url_for("payment", amount=total_amount, order_id=order["id"]))

@app.route("/payment/<amount>/<order_id>")
def payment(amount, order_id):
    upi_id = "7083334646@ybl"
    upi_link = f"upi://pay?pa={upi_id}&pn=Xerox&mc=&tid=&tr={order_id}&tn=Xerox Order&am={amount}&cu=INR"
    
    qr = qrcode.make(upi_link)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render_template("payment.html", qr_base64=qr_base64, order_id=order_id, total=amount)

@app.route("/confirm-payment/<order_id>")
def confirm_payment(order_id):
    orders = load_orders()
    found = False  

    for order in orders:
        if order["id"] == order_id:
            order["status"] = "confirmed"
            found = True
            break  

    if found:
        save_orders(orders)
        return render_template("status.html", message="Payment successful! Your Xerox order is being processed.", order_id=order_id)
    else:
        return render_template("status.html", message="Order not found!", order_id=order_id), 404

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("admin.html", error="Invalid password")
    return render_template("admin.html", error=None)

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin"))
    
    orders = load_orders()
    settings = load_settings()
    return render_template("dashboard.html", orders=orders, settings=settings)
# @app.route("/mark-ready/<order_id>")
# def mark_ready(order_id):
#     orders = load_orders()
#     for order in orders:
#         if order["id"] == order_id:
#             order["status"] = "ready"
#             # Store a notification for the user
#             session[f"notification_{order['student_id']}"] = f"Your Xerox order (ID: {order_id}) is ready!"
#             break

#     save_orders(orders)
#     return redirect(url_for("admin_dashboard"))

@app.route("/mark-ready/<order_id>")
def mark_ready(order_id):
    orders = load_orders()
    for order in orders:
        if order["id"] == order_id:
            order["status"] = "ready"
            save_orders(orders)

            # Store notification in session
            session["notification"] = f"Your Xerox order (ID: {order_id}) is ready!"

            break

    return redirect(url_for("admin_dashboard"))

@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin"))

# @app.route("/check-status", methods=["GET", "POST"])
# def check_status():
#     if request.method == "POST":
#         student_id = request.form.get("student_id")

#         if not student_id:
#             return render_template("check_status.html", message="Please enter a valid Student ID.")

#         # Load orders and filter only the ones belonging to this student
#         orders = load_orders()
#         student_orders = [order for order in orders if order["student_id"] == student_id]

#         if not student_orders:
#             return render_template("check_status.html", message="No orders found for this Student ID!")

#         return render_template("check_status.html", orders=student_orders)

#     return render_template("check_status.html")

@app.route("/check-status", methods=["GET", "POST"])
def check_status():
    """Handles status checking based on Student ID"""
    if request.method == "GET":
        return render_template("check_status.html")  # Show the page with an input field

    student_id = request.form.get("student_id")

    if not student_id:
        return render_template("check_status.html", message="Please enter a valid Student ID.")

    # Load orders and filter by Student ID
    orders = load_orders()
    student_orders = [order for order in orders if order["student_id"] == student_id]

    if not student_orders:
        return render_template("check_status.html", message="No orders found for this Student ID!")

    # Sort orders by timestamp (newest first)
    student_orders.sort(key=lambda x: float(x["id"]), reverse=True)

    # Get the most recent order
    latest_order = student_orders[0] if student_orders else None

    # Get the last 3 previous orders (excluding the latest one)
    previous_orders = student_orders[1:4]  

    return render_template("check_status.html", latest_order=latest_order, previous_orders=previous_orders)



if __name__ == "__main__":
    app.run(debug=True)