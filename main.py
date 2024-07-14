'''
import calendar
from datetime import datetime
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
from pymongo import MongoClient
import requests
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import threading

# MongoDB connection
client = MongoClient("mongodb+srv://Nexus_Coder:Ketan%402005@expensetracker.ddtuk3v.mongodb.net/?retryWrites=true&w=majority&appName=ExpenseTracker")
db = client["ExpenseTracker"]
collection = db["expenses"]
users_collection = db["users"]

# Flask endpoints base URL
flask_base_url = "http://localhost:5000"

def authenticate_user(action, username, password):
    url = f"{flask_base_url}/{action}"
    response = requests.post(url, json={"username": username, "password": password})
    return response

# Flask backend
app = Flask(__name__)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if users_collection.find_one({'username': username}):
        return jsonify({"error": "User already exists"}), 400

    hashed_password = generate_password_hash(password, method='sha256')
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

def main():
    incomes = ['Salary', 'Other Income']
    expenses = ["Rent", "Utilities", "Groceries", "Loan Instalments", "Petrol/Diesel", "Car", "Other Expenses", "Saving"]
    currency = "Rs"
    page_title = "Income and Expense Tracker"
    page_icon = ":money_with_wings:"
    layout = "centered"

    st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
    st.title(page_title + " " + page_icon)

    years = [datetime.today().year, datetime.today().year + 1]
    months = list(calendar.month_name[1:])

    # Custom CSS to change cursor to pointer for dropdown lists
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

    if 'delete_complete' not in st.session_state:
        st.session_state['delete_complete'] = False

    if not st.session_state['authenticated']:
        if st.session_state['signup_success']:
            st.session_state['signup_success'] = False
            st.success("Account Created Successfully. Please log in.")
            st.experimental_rerun()
        
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
                submitted = st.form_submit_button("Login")  # Correct placement of form submit button
                if submitted:
                    with st.spinner("Authenticating..."):
                        response = authenticate_user("login", username, password)
                    if response.status_code == 200:
                        st.success("Login successful")
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = username
                        st.experimental_rerun()  # Rerun the app to reflect authenticated state
                    else:
                        st.error("Invalid credentials")

        if auth_selected == "Signup":
            st.header("Signup")
            with st.form("signup_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Signup")  # Correct placement of form submit button
                if submitted:
                    with st.spinner("Creating account..."):
                        response = authenticate_user("signup", username, password)
                    if response.status_code == 201:
                        st.session_state['signup_success'] = True
                        st.experimental_rerun()  # Rerun the app to reset to login form
                    elif response.status_code == 400:
                        st.error("Account already exists")

    else:
        if st.session_state['delete_complete']:
            st.success("Data Deleted!")
            st.session_state['delete_complete'] = False
            st.experimental_rerun()  # Rerun the app to go back to data entry section
        else:
            selected = option_menu(
                menu_title=None,
                options=["Data Entry", "Data Visualization", "Update/Delete Data", "Logout"],
                icons=["pencil-fill", "bar-chart-fill", "gear-fill", "box-arrow-right"],
                orientation="horizontal",
            )

            def get_all_periods():
                periods = collection.distinct("period", {"username": st.session_state['username']})
                return periods

            if selected == "Data Entry":
                st.header(f"Data Entry in {currency}")
                col1, col2 = st.columns(2)
                selected_month = col1.selectbox("Select Month:", months, key="month", format_func=lambda x: x.title())
                selected_year = col2.selectbox("Select Year:", years, key="year")

                period = str(selected_year) + "_" + str(selected_month)

                # Check if data for the selected period already exists
                existing_data = collection.find_one({"period": period, "username": st.session_state['username']})
                if existing_data:
                    st.error(f"Data for {selected_month} {selected_year} already exists. Please choose a different period.")
                else:
                    with st.form("entry_form", clear_on_submit=True):
                        "---"
                        with st.expander("Income"):
                            for income in incomes:
                                value = st.text_input(f"{income}:", key=f"input_{income}", placeholder="Enter the value")
                                st.session_state[income] = int(value) if value else 0
                        with st.expander("Expenses"):
                            for expense in expenses:
                                value = st.text_input(f"{expense}:", key=f"input_{expense}", placeholder="Enter the value")
                                st.session_state[expense] = int(value) if value else 0
                        with st.expander("Comment"):
                            comment = st.text_area("", placeholder="Enter a comment here...")

                        "---"
                        submitted = st.form_submit_button("Save Data")  # Correct placement of form submit button
                        if submitted:
                            with st.spinner("Saving data..."):
                                incomes_data = {income: st.session_state[income] for income in incomes}
                                expenses_data = {expense: st.session_state[expense] for expense in expenses}

                                # Save data to MongoDB
                                entry = {
                                    "period": period,
                                    "incomes": incomes_data,
                                    "expenses": expenses_data,
                                    "comment": comment,
                                    "username": st.session_state['username']
                                }
                                collection.insert_one(entry)

                                st.write(f"Income: {incomes_data}")
                                st.write(f"Expenses: {expenses_data}")
                                st.success("Data Saved!")

            elif selected == "Data Visualization":
                st.header("Data Visualization")
                with st.form("saved_periods"):
                    # Get periods from database
                    with st.spinner("Loading periods..."):
                        periods = get_all_periods()
                    period = st.selectbox("Select Period:", periods)
                    submitted = st.form_submit_button("Plot Period")  # Correct placement of form submit button
                    if submitted:
                        with st.spinner("Loading data..."):
                            # Get data from database
                            data = collection.find_one({"period": period, "username": st.session_state['username']})
                        if data:
                            comment = data.get("comment", "")
                            incomes_data = data.get("incomes", {})
                            expenses_data = data.get("expenses", {})

                            total_income = sum(incomes_data.values())
                            total_expense = sum(expenses_data.values())
                            remaining_budget = total_income - total_expense
                            col1, col2, col3 = st.columns(3)
                            col1.subheader("Income")
                            col1.write(incomes_data)
                            col2.subheader("Expenses")
                            col2.write(expenses_data)
                            col3.subheader("Remaining Budget")
                            col3.write(f"{remaining_budget} {currency}")

                            label = ["Income"] + list(incomes_data.keys()) + ["Expense"] + list(expenses_data.keys())
                            source = [0] * (len(incomes_data.keys()) + 1) + [i + 1 for i in range(len(expenses_data.keys()))]
                            target = [i + 1 for i in range(len(incomes_data.keys()))] + [len(incomes_data.keys()) + 1 + i for i in
                                                                                         range(len(expenses_data.keys()))]
                            value = [total_income] + [incomes_data[k] for k in incomes_data.keys()] + [total_expense] + \
                                    [expenses_data[k] for k in expenses_data.keys()]
                            fig = go.Figure(data=[go.Sankey(
                                node=dict(
                                    pad=15,
                                    thickness=20,
                                    line=dict(color="black", width=0.5),
                                    label=label,
                                ),
                                link=dict(
                                    source=source,
                                    target=target,
                                    value=value
                                ))])
                            fig.update_layout(title_text="Income and Expense Flow", font_size=10)
                            st.plotly_chart(fig)

            elif selected == "Update/Delete Data":
                st.header("Update or Delete Data")
                periods = get_all_periods()
                period_to_modify = st.selectbox("Select Period to Modify:", periods)
                action = st.radio("Select Action:", ["Update", "Delete"])

                if action == "Update":
                    data = collection.find_one({"period": period_to_modify, "username": st.session_state['username']})
                    if data:
                        "---"
                        with st.spinner("Loading data..."):
                            st.empty()  # Clear previous content
                            with st.form("update_form"):  # Wrap update logic within the form
                                st.subheader(f"Existing Data for {period_to_modify}")
                                with st.expander("Current Income Data"):
                                    for income in incomes:
                                        st.text(f"{income}: {data['incomes'].get(income, 0)} {currency}")
                                with st.expander("Current Expense Data"):
                                    for expense in expenses:
                                        st.text(f"{expense}: {data['expenses'].get(expense, 0)} {currency}")
                                with st.expander("Comment"):
                                    st.text(f"{data.get('comment', '')}")

                                "---"
                                st.subheader("Update Data")
                                with st.expander("Income", expanded=False):
                                    update_incomes_data = {}
                                    for income in incomes:
                                        update_incomes_data[income] = st.number_input(f"{income}:", min_value=0, format="%i", step=10, key=f"update_{income}", placeholder="Enter the value", value=data["incomes"].get(income, 0))
                                with st.expander("Expenses", expanded=False):
                                    update_expenses_data = {}
                                    for expense in expenses:
                                        update_expenses_data[expense] = st.number_input(f"{expense}:", min_value=0, format="%i", step=10, key=f"update_{expense}", placeholder="Enter the value", value=data["expenses"].get(expense, 0))
                                with st.expander("Comment", expanded=False):
                                    update_comment = st.text_area("", placeholder="Enter a comment here...", value=data.get("comment", ""))

                                "---"
                                submitted = st.form_submit_button("Update Data")  # Correct placement of form submit button
                                if submitted:
                                    with st.spinner("Updating data..."):
                                        # Update data in MongoDB
                                        incomes_data = {income: update_incomes_data[income] for income in incomes}
                                        expenses_data = {expense: update_expenses_data[expense] for expense in expenses}
                                        collection.update_one(
                                            {"period": period_to_modify, "username": st.session_state['username']},
                                            {"$set": {"incomes": incomes_data, "expenses": expenses_data, "comment": update_comment}}
                                        )
                                        st.success("Data Updated!")
                                        st.experimental_rerun()  # Rerun the app to refresh

                elif action == "Delete":
                    st.warning(f"Are you sure you want to delete the data for {period_to_modify}? This action cannot be undone.")
                    confirmed = st.checkbox("Confirm Deletion")
                    if confirmed:
                        with st.spinner("Deleting data..."):
                            # Delete data from MongoDB
                            collection.delete_one({"period": period_to_modify, "username": st.session_state['username']})
                            st.success("Data Deleted!")
                            st.session_state['delete_complete'] = True
                            st.experimental_rerun()

            elif selected == "Logout":
                st.header("Logout")
                st.info("You have been logged out successfully.")
                st.session_state['authenticated'] = False

if __name__ == "__main__":
    threading.Thread(target=run_flask_app).start()
    main()
'''
import calendar
from datetime import datetime
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
from pymongo import MongoClient
import requests
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import threading
import pandas as pd
from googleapiclient import discovery
from google.oauth2 import service_account

