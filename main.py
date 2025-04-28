import calendar
import os
import threading
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from flask import Flask, request, jsonify
from pymongo import MongoClient
from streamlit_option_menu import option_menu
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai

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
    app.run(debug=False, port=5000, use_reloader=False)

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
    st.title("Income and Expense Tracker 💸")
    st.sidebar.title("Navigation")

    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if not st.session_state['authenticated']:
        auth_option = st.sidebar.selectbox("Select", ["Login", "Signup"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if auth_option == "Login":
            if st.button("Login"):
                response = authenticate_user("login", username, password)
                if response.status_code == 200:
                    st.success("Login successful")
                    st.session_state['authenticated'] = True
                    st.session_state['username'] = username
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        if auth_option == "Signup":
            if st.button("Signup"):
                response = authenticate_user("signup", username, password)
                if response.status_code == 201:
                    st.success("Signup successful. Please login now.")
                else:
                    st.error("Signup failed. Try again.")

    else:
        menu = option_menu(
            menu_title=None,
            options=["Data Entry", "Visualize Data", "Predict Future", "Logout"],
            icons=["pencil-fill", "bar-chart-line", "lightning-fill", "box-arrow-right"],
            orientation="horizontal",
        )

        if menu == "Data Entry":
            months = list(calendar.month_name[1:])
            years = [datetime.today().year, datetime.today().year + 1]
            month = st.selectbox("Select Month", months)
            year = st.selectbox("Select Year", years)
            period = f"{year}_{month}"

            income = st.number_input("Enter total Income (₹)", min_value=0)
            expense = st.number_input("Enter total Expenses (₹)", min_value=0)

            if st.button("Save Entry"):
                collection.insert_one({
                    "period": period,
                    "incomes": {"Total Income": income},
                    "expenses": {"Total Expenses": expense},
                    "username": st.session_state['username']
                })
                st.success(f"Data for {period} saved successfully!")

        elif menu == "Visualize Data":
            periods = get_all_periods()
            if periods:
                selected_period = st.selectbox("Select Period", periods)
                data = collection.find_one({"period": selected_period, "username": st.session_state['username']})

                if data:
                    income = data.get("incomes", {})
                    expense = data.get("expenses", {})

                    st.subheader("Income and Expenses Overview")
                    fig = px.pie(names=["Income", "Expenses"], values=[sum(income.values()), sum(expense.values())])
                    st.plotly_chart(fig)

        elif menu == "Predict Future":
            months = list(calendar.month_name[1:])
            years = [datetime.today().year, datetime.today().year + 1]
            predict_month = st.selectbox("Select Month for Prediction", months)
            predict_year = st.selectbox("Select Year for Prediction", years)
            predict_period = f"{predict_year}_{predict_month}"

            if st.button("Predict"):
                result = predict_future_income_expense(predict_period)
                st.subheader("Predicted Summary")
                st.write(result)

        elif menu == "Logout":
            st.session_state.clear()
            st.success("Logged out successfully.")
            st.rerun()

if __name__ == "__main__":
    threading.Thread(target=run_flask_app).start()
    os.system("streamlit run main.py")
