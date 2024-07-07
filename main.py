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
            with st.form("entry_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                col1.selectbox("Select Month:", months, key="month", format_func=lambda x: x.title())
                col2.selectbox("Select Year:", years, key="year")

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
                        period = str(st.session_state["year"]) + "_" + str(st.session_state["month"])
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
                        col1.metric("Total Income", f"{total_income} {currency}")
                        col2.metric("Total Expense", f"{total_expense} {currency}")
                        col3.metric("Total Budget", f"{remaining_budget} {currency}")
                        st.text(f"Comment: {comment}")

                        # Create sankey chart
                        label = list(incomes_data.keys()) + ["Total Income"] + list(expenses_data.keys())
                        source = list(range(len(incomes_data))) + [len(incomes_data)] * len(expenses_data)
                        target = [len(incomes_data)] * len(incomes_data) + [label.index(expense) for expense in expenses_data.keys()]
                        value = list(incomes_data.values()) + list(expenses_data.values())

                        # Data to dict, dict to sankey
                        link = dict(source=source, target=target, value=value)
                        node = dict(label=label, pad=20, thickness=30, color="#4e67c8")
                        data = go.Sankey(link=link, node=node)

                        # Plot it!
                        fig = go.Figure(data)
                        fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("No data found for the selected period")

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
                            with st.expander("Income", expanded=True):
                                update_incomes_data = {}
                                for income in incomes:
                                    update_incomes_data[income] = st.number_input(f"{income}:", min_value=0, format="%i", step=10, key=f"update_{income}", placeholder="Enter the value", value=data["incomes"].get(income, 0))
                            with st.expander("Expenses", expanded=True):
                                update_expenses_data = {}
                                for expense in expenses:
                                    update_expenses_data[expense] = st.number_input(f"{expense}:", min_value=0, format="%i", step=10, key=f"update_{expense}", placeholder="Enter the value", value=data["expenses"].get(expense, 0))
                            with st.expander("Comment", expanded=True):
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
                confirmed = st.checkbox("Confirm Deletion")
                if confirmed:
                    with st.spinner("Deleting data..."):
                        # Delete data from MongoDB
                        collection.delete_one({"period": period_to_modify, "username": st.session_state['username']})
                        st.success("Data Deleted!")

        elif selected == "Logout":
            st.session_state['authenticated'] = False
            st.success("Logged out successfully!")
            st.experimental_rerun()

if __name__ == "__main__":
    # Run Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    # Run Streamlit app
    main()
