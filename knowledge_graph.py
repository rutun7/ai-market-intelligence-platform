financial_graph = {

"NVDA": {
"sector": "Semiconductors",
"industry": "AI chips",
"related_companies": ["AMD","INTC","TSM"],
"indices": ["NASDAQ"]
},

"TSLA": {
"sector": "Electric Vehicles",
"industry": "Automotive",
"related_companies": ["RIVN","NIO","BYD"],
"indices": ["NASDAQ"]
},

"AMZN": {
"sector": "Technology",
"industry": "Cloud Computing",
"related_companies": ["MSFT","GOOGL"],
"indices": ["NASDAQ"]
}

}


def get_graph_context(ticker):

    ticker = ticker.upper()

    if ticker in financial_graph:

        data = financial_graph[ticker]

        return f"""
Sector: {data['sector']}
Industry: {data['industry']}
Related Companies: {', '.join(data['related_companies'])}
Indices: {', '.join(data['indices'])}
"""

    return "No structured graph relationships available."
