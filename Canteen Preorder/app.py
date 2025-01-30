# from flask import Flask, render_template, request, redirect, url_for, session, jsonify
# import json
# import qrcode
# from io import BytesIO
# import base64
# from datetime import datetime

# app = Flask(__name__)
# app.secret_key = "supersecretkey"
# ADMIN_PASSWORD = "admin123"

# # Load menu from JSON
# def load_menu():
#     with open("menu.json", "r") as f:
#         return json.load(f)

# # Load orders from JSON
# def load_orders():
#     try:
#         with open("orders.json", "r") as f:
#             return json.load(f)
#     except FileNotFoundError:
#         return []

# # Save orders to JSON
# def save_orders(orders):
#     with open("orders.json", "w") as f:
#         json.dump(orders, f, indent=2)

# @app.route("/")
# def home():
#     menu = load_menu()
#     return render_template("menu.html", menu=menu)

# @app.route("/order", methods=["POST"])
# def place_order():
#     student_id = request.form.get("student_id")
#     item_ids = request.form.getlist("item_ids")  # Get a list of selected items
#     quantity = int(request.form.get("quantity", 1))

#     menu = load_menu()
#     orders = load_orders()

#     order_items = []
#     total_amount = 0

#     for item_id in item_ids:
#         item_id = int(item_id)
#         item = None
#         # Loop through all categories to find the item
#         for category, items in menu.items():
#             item = next((i for i in items if i["id"] == item_id), None)
#             if item:
#                 break

#         if item:
#             order_items.append({
#                 "name": item["name"],
#                 "price": item["price"],
#                 "quantity": quantity,
#                 "total": item["price"] * quantity
#             })
#             total_amount += item["price"] * quantity

#     if order_items:
#         order = {
#             "id": str(datetime.now().timestamp()),
#             "student_id": student_id,
#             "items": order_items,
#             "total": total_amount,
#             "status": "pending_payment",
#             "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         }
#         orders.append(order)
#         save_orders(orders)
#         return redirect(url_for("payment", amount=total_amount, order_id=order["id"]))

#     return "No items selected!", 400

# @app.route("/payment/<amount>/<order_id>")
# def payment(amount, order_id):
#     upi_id = "7083334646@ybl"  # Your UPI ID
#     upi_link = f"upi://pay?pa={upi_id}&pn=Canteen&mc=&tid=&tr={order_id}&tn=Canteen Order&am={amount}&cu=INR"
    
#     qr = qrcode.make(upi_link)
#     buffer = BytesIO()
#     qr.save(buffer, format="PNG")
#     qr_base64 = base64.b64encode(buffer.getvalue()).decode()

#     return render_template("payment.html", qr_base64=qr_base64, order_id=order_id, total=amount)

# @app.route("/confirm-payment/<order_id>")
# def confirm_payment(order_id):
#     orders = load_orders()
#     found = False  

#     for order in orders:
#         if order["id"] == order_id:
#             order["status"] = "confirmed"
#             found = True
#             break  

#     if found:
#         save_orders(orders)
#         return render_template("status.html", message="Payment successful! Your order is being prepared.", order_id=order_id)
#     else:
#         return render_template("status.html", message="Order not found!", order_id=order_id), 404

# @app.route("/admin", methods=["GET", "POST"])
# def admin():
#     if request.method == "POST":
#         password = request.form.get("password")
#         if password == ADMIN_PASSWORD:
#             session["admin_logged_in"] = True
#             return redirect(url_for("admin_dashboard"))
#         else:
#             return render_template("admin.html", error="Invalid password")
#     return render_template("admin.html", error=None)

# @app.route("/admin/dashboard")
# def admin_dashboard():
#     if not session.get("admin_logged_in"):
#         return redirect(url_for("admin"))
    
#     orders = load_orders()
#     return render_template("dashboard.html", orders=orders)

# @app.route("/mark-ready/<order_id>")
# def mark_ready(order_id):
#     orders = load_orders()
#     updated_orders = [order for order in orders if order["id"] != order_id]  # Remove order

#     if len(updated_orders) < len(orders):  # Check if order was removed
#         save_orders(updated_orders)
#         return redirect(url_for("admin_dashboard"))
#     else:
#         return "Order not found!", 404

# @app.route("/logout")
# def logout():
#     session.pop("admin_logged_in", None)
#     return redirect(url_for("admin"))

# if __name__ == "__main__":
#     app.run(debug=True)



from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import qrcode
from io import BytesIO
import base64
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"
ADMIN_PASSWORD = "admin123"

# Load menu from JSON
def load_menu():
    with open("menu.json", "r") as f:
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

@app.route("/")
def home():
    menu = load_menu()
    return render_template("menu.html", menu=menu)

@app.route("/order", methods=["POST"])
def place_order():
    student_id = request.form.get("student_id")
    item_ids = request.form.getlist("item_ids")  # Get a list of selected items
    quantities = request.form.getlist("quantities")  # Get a list of quantities

    menu = load_menu()
    orders = load_orders()

    order_items = []
    total_amount = 0

    for item_id, quantity in zip(item_ids, quantities):
        item_id = int(item_id)
        quantity = int(quantity)
        item = None
        # Loop through all categories to find the item
        for category, items in menu.items():
            item = next((i for i in items if i["id"] == item_id), None)
            if item:
                break

        if item:
            order_items.append({
                "name": item["name"],
                "price": item["price"],
                "quantity": quantity,
                "total": item["price"] * quantity
            })
            total_amount += item["price"] * quantity

    if order_items:
        order = {
            "id": str(datetime.now().timestamp()),
            "student_id": student_id,
            "items": order_items,
            "total": total_amount,
            "status": "pending_payment",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders.append(order)
        save_orders(orders)
        return redirect(url_for("menu"))

    return "No items selected!", 400

@app.route("/menu")
def menu():
    menu_items = load_menu()
    return render_template("menu.html", menu=menu_items)

@app.route("/process_payment", methods=["POST"])
def process_payment():
    data = request.json
    order_id = data.get("order_id")
    
    orders = load_orders()
    for order in orders:
        if order["id"] == order_id:
            order["status"] = "completed"
            save_orders(orders)
            return jsonify({"message": "Payment successful", "redirect": url_for("menu")}), 200
    
    return jsonify({"error": "Order not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