# MongoDB connection
client = MongoClient("mongodb+srv://Nexus_Coder:Ketan%402005@expensetracker.ddtuk3v.mongodb.net/?retryWrites=true&w=majority&appName=ExpenseTracker")
db = client["ExpenseTracker"]
collection = db["expenses"]
fixed_expenses_collection = db["fixed_expenses"]
users_collection = db["users"]

# Flask endpoints base URL
flask_base_url = "http://localhost:5000"

# Google Cloud credentials and API setup
credentials = service_account.Credentials.from_service_account_file(
    'delta-student-429403-j2-4710a9d9ad67.json')  # Replace with the actual path to your JSON key file
service = discovery.build('ml', 'v1', credentials=credentials)

def authenticate_user(action, username, password):
    url = f"{flask_base_url}/{action}"
    response = requests.post(url, json={"username": username, "password": password})
    return response

# Flask backend
app = Flask(__name__)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if users_collection.find_one({'username': username}):
        return jsonify({"error": "User already exists"}), 400

    hashed_password = generate_password_hash(password, method='sha256')
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

# Function to fetch past expenses data
def fetch_past_expenses(username):
    cursor = collection.find({"username": username})
    data = []
    for doc in cursor:
        period = doc['period']
        for expense, value in doc['expenses'].items():
            data.append({'period': period, 'expense': expense, 'value': value})
    df = pd.DataFrame(data)
    return df

