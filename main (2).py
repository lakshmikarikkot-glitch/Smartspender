import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="ScholarSpend AI | Student Expense Planner", layout="wide")

# Custom CSS for the Cinematic/High-Contrast Look
st.markdown("""
    <style>
    .main { background-color: #121212; }
    .stMetric { 
        background-color: #1E1E1E; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #333; 
    }
    .ai-box { 
        background-color: #1E1E1E; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #BB86FC; 
        color: #E0E0E0;
        font-family: 'Segoe UI', sans-serif;
    }
    </style>
    """, unsafe_allow_stdio=True)

# --- State Management ---
# Using session_state ensures data persists during the Streamlit rerun cycle
if 'expenses' not in st.session_state:
    st.session_state.expenses = []
if 'budget' not in st.session_state:
    st.session_state.budget = 0.0

# --- Sidebar: Input Area ---
with st.sidebar:
    st.title("✨ ScholarSpend AI")
    st.subheader("Student Expense Planner")
    
    # Budget Input
    new_budget = st.number_input("Monthly Budget ($)", min_value=0.0, value=st.session_state.budget, step=10.0)
    if st.button("Set Budget"):
        st.session_state.budget = new_budget
        st.success(f"Budget updated to ${new_budget:.2f}")

    st.divider()

    # Expense Input Form
    with st.form("expense_form", clear_on_submit=True):
        st.write("### Add New Expense")
        item = st.text_input("Expense Item (e.g., Coffee, Textbooks)")
        amount = st.number_input("Amount ($)", min_value=0.01, step=1.0)
        category = st.selectbox("Category", ["Food", "Rent", "Study Materials", "Fun", "Transport", "Other"])
        
        if st.form_submit_button("Add Expense"):
            if item and amount > 0:
                new_expense = {
                    "Item": item,
                    "Amount": amount,
                    "Category": category,
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.expenses.append(new_expense)
            else:
                st.error("Please enter both an item name and a valid amount.")

# --- Main Dashboard ---
col1, col2 = st.columns([2, 1])

with col1:
    # Calculations
    total_spent = sum(ex['Amount'] for ex in st.session_state.expenses)
    balance = st.session_state.budget - total_spent
    
    # Top Stats Cards
    c1, c2 = st.columns(2)
    c1.metric("Total Spent", f"${total_spent:.2f}")
    c2.metric("Remaining Balance", f"${balance:.2f}", delta=balance, delta_color="normal")

    # AI Insights Panel
    st.markdown("### ✨ AI SAVINGS ADVISOR")
    
    if not st.session_state.expenses:
        insight_text = "👋 Welcome! Start by adding your budget and expenses to get personalized AI financial tips."
    else:
        food_total = sum(e['Amount'] for e in st.session_state.expenses if e['Category'] == "Food")
        fun_total = sum(e['Amount'] for e in st.session_state.expenses if e['Category'] == "Fun")

        # Fixed multi-line string logic for AI feedback
        if st.session_state.budget > 0 and total_spent >= (st.session_state.budget * 0.8):
            insight_text = "⚠️ Warning: You've used over 80% of your budget. High risk of overspending this month!"
        elif st.session_state.budget > 0 and food_total > (st.session_state.budget * 0.4):
            insight_text = "🍔 Tip: Your food spending is quite high. Consider meal-prepping to save significantly."
        elif fun_total > food_total:
            insight_text = "🎬 Insight: You're spending more on entertainment than essentials. Check the 50/30/20 rule."
        else:
            insight_text = "✅ Great job! Your spending pattern looks sustainable for a student budget."

    st.markdown(f"<div class='ai-box'>{insight_text}</div>", unsafe_allow_stdio=True)

with col2:
    # Chart Area
    st.markdown("### Spending Breakdown")
    if st.session_state.expenses:
        df = pd.DataFrame(st.session_state.expenses)
        cat_data = df.groupby('Category')['Amount'].sum()

        fig, ax = plt.subplots(figsize=(5, 5))
        fig.patch.set_facecolor('#1E1E1E')
        ax.set_facecolor('#1E1E1E')
        
        # High-contrast palette
        colors = ['#BB86FC', '#03DAC6', '#CF6679', '#F48FB1', '#90CAF9', '#A5D6A7']
        ax.pie(cat_data, labels=cat_data.index, autopct='%1.1f%%', colors=colors, 
               textprops={'color':"w", 'fontsize': 10}, startangle=140)
        st.pyplot(fig)
        plt.close(fig) # Memory management
    else:
        st.info("No expense data available for visualization.")

# --- Transaction History ---
st.divider()
st.subheader("Recent Transactions")
if st.session_state.expenses:
    # Convert to DataFrame and reverse to show most recent at top
    history_df = pd.DataFrame(st.session_state.expenses)
    st.dataframe(history_df.iloc[::-1], use_container_width=True)
    
    # Download Button for the Data
    csv = history_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Expenses as CSV",
        data=csv,
        file_name='scholar_spend_report.csv',
        mime='text/csv',
    )
else:
    st.write("No transactions recorded yet.")