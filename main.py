import calendar
from datetime import datetime
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import plotly.express as px
from pymongo import MongoClient
import google.generativeai as genai
import requests
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import threading
import pandas as pd

# MongoDB connection
client = MongoClient("mongodb+srv://Nexus_Coder:Ketan%402005@expensetracker.ddtuk3v.mongodb.net/?retryWrites=true&w=majority&appName=ExpenseTracker")
db = client["ExpenseTracker"]
collection = db["expenses"]
users_collection = db["users"]
fixed_values_collection = db["fixed_values"]

# Gemini AI setup
genai.configure(api_key="AIzaSyBXn83YAEyl6tjrMeMucHYsPiRmxQwgii4")

# Flask backend
app = Flask(__name__)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if users_collection.find_one({'username': username}):
        return jsonify({"error": "User already exists"}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    users_collection.insert_one({'username': username, 'password': hashed_password})
    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = users_collection.find_one({'username': username})
    if user and check_password_hash(user['password'], password):
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"error": "Invalid credentials"}), 401

def run_flask_app():
    app.run(debug=False, port=5000)

def authenticate_user(action, username, password):
    url = f"http://localhost:5000/{action}"
    response = requests.post(url, json={"username": username, "password": password})
    return response

def save_fixed_value(username, value_type, item_name, amount):
    fixed_values_collection.update_one(
        {"username": username},
        {"$set": {f"{value_type.lower()}s.{item_name}": amount}},
        upsert=True
    )

def delete_fixed_value(username, value_type, item_name):
    fixed_values_collection.update_one(
        {"username": username},
        {"$unset": {f"{value_type.lower()}s.{item_name}": ""}}
    )

def get_fixed_values(username):
    fixed_values = fixed_values_collection.find_one({"username": username})
    if fixed_values:
        return fixed_values.get("incomes", {}), fixed_values.get("expenses", {})
    return {}, {}

def get_all_periods():
    periods = collection.distinct("period", {"username": st.session_state['username']})
    return periods

def predict_future_income_expense(period):
    prompt = f"Predict the income and expense patterns for the period {period} for a typical individual in India. Provide the predictions in INR."
    model = genai.GenerativeModel('gemini-1.0-pro-latest')
    response = model.generate_content(prompt)
    return response.text

def main():
    # your Streamlit app main logic here
    pass

if __name__ == "__main__":
    threading.Thread(target=run_flask_app).start()
    import os
    os.system('streamlit run main.py')

