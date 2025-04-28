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
<<<<<<< HEAD
import streamlit as st
=======
>>>>>>> f6160937040bd5f32fc082c8c2c39ba8d2cd80d2

# MongoDB connection
client = MongoClient("mongodb+srv://Nexus_Coder:Ketan%402005@expensetracker.ddtuk3v.mongodb.net/?retryWrites=true&w=majority&appName=ExpenseTracker")
db = client["ExpenseTracker"]
collection = db["expenses"]
users_collection = db["users"]
fixed_values_collection = db["fixed_values"]

# Gemini AI setup
genai.configure(api_key="AIzaSyBXn83YAEyl6tjrMeMucHYsPiRmxQwgii4")

def authenticate_user(action, username, password):
    url = f"http://localhost:5000/{action}"
    response = requests.post(url, json={"username": username, "password": password})
    return response

<<<<<<< HEAD
def predict_future_income_expense(period, username):
    """Function to predict future income and expense patterns using AI."""
    
    # Fetch the last 6 months of data
    past_six_months_data = list(collection.find({"username": username}).sort("period", -1).limit(6))
    
    if len(past_six_months_data) < 6:
        return None  # Not enough data for prediction
    
    # Calculate average income and expenses over the last 6 months
    total_income = 0
    total_expenses = 0
    for data in past_six_months_data:
        total_income += sum(data.get("incomes", {}).values())
        total_expenses += sum(data.get("expenses", {}).values())
    
    avg_income = total_income // 6
    avg_expenses = total_expenses // 6
    
    # Fetch fixed values
    fixed_incomes, fixed_expenses = get_fixed_values(username)
    
    # Construct the prompt for AI
    prompt = f"Based on the last 6 months, predict the income and expense patterns for the period {period} for a typical individual in India. The average income is {avg_income} INR, and the average expenses are {avg_expenses} INR. The fixed incomes are {fixed_incomes} and fixed expenses are {fixed_expenses}. Provide the predictions in INR."
    
=======
def predict_future_income_expense(period):
    """Function to predict future income and expense patterns using AI."""
    prompt = f"Predict the income and expense patterns for the period {period} for a typical individual in India. Provide the predictions in INR."
>>>>>>> f6160937040bd5f32fc082c8c2c39ba8d2cd80d2
    model = genai.GenerativeModel('gemini-1.0-pro-latest')
    response = model.generate_content(prompt)
    return response.text

def save_fixed_value(username, value_type, item_name, amount):
    """Function to save a fixed income or expense value."""
    fixed_values_collection.update_one(
        {"username": username},
        {"$set": {f"{value_type.lower()}s.{item_name}": amount}},
        upsert=True
    )

def delete_fixed_value(username, value_type, item_name):
    """Function to delete a fixed income or expense value."""
    fixed_values_collection.update_one(
        {"username": username},
        {"$unset": {f"{value_type.lower()}s.{item_name}": ""}}
    )

def get_fixed_values(username):
    """Function to retrieve fixed income and expense values for the user."""
    fixed_values = fixed_values_collection.find_one({"username": username})
    if fixed_values:
        return fixed_values.get("incomes", {}), fixed_values.get("expenses", {})
    return {}, {}

def get_all_periods():
    """Function to retrieve all available periods."""
    periods = collection.distinct("period", {"username": st.session_state['username']})
    return periods

def get_custom_expenses_from_previous_period(username, current_period):
    """Retrieve custom expenses from the previous period."""
    previous_period_data = list(collection.find({"username": username}).sort("period", -1).limit(1))
    previous_period = previous_period_data[0] if len(previous_period_data) > 0 else None
    
    if previous_period and previous_period['period'] != current_period:
        return previous_period.get("custom_expenses", [])
    return []

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

    if 'delete_complete' not in st.session_state:
        st.session_state['delete_complete'] = False

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
<<<<<<< HEAD
                        st.rerun()
=======
                        st.experimental_rerun()
>>>>>>> f6160937040bd5f32fc082c8c2c39ba8d2cd80d2
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
<<<<<<< HEAD
                        st.rerun()
=======
                        st.experimental_rerun()
>>>>>>> f6160937040bd5f32fc082c8c2c39ba8d2cd80d2
                    elif response.status_code == 400:
                        st.error("Account already exists")

    else:
        if st.session_state['delete_complete']:
            st.success("Data Deleted!")
            st.session_state['delete_complete'] = False
<<<<<<< HEAD
            st.rerun()
=======
            st.experimental_rerun()
