🚀 Autonomous AI Investment Advisor
News-Aware, Strategy-Driven, Multi-Iteration Stock Selection Engine
📌 Overview

This project is a fully autonomous AI-driven investment advisory system designed to generate high-confidence stock recommendations for the Indian equity market (NSE/BSE) — with future support for global markets.

Unlike traditional screeners or static models, this system combines:

📊 Fundamental screening (configurable by client)
📰 Real-time global + Indian news intelligence
🌐 Web-scale information discovery
🧠 LLM-powered reasoning & strategy simulation
🔁 Multi-iteration consensus-based stock selection
💼 Dynamic portfolio allocation & rebalancing
📈 Continuous performance tracking via virtual trading
🧠 Core Philosophy

“Not just data-driven. Context-aware. Strategy-aligned. Continuously learning.”

This system mimics how elite investors think:

Filter → Analyze → Validate → Allocate → Track → Adapt
🎯 Objectives
Identify high-quality stocks using fundamental filters
Incorporate macro + micro news signals
Apply proven investor strategies
Reduce randomness via multi-iteration consensus
Simulate real-world performance
Enable future transition to real capital deployment
⚙️ High-Level Architecture
What is this?
🔍 Step 1: Stock Universe & Fundamental Screening
📥 Data Source
NSE / BSE listed stocks
Currently extracted via scraping: Screener.in
(Temporary solution due to lack of free structured APIs)
⚙️ Client-Configurable Filters

Users define their own investment criteria:

filters:
  promoter_holding: "> 51"
  debtor_days: "< 90"
  sales_growth_5y: "> 10"
  profit_growth_5y: "> 12"
🎯 Output
Filtered universe → ~50 high-quality stocks
📰 Step 2: News & Information Intelligence Layer
🌐 Sources
APIs Used:
NEWSAPI
MARKETAUX
FINNHUB
NEWSDATA
WORLDNEWSAPI
Categories:
🌍 Global Headlines
💰 Financial & Economic News
🇮🇳 India-specific News
📊 Business & Market News
🔎 Web Discovery
Firecrawl-based web search
Extracts:
Hidden or niche news
Company-specific developments
Sector-level disruptions
🧠 Signal Extraction

LLM filters raw data to:

Remove noise ❌
Extract impactful events ✅
Identify:
Market-moving signals
Sentiment shifts
Risk triggers
Opportunity catalysts
🧠 Step 3: Strategy-Driven LLM Decision Engine
🎓 Embedded Investment Strategies

System leverages philosophies inspired by:

Warren Buffett → Value Investing
Peter Lynch → Growth at Reasonable Price
Ray Dalio → Macro-driven allocation
George Soros → Reflexivity & momentum
⚙️ Model Configurability
Supports multiple frontier models (via flag)
Strategy selection:
Single strategy
Hybrid strategies
Weighted strategy blending
🔁 Step 4: Multi-Iteration Stock Selection

Instead of a single pass:

🔄 Process
Run stock selection N times (configurable)
Each iteration:
Re-analyzes same dataset
Applies reasoning independently
🧮 Consensus Mechanism
Stocks selected across iterations are counted
Final selection based on:
Frequency of selection
Confidence score
🎯 Output
{
  "final_stocks": ["StockA", "StockB", "StockC", "StockD", "StockE"]
}
💼 Step 5: Portfolio Allocation Engine

Once stocks are selected:

💰 Input
Total capital (e.g., ₹10,000)
🧠 Allocation Logic

LLM determines:

Risk distribution
Conviction level
Diversification
📊 Example
{
  "investment": 10000,
  "allocation": [
    {"stock": "A", "amount": 2500},
    {"stock": "B", "amount": 2000},
    {"stock": "C", "amount": 2000},
    {"stock": "D", "amount": 1500},
    {"stock": "E", "amount": 2000}
  ]
}
📉 Step 6: Virtual Trading Engine
📥 Execution
Simulates buy at current market price
Stores:
Stock
Price
Quantity
Timestamp
🗃 Storage
Database / File system
Separate logs for:
Daily trades
Portfolio states
📈 Step 7: Performance Tracking
📊 Daily Evaluation
Compare:
Yesterday’s buy price
Today’s market price
🧮 Formula
Return = (Current Price - Buy Price) × Quantity
📅 Metrics
Daily return
Cumulative return
Portfolio growth
Strategy performance
🔄 Step 8: Rebalancing Engine
📥 Inputs
Current portfolio
Latest news signals
Updated analysis
⚖️ Decision Logic
What is this?
🔁 Actions
Add new stocks
Remove weak performers
Adjust allocation weights
🔁 Continuous Learning Loop
Diagram is not supported.
What is this?
⚡ Key Features
✅ Client-configurable screening filters
🌍 Multi-source news intelligence
🔎 Web-scale discovery (Firecrawl)
🧠 Strategy-driven LLM reasoning
🔁 Multi-iteration consensus selection
💼 Intelligent portfolio allocation
📉 Virtual trading simulation
📊 Performance tracking
🔄 Daily rebalancing
🛠️ Tech Stack
Backend: Python (Async architecture)
Data Modeling: Pydantic
Concurrency: AsyncIO
LLM Integration: Multi-model support
Scraping: Screener.in + Firecrawl
APIs: News providers
Storage: DB / File-based logs
⚠️ Current Limitations
❌ No official fundamental API (scraping dependency)
❌ No real-time trading
❌ No intraday / derivatives support
❌ Latency in news ingestion vs HFT systems
🚀 Future Roadmap
🌍 Market Expansion
US (NASDAQ, NYSE)
EU, Asia markets
📊 Advanced Analytics
Technical indicators (RSI, MACD)
Risk-adjusted metrics (Sharpe Ratio)
Factor investing models
🧠 AI Enhancements
Reinforcement learning loop
Self-improving strategy selection
Memory-based decision refinement
💰 Production Deployment
Broker API integration
Live trading execution
Risk management layer
📌 Example End-to-End Flow
What is this?
🧾 Summary

This system is not just a stock picker — it is a:

🧠 Reasoning engine
🌍 Market-aware intelligence system
🔁 Self-evolving investment loop

It:

Filters intelligently
Thinks strategically
Acts consistently
Learns continuously
⚠️ Disclaimer

This system is for research and simulation purposes only.
It does not constitute financial advice.
Real trading involves risk.

⭐ Contribution

Contributions, ideas, and improvements are welcome!

📜 License

MIT License

💡 Final Thought

“Alpha comes not from more data, but from better interpretation of data.”