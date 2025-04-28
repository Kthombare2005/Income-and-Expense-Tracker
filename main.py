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
    incomes = ['Salary', 'Other Income']
    expenses = ["Rent", "Utilities", "Groceries", "Loan Instalments", "Petrol/Diesel", "Car", "Other Expenses"]
    currency = "₹"
    page_title = "Income and Expense Tracker"
    page_icon = ":money_with_wings:"
    layout = "centered"

    st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
    st.title(page_title + " " + page_icon)

    years = [datetime.today().year, datetime.today().year + 1]
    months = list(calendar.month_name[1:])

    st.markdown("""
        <style>
            .pointer:hover {
                cursor: pointer;
            }
        </style>
    """, unsafe_allow_html=True)

    hide_st_style = """
                    <style>
                    #MainMenu {visibility:hidden;}
                    footer {visibility: hidden;}
                    header {visibility: hidden;}
                    </style>
                    """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if 'signup_success' not in st.session_state:
        st.session_state['signup_success'] = False

    if not st.session_state['authenticated']:
        if st.session_state['signup_success']:
            st.session_state['signup_success'] = False
            st.success("Account Created Successfully. Please log in.")
            st.rerun()
        
        auth_selected = option_menu(
            menu_title=None,
            options=["Login", "Signup"],
            icons=["key", "person-plus"],
            orientation="horizontal",
        )

        if auth_selected == "Login":
            st.header("Login")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")
                if submitted:
                    with st.spinner("Authenticating..."):
                        response = authenticate_user("login", username, password)
                    if response.status_code == 200:
                        st.success("Login successful")
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = username
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

        if auth_selected == "Signup":
            st.header("Signup")
            with st.form("signup_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Signup")
                if submitted:
                    with st.spinner("Creating account..."):
                        response = authenticate_user("signup", username, password)
                    if response.status_code == 201:
                        st.session_state['signup_success'] = True
                        st.rerun()
                    elif response.status_code == 400:
                        st.error("Account already exists")

    else:
        selected = option_menu(
            menu_title=None,
            options=["Data Entry", "Manage Fixed Income/Expenses", "Data Visualization", "Predict Future Patterns", "Logout"],
            icons=["pencil-fill", "file-earmark-text", "bar-chart-fill", "graph-up-arrow", "box-arrow-right"],
            orientation="horizontal",
            styles={
                "nav-link": {"font-size": "14px", "padding": "12px"},
                "container": {"padding": "0!important", "margin": "0!important"}
            },
        )

        if selected == "Manage Fixed Income/Expenses":
            st.header("Manage Fixed Income and Expenses")
            st.info("You can add, update, or remove fixed incomes or expenses. These values will be automatically populated when entering data.")

            col1, col2 = st.columns(2)
            value_type = col1.selectbox("Select Type:", ["Income", "Expense"], key="value_type_selection")
            item_name = col2.text_input(f"Enter {value_type} Name:", key="item_name_input")

            fixed_incomes, fixed_expenses = get_fixed_values(st.session_state['username'])

            with st.form("fixed_value_form"):
                st.subheader(f"Set Fixed {value_type} Value")
                value = st.text_input(f"{item_name} ({currency}):", value="", placeholder="Enter the value")
                save_button = st.form_submit_button("Save Fixed Value")
                if save_button:
                    try:
                        value = int(value)
                        save_fixed_value(st.session_state['username'], value_type, item_name, value)
                        st.success(f"{value_type} '{item_name}' set as fixed with value {currency}{value}!")
                        st.rerun()
                    except ValueError:
                        st.error("Please enter a valid integer.")

        elif selected == "Data Entry":
            st.header(f"Data Entry in {currency}")
            col1, col2 = st.columns(2)
            selected_month = col1.selectbox("Select Month:", months, key="month")
            selected_year = col2.selectbox("Select Year:", years, key="year")

            period = f"{selected_year}_{selected_month}"

            existing_data = collection.find_one({"period": period, "username": st.session_state['username']})
            if existing_data:
                st.error(f"Data for {selected_month} {selected_year} already exists. Please choose a different period.")
            else:
                with st.form("entry_form"):
                    "---"
                    income_data = {}
                    expense_data = {}
                    with st.expander("Income"):
                        for income in incomes:
                            field_value = st.text_input(f"{income} ({currency}):", key=f"input_{income}")
                            if field_value:
                                income_data[income] = int(field_value)

                    with st.expander("Expenses"):
                        for expense in expenses:
                            field_value = st.text_input(f"{expense} ({currency}):", key=f"input_{expense}")
                            if field_value:
                                expense_data[expense] = int(field_value)

                    "---"
                    if st.form_submit_button("Save Data"):
                        total_income = sum(income_data.values())
                        total_expenses = sum(expense_data.values())
                        savings = total_income - total_expenses

                        entry = {
                            "period": period,
                            "incomes": income_data,
                            "expenses": expense_data,
                            "savings": savings,
                            "username": st.session_state['username']
                        }
                        collection.insert_one(entry)
                        st.success("Data Saved Successfully!")

        elif selected == "Data Visualization":
            st.header("Data Visualization")
            periods = get_all_periods()
            selected_period = st.selectbox("Select Period:", periods)
            if selected_period:
                data = collection.find_one({"period": selected_period, "username": st.session_state['username']})
                if data:
                    incomes_data = data.get("incomes", {})
                    expenses_data = data.get("expenses", {})
                    savings = data.get("savings", 0)

                    st.write(f"Incomes: {incomes_data}")
                    st.write(f"Expenses: {expenses_data}")
                    st.write(f"Savings: ₹{savings}")

                    pie_chart = px.pie(
                        names=["Income", "Expenses"],
                        values=[sum(incomes_data.values()), sum(expenses_data.values())],
                        title="Income vs Expenses"
                    )
                    st.plotly_chart(pie_chart)

        elif selected == "Predict Future Patterns":
            st.header("Predict Future Income and Expenses")
            col1, col2 = st.columns(2)
            selected_month = col1.selectbox("Select Month for Prediction:", months, key="predict_month")
            selected_year = col2.selectbox("Select Year for Prediction:", years, key="predict_year")

            predict_period = f"{selected_year}_{selected_month}"

            if st.button("Predict"):
                prediction = predict_future_income_expense(predict_period)
                st.success(prediction)

        elif selected == "Logout":
            st.session_state.clear()
            st.success("Logged out successfully")
            st.rerun()

if __name__ == "__main__":
    threading.Thread(target=run_flask_app).start()
    main()