>>>>>>> f6160937040bd5f32fc082c8c2c39ba8d2cd80d2
        else:
            selected = option_menu(
                menu_title=None,
                options=["Data Entry", "Manage Fixed Income/Expenses", "Data Visualization", "Predict Future Patterns", "Update/Delete Data", "Logout"],
                icons=["pencil-fill", "file-earmark-text", "bar-chart-fill", "graph-up-arrow", "gear-fill", "box-arrow-right"],
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
                item_name = col2.selectbox(
                    f"Select {value_type} to Manage:", 
                    incomes if value_type == "Income" else expenses, 
                    key="item_name_selection"
                )

                fixed_incomes, fixed_expenses = get_fixed_values(st.session_state['username'])
                fixed_value = fixed_incomes.get(item_name, "") if value_type == "Income" else fixed_expenses.get(item_name, "")

                # Display current fixed values
                with st.expander("Current Fixed Values"):
                    st.write("**Fixed Incomes:**", fixed_incomes)
                    st.write("**Fixed Expenses:**", fixed_expenses)

                # Add or update fixed value
                with st.form("fixed_value_form"):
                    st.subheader(f"Set Fixed {value_type} Value for '{item_name}'")
                    value = st.text_input(f"{item_name} ({currency}):", value="", placeholder="Enter the value")
                    save_button = st.form_submit_button("Save Fixed Value")
                    if save_button:
                        try:
                            value = int(value)
                            save_fixed_value(st.session_state['username'], value_type, item_name, value)
                            st.success(f"{value_type} '{item_name}' set as fixed with value {currency}{value}!")
                        except ValueError:
                            st.error("Please enter a valid integer.")

                # Remove fixed value
                with st.form("remove_fixed_value_form"):
                    st.subheader(f"Remove Fixed {value_type} Value for '{item_name}'")
                    remove_button = st.form_submit_button("Remove Fixed Value")
                    if remove_button:
                        delete_fixed_value(st.session_state['username'], value_type, item_name)
                        st.success(f"{value_type} '{item_name}' removed!")

            if selected == "Data Entry":
                st.header(f"Data Entry in {currency}")
                col1, col2 = st.columns(2)
                selected_month = col1.selectbox("Select Month:", months, key="month", format_func=lambda x: x.title())
                selected_year = col2.selectbox("Select Year:", years, key="year")

                period = str(selected_year) + "_" + str(selected_month)

                existing_data = collection.find_one({"period": period, "username": st.session_state['username']})
                if existing_data:
                    st.error(f"Data for {selected_month} {selected_year} already exists. Please choose a different period.")
                else:
                    if 'custom_expenses' not in st.session_state:
                        st.session_state['custom_expenses'] = []

                    # Fetch custom expenses from the previous period
                    previous_custom_expenses = get_custom_expenses_from_previous_period(st.session_state['username'], period)

                    if previous_custom_expenses:
                        st.info("Custom expenses from the previous period detected.")
                        selected_expenses = st.multiselect("Which custom expenses do you want to consider this month?", 
                                                           [expense[0] for expense in previous_custom_expenses], 
                                                           default=[expense[0] for expense in previous_custom_expenses])
                        st.session_state['custom_expenses'] = [expense for expense in previous_custom_expenses if expense[0] in selected_expenses]

                    with st.form("entry_form", clear_on_submit=False):
                        "---"
                        income_data = {}
                        expense_data = {}
                        savings = None  # Initialize savings as None

                        # Check and store income fields
                        with st.expander("Income"):
                            fixed_incomes, fixed_expenses = get_fixed_values(st.session_state['username'])
                            for income in incomes:
                                value = fixed_incomes.get(income, "")
                                field_value = st.text_input(f"{income} ({currency}):", value=value, placeholder="Enter the value", key=f"input_{income}")
                                if field_value:
                                    income_data[income] = int(field_value)
                                    if income in fixed_incomes:
                                        st.caption(f"This is a fixed {income} value.")

                        # Check and store expense fields
                        with st.expander("Expenses"):
                            for expense in expenses:
                                value = fixed_expenses.get(expense, "")
                                field_value = st.text_input(f"{expense} ({currency}):", value=value, placeholder="Enter the value", key=f"input_{expense}")
                                if field_value:
                                    expense_data[expense] = int(field_value)
                                    if expense in fixed_expenses:
                                        st.caption(f"This is a fixed {expense} value.")

                            # Display custom expenses with other expenses in the form
                            for index, (name, amount) in enumerate(st.session_state['custom_expenses']):
                                value = st.text_input(f"{name} ({currency}):", value=amount, key=f"custom_expense_{index}")
                                if value:
                                    expense_data[name] = int(value)

                            # Button to add new custom expense
                            if st.form_submit_button("Add New Expense"):
                                st.session_state['show_custom_expense_entry'] = True

                            # Custom expense entry fields
                            if st.session_state.get('show_custom_expense_entry', False):
                                new_expense_name = st.text_input("Enter new expense name:")
                                new_expense_value = st.text_input("Enter amount:")
                                if st.form_submit_button("Submit Expense"):
                                    if new_expense_name and new_expense_value:
                                        try:
                                            st.session_state['custom_expenses'].append((new_expense_name, int(new_expense_value)))
                                            st.session_state['show_custom_expense_entry'] = False  # Hide the fields after adding
<<<<<<< HEAD
                                            st.rerun()  # Refresh the form to display the new custom expense
=======
                                            st.experimental_rerun()  # Refresh the form to display the new custom expense
>>>>>>> f6160937040bd5f32fc082c8c2c39ba8d2cd80d2
                                        except ValueError:
                                            st.error("Please enter a valid integer for the amount.")

                        "---"

                        # Submit button to save data and calculate savings
                        if st.form_submit_button("Save Data"):
                            total_income = sum(income_data.values())
                            total_expenses = sum(expense_data.values())
                            savings = total_income - total_expenses

                            # Save data including calculated savings
                            entry = {
                                "period": period,
                                "incomes": income_data,
                                "expenses": expense_data,
                                "savings": savings,
                                "custom_expenses": st.session_state['custom_expenses'],
                                "username": st.session_state['username']
                            }
                            collection.insert_one(entry)

                            # Display the calculated savings
                            st.write(f"Calculated Savings: {currency}{savings}")
                            st.success("Data Saved with Calculated Savings!")

            elif selected == "Data Visualization":
                st.header("Data Visualization")
                with st.form("saved_periods"):
                    with st.spinner("Loading periods..."):
                        periods = get_all_periods()
                    period = st.selectbox("Select Period:", periods)
                    submitted = st.form_submit_button("Plot Period")
                    if submitted:
                        with st.spinner("Loading data..."):
                            data = collection.find_one({"period": period, "username": st.session_state['username']})
                        if data:
                            comment = data.get("comment", "")
                            incomes_data = data.get("incomes", {})
                            expenses_data = data.get("expenses", {})
                            savings = data.get("savings", 0)

                            total_income = sum(incomes_data.values())
                            total_expense = sum(expenses_data.values())
                            remaining_budget = total_income - total_expense
                            
                            # Display Income, Expenses, and Savings
                            col1, col2, col3 = st.columns(3)
                            col1.subheader("Income")
                            col1.write({k: f"{currency}{v}" for k, v in incomes_data.items()})
                            col2.subheader("Expenses")
                            col2.write({k: f"{currency}{v}" for k, v in expenses_data.items()})
                            col3.subheader("Savings")
                            col3.write(f"{currency}{savings}")

                            # Income vs Expenses Pie Chart
                            st.subheader("Income vs Expenses Distribution")
                            fig_pie = px.pie(
                                names=["Income", "Expenses"],
                                values=[total_income, total_expense],
                                hole=0.3,
                                title="Income vs Expenses"
                            )
                            st.plotly_chart(fig_pie)

                            # Detailed Income and Expenses Bar Chart
                            st.subheader("Detailed Income and Expenses")
                            df = pd.DataFrame({
                                "Category": list(incomes_data.keys()) + list(expenses_data.keys()),
                                "Amount": list(incomes_data.values()) + list(expenses_data.values()),
                                "Type": ["Income"] * len(incomes_data) + ["Expense"] * len(expenses_data)
                            })
                            fig_bar = px.bar(
                                df, 
                                x="Category", 
                                y="Amount", 
                                color="Type", 
                                title="Income and Expenses Breakdown"
                            )
                            st.plotly_chart(fig_bar)

                            # Sankey Diagram for Income and Expenses Flow
                            st.subheader("Income and Expense Flow")
                            label = ["Income"] + list(incomes_data.keys()) + ["Expense"] + list(expenses_data.keys())
                            source = [0] * (len(incomes_data.keys()) + 1) + [i + 1 for i in range(len(expenses_data.keys()))]
<<<<<<< HEAD
                            target = [i + 1 for i in range(len(incomes_data.keys()))] + [len(incomes_data.keys()) + 1 + i for i in range(len(expenses_data.keys()))]
                            value = [total_income] + [incomes_data[k] for k in incomes_data.keys()] + [total_expense] + [expenses_data[k] for k in expenses_data.keys()]
                            fig_sankey = go.Figure(data=[go.Sankey(
=======
                            target = [i + 1 for i in range(len(incomes_data.keys()))] + [len(incomes_data.keys()) + 1 + i for i in
                                                                                         range(len(expenses_data.keys()))]
                            value = [total_income] + [incomes_data[k] for k in incomes_data.keys()] + [total_expense] + \
                                    [expenses_data[k] for k in expenses_data.keys()]
                            fig = go.Figure(data=[go.Sankey(
>>>>>>> f6160937040bd5f32fc082c8c2c39ba8d2cd80d2
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
                            fig_sankey.update_layout(title_text="Income and Expense Flow", font_size=10)
                            st.plotly_chart(fig_sankey)

            elif selected == "Predict Future Patterns":
                st.header("Predict Future Income and Expense Patterns")
                
                col1, col2 = st.columns(2)
                selected_month = col1.selectbox("Select Month for Prediction:", months, key="predict_month", format_func=lambda x: x.title())
                selected_year = col2.selectbox("Select Year for Prediction:", years, key="predict_year")

                predict_period = str(selected_year) + "_" + str(selected_month)

                prediction = predict_future_income_expense(period=predict_period, username=st.session_state['username'])

                if prediction is None:
                    st.error("Insufficient data to make a prediction. Please ensure you have at least 6 months of data.")
                else:
                    with st.spinner("Predicting future income and expense patterns..."):
                        st.write(prediction)
                        st.success("Prediction Complete!")

            elif selected == "Predict Future Patterns":
                st.header("Predict Future Income and Expense Patterns")
                
                col1, col2 = st.columns(2)
                selected_month = col1.selectbox("Select Month for Prediction:", months, key="predict_month", format_func=lambda x: x.title())
                selected_year = col2.selectbox("Select Year for Prediction:", years, key="predict_year")

                predict_period = str(selected_year) + "_" + str(selected_month)

                if st.button("Predict Future"):
                    with st.spinner("Predicting future income and expense patterns..."):
                        prediction = predict_future_income_expense(period=predict_period)
                        st.write(prediction)
                        st.success("Prediction Complete!")

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
                            st.empty()
                            with st.form("update_form"):
                                st.subheader(f"Existing Data for {period_to_modify}")
                                with st.expander("Current Income Data"):
                                    for income in incomes:
                                        st.text(f"{income}: {currency}{data['incomes'].get(income, 0)}")
                                with st.expander("Current Expense Data"):
                                    for expense in expenses:
                                        st.text(f"{expense}: {currency}{data['expenses'].get(expense, 0)}")
                                with st.expander("Savings"):
                                    st.text(f"Savings: {currency}{data.get('savings', 0)}")

                                "---"
                                st.subheader("Update Data")
                                with st.expander("Income", expanded=False):
                                    update_incomes_data = {}
                                    for income in incomes:
                                        update_incomes_data[income] = st.number_input(
                                            f"{income}:",
                                            min_value=0,
                                            format="%i",
                                            step=10,
                                            key=f"update_{income}",
                                            placeholder="Enter the value",
                                            value=int(data["incomes"].get(income, 0))
                                        )
                                with st.expander("Expenses", expanded=False):
                                    update_expenses_data = {}
                                    for expense in expenses:
                                        update_expenses_data[expense] = st.number_input(
                                            f"{expense}:",
                                            min_value=0,
                                            format="%i",
                                            step=10,
                                            key=f"update_{expense}",
                                            placeholder="Enter the value",
                                            value=int(data["expenses"].get(expense, 0))
                                        )
                                with st.expander("Comment", expanded=False):
                                    update_comment = st.text_area("", placeholder="Enter a comment here...", value=data.get("comment", ""))

                                "---"
                                submitted = st.form_submit_button("Update Data")
                                if submitted:
                                    with st.spinner("Updating data..."):
                                        incomes_data = {income: update_incomes_data[income] for income in incomes}
                                        expenses_data = {expense: update_expenses_data[expense] for expense in expenses}
                                        savings = int(data.get("savings", 0))
                                        collection.update_one(
                                            {"period": period_to_modify, "username": st.session_state['username']},
                                            {"$set": {"incomes": incomes_data, "expenses": expenses_data, "savings": savings, "comment": update_comment}}
                                        )
                                        st.success("Data Updated!")
<<<<<<< HEAD
                                        st.rerun()
=======
                                        st.experimental_rerun()
>>>>>>> f6160937040bd5f32fc082c8c2c39ba8d2cd80d2

                elif action == "Delete":
                    st.warning(f"Are you sure you want to delete the data for {period_to_modify}? This action cannot be undone.")
                    confirmed = st.checkbox("Confirm Deletion")
                    if confirmed:
                        with st.spinner("Deleting data..."):
                            collection.delete_one({"period": period_to_modify, "username": st.session_state['username']})
                            st.success("Data Deleted!")
                            st.session_state['delete_complete'] = True
                            st.rerun()

            elif selected == "Logout":
                st.header("Logout")
                st.info("You have been logged out successfully.")
                st.session_state['authenticated'] = False

if __name__ == "__main__":
    threading.Thread(target=run_flask_app).start()
    main()
<<<<<<< HEAD






































# import calendar
# from datetime import datetime
# import streamlit as st
# from streamlit_option_menu import option_menu
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# import pandas as pd
# from pymongo import MongoClient
# from flask import Flask, request, jsonify
# from werkzeug.security import generate_password_hash, check_password_hash
# import threading
# import requests
# import months,years

# # MongoDB connection
# client = MongoClient("mongodb+srv://Nexus_Coder:Ketan%402005@expensetracker.ddtuk3v.mongodb.net/?retryWrites=true&w=majority&appName=ExpenseTracker")
# db = client["ExpenseTracker"]
# collection = db["expenses"]
# fixed_values_collection = db["fixed_values"]
# users_collection = db["users"]

# def authenticate_user(action, username, password):
#     url = f"http://localhost:5000/{action}"
#     response = requests.post(url, json={"username": username, "password": password})
#     return response

# def save_fixed_value(username, value_type, item_name, amount):
#     """Function to save a fixed income or expense value."""
#     fixed_values_collection.update_one(
#         {"username": username},
#         {"$set": {f"{value_type.lower()}s.{item_name}": amount}},
#         upsert=True
#     )

# def delete_fixed_value(username, value_type, item_name):
#     """Function to delete a fixed income or expense value."""
#     fixed_values_collection.update_one(
#         {"username": username},
#         {"$unset": {f"{value_type.lower()}s.{item_name}": ""}}
#     )

# def get_fixed_values(username):
#     """Function to retrieve fixed income and expense values for the user."""
#     fixed_values = fixed_values_collection.find_one({"username": username})
#     if fixed_values:
#         return fixed_values.get("incomes", {}), fixed_values.get("expenses", {})
#     return {}, {}

# def get_all_periods():
#     """Function to retrieve all available periods."""
#     periods = collection.distinct("period", {"username": st.session_state['username']})
#     return periods

# def load_data_for_period(period, username):
#     """Function to load data for a specific period."""
#     return collection.find_one({"period": period, "username": username})

# # Flask backend
# app = Flask(__name__)

# @app.route('/signup', methods=['POST'])
# def signup():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')

#     if users_collection.find_one({'username': username}):
#         return jsonify({"error": "User already exists"}), 400

#     hashed_password = generate_password_hash(password, method='sha256')
#     users_collection.insert_one({'username': username, 'password': hashed_password})
#     return jsonify({"message": "User created successfully"}), 201

# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')

#     user = users_collection.find_one({'username': username})
#     if user and check_password_hash(user['password'], password):
#         return jsonify({"message": "Login successful"}), 200
#     return jsonify({"error": "Invalid credentials"}), 401

# def run_flask_app():
#     app.run(debug=False, port=5000)

# def main():
#     incomes = ['Salary', 'Other Income']
#     expenses = ["Rent", "Utilities", "Groceries", "Loan Instalments", "Petrol/Diesel", "Car", "Other Expenses"]
#     currency = "₹"
#     page_title = "Income and Expense Tracker"
#     page_icon = ":money_with_wings:"
#     layout = "centered"

#     st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
#     st.title(page_title + " " + page_icon)

#     # Check if session state for authentication exists, if not, initialize it
#     if 'authenticated' not in st.session_state:
#         st.session_state['authenticated'] = False
#     if 'username' not in st.session_state:
#         st.session_state['username'] = None

#     # Login/Signup Logic
#     if not st.session_state['authenticated']:
#         st.subheader("Login")
#         with st.form("login_form"):
#             username = st.text_input("Username")
#             password = st.text_input("Password", type="password")
#             submitted = st.form_submit_button("Login")
#             if submitted:
#                 with st.spinner("Authenticating..."):
#                     response = authenticate_user("login", username, password)
#                 if response.status_code == 200:
#                     st.session_state['authenticated'] = True
#                     st.session_state['username'] = username
#                     st.success("Login successful!")
#                     st.rerun()
#                 else:
#                     st.error("Invalid credentials")

#         st.subheader("Signup")
#         with st.form("signup_form"):
#             new_username = st.text_input("New Username")
#             new_password = st.text_input("New Password", type="password")
#             submitted_signup = st.form_submit_button("Signup")
#             if submitted_signup:
#                 with st.spinner("Creating account..."):
#                     response = authenticate_user("signup", new_username, new_password)
#                 if response.status_code == 201:
#                     st.success("Account created successfully! Please log in.")
#                 else:
#                     st.error("Account creation failed. User might already exist.")

#     else:
#         # Render the rest of the application if logged in
#         if 'custom_expenses' not in st.session_state:
#             st.session_state['custom_expenses'] = []

#         selected = option_menu(
#             menu_title=None,
#             options=["Data Entry", "Manage Fixed Income/Expenses", "Data Visualization", "Predict Future Patterns", "Update/Delete Data", "Logout"],
#             icons=["pencil-fill", "file-earmark-text", "bar-chart-fill", "graph-up-arrow", "gear-fill", "box-arrow-right"],
#             orientation="horizontal",
#             styles={
#                 "nav-link": {"font-size": "14px", "padding": "12px"},
#                 "container": {"padding": "0!important", "margin": "0!important"}
#             },
#         )

#         if selected == "Manage Fixed Income/Expenses":
#             st.header("Manage Fixed Income and Expenses")
#             st.info("You can add, update, or remove fixed incomes or expenses. These values will be automatically populated when entering data.")

#             col1, col2 = st.columns(2)
#             value_type = col1.selectbox("Select Type:", ["Income", "Expense"], key="value_type_selection")
#             item_name = col2.selectbox(
#                 f"Select {value_type} to Manage:", 
#                 incomes if value_type == "Income" else expenses, 
#                 key="item_name_selection"
#             )

#             fixed_incomes, fixed_expenses = get_fixed_values(st.session_state['username'])
#             fixed_value = fixed_incomes.get(item_name, "") if value_type == "Income" else fixed_expenses.get(item_name, "")

#             # Display current fixed values
#             with st.expander("Current Fixed Values"):
#                 st.write("**Fixed Incomes:**", fixed_incomes)
#                 st.write("**Fixed Expenses:**", fixed_expenses)

#             # Add or update fixed value
#             with st.form("fixed_value_form"):
#                 st.subheader(f"Set Fixed {value_type} Value for '{item_name}'")
#                 value = st.text_input(f"{item_name} ({currency}):", value="", placeholder="Enter the value")
#                 save_button = st.form_submit_button("Save Fixed Value")
#                 if save_button:
#                     try:
#                         value = int(value)
#                         save_fixed_value(st.session_state['username'], value_type, item_name, value)
#                         st.success(f"{value_type} '{item_name}' set as fixed with value {currency}{value}!")
#                     except ValueError:
#                         st.error("Please enter a valid integer.")

#             # Remove fixed value
#             with st.form("remove_fixed_value_form"):
#                 st.subheader(f"Remove Fixed {value_type} Value for '{item_name}'")
#                 remove_button = st.form_submit_button("Remove Fixed Value")
#                 if remove_button:
#                     delete_fixed_value(st.session_state['username'], value_type, item_name)
#                     st.success(f"{value_type} '{item_name}' removed!")

#         elif selected == "Data Entry":
#             st.header(f"Data Entry in {currency}")
#             col1, col2 = st.columns(2)
#             selected_month = col1.selectbox("Select Month:", months, key="month", format_func=lambda x: x.title())
#             selected_year = col2.selectbox("Select Year:", years, key="year")

#             period = str(selected_year) + "_" + str(selected_month)

#             existing_data = collection.find_one({"period": period, "username": st.session_state['username']})
#             if existing_data:
#                 st.error(f"Data for {selected_month} {selected_year} already exists. Please choose a different period.")
#             else:
#                 with st.form("entry_form", clear_on_submit=False):
#                     "---"
#                     income_data = {}
#                     expense_data = {}
#                     savings = None  # Initialize savings as None

#                     # Check and store income fields
#                     with st.expander("Income"):
#                         fixed_incomes, fixed_expenses = get_fixed_values(st.session_state['username'])
#                         for income in incomes:
#                             value = fixed_incomes.get(income, "")
#                             field_value = st.text_input(f"{income} ({currency}):", value=value, placeholder="Enter the value", key=f"input_{income}")
#                             if field_value:
#                                 income_data[income] = int(field_value)
#                                 if income in fixed_incomes:
#                                     st.caption(f"This is a fixed {income} value.")

#                     # Check and store expense fields
#                     with st.expander("Expenses"):
#                         for expense in expenses:
#                             value = fixed_expenses.get(expense, "")
#                             field_value = st.text_input(f"{expense} ({currency}):", value=value, placeholder="Enter the value", key=f"input_{expense}")
#                             if field_value:
#                                 expense_data[expense] = int(field_value)
#                                 if expense in fixed_expenses:
#                                     st.caption(f"This is a fixed {expense} value.")

#                         # Display custom expenses with other expenses in the form
#                         for index, (name, amount) in enumerate(st.session_state['custom_expenses']):
#                             value = st.text_input(f"{name} ({currency}):", value=amount, key=f"custom_expense_{index}")
#                             if value:
#                                 expense_data[name] = int(value)

#                         # Button to add new custom expense
#                         if st.form_submit_button("Add New Expense"):
#                             st.session_state['show_custom_expense_entry'] = True

#                         # Custom expense entry fields
#                         if st.session_state.get('show_custom_expense_entry', False):
#                             new_expense_name = st.text_input("Enter new expense name:")
#                             new_expense_value = st.text_input("Enter amount:")
#                             if st.form_submit_button("Submit Expense"):
#                                 if new_expense_name and new_expense_value:
#                                     try:
#                                         st.session_state['custom_expenses'].append((new_expense_name, int(new_expense_value)))
#                                         st.session_state['show_custom_expense_entry'] = False  # Hide the fields after adding
#                                         st.rerun()  # Refresh the form to display the new custom expense
#                                     except ValueError:
#                                         st.error("Please enter a valid integer for the amount.")

#                     "---"

#                     # Submit button to save data and calculate savings
#                     if st.form_submit_button("Save Data"):
#                         total_income = sum(income_data.values())
#                         total_expenses = sum(expense_data.values())
#                         savings = total_income - total_expenses

#                         # Save data including calculated savings
#                         entry = {
#                             "period": period,
#                             "incomes": income_data,
#                             "expenses": expense_data,
#                             "savings": savings,
#                             "username": st.session_state['username']
#                         }
#                         collection.insert_one(entry)

#                         # Display the calculated savings
#                         st.write(f"Calculated Savings: {currency}{savings}")
#                         st.success("Data Saved with Calculated Savings!")

#         elif selected == "Data Visualization":
#             st.header("Data Visualization")
#             with st.form("saved_periods"):
#                 with st.spinner("Loading periods..."):
#                     periods = get_all_periods()
#                 period = st.selectbox("Select Period:", periods)
#                 submitted = st.form_submit_button("Plot Period")
#                 if submitted:
#                     with st.spinner("Loading data..."):
#                         data = load_data_for_period(period, st.session_state['username'])
#                     if data:
#                         incomes_data = data.get("incomes", {})
#                         expenses_data = data.get("expenses", {})
#                         savings = data.get("savings", 0)

#                         # Interactive Bar Chart for Income and Expenses
#                         st.subheader("Income vs Expenses")
#                         fig = make_subplots(specs=[[{"secondary_y": True}]])
#                         fig.add_trace(go.Bar(x=list(incomes_data.keys()), y=list(incomes_data.values()), name='Income', marker=dict(color='green')), secondary_y=False)
#                         fig.add_trace(go.Bar(x=list(expenses_data.keys()), y=list(expenses_data.values()), name='Expenses', marker=dict(color='red')), secondary_y=False)
#                         fig.update_layout(barmode='group', title="Income vs Expenses", xaxis_title="Category", yaxis_title="Amount (₹)")
#                         st.plotly_chart(fig)

#                         # Pie Chart for Expense Distribution
#                         st.subheader("Expense Distribution")
#                         fig_pie = go.Figure(data=[go.Pie(labels=list(expenses_data.keys()), values=list(expenses_data.values()), hole=.3)])
#                         fig_pie.update_layout(title="Expense Distribution")
#                         st.plotly_chart(fig_pie)

#                         # Time Series Line Chart for Savings over Time
#                         st.subheader("Savings Over Time")
#                         history_data = list(collection.find({"username": st.session_state['username']}).sort("period", 1))
#                         if len(history_data) > 1:
#                             df_history = pd.DataFrame(history_data)
#                             df_history['Month'] = df_history['period'].apply(lambda x: datetime.strptime(x, '%Y_%B'))
#                             df_history.sort_values('Month', inplace=True)

#                             fig_line = go.Figure()
#                             fig_line.add_trace(go.Scatter(x=df_history['Month'], y=df_history['savings'], mode='lines+markers', name='Savings', marker=dict(color='blue')))
#                             fig_line.update_layout(title="Savings Over Time", xaxis_title="Month", yaxis_title="Savings (₹)")
#                             st.plotly_chart(fig_line)

#         elif selected == "Predict Future Patterns":
#             st.header("Predict Future Income and Expense Patterns")
#             st.warning("Prediction feature is not available due to insufficient data. Please enter data for at least 6 months.")

#         elif selected == "Update/Delete Data":
#             st.header("Update or Delete Data")
#             periods = get_all_periods()
#             period_to_modify = st.selectbox("Select Period to Modify:", periods)
#             action = st.radio("Select Action:", ["Update", "Delete"])

#             if action == "Update":
#                 data = load_data_for_period(period_to_modify, st.session_state['username'])
#                 if data:
#                     "---"
#                     with st.spinner("Loading data..."):
#                         st.empty()
#                         with st.form("update_form"):
#                             st.subheader(f"Existing Data for {period_to_modify}")
#                             with st.expander("Current Income Data"):
#                                 for income in incomes:
#                                     st.text(f"{income}: {currency}{data['incomes'].get(income, 0)}")
#                             with st.expander("Current Expense Data"):
#                                 for expense in expenses:
#                                     st.text(f"{expense}: {currency}{data['expenses'].get(expense, 0)}")
#                             with st.expander("Savings"):
#                                 st.text(f"Savings: {currency}{data.get('savings', 0)}")

#                             "---"
#                             st.subheader("Update Data")
#                             with st.expander("Income", expanded=False):
#                                 update_incomes_data = {}
#                                 for income in incomes:
#                                     update_incomes_data[income] = st.number_input(
#                                         f"{income}:",
#                                         min_value=0,
#                                         format="%i",
#                                         step=10,
#                                         key=f"update_{income}",
#                                         placeholder="Enter the value",
#                                         value=int(data["incomes"].get(income, 0))
#                                     )
#                             with st.expander("Expenses", expanded=False):
#                                 update_expenses_data = {}
#                                 for expense in expenses:
#                                     update_expenses_data[expense] = st.number_input(
#                                         f"{expense}:",
#                                         min_value=0,
#                                         format="%i",
#                                         step=10,
#                                         key=f"update_{expense}",
#                                         placeholder="Enter the value",
#                                         value=int(data["expenses"].get(expense, 0))
#                                     )
#                             with st.expander("Comment", expanded=False):
#                                 update_comment = st.text_area("", placeholder="Enter a comment here...", value=data.get("comment", ""))

#                             "---"
#                             submitted = st.form_submit_button("Update Data")
#                             if submitted:
#                                 with st.spinner("Updating data..."):
#                                     incomes_data = {income: update_incomes_data[income] for income in incomes}
#                                     expenses_data = {expense: update_expenses_data[expense] for expense in expenses}
#                                     savings = int(data.get("savings", 0))
#                                     collection.update_one(
#                                         {"period": period_to_modify, "username": st.session_state['username']},
#                                         {"$set": {"incomes": incomes_data, "expenses": expenses_data, "savings": savings, "comment": update_comment}}
#                                     )
#                                     st.success("Data Updated!")
#                                     st.rerun()

#             elif action == "Delete":
#                 st.warning(f"Are you sure you want to delete the data for {period_to_modify}? This action cannot be undone.")
#                 confirmed = st.checkbox("Confirm Deletion")
#                 if confirmed:
#                     with st.spinner("Deleting data..."):
#                         collection.delete_one({"period": period_to_modify, "username": st.session_state['username']})
#                         st.success("Data Deleted!")
#                         st.session_state['delete_complete'] = True
#                         st.rerun()

#         elif selected == "Logout":
#             st.header("Logout")
#             st.info("You have been logged out successfully.")
#             st.session_state['authenticated'] = False
#             st.rerun()

# if __name__ == "__main__":
#     threading.Thread(target=run_flask_app).start()
#     main()












































# import calendar
# from datetime import datetime
# import streamlit as st
# from streamlit_option_menu import option_menu
# import plotly.graph_objects as go
# from pymongo import MongoClient
# import requests
# from flask import Flask, request, jsonify
# from werkzeug.security import generate_password_hash, check_password_hash
# import threading
# import pandas as pd
# from googleapiclient import discovery
# from google.oauth2 import service_account
# from io import BytesIO

# # MongoDB connection
# client = MongoClient("mongodb+srv://Nexus_Coder:Ketan%402005@expensetracker.ddtuk3v.mongodb.net/?retryWrites=true&w=majority&appName=ExpenseTracker")
# db = client["ExpenseTracker"]
# collection = db["expenses"]
# fixed_expenses_collection = db["fixed_expenses"]
# users_collection = db["users"]

# # Flask endpoints base URL
# flask_base_url = "http://localhost:5000"

# # Google Cloud credentials and API setup
# credentials = service_account.Credentials.from_service_account_file(
#     'delta-student-429403-j2-4710a9d9ad67.json')  # Replace with the actual path to your JSON key file
# service = discovery.build('ml', 'v1', credentials=credentials)

# def authenticate_user(action, username, password):
#     url = f"{flask_base_url}/{action}"
#     response = requests.post(url, json={"username": username, "password": password})
#     return response

# # Flask backend
# app = Flask(__name__)

# @app.route('/signup', methods=['POST'])
# def signup():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')

#     if users_collection.find_one({'username': username}):
#         return jsonify({"error": "User already exists"}), 400

#     hashed_password = generate_password_hash(password, method='sha256')
#     users_collection.insert_one({'username': username, 'password': hashed_password})
#     return jsonify({"message": "User created successfully"}), 201

# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')

#     user = users_collection.find_one({'username': username})
#     if user and check_password_hash(user['password'], password):
#         return jsonify({"message": "Login successful"}), 200
#     return jsonify({"error": "Invalid credentials"}), 401

# def run_flask_app():
#     app.run(debug=False, port=5000)

# # Function to fetch past expenses data
# def fetch_past_expenses(username):
#     cursor = collection.find({"username": username})
#     data = []
#     for doc in cursor:
#         period = doc['period']
#         for expense, value in doc['expenses'].items():
#             data.append({'period': period, 'expense': expense, 'value': value})
#     df = pd.DataFrame(data)
#     return df

# # Function to predict future expenses
# def predict_future_expenses(df, next_period, fixed_expenses_data):
#     # Group by period and expense, summing the values
#     df_grouped = df.groupby(['period', 'expense']).sum().reset_index()

#     # Placeholder for predictions - in practice, you'd use an ML model here
#     predictions = {}
#     for expense in df_grouped['expense'].unique():
#         # For simplicity, predict the average of the past values if not a fixed expense
#         if expense not in fixed_expenses_data:
#             expense_data = df_grouped[df_grouped['expense'] == expense]
#             predictions[expense] = expense_data['value'].mean()
#         else:
#             predictions[expense] = fixed_expenses_data[expense]

#     return {next_period: predictions}

# # Function to get fixed expenses for a user
# def get_fixed_expenses(username):
#     fixed_expenses = fixed_expenses_collection.find_one({"username": username})
#     return fixed_expenses.get("expenses", {}) if fixed_expenses else {}

# # Function to save fixed expenses for a user
# def save_fixed_expenses(username, fixed_expenses):
#     fixed_expenses_collection.update_one(
#         {"username": username},
#         {"$set": {"expenses": fixed_expenses}},
#         upsert=True
#     )

# # Function to export user data to Excel
# def export_to_excel(username):
#     df = fetch_past_expenses(username)
#     output = BytesIO()
#     writer = pd.ExcelWriter(output, engine='xlsxwriter')
#     df.to_excel(writer, index=False, sheet_name='Expenses')
#     writer.close()  # Corrected line
#     processed_data = output.getvalue()
#     return processed_data

# def main():
#     incomes = ['Salary', 'Other Income']
#     expenses = ["Rent", "Utilities", "Groceries", "Loan Instalments", "Petrol/Diesel", "Car", "Other Expenses", "Saving"]
#     fixed_expenses = ["Rent", "Loan Instalments"]
#     currency = "Rs"
#     page_title = "Income and Expense Tracker"
#     page_icon = ":money_with_wings:"
#     layout = "centered"

#     st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
#     st.title(page_title + " " + page_icon)

#     years = [datetime.today().year, datetime.today().year + 1]
#     months = list(calendar.month_name[1:])

#     # Custom CSS to change cursor to pointer for dropdown lists and highlight sections
#     st.markdown("""
#         <style>
#             .pointer:hover {
#                 cursor: pointer;
#             }
#             .highlight {
#                 background-color: #f0f8ff;
#                 padding: 10px;
#                 border-radius: 5px;
#                 border: 2px solid #00f;
#                 margin-bottom: 15px;
#             }
#             .fixed-expense input {
#                 background-color: inherit;
#                 color: inherit;
#             }
#         </style>
#     """, unsafe_allow_html=True)

#     hide_st_style = """
#                     <style>
#                     #MainMenu {visibility:hidden;}
#                     footer {visibility: hidden;}
#                     header {visibility: hidden;}
#                     </style>
#                     """
#     st.markdown(hide_st_style, unsafe_allow_html=True)

#     if 'authenticated' not in st.session_state:
#         st.session_state['authenticated'] = False

#     if 'signup_success' not in st.session_state:
#         st.session_state['signup_success'] = False

#     if 'delete_complete' not in st.session_state:
#         st.session_state['delete_complete'] = False

#     if 'updated' not in st.session_state:
#         st.session_state['updated'] = False

#     if not st.session_state['authenticated']:
#         if st.session_state['signup_success']:
#             st.session_state['signup_success'] = False
#             st.success("Account Created Successfully. Please log in.")
#             st.rerun()
        
#         auth_selected = option_menu(
#             None,
#             ["Login", "Signup"],
#             icons=["key", "person-plus"],
#             menu_icon="cast", default_index=0, orientation="horizontal"
#         )

#         if auth_selected == "Login":
#             st.header("Login")
#             with st.form("login_form"):
#                 username = st.text_input("Username")
#                 password = st.text_input("Password", type="password")
#                 submitted = st.form_submit_button("Login")
#                 if submitted:
#                     with st.spinner("Authenticating..."):
#                         response = authenticate_user("login", username, password)
#                     if response.status_code == 200:
#                         st.success("Login successful")
#                         st.session_state['authenticated'] = True
#                         st.session_state['username'] = username
#                         st.rerun()
#                     else:
#                         st.error("Invalid credentials")

#         if auth_selected == "Signup":
#             st.header("Signup")
#             with st.form("signup_form"):
#                 username = st.text_input("Username")
#                 password = st.text_input("Password", type="password")
#                 submitted = st.form_submit_button("Signup")
#                 if submitted:
#                     with st.spinner("Creating account..."):
#                         response = authenticate_user("signup", username, password)
#                     if response.status_code == 201:
#                         st.session_state['signup_success'] = True
#                         st.rerun()
#                     elif response.status_code == 400:
#                         st.error("Account already exists")

#     else:
#         if st.session_state['delete_complete']:
#             st.success("Data Deleted!")
#             st.session_state['delete_complete'] = False
#             st.rerun()
#         else:
#             selected = option_menu(
#                 None,
#                 ["Data Entry", "Data Visualization", "Update/Delete Data", "Manage Fixed Expenses", "Predict Expenditures", "Export Data", "Logout"],
#                 icons=["pencil-fill", "bar-chart-fill", "gear-fill", "gear-fill", "activity", "file-earmark-excel", "box-arrow-right"],
#                 menu_icon="cast", default_index=0, orientation="horizontal"
#             )

#             def get_all_periods():
#                 periods = collection.distinct("period", {"username": st.session_state['username']})
#                 return periods

#             if selected == "Data Entry":
#                 st.header(f"Data Entry in {currency}")
#                 col1, col2 = st.columns(2)
#                 selected_month = col1.selectbox("Select Month:", months, key="month", format_func=lambda x: x.title())
#                 selected_year = col2.selectbox("Select Year:", years, key="year")

#                 period = str(selected_year) + "_" + str(selected_month)

#                 # Check if data for the selected period already exists
#                 existing_data = collection.find_one({"period": period, "username": st.session_state['username']})
#                 if existing_data:
#                     st.error(f"Data for {selected_month} {selected_year} already exists. Please choose a different period.")
#                 else:
#                     fixed_expenses_data = get_fixed_expenses(st.session_state['username'])
#                     all_expenses = set(expenses + list(fixed_expenses_data.keys()))
#                     with st.form("entry_form", clear_on_submit=True):
#                         "---"
#                         with st.expander("Income"):
#                             for income in incomes:
#                                 value = st.text_input(f"{income}:", key=f"input_{income}", placeholder="Enter the value")
#                                 st.session_state[income] = int(value) if value else 0
#                         with st.expander("Expenses"):
#                             for expense in all_expenses:
#                                 if expense in fixed_expenses_data:
#                                     st.text_input(f"{expense}:", value=fixed_expenses_data[expense], key=f"fixed_{expense}", disabled=True)
#                                     st.markdown(f"<small>This is a fixed expenditure. You can edit it from the fixed expenditure section.</small>", unsafe_allow_html=True)
#                                 else:
#                                     value = st.text_input(f"{expense}:", key=f"input_{expense}", placeholder="Enter the value")
#                                     st.session_state[expense] = int(value) if value else 0
#                         with st.expander("Comment"):
#                             comment = st.text_area("", placeholder="Enter a comment here...")

#                         "---"
#                         submitted = st.form_submit_button("Save Data")
#                         if submitted:
#                             with st.spinner("Saving data..."):
#                                 incomes_data = {income: st.session_state[income] for income in incomes}
#                                 expenses_data = {expense: st.session_state[expense] for expense in all_expenses if expense not in fixed_expenses_data}

#                                 # Save data to MongoDB
#                                 entry = {
#                                     "period": period,
#                                     "incomes": incomes_data,
#                                     "expenses": {**expenses_data, **fixed_expenses_data},
#                                     "comment": comment,
#                                     "username": st.session_state['username']
#                                 }
#                                 collection.insert_one(entry)
#                                 save_fixed_expenses(st.session_state['username'], fixed_expenses_data)

#                                 st.write(f"Income: {incomes_data}")
#                                 st.write(f"Expenses: {expenses_data}")
#                                 st.success("Data Saved!")

#             elif selected == "Data Visualization":
#                 st.header("Data Visualization")
#                 with st.form("saved_periods"):
#                     with st.spinner("Loading periods..."):
#                         periods = get_all_periods()
#                     period = st.selectbox("Select Period:", periods)
#                     submitted = st.form_submit_button("Plot Period")
#                     if submitted:
#                         with st.spinner("Loading data..."):
#                             data = collection.find_one({"period": period, "username": st.session_state['username']})
#                         if data:
#                             comment = data.get("comment", "")
#                             incomes_data = data.get("incomes", {})
#                             expenses_data = data.get("expenses", {})

#                             total_income = sum(incomes_data.values())
#                             total_expense = sum([int(value) for value in expenses_data.values()])
#                             remaining_budget = total_income - total_expense
#                             col1, col2, col3 = st.columns(3)
#                             col1.subheader("Income")
#                             col1.write(incomes_data)
#                             col2.subheader("Expenses")
#                             col2.write(expenses_data)
#                             col3.subheader("Remaining Budget")
#                             col3.write(f"{remaining_budget} {currency}")

#                             label = ["Income"] + list(incomes_data.keys()) + ["Expense"] + list(expenses_data.keys())
#                             source = [0] * (len(incomes_data.keys()) + 1) + [i + 1 for i in range(len(expenses_data.keys()))]
#                             target = [i + 1 for i in range(len(incomes_data.keys()))] + [len(incomes_data.keys()) + 1 + i for i in
#                                                                                          range(len(expenses_data.keys()))]
#                             value = [total_income] + [incomes_data[k] for k in incomes_data.keys()] + [total_expense] + \
#                                     [int(expenses_data[k]) for k in expenses_data.keys()]
#                             fig = go.Figure(data=[go.Sankey(
#                                 node=dict(
#                                     pad=15,
#                                     thickness=20,
#                                     line=dict(color="black", width=0.5),
#                                     label=label,
#                                 ),
#                                 link=dict(
#                                     source=source,
#                                     target=target,
#                                     value=value
#                                 ))])
#                             fig.update_layout(title_text="Income and Expense Flow", font_size=10)
#                             st.plotly_chart(fig)

#             elif selected == "Update/Delete Data":
#                 st.header("Update or Delete Data")
#                 periods = get_all_periods()
#                 period_to_modify = st.selectbox("Select Period to Modify:", periods)
#                 action = st.radio("Select Action:", ["Update", "Delete"])

#                 if action == "Update":
#                     data = collection.find_one({"period": period_to_modify, "username": st.session_state['username']})
#                     if data:
#                         "---"
#                         with st.spinner("Loading data..."):
#                             st.empty()
#                             with st.form("update_form"):
#                                 st.subheader(f"Existing Data for {period_to_modify}")
#                                 with st.expander("Current Income Data", expanded=True):
#                                     for income in incomes:
#                                         st.text(f"{income}: {data['incomes'].get(income, 0)} {currency}")
#                                 with st.expander("Current Expense Data", expanded=True):
#                                     for expense in expenses:
#                                         st.text(f"{expense}: {data['expenses'].get(expense, 0)} {currency}")
#                                 with st.expander("Comment", expanded=True):
#                                     st.text(f"{data.get('comment', '')}")

#                                 "---"
#                                 st.subheader("Update Data")
#                                 with st.expander("Income", expanded=False):
#                                     update_incomes_data = {}
#                                     for income in incomes:
#                                         value = data["incomes"].get(income, 0)
#                                         update_incomes_data[income] = st.number_input(f"{income}:", min_value=0, format="%i", step=10, key=f"update_{income}", placeholder="Enter the value", value=int(value))
#                                 with st.expander("Expenses", expanded=False):
#                                     update_expenses_data = {}
#                                     for expense in expenses:
#                                         value = data["expenses"].get(expense, 0)
#                                         update_expenses_data[expense] = st.number_input(f"{expense}:", min_value=0, format="%i", step=10, key=f"update_{expense}", placeholder="Enter the value", value=int(value))
#                                 with st.expander("Comment", expanded=False):
#                                     update_comment = st.text_area("", placeholder="Enter a comment here...", value=data.get("comment", ""))

#                                 "---"
#                                 submitted = st.form_submit_button("Update Data")
#                                 if submitted:
#                                     with st.spinner("Updating data..."):
#                                         incomes_data = {income: update_incomes_data[income] for income in incomes}
#                                         expenses_data = {expense: update_expenses_data[expense] for expense in expenses}
#                                         collection.update_one(
#                                             {"period": period_to_modify, "username": st.session_state['username']},
#                                             {"$set": {"incomes": incomes_data, "expenses": expenses_data, "comment": update_comment}}
#                                         )
#                                         st.success("Data Updated!")
#                                         st.session_state['updated'] = True
#                                         st.rerun()

#                 elif action == "Delete":
#                     st.warning(f"Are you sure you want to delete the data for {period_to_modify}? This action cannot be undone.")
#                     confirmed = st.checkbox("Confirm Deletion")
#                     if confirmed:
#                         with st.spinner("Deleting data..."):
#                             collection.delete_one({"period": period_to_modify, "username": st.session_state['username']})
#                             st.success("Data Deleted!")
#                             st.session_state['delete_complete'] = True
#                             st.rerun()

#             elif selected == "Manage Fixed Expenses":
#                 st.header("Manage Fixed Expenses")
#                 fixed_expenses_data = get_fixed_expenses(st.session_state['username'])

#                 with st.form("add_fixed_expense_form"):
#                     st.write("Add Fixed Expense:")
#                     new_expense_name = st.text_input("Expense Name")
#                     new_expense_value = st.text_input("Expense Value")
#                     add_submitted = st.form_submit_button("Add Expense")
#                     if add_submitted:
#                         if new_expense_name and new_expense_value:
#                             if new_expense_name in fixed_expenses_data:
#                                 st.warning(f"Expense '{new_expense_name}' already exists. Updating its value.")
#                             fixed_expenses_data[new_expense_name] = new_expense_value
#                             save_fixed_expenses(st.session_state['username'], fixed_expenses_data)
#                             st.success(f"Fixed expense '{new_expense_name}' added/updated successfully.")
#                             st.rerun()

#                 with st.form("delete_fixed_expense_form"):
#                     st.write("Delete Fixed Expense:")
#                     delete_expense_name = st.text_input("Expense Name to Delete")
#                     delete_submitted = st.form_submit_button("Delete Expense")
#                     if delete_submitted:
#                         if delete_expense_name in fixed_expenses_data:
#                             del fixed_expenses_data[delete_expense_name]
#                             save_fixed_expenses(st.session_state['username'], fixed_expenses_data)
#                             st.success(f"Fixed expense '{delete_expense_name}' deleted successfully.")
#                             st.rerun()
#                         else:
#                             st.error(f"Expense '{delete_expense_name}' not found.")

#                 with st.form("fixed_expenses_form"):
#                     st.write("Current Fixed Expenses:")
#                     for expense in fixed_expenses_data:
#                         st.text(f"{expense}: {fixed_expenses_data[expense]}")

#                     st.form_submit_button("Refresh")

#             elif selected == "Predict Expenditures":
#                 st.header("Predict Future Expenditures")
#                 with st.spinner("Fetching past data..."):
#                     df = fetch_past_expenses(st.session_state['username'])
#                 fixed_expenses_data = get_fixed_expenses(st.session_state['username'])

#                 if not df.empty:
#                     selected_month = st.selectbox("Select Month for Prediction:", months, key="predict_month", format_func=lambda x: x.title())
#                     selected_year = st.selectbox("Select Year for Prediction:", years, key="predict_year")

#                     next_period = f"{selected_year}_{selected_month}"

#                     with st.spinner("Predicting future expenditures..."):
#                         predictions = predict_future_expenses(df, next_period, fixed_expenses_data)

#                     if next_period in predictions:
#                         st.subheader(f"Predicted Expenditures for {selected_month} {selected_year}")
#                         predicted_expenses = predictions[next_period]
#                         for expense, value in predicted_expenses.items():
#                             st.write(f"{expense}: {float(value):.2f} {currency}")
#                     else:
#                         st.error("Could not generate predictions.")
#                 else:
#                     st.error("No past data available to analyze.")

#             elif selected == "Export Data":
#                 st.header("Export Data")
#                 st.write("Click the button below to export your data to an Excel file.")
#                 if st.button("Export to Excel"):
#                     with st.spinner("Exporting data..."):
#                         excel_data = export_to_excel(st.session_state['username'])
#                         st.download_button(
#                             label="Download Excel file",
#                             data=excel_data,
#                             file_name=f"{st.session_state['username']}_expenses.xlsx",
#                             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#                         )

#             elif selected == "Logout":
#                 st.header("Logout")
#                 st.info("You have been logged out successfully.")
#                 st.session_state['authenticated'] = False

# if __name__ == "__main__":
#     threading.Thread(target=run_flask_app).start()
#     main()


# # import calendar
# # from datetime import datetime
# # import streamlit as st
# # from streamlit_option_menu import option_menu
# # import plotly.graph_objects as go
# # from pymongo import MongoClient
# # import requests
# # from flask import Flask, request, jsonify
# # from werkzeug.security import generate_password_hash, check_password_hash
# # import threading
# # import pandas as pd
# # from googleapiclient import discovery
# # from google.oauth2 import service_account
# # from io import BytesIO

# # # MongoDB connection
# # client = MongoClient("mongodb+srv://Nexus_Coder:Ketan%402005@expensetracker.ddtuk3v.mongodb.net/?retryWrites=true&w=majority&appName=ExpenseTracker")
# # db = client["ExpenseTracker"]
# # collection = db["expenses"]
# # fixed_expenses_collection = db["fixed_expenses"]
# # users_collection = db["users"]

# # # Flask endpoints base URL
# # flask_base_url = "http://localhost:5000"

# # # Google Cloud credentials and API setup
# # credentials = service_account.Credentials.from_service_account_file('delta-student-429403-j2-4710a9d9ad67.json')
# # service = discovery.build('ml', 'v1', credentials=credentials)

# # def authenticate_user(action, username, password):
# #     url = f"{flask_base_url}/{action}"
# #     response = requests.post(url, json={"username": username, "password": password})
# #     return response

# # # Flask backend
# # app = Flask(__name__)

# # @app.route('/signup', methods=['POST'])
# # def signup():
# #     data = request.get_json()
# #     username = data.get('username')
# #     password = data.get('password')

# #     if users_collection.find_one({'username': username}):
# #         return jsonify({"error": "User already exists"}), 400

# #     hashed_password = generate_password_hash(password, method='sha256')
# #     users_collection.insert_one({'username': username, 'password': hashed_password})
# #     return jsonify({"message": "User created successfully"}), 201

# # @app.route('/login', methods=['POST'])
# # def login():
# #     data = request.get_json()
# #     username = data.get('username')
# #     password = data.get('password')

# #     user = users_collection.find_one({'username': username})
# #     if user and check_password_hash(user['password'], password):
# #         return jsonify({"message": "Login successful"}), 200
# #     return jsonify({"error": "Invalid credentials"}), 401

# # def run_flask_app():
# #     app.run(debug=False, port=5000)

# # # Function to fetch past expenses data
# # def fetch_past_expenses(username):
# #     cursor = collection.find({"username": username})
# #     data = []
# #     for doc in cursor:
# #         period = doc['period']
# #         for expense, value in doc['expenses'].items():
# #             data.append({'period': period, 'expense': expense, 'value': value})
# #     df = pd.DataFrame(data)
# #     return df

# # # Function to predict future expenses
# # def predict_future_expenses(df, next_period, fixed_expenses_data):
# #     # Group by period and expense, summing the values
# #     df_grouped = df.groupby(['period', 'expense']).sum().reset_index()

# #     # Placeholder for predictions - in practice, you'd use an ML model here
# #     predictions = {}
# #     for expense in df_grouped['expense'].unique():
# #         # For simplicity, predict the average of the past values if not a fixed expense
# #         if expense not in fixed_expenses_data:
# #             expense_data = df_grouped[df_grouped['expense'] == expense]
# #             predictions[expense] = expense_data['value'].mean()
# #         else:
# #             predictions[expense] = fixed_expenses_data[expense]

# #     return {next_period: predictions}

# # # Function to get fixed expenses for a user
# # def get_fixed_expenses(username):
# #     fixed_expenses = fixed_expenses_collection.find_one({"username": username})
# #     return fixed_expenses.get("expenses", {}) if fixed_expenses else {}

# # # Function to save fixed expenses for a user
# # def save_fixed_expenses(username, fixed_expenses):
# #     fixed_expenses_collection.update_one(
# #         {"username": username},
# #         {"$set": {"expenses": fixed_expenses}},
# #         upsert=True
# #     )

# # # Function to export user data to Excel
# # def export_to_excel(username):
# #     df = fetch_past_expenses(username)
# #     output = BytesIO()
# #     writer = pd.ExcelWriter(output, engine='xlsxwriter')
# #     df.to_excel(writer, index=False, sheet_name='Expenses')
# #     writer.close()  # Corrected line
# #     processed_data = output.getvalue()
# #     return processed_data

# # def main():
# #     incomes = ['Salary', 'Other Income']
# #     expenses = ["Rent", "Utilities", "Groceries", "Loan Instalments", "Petrol/Diesel", "Car", "Other Expenses", "Saving"]
# #     fixed_expenses = ["Rent", "Loan Instalments"]
# #     currency = "Rs"
# #     page_title = "Income and Expense Tracker"
# #     page_icon = ":money_with_wings:"
# #     layout = "centered"

# #     st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
# #     st.title(page_title + " " + page_icon)

# #     years = [datetime.today().year, datetime.today().year + 1]
# #     months = list(calendar.month_name[1:])

# #     # Custom CSS to change cursor to pointer for dropdown lists and highlight sections
# #     st.markdown("""
# #         <style>
# #             .pointer:hover {
# #                 cursor: pointer;
# #             }
# #             .highlight {
# #                 background-color: #f0f8ff;
# #                 padding: 10px;
# #                 border-radius: 5px;
# #                 border: 2px solid #00f;
# #                 margin-bottom: 15px;
# #             }
# #             .fixed-expense input {
# #                 background-color: inherit;
# #                 color: inherit;
# #             }
# #         </style>
# #     """, unsafe_allow_html=True)

# #     hide_st_style = """
# #                     <style>
# #                     #MainMenu {visibility:hidden;}
# #                     footer {visibility: hidden;}
# #                     header {visibility: hidden;}
# #                     </style>
# #                     """
# #     st.markdown(hide_st_style, unsafe_allow_html=True)

# #     if 'authenticated' not in st.session_state:
# #         st.session_state['authenticated'] = False

# #     if 'signup_success' not in st.session_state:
# #         st.session_state['signup_success'] = False

# #     if 'delete_complete' not in st.session_state:
# #         st.session_state['delete_complete'] = False

# #     if 'updated' not in st.session_state:
# #         st.session_state['updated'] = False

# #     if not st.session_state['authenticated']:
# #         if st.session_state['signup_success']:
# #             st.session_state['signup_success'] = False
# #             st.success("Account Created Successfully. Please log in.")
# #             st.rerun()
        
# #         auth_selected = option_menu(
# #             None,
# #             ["Login", "Signup"],
# #             icons=["key", "person-plus"],
# #             menu_icon="cast", default_index=0, orientation="horizontal"
# #         )

# #         if auth_selected == "Login":
# #             st.header("Login")
# #             with st.form("login_form"):
# #                 username = st.text_input("Username")
# #                 password = st.text_input("Password", type="password")
# #                 submitted = st.form_submit_button("Login")
# #                 if submitted:
# #                     with st.spinner("Authenticating..."):
# #                         response = authenticate_user("login", username, password)
# #                     if response.status_code == 200:
# #                         st.success("Login successful")
# #                         st.session_state['authenticated'] = True
# #                         st.session_state['username'] = username
# #                         st.rerun()
# #                     else:
# #                         st.error("Invalid credentials")

# #         if auth_selected == "Signup":
# #             st.header("Signup")
# #             with st.form("signup_form"):
# #                 username = st.text_input("Username")
# #                 password = st.text_input("Password", type="password")
# #                 submitted = st.form_submit_button("Signup")
# #                 if submitted:
# #                     with st.spinner("Creating account..."):
# #                         response = authenticate_user("signup", username, password)
# #                     if response.status_code == 201:
# #                         st.session_state['signup_success'] = True
# #                         st.rerun()
# #                     elif response.status_code == 400:
# #                         st.error("Account already exists")

# #     else:
# #         if st.session_state['delete_complete']:
# #             st.success("Data Deleted!")
# #             st.session_state['delete_complete'] = False
# #             st.rerun()
# #         else:
# #             selected = option_menu(
# #                 None,
# #                 ["Data Entry", "Data Visualization", "Update/Delete Data", "Manage Fixed Expenses", "Predict Expenditures", "Export Data", "Logout"],
# #                 icons=["pencil-fill", "bar-chart-fill", "gear-fill", "gear-fill", "activity", "file-earmark-excel", "box-arrow-right"],
# #                 menu_icon="cast", default_index=0, orientation="horizontal"
# #             )

# #             def get_all_periods():
# #                 periods = collection.distinct("period", {"username": st.session_state['username']})
# #                 return periods

# #             if selected == "Data Entry":
# #                 st.header(f"Data Entry in {currency}")
# #                 col1, col2 = st.columns(2)
# #                 selected_month = col1.selectbox("Select Month:", months, key="month", format_func=lambda x: x.title())
# #                 selected_year = col2.selectbox("Select Year:", years, key="year")

# #                 period = str(selected_year) + "_" + str(selected_month)

# #                 # Check if data for the selected period already exists
# #                 existing_data = collection.find_one({"period": period, "username": st.session_state['username']})
# #                 if existing_data:
# #                     st.error(f"Data for {selected_month} {selected_year} already exists. Please choose a different period.")
# #                 else:
# #                     fixed_expenses_data = get_fixed_expenses(st.session_state['username'])
# #                     all_expenses = set(expenses + list(fixed_expenses_data.keys()))
# #                     with st.form("entry_form", clear_on_submit=True):
# #                         "---"
# #                         with st.expander("Income"):
# #                             for income in incomes:
# #                                 value = st.text_input(f"{income}:", key=f"input_{income}", placeholder="Enter the value")
# #                                 st.session_state[income] = int(value) if value else 0
# #                         with st.expander("Expenses"):
# #                             for expense in all_expenses:
# #                                 if expense in fixed_expenses_data:
# #                                     st.text_input(f"{expense}:", value=fixed_expenses_data[expense], key=f"fixed_{expense}", disabled=True)
# #                                     st.markdown(f"<small>This is a fixed expenditure. You can edit it from the fixed expenditure section.</small>", unsafe_allow_html=True)
# #                                 else:
# #                                     value = st.text_input(f"{expense}:", key=f"input_{expense}", placeholder="Enter the value")
# #                                     st.session_state[expense] = int(value) if value else 0
# #                         with st.expander("Comment"):
# #                             comment = st.text_area("", placeholder="Enter a comment here...")

# #                         "---"
# #                         submitted = st.form_submit_button("Save Data")
# #                         if submitted:
# #                             with st.spinner("Saving data..."):
# #                                 incomes_data = {income: st.session_state[income] for income in incomes}
# #                                 expenses_data = {expense: st.session_state[expense] for expense in all_expenses if expense not in fixed_expenses_data}

# #                                 # Save data to MongoDB
# #                                 entry = {
# #                                     "period": period,
# #                                     "incomes": incomes_data,
# #                                     "expenses": {**expenses_data, **fixed_expenses_data},
# #                                     "comment": comment,
# #                                     "username": st.session_state['username']
# #                                 }
# #                                 collection.insert_one(entry)
# #                                 save_fixed_expenses(st.session_state['username'], fixed_expenses_data)

# #                                 st.write(f"Income: {incomes_data}")
# #                                 st.write(f"Expenses: {expenses_data}")
# #                                 st.success("Data Saved!")

# #             elif selected == "Data Visualization":
# #                 st.header("Data Visualization")
# #                 with st.form("saved_periods"):
# #                     with st.spinner("Loading periods..."):
# #                         periods = get_all_periods()
# #                     period = st.selectbox("Select Period:", periods)
# #                     submitted = st.form_submit_button("Plot Period")
# #                     if submitted:
# #                         with st.spinner("Loading data..."):
# #                             data = collection.find_one({"period": period, "username": st.session_state['username']})
# #                         if data:
# #                             comment = data.get("comment", "")
# #                             incomes_data = data.get("incomes", {})
# #                             expenses_data = data.get("expenses", {})

# #                             total_income = sum(incomes_data.values())
# #                             total_expense = sum([int(value) for value in expenses_data.values()])
# #                             remaining_budget = total_income - total_expense
# #                             col1, col2, col3 = st.columns(3)
# #                             col1.subheader("Income")
# #                             col1.write(incomes_data)
# #                             col2.subheader("Expenses")
# #                             col2.write(expenses_data)
# #                             col3.subheader("Remaining Budget")
# #                             col3.write(f"{remaining_budget} {currency}")

# #                             label = ["Income"] + list(incomes_data.keys()) + ["Expense"] + list(expenses_data.keys())
# #                             source = [0] * (len(incomes_data.keys()) + 1) + [i + 1 for i in range(len(expenses_data.keys()))]
# #                             target = [i + 1 for i in range(len(incomes_data.keys()))] + [len(incomes_data.keys()) + 1 + i for i in range(len(expenses_data.keys()))]
# #                             value = [total_income] + [incomes_data[k] for k in incomes_data.keys()] + [total_expense] + [int(expenses_data[k]) for k in expenses_data.keys()]
# #                             fig = go.Figure(data=[go.Sankey(
# #                                 node=dict(
# #                                     pad=15,
# #                                     thickness=20,
# #                                     line=dict(color="black", width=0.5),
# #                                     label=label,
# #                                 ),
# #                                 link=dict(
# #                                     source=source,
# #                                     target=target,
# #                                     value=value
# #                                 ))])
# #                             fig.update_layout(title_text="Income and Expense Flow", font_size=10)
# #                             st.plotly_chart(fig)

# #             elif selected == "Update/Delete Data":
# #                 st.header("Update or Delete Data")
# #                 periods = get_all_periods()
# #                 period_to_modify = st.selectbox("Select Period to Modify:", periods)
# #                 action = st.radio("Select Action:", ["Update", "Delete"])

# #                 if action == "Update":
# #                     data = collection.find_one({"period": period_to_modify, "username": st.session_state['username']})
# #                     if data:
# #                         "---"
# #                         with st.spinner("Loading data..."):
# #                             st.empty()
# #                             with st.form("update_form"):
# #                                 st.subheader(f"Existing Data for {period_to_modify}")
# #                                 with st.expander("Current Income Data", expanded=True):
# #                                     for income in incomes:
# #                                         st.text(f"{income}: {data['incomes'].get(income, 0)} {currency}")
# #                                 with st.expander("Current Expense Data", expanded=True):
# #                                     for expense in expenses:
# #                                         st.text(f"{expense}: {data['expenses'].get(expense, 0)} {currency}")
# #                                 with st.expander("Comment", expanded=True):
# #                                     st.text(f"{data.get('comment', '')}")

# #                                 "---"
# #                                 st.subheader("Update Data")
# #                                 with st.expander("Income", expanded=False):
# #                                     update_incomes_data = {}
# #                                     for income in incomes:
# #                                         value = data["incomes"].get(income, 0)
# #                                         update_incomes_data[income] = st.number_input(f"{income}:", min_value=0, format="%i", step=10, key=f"update_{income}", placeholder="Enter the value", value=int(value))
# #                                 with st.expander("Expenses", expanded=False):
# #                                     update_expenses_data = {}
# #                                     for expense in expenses:
# #                                         value = data["expenses"].get(expense, 0)
# #                                         update_expenses_data[expense] = st.number_input(f"{expense}:", min_value=0, format="%i", step=10, key=f"update_{expense}", placeholder="Enter the value", value=int(value))
# #                                 with st.expander("Comment", expanded=False):
# #                                     update_comment = st.text_area("", placeholder="Enter a comment here...", value=data.get("comment", ""))

# #                                 "---"
# #                                 submitted = st.form_submit_button("Update Data")
# #                                 if submitted:
# #                                     with st.spinner("Updating data..."):
# #                                         incomes_data = {income: update_incomes_data[income] for income in incomes}
# #                                         expenses_data = {expense: update_expenses_data[expense] for expense in expenses}
# #                                         collection.update_one(
# #                                             {"period": period_to_modify, "username": st.session_state['username']},
# #                                             {"$set": {"incomes": incomes_data, "expenses": expenses_data, "comment": update_comment}}
# #                                         )
# #                                         st.success("Data Updated!")
# #                                         st.session_state['updated'] = True
# #                                         st.rerun()

# #                 elif action == "Delete":
# #                     st.warning(f"Are you sure you want to delete the data for {period_to_modify}? This action cannot be undone.")
# #                     confirmed = st.checkbox("Confirm Deletion")
# #                     if confirmed:
# #                         with st.spinner("Deleting data..."):
# #                             collection.delete_one({"period": period_to_modify, "username": st.session_state['username']})
# #                             st.success("Data Deleted!")
# #                             st.session_state['delete_complete'] = True
# #                             st.rerun()

# #             elif selected == "Manage Fixed Expenses":
# #                 st.header("Manage Fixed Expenses")
# #                 fixed_expenses_data = get_fixed_expenses(st.session_state['username'])

# #                 with st.form("add_fixed_expense_form"):
# #                     st.write("Add Fixed Expense:")
# #                     new_expense_name = st.text_input("Expense Name")
# #                     new_expense_value = st.text_input("Expense Value")
# #                     add_submitted = st.form_submit_button("Add Expense")
# #                     if add_submitted:
# #                         if new_expense_name and new_expense_value:
# #                             if new_expense_name in fixed_expenses_data:
# #                                 st.warning(f"Expense '{new_expense_name}' already exists. Updating its value.")
# #                             fixed_expenses_data[new_expense_name] = new_expense_value
# #                             save_fixed_expenses(st.session_state['username'], fixed_expenses_data)
# #                             st.success(f"Fixed expense '{new_expense_name}' added/updated successfully.")
# #                             st.rerun()

# #                 with st.form("delete_fixed_expense_form"):
# #                     st.write("Delete Fixed Expense:")
# #                     delete_expense_name = st.text_input("Expense Name to Delete")
# #                     delete_submitted = st.form_submit_button("Delete Expense")
# #                     if delete_submitted:
# #                         if delete_expense_name in fixed_expenses_data:
# #                             del fixed_expenses_data[delete_expense_name]
# #                             save_fixed_expenses(st.session_state['username'], fixed_expenses_data)
# #                             st.success(f"Fixed expense '{delete_expense_name}' deleted successfully.")
# #                             st.rerun()
# #                         else:
# #                             st.error(f"Expense '{delete_expense_name}' not found.")

# #                 with st.form("fixed_expenses_form"):
# #                     st.write("Current Fixed Expenses:")
# #                     for expense in fixed_expenses_data:
# #                         st.text(f"{expense}: {fixed_expenses_data[expense]}")

# #                     st.form_submit_button("Refresh")

# #             elif selected == "Predict Expenditures":
# #                 st.header("Predict Future Expenditures")
# #                 with st.spinner("Fetching past data..."):
# #                     df = fetch_past_expenses(st.session_state['username'])
# #                 fixed_expenses_data = get_fixed_expenses(st.session_state['username'])

# #                 if not df.empty:
# #                     selected_month = st.selectbox("Select Month for Prediction:", months, key="predict_month", format_func=lambda x: x.title())
# #                     selected_year = st.selectbox("Select Year for Prediction:", years, key="predict_year")

# #                     next_period = f"{selected_year}_{selected_month}"

# #                     with st.spinner("Predicting future expenditures..."):
# #                         predictions = predict_future_expenses(df, next_period, fixed_expenses_data)

# #                     if next_period in predictions:
# #                         st.subheader(f"Predicted Expenditures for {selected_month} {selected_year}")
# #                         predicted_expenses = predictions[next_period]
# #                         for expense, value in predicted_expenses.items():
# #                             st.write(f"{expense}: {float(value):.2f} {currency}")
# #                     else:
# #                         st.error("Could not generate predictions.")
# #                 else:
# #                     st.error("No past data available to analyze.")

# #             elif selected == "Export Data":
# #                 st.header("Export Data")
# #                 st.write("Click the button below to export your data to an Excel file.")
# #                 if st.button("Export to Excel"):
# #                     with st.spinner("Exporting data..."):
# #                         excel_data = export_to_excel(st.session_state['username'])
# #                         st.download_button(
# #                             label="Download Excel file",
# #                             data=excel_data,
# #                             file_name=f"{st.session_state['username']}_expenses.xlsx",
# #                             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
# #                         )

# #             elif selected == "Logout":
# #                 st.header("Logout")
# #                 st.info("You have been logged out successfully.")
# #                 st.session_state['authenticated'] = False

# # if __name__ == "__main__":
# #     threading.Thread(target=run_flask_app).start()
# #     main()


=======
>>>>>>> f6160937040bd5f32fc082c8c2c39ba8d2cd80d2
