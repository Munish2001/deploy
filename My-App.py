# app.py

import streamlit as st

# Example function
def greet_user(name):
    return f"Hello, {name}! 👋"

# Streamlit UI
st.title("My Streamlit App with Functions")

# Input from user
name = st.text_input("Enter your name:")

# Button to trigger function
if st.button("Greet Me"):
    if name:
        greeting = greet_user(name)
        st.success(greeting)
    else:
        st.warning("Please enter a name.")
