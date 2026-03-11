import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import requests
import os
import re
import dateparser

from dotenv import load_dotenv
from datetime import datetime, timedelta
from openai import OpenAI

from financial_rag import retrieve_context
from knowledge_graph import get_graph_context


# ---------------- ENV ----------------

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")


# ---------------- COMPANY EXTRACTION ----------------

def extract_company_name(question):

    prompt = f"""
Extract the publicly traded company name from the sentence.
Return ONLY the company name.

Sentence:
{question}
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )
        return response.output_text.strip()

    except:
        return None


# ---------------- TICKER RESOLUTION ----------------

def resolve_ticker(question):

    company = extract_company_name(question)

    if company is None:
        return None

    url = "https://finnhub.io/api/v1/search"

    params = {
        "q": company,
        "token": FINNHUB_API_KEY
    }

    try:

        r = requests.get(url, params=params)
        data = r.json()

        if "result" not in data:
            return None

        for item in data["result"]:

            symbol = item.get("symbol","")
            type_ = item.get("type","")

            if type_ == "Common Stock" and "." not in symbol:
                return symbol

        return data["result"][0]["symbol"]

    except:
        return None


# ---------------- ABSOLUTE DATE RANGE DETECTION ----------------

def detect_time_range(question):

    q = question.lower()

    date_matches = re.findall(
        r'(\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|'
        r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{1,2}(?:st|nd|rd|th)?\,?\s*\d{4}|'
        r'\d{1,2}\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{4}|'
        r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{4}|'
        r'\b\d{4}\b)',
        q
    )

    if len(date_matches) >= 2:

        start = dateparser.parse(date_matches[0])
        end = dateparser.parse(date_matches[1])

        if start and end:
            return start, end

    if len(date_matches) == 1:

        start = dateparser.parse(date_matches[0])

        if start:
            end = start + timedelta(days=1)
            return start, end

    return None, None


# ---------------- FREE-FORM RELATIVE TIME DETECTION ----------------

def detect_time_period(question):

    q = question.lower()

    if "today" in q:
        return "1d"

    if "yesterday" in q:
        return "2d"

    match = re.search(
        r'(?:last|past|previous|over the last|in the last)?\s*(\d+)\s*(day|days|week|weeks|month|months|year|years)',
        q
    )

    if match:

        num = int(match.group(1))
        unit = match.group(2)

        if "day" in unit:
            return f"{num}d"

        if "week" in unit:
            return f"{num*7}d"

        if "month" in unit:
            return f"{num}mo"

        if "year" in unit:
            return f"{num}y"

    if "last week" in q:
        return "7d"

    if "last month" in q:
        return "1mo"

    if "last year" in q:
        return "1y"

    return "7d"


# ---------------- STOCK DATA ----------------

def get_stock_data(ticker, start=None, end=None, period=None):

    try:

        stock = yf.Ticker(ticker)

        if start and end:
            return stock.history(start=start, end=end)

        return stock.history(period=period)

    except:
        return None


# ---------------- NEWS ----------------

def get_news(ticker, start=None, end=None, period=None):

    if start and end:

        start_date = start
        end_date = end

    else:

        days = 7

        if period:

            if period.endswith("d"):
                days = int(period.replace("d",""))

            if period.endswith("mo"):
                days = int(period.replace("mo","")) * 30

            if period.endswith("y"):
                days = int(period.replace("y","")) * 365

        start_date = datetime.today() - timedelta(days=days)
        end_date = datetime.today()

    url = "https://finnhub.io/api/v1/company-news"

    params = {
        "symbol": ticker,
        "from": start_date.strftime("%Y-%m-%d"),
        "to": end_date.strftime("%Y-%m-%d"),
        "token": FINNHUB_API_KEY
    }

    try:
        r = requests.get(url, params=params)
        data = r.json()
        return data[:10]

    except:
        return []


# ---------------- EVENT DETECTION ----------------

def detect_events(news):

    keywords = ["earnings","downgrade","upgrade","forecast","lawsuit","acquisition","merger"]

    events = []

    for article in news:
        for k in keywords:
            if k in article.lower():
                events.append(article)

    return events


# ---------------- SENTIMENT ----------------

def sentiment_agent(news):

    negative_words = ["fall","drop","downgrade","lawsuit"]

    score = 0

    for headline in news:
        for w in negative_words:
            if w in headline.lower():
                score -= 1

    if score < 0:
        return "Negative sentiment"

    return "Neutral sentiment"


# ---------------- AI SYNTHESIS ----------------

def synthesis_agent(ticker, price_info, news_info, event_info, rag_context, graph_context, sentiment):

    prompt = f"""
