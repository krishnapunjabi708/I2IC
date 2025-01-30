import streamlit as st
import mysql.connector

# Database setup
def init_db():
    conn = mysql.connector.connect(host="localhost", user="root", password="Krishna708@", database="canteen")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            item VARCHAR(255),
            quantity INT,
            status VARCHAR(50) DEFAULT 'Pending'
        )
    """)
    conn.commit()
    conn.close()

# Function to add order
def add_order(name, item, quantity):
    conn = mysql.connector.connect(host="localhost", user="root", password="", database="canteen")
    c = conn.cursor()
    c.execute("INSERT INTO orders (name, item, quantity) VALUES (%s, %s, %s)", (name, item, quantity))
    conn.commit()
    conn.close()

# Function to get all orders
def get_orders():
    conn = mysql.connector.connect(host="localhost", user="root", password="", database="canteen")
    c = conn.cursor()
    c.execute("SELECT * FROM orders")
    orders = c.fetchall()
    conn.close()
    return orders

# Initialize database
init_db()

# Streamlit UI
st.title("Canteen Preorder System")

menu = ["Pizza", "Burger", "Pasta", "Sandwich", "Coffee"]

st.subheader("Place Your Order")
name = st.text_input("Enter your name:")
item = st.selectbox("Select item:", menu)
quantity = st.number_input("Quantity:", min_value=1, step=1)

if st.button("Order Now"):
    if name and item and quantity:
        add_order(name, item, quantity)
        st.success(f"Order placed: {quantity}x {item} for {name}")
    else:
        st.error("Please enter all details")

st.subheader("View Orders")
orders = get_orders()
for order in orders:
    st.write(f"{order[1]} ordered {order[3]}x {order[2]} - Status: {order[4]}")
