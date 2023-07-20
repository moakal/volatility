import datetime
import feedparser
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import pytz
import streamlit as st
import streamlit_pandas as sp
import streamlit.components.v1 as components
import yfinance as yf


# Set page configuration and style
st.set_page_config(
    page_title="Volatility checker",
    page_icon="📈",
    initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': 'https://www.github.com/moakal',
        'About': 'https://www.github.com/moakal',
    }
)

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Sidebar inputs for stock, start date, and end date
with st.sidebar:
    stock = st.text_input('Enter stock', 'BLK')
    startdate = st.date_input('Start date', datetime.date(2013, 1, 1))
    enddate = st.date_input('End date', datetime.date(2023, 1, 1))

# Fetch historical stock data using yfinance
data = yf.download(stock, start=startdate, end=enddate)
volatility = data['Adj Close'].std()
highest = max(data['Adj Close'])
lowest = min(data['Adj Close'])

# Prettify table by formatting date
data.reset_index(inplace=True)
data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')

# Create and display the stock price graph using Plotly
st.title(stock)
data['Adj Close'].plot()
graph = px.line(data, x=data.index, y=data['Adj Close'])
st.plotly_chart(graph)

# Display metrics in columns
col1, col2, col3 = st.columns(3)
col1.metric(label='Volatility', value=round(volatility, 3))
col2.metric(label='Highest', value=round(highest, 3))
col3.metric(label='Lowest', value=round(lowest, 3))

# Table of historical stock data
with st.expander('View table'):
    st.table(data)

# Function to scrape news related to the stock
def scrape_news(stock, startdate, enddate):
    url = f"https://news.google.com/rss/search?q={stock}&hl=en-US&gl=US&ceid=US:en"

    feed = feedparser.parse(url)
    entries = feed.entries

    headlines = []
    dates = []
    timezone = pytz.timezone('UTC')  # Set the timezone to match the timestamps from the news articles

    for entry in entries:
        timestamp = pd.to_datetime(entry.published).tz_convert(timezone)
        if startdate <= timestamp.tz_localize(None) <= enddate:
            headlines.append(entry.title)
            dates.append(timestamp.date())  # Extract only the date component

    data = {'Date': dates, 'Headline': headlines}
    df = pd.DataFrame(data)
    if not df.empty:
        df = df.sort_values(by='Date', ascending=False).reset_index(drop=True)

    return df

# Load and display news on button click
if st.button('Load news'):
    news_df = scrape_news(stock, startdate, enddate)
    st.table(news_df)
