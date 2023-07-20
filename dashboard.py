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
    initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': 'https://www.github.com/moakal',
        'About': 'https://www.github.com/moakal',
    }
)

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Sidebar inputs for stock, start date, end date, and further news queries
with st.sidebar:
    stock = st.text_input('Enter stock', 'BLK')
    startDate = st.date_input('Start date', datetime.date(2013, 1, 1))
    endDate = st.date_input('End date', datetime.date(2023, 1, 1))
    query = st.text_input('News query', 'BlackRock')

# Fetch historical stock data using yfinance
data = yf.download(stock, startDate, endDate)

data['Returns'] = data['Close'].pct_change() * 100
volatility = data['Returns'].std()

highest = max(data['Close'])
lowest = min(data['Close'])

# Prettify table by formatting date
data.reset_index(inplace=True)
data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')

# Create and display the stock price graph using Plotly
st.title(stock)
data['Adj Close'].plot()
graph = px.line(data, x=data['Date'], y=data['Close'])
st.plotly_chart(graph)

# Display metrics in columns
col1, col2, col3 = st.columns(3)
col1.metric(label='Volatility*', value=round(volatility, 3))
col2.metric(label='Highest', value=round(highest, 3))
col3.metric(label='Lowest', value=round(lowest, 3))

# Table of historical stock data
with st.expander('View table'):
    st.table(data)

# Function to scrape news related to the stock
def scrapeNews(stock, startDate, endDate):
    url = f"https://news.google.com/rss/search?q={stock}&hl=en-US&gl=US&ceid=US:en"

    feed = feedparser.parse(url)
    entries = feed.entries

    headlines = []
    dates = []
    links = []
    timezone = pytz.timezone('UTC')  # Set the timezone to match the timestamps from the news articles

    for entry in entries:
        timestamp = pd.to_datetime(entry.published).tz_convert(timezone)
        if startDate <= timestamp.tz_localize(None) <= endDate:
            headlines.append(entry.title)
            dates.append(timestamp.date())
            links.append(entry.link)

    data = {'Date': dates, 'Headline': headlines, 'Link': links}
    df = pd.DataFrame(data)
    if not df.empty:
        df = df.sort_values(by='Date', ascending=False).reset_index(drop=True)

    return df

# Load and display news on button click
if st.button('Load news'):
    news = scrapeNews(stock, startDate, endDate)
    newsq = scrapeNews(query, startDate, endDate)

    news['Headline'] = news.apply(lambda row: f'<a href="{row["Link"]}" target="_blank">&#128279;</a> {row["Headline"]}', axis=1)
    newsq['Headline'] = newsq.apply(lambda row: f'<a href="{row["Link"]}" target="_blank">&#128279;</a> {row["Headline"]}', axis=1)

    # st.table(news)
    # st.subheader('News query')
    # st.table(newsq)

    st.subheader(stock + ' query')
    st.write(news.drop(columns=['Link']).to_html(escape=False, index=False), unsafe_allow_html=True)
    st.write('')
    st.subheader('News query')
    st.write(newsq.drop(columns=['Link']).to_html(escape=False, index=False), unsafe_allow_html=True)

st.write('\* Volatility calculated using standard deviation of returns')
