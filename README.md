# AI Market Intelligence Platform

## Overview

The **AI Market Intelligence Platform** is an AI-powered application that analyzes stock market movements and explains **why a stock price changed during a specific time period**.

Instead of manually reviewing multiple financial sources, users can ask **natural language questions** such as:

- "What happened to Bank of America in the last 12 days?"
- "How did Apple perform in the last 3 months?"
- "Why did Tesla stock move last week?"

The platform retrieves **stock price data, market news, and contextual information**, then generates an **AI-driven explanation of the stock movement**.

---

## Key Features

### Natural Language Stock Queries
Users can ask questions in free-form language.

Example:

```
What happened to Bank of America in the last 12 days?
```

The system interprets the question and determines the correct company and time range.

---

### Dynamic Time Interpretation

The platform understands flexible time expressions such as:

- Last 7 days
- Last 2 weeks
- Last 3 months
- Last 1 year
- Today

This allows users to analyze market movements without specifying exact dates.

---

### Financial Data Retrieval

The system retrieves stock price data using **Yahoo Finance (yfinance)**.

It calculates indicators such as:

- Moving averages (MA20, MA50)
- Price changes over time
- Volume trends

---

### Financial News Context

The system retrieves relevant financial news using the **Finnhub API** to provide context for market movements.

---

### Retrieval Augmented Generation (RAG)

The platform uses **RAG (Retrieval Augmented Generation)** to combine:

1. Stock price data
2. Financial news context
3. AI reasoning using large language models

FAISS is used for **vector search and contextual retrieval**.

---

## Architecture

The system follows this pipeline:

```
User Question
      ↓
Time Interpretation
      ↓
Stock Data Retrieval (Yahoo Finance)
      ↓
Financial News Retrieval (Finnhub)
      ↓
Vector Search (FAISS)
      ↓
Context Engineering
      ↓
LLM Explanation Generation
      ↓
AI Market Intelligence Output
```

---

## Tech Stack

- Python
- Streamlit
- LangChain
- OpenAI
- FAISS
- Yahoo Finance API (yfinance)
- Finnhub API
- Pandas
- NumPy
- python-dotenv
- dateparser

---

## Installation

Clone the repository:

```
git clone https://github.com/YOUR_USERNAME/ai-market-intelligence-platform.git
```

Navigate to the project folder:

```
cd ai-market-intelligence-platform
```

Install dependencies:

```
pip install -r requirements.txt
```

---

## API Setup

This project requires API keys.

### OpenAI API

Create an API key at:

https://platform.openai.com/api-keys

### Finnhub API

Create an API key at:

https://finnhub.io

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key
FINNHUB_API_KEY=your_finnhub_api_key
```

---

## Running the Application

Run the Streamlit application:

```
streamlit run app.py
```

Then open the browser URL shown in the terminal.

---

## Example Use Case

User Query:

```
What happened to Bank of America in the last 12 days?
```

The system will:

1. Identify the stock ticker
2. Retrieve stock data
3. Retrieve financial news
4. Retrieve contextual information using FAISS
5. Generate an AI explanation of the stock movement

---

## Business Value

The **AI Market Intelligence Platform** helps investors, analysts, and researchers quickly understand **what caused stock market movements**.

Instead of manually reviewing multiple financial data sources, the platform automatically combines:

- Stock market data
- Financial news
- AI reasoning

This reduces analysis time and improves **decision-making speed in financial research workflows**.

---

## Project Structure

```
ai-market-intelligence-platform
│
├── app.py
├── financial_rag.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env.example
```

---

## Future Improvements

- Real-time financial news integration
- Advanced technical indicators
- Multi-stock comparison
- Market sentiment analysis
- Portfolio analytics

---

## Author

**Rutunjay Chundur**

Data Analytics professional focused on translating **data into actionable business insights using analytics, AI, and intelligent data systems**.