# Function to predict future expenses
def predict_future_expenses(df, next_period, fixed_expenses_data):
    # Group by period and expense, summing the values
    df_grouped = df.groupby(['period', 'expense']).sum().reset_index()

    # Placeholder for predictions - in practice, you'd use an ML model here
    predictions = {}
    for expense in df_grouped['expense'].unique():
        # For simplicity, predict the average of the past values if not a fixed expense
        if expense not in fixed_expenses_data:
            expense_data = df_grouped[df_grouped['expense'] == expense]
            predictions[expense] = expense_data['value'].mean()
        else:
            predictions[expense] = fixed_expenses_data[expense]

    return {next_period: predictions}

# Function to get fixed expenses for a user
def get_fixed_expenses(username):
    fixed_expenses = fixed_expenses_collection.find_one({"username": username})
    return fixed_expenses.get("expenses", {}) if fixed_expenses else {}

# Function to save fixed expenses for a user
def save_fixed_expenses(username, fixed_expenses):
    fixed_expenses_collection.update_one(
        {"username": username},
        {"$set": {"expenses": fixed_expenses}},
        upsert=True
    )

def main():
    incomes = ['Salary', 'Other Income']
    expenses = ["Rent", "Utilities", "Groceries", "Loan Instalments", "Petrol/Diesel", "Car", "Other Expenses", "Saving"]
    fixed_expenses = ["Rent", "Loan Instalments"]
    currency = "Rs"
    page_title = "Income and Expense Tracker"
    page_icon = ":money_with_wings:"
    layout = "centered"

    st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
    st.title(page_title + " " + page_icon)

    years = [datetime.today().year, datetime.today().year + 1]
    months = list(calendar.month_name[1:])

    # Custom CSS to change cursor to pointer for dropdown lists
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

    if 'delete_complete' not in st.session_state:
        st.session_state['delete_complete'] = False

    if not st.session_state['authenticated']:
        if st.session_state['signup_success']:
            st.session_state['signup_success'] = False
            st.success("Account Created Successfully. Please log in.")
            st.experimental_rerun()
        
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
                submitted = st.form_submit_button("Login")  # Correct placement of form submit button
                if submitted:
                    with st.spinner("Authenticating..."):
                        response = authenticate_user("login", username, password)
                    if response.status_code == 200:
                        st.success("Login successful")
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = username
                        st.experimental_rerun()  # Rerun the app to reflect authenticated state
                    else:
                        st.error("Invalid credentials")

        if auth_selected == "Signup":
            st.header("Signup")
            with st.form("signup_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Signup")  # Correct placement of form submit button
                if submitted:
                    with st.spinner("Creating account..."):
                        response = authenticate_user("signup", username, password)
                    if response.status_code == 201:
                        st.session_state['signup_success'] = True
                        st.experimental_rerun()  # Rerun the app to reset to login form
                    elif response.status_code == 400:
                        st.error("Account already exists")

    else:
        if st.session_state['delete_complete']:
            st.success("Data Deleted!")
            st.session_state['delete_complete'] = False
            st.experimental_rerun()  # Rerun the app to go back to data entry section
        else:
            selected = option_menu(
                menu_title=None,
                options=["Data Entry", "Data Visualization", "Update/Delete Data", "Manage Fixed Expenses", "Predict Expenditures", "Logout"],
                icons=["pencil-fill", "bar-chart-fill", "gear-fill", "gear-fill", "activity", "box-arrow-right"],
                orientation="horizontal",
            )

            def get_all_periods():
                periods = collection.distinct("period", {"username": st.session_state['username']})
                return periods

            if selected == "Data Entry":
                st.header(f"Data Entry in {currency}")
                col1, col2 = st.columns(2)
                selected_month = col1.selectbox("Select Month:", months, key="month", format_func=lambda x: x.title())
                selected_year = col2.selectbox("Select Year:", years, key="year")

                period = str(selected_year) + "_" + str(selected_month)

                # Check if data for the selected period already exists
                existing_data = collection.find_one({"period": period, "username": st.session_state['username']})
                if existing_data:
                    st.error(f"Data for {selected_month} {selected_year} already exists. Please choose a different period.")
                else:
                    fixed_expenses_data = get_fixed_expenses(st.session_state['username'])
                    with st.form("entry_form", clear_on_submit=True):
                        "---"
                        with st.expander("Income"):
                            for income in incomes:
                                value = st.text_input(f"{income}:", key=f"input_{income}", placeholder="Enter the value")
                                st.session_state[income] = int(value) if value else 0
                        with st.expander("Expenses"):
                            for expense in expenses:
                                if expense in fixed_expenses_data:
                                    st.text_input(f"{expense} (Fixed)", value=fixed_expenses_data[expense], key=f"fixed_{expense}", disabled=True)
                                    st.markdown(f"<small>This is a fixed expenditure. You can edit it from the fixed expenditure section.</small>", unsafe_allow_html=True)
                                else:
                                    value = st.text_input(f"{expense}:", key=f"input_{expense}", placeholder="Enter the value")
                                    st.session_state[expense] = int(value) if value else 0
                        with st.expander("Comment"):
                            comment = st.text_area("", placeholder="Enter a comment here...")

                        "---"
                        submitted = st.form_submit_button("Save Data")  # Correct placement of form submit button
                        if submitted:
                            with st.spinner("Saving data..."):
                                incomes_data = {income: st.session_state[income] for income in incomes}
                                expenses_data = {expense: st.session_state[expense] for expense in expenses if expense not in fixed_expenses_data}

                                # Save data to MongoDB
                                entry = {
                                    "period": period,
                                    "incomes": incomes_data,
                                    "expenses": {**expenses_data, **fixed_expenses_data},
                                    "comment": comment,
                                    "username": st.session_state['username']
                                }
                                collection.insert_one(entry)
                                save_fixed_expenses(st.session_state['username'], fixed_expenses_data)

                                st.write(f"Income: {incomes_data}")
                                st.write(f"Expenses: {expenses_data}")
                                st.success("Data Saved!")

            elif selected == "Data Visualization":
                st.header("Data Visualization")
                with st.form("saved_periods"):
                    # Get periods from database
                    with st.spinner("Loading periods..."):
                        periods = get_all_periods()
                    period = st.selectbox("Select Period:", periods)
                    submitted = st.form_submit_button("Plot Period")  # Correct placement of form submit button
                    if submitted:
                        with st.spinner("Loading data..."):
                            # Get data from database
                            data = collection.find_one({"period": period, "username": st.session_state['username']})
                        if data:
                            comment = data.get("comment", "")
                            incomes_data = data.get("incomes", {})
                            expenses_data = data.get("expenses", {})

                            total_income = sum(incomes_data.values())
                            total_expense = sum(expenses_data.values())
                            remaining_budget = total_income - total_expense
                            col1, col2, col3 = st.columns(3)
                            col1.subheader("Income")
                            col1.write(incomes_data)
                            col2.subheader("Expenses")
                            col2.write(expenses_data)
                            col3.subheader("Remaining Budget")
                            col3.write(f"{remaining_budget} {currency}")

                            label = ["Income"] + list(incomes_data.keys()) + ["Expense"] + list(expenses_data.keys())
                            source = [0] * (len(incomes_data.keys()) + 1) + [i + 1 for i in range(len(expenses_data.keys()))]
                            target = [i + 1 for i in range(len(incomes_data.keys()))] + [len(incomes_data.keys()) + 1 + i for i in
                                                                                         range(len(expenses_data.keys()))]
                            value = [total_income] + [incomes_data[k] for k in incomes_data.keys()] + [total_expense] + \
                                    [expenses_data[k] for k in expenses_data.keys()]
                            fig = go.Figure(data=[go.Sankey(
                                node=dict(
                                    pad=15,
                                    thickness=20,
                                    line=dict(color="black", width=0.5),
                                    label=label,
                                ),
                                link=dict(
                                    source=source,
                                    target=target,
                                    value=value
                                ))])
                            fig.update_layout(title_text="Income and Expense Flow", font_size=10)
                            st.plotly_chart(fig)

            elif selected == "Update/Delete Data":
                st.header("Update or Delete Data")
                periods = get_all_periods()
                period_to_modify = st.selectbox("Select Period to Modify:", periods)
                action = st.radio("Select Action:", ["Update", "Delete"])

                if action == "Update":
                    data = collection.find_one({"period": period_to_modify, "username": st.session_state['username']})
                    if data:
                        "---"
                        with st.spinner("Loading data..."):
                            st.empty()  # Clear previous content
                            with st.form("update_form"):  # Wrap update logic within the form
                                st.subheader(f"Existing Data for {period_to_modify}")
                                with st.expander("Current Income Data"):
                                    for income in incomes:
                                        st.text(f"{income}: {data['incomes'].get(income, 0)} {currency}")
                                with st.expander("Current Expense Data"):
                                    for expense in expenses:
                                        st.text(f"{expense}: {data['expenses'].get(expense, 0)} {currency}")
                                with st.expander("Comment"):
                                    st.text(f"{data.get('comment', '')}")

                                "---"
                                st.subheader("Update Data")
                                with st.expander("Income", expanded=False):
                                    update_incomes_data = {}
                                    for income in incomes:
                                        update_incomes_data[income] = st.number_input(f"{income}:", min_value=0, format="%i", step=10, key=f"update_{income}", placeholder="Enter the value", value=data["incomes"].get(income, 0))
                                with st.expander("Expenses", expanded=False):
                                    update_expenses_data = {}
                                    for expense in expenses:
                                        update_expenses_data[expense] = st.number_input(f"{expense}:", min_value=0, format="%i", step=10, key=f"update_{expense}", placeholder="Enter the value", value=data["expenses"].get(expense, 0))
                                with st.expander("Comment", expanded=False):
                                    update_comment = st.text_area("", placeholder="Enter a comment here...", value=data.get("comment", ""))

                                "---"
                                submitted = st.form_submit_button("Update Data")  # Correct placement of form submit button
                                if submitted:
                                    with st.spinner("Updating data..."):
                                        # Update data in MongoDB
                                        incomes_data = {income: update_incomes_data[income] for income in incomes}
                                        expenses_data = {expense: update_expenses_data[expense] for expense in expenses}
                                        collection.update_one(
                                            {"period": period_to_modify, "username": st.session_state['username']},
                                            {"$set": {"incomes": incomes_data, "expenses": expenses_data, "comment": update_comment}}
                                        )
                                        st.success("Data Updated!")
                                        st.experimental_rerun()  # Rerun the app to refresh

                elif action == "Delete":
                    st.warning(f"Are you sure you want to delete the data for {period_to_modify}? This action cannot be undone.")
                    confirmed = st.checkbox("Confirm Deletion")
                    if confirmed:
                        with st.spinner("Deleting data..."):
                            # Delete data from MongoDB
                            collection.delete_one({"period": period_to_modify, "username": st.session_state['username']})
                            st.success("Data Deleted!")
                            st.session_state['delete_complete'] = True
                            st.experimental_rerun()

            elif selected == "Manage Fixed Expenses":
                st.header("Manage Fixed Expenses")
                fixed_expenses_data = get_fixed_expenses(st.session_state['username'])
                with st.form("fixed_expenses_form"):
                    st.write("Fixed Expenses:")
                    for expense in fixed_expenses:
                        current_value = fixed_expenses_data.get(expense, "")
                        new_value = st.text_input(f"{expense}:", value=current_value, key=f"fixed_{expense}")
                        if new_value:
                            fixed_expenses_data[expense] = new_value
                        elif expense in fixed_expenses_data:
                            del fixed_expenses_data[expense]

                    submitted = st.form_submit_button("Save Fixed Expenses")
                    if submitted:
                        with st.spinner("Saving fixed expenses..."):
                            save_fixed_expenses(st.session_state['username'], fixed_expenses_data)
                            st.success("Fixed expenses updated successfully.")
                            st.experimental_rerun()

            elif selected == "Predict Expenditures":
                st.header("Predict Future Expenditures")
                with st.spinner("Fetching past data..."):
                    df = fetch_past_expenses(st.session_state['username'])
                fixed_expenses_data = get_fixed_expenses(st.session_state['username'])

                if not df.empty:
                    selected_month = st.selectbox("Select Month for Prediction:", months, key="predict_month", format_func=lambda x: x.title())
                    selected_year = st.selectbox("Select Year for Prediction:", years, key="predict_year")

                    next_period = f"{selected_year}_{selected_month}"

                    with st.spinner("Predicting future expenditures..."):
                        predictions = predict_future_expenses(df, next_period, fixed_expenses_data)

                    if next_period in predictions:
                        st.subheader(f"Predicted Expenditures for {selected_month} {selected_year}")
                        predicted_expenses = predictions[next_period]
                        for expense, value in predicted_expenses.items():
                            st.write(f"{expense}: {float(value):.2f} {currency}")
                    else:
                        st.error("Could not generate predictions.")
                else:
                    st.error("No past data available to analyze.")

            elif selected == "Logout":
                st.header("Logout")
                st.info("You have been logged out successfully.")
                st.session_state['authenticated'] = False

if __name__ == "__main__":
    threading.Thread(target=run_flask_app).start()
    main()

