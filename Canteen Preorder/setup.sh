#!/bin/bash

echo "Setting up the Canteen System..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask

# Create empty JSON files if not exist
touch menu.json orders.json
echo '[]' > orders.json

# Add sample menu
echo '[{"id": 1, "name": "Burger", "price": 50}, {"id": 2, "name": "Pizza", "price": 80}]' > menu.json

echo "Setup complete! Run the app using: python app.py"
