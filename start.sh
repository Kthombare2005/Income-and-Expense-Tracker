#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Start Flask backend in the background
nohup python app.py &

# Start Streamlit frontend
streamlit run main.py --server.port $PORT --server.enableCORS false
