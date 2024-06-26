import calendar
from datetime import datetime
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb+srv://Nexus_Coder:Ketan%402005@expensetracker.ddtuk3v.mongodb.net/?retryWrites=true&w=majority&appName=ExpenseTracker")
db = client["ExpenseTracker"]
collection = db["expenses"]

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

hide_st_style = """
                <style>
                #MainMenu {visibility:hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)

selected = option_menu(
    menu_title=None,
    options=["Data Entry", "Data Visualization"],
    icons=["pencil-fill", "bar-chart-fill"],
    orientation="horizontal",
)

def get_all_periods():
    periods = collection.distinct("period")
    return periods

if selected == "Data Entry":
    st.header(f"Data Entry in {currency}")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox("Select Month:", months, key="month")
        col2.selectbox("Select Year:", years, key="year")

        "---"
        with st.expander("Income"):
            for income in incomes:
                st.number_input(f"{income}:", min_value=0, format="%i", step=10, key=income)
        with st.expander("Expenses"):
            for expense in expenses:
                st.number_input(f"{expense}:", min_value=0, format="%i", step=10, key=expense)
        with st.expander("Comment"):
            comment = st.text_area("", placeholder="Enter a comment here...")

        "---"
        submitted = st.form_submit_button("Save Data")
        if submitted:
            period = str(st.session_state["year"]) + "_" + str(st.session_state["month"])
            incomes_data = {income: st.session_state[income] for income in incomes}
            expenses_data = {expense: st.session_state[expense] for expense in expenses}

            # Save data to MongoDB
            entry = {
                "period": period,
                "incomes": incomes_data,
                "expenses": expenses_data,
                "comment": comment
            }
            collection.insert_one(entry)

            st.write(f"Income: {incomes_data}")
            st.write(f"Expenses: {expenses_data}")
            st.success("Data Saved!")

if selected == "Data Visualization":
    st.header("Data Visualization")
    with st.form("saved_periods"):
        # Get periods from database
        periods = get_all_periods()
        period = st.selectbox("Select Period:", periods)
        submitted = st.form_submit_button("Plot Period")
        if submitted:
            # Get data from database
            data = collection.find_one({"period": period})
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

# Footer
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("Developed by Ketan Thombare ❤️", unsafe_allow_html=True)