You are a hedge fund research analyst.

Stock: {ticker}

Knowledge Graph Context:
{graph_context}

Price Analysis:
{price_info}

News Intelligence:
{news_info}

Detected Events:
{event_info}

Historical Context:
{rag_context}

Market Sentiment:
{sentiment}

Write a concise professional explanation of the stock movement.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


# ---------------- UI ----------------

st.set_page_config(layout="wide")

st.title("📊 AI Market Intelligence Platform")

question = st.text_input("Ask a stock question")

if st.button("Analyze"):

    ticker = resolve_ticker(question)

    if ticker is None:
        st.warning("Stock not detected")
        st.stop()

    stock = yf.Ticker(ticker)

    try:
        info = stock.info
        company_name = info.get("shortName", ticker)
        sector = info.get("sector","")
        industry = info.get("industry","")
    except:
        company_name = ticker
        sector = ""
        industry = ""

    start, end = detect_time_range(question)

    if start and end:
        data = get_stock_data(ticker, start=start, end=end)
        news = get_news(ticker, start=start, end=end)
    else:
        period = detect_time_period(question)
        data = get_stock_data(ticker, period=period)
        news = get_news(ticker, period=period)


    st.subheader("Company Overview")

    col1, col2 = st.columns([3,2])

    with col1:
        st.markdown(f"### {company_name}")
        st.markdown(f"**Ticker:** {ticker}")
        st.markdown(f"**Sector:** {sector}")
        st.markdown(f"**Industry:** {industry}")

    if data is not None and not data.empty:

        data["MA20"] = data["Close"].rolling(20).mean()
        data["MA50"] = data["Close"].rolling(50).mean()

        start_price = data["Close"].iloc[0]
        end_price = data["Close"].iloc[-1]

        change = end_price - start_price
        pct = (change / start_price) * 100

        with col2:
            st.metric("Start Price", round(start_price,2))
            st.metric("End Price", round(end_price,2))
            st.metric("Change %", round(pct,2))

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="Price"
        ))

        fig.add_trace(go.Scatter(x=data.index,y=data["MA20"],name="MA20"))
        fig.add_trace(go.Scatter(x=data.index,y=data["MA50"],name="MA50"))

        fig.add_trace(go.Bar(x=data.index,y=data["Volume"],name="Volume",opacity=0.3,yaxis="y2"))

        fig.update_layout(
            template="plotly_dark",
            height=650,
            yaxis_title="Price",
            yaxis2=dict(overlaying='y',side='right',title='Volume',showgrid=False)
        )

        st.plotly_chart(fig,use_container_width=True)

    st.subheader("Market News")

    headlines = []

    for article in news[:5]:
        st.markdown(f"• {article['headline']}")
        headlines.append(article["headline"])

    events = detect_events(headlines)

    rag_context = retrieve_context(question)
    graph_context = get_graph_context(ticker)

    news_info = ". ".join(headlines[:3])
    event_info = ", ".join(events[:3])
    sentiment = sentiment_agent(headlines)

    price_info = f"Stock moved {round(pct,2)}% during the analyzed period."

    report = synthesis_agent(
        ticker,
        price_info,
        news_info,
        event_info,
        rag_context,
        graph_context,
        sentiment
    )

    st.subheader("AI Hedge Fund Research Report")

    st.write(report)
