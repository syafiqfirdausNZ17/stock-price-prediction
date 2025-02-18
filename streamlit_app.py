{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "361dcdd3-b729-4455-a5b1-000587c47c9b",
   "metadata": {},
   "outputs": [],
   "source": [
    "import streamlit as st\n",
    "import numpy as np\n",
    "import pandas as pd\n",
    "import yfinance as yf\n",
    "import datetime\n",
    "import tensorflow as tf\n",
    "from tensorflow.keras.models import Sequential\n",
    "from tensorflow.keras.layers import LSTM, Dense, Dropout\n",
    "from tensorflow.keras import Input\n",
    "from sklearn.preprocessing import MinMaxScaler\n",
    "from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer\n",
    "import feedparser\n",
    "import matplotlib.pyplot as plt\n",
    "\n",
    "# Dictionary to map stock tickers to company names\n",
    "stock_names = {\"SIME\": \"4197.KL\"}\n",
    "\n",
    "# Streamlit UI\n",
    "st.title(\"Stock Price Prediction & Sentiment Analysis\")\n",
    "\n",
    "# Stock symbol selection\n",
    "stock_symbol = st.selectbox(\"Select a stock:\", list(stock_names.values()))\n",
    "\n",
    "# Date inputs for the time period of stock data\n",
    "start_date = st.date_input(\"Start Date\", datetime.date(2005, 1, 1))\n",
    "end_date = st.date_input(\"End Date\", datetime.date.today())\n",
    "\n",
    "# Button to trigger stock data fetching and prediction\n",
    "if st.button(\"Fetch & Predict\"):\n",
    "    # Fetch stock data from Yahoo Finance\n",
    "    st.write(\"Fetching stock data...\")\n",
    "    df = yf.download(stock_symbol, start=start_date, end=end_date)\n",
    "    \n",
    "    if df.empty:\n",
    "        st.error(\"No stock data found! Please check the ticker symbol.\")\n",
    "    else:\n",
    "        st.success(\"Stock data retrieved successfully!\")\n",
    "\n",
    "        # Display the stock price history\n",
    "        st.subheader(\"Stock Price History\")\n",
    "        st.line_chart(df[\"Close\"])\n",
    "\n",
    "        # Function to fetch and analyze news sentiment\n",
    "        st.write(\"Fetching news data...\")\n",
    "        def get_google_news(ticker):\n",
    "            company_name = stock_names.get(ticker, ticker)\n",
    "            url = f\"https://news.google.com/rss/search?q={company_name}+stock+share+price+Bursa+Malaysia+financial&hl=en-US&gl=US&ceid=US:en\"\n",
    "            \n",
    "            articles = []\n",
    "            analyzer = SentimentIntensityAnalyzer()\n",
    "            feed = feedparser.parse(url)\n",
    "\n",
    "            for entry in feed.entries[:30]:\n",
    "                sentiment_score = analyzer.polarity_scores(entry.title)['compound']\n",
    "                articles.append({\n",
    "                    \"title\": entry.title,\n",
    "                    \"published\": entry.get(\"published\", \"No Date Available\"),\n",
    "                    \"sentiment_score\": sentiment_score\n",
    "                })\n",
    "            \n",
    "            return articles\n",
    "        \n",
    "        news_articles = get_google_news(stock_symbol)\n",
    "        if news_articles:\n",
    "            df_news = pd.DataFrame(news_articles)\n",
    "            st.subheader(\"News Sentiment Analysis\")\n",
    "            st.dataframe(df_news)\n",
    "        else:\n",
    "            st.warning(\"No relevant news found!\")\n",
    "\n",
    "        # Train LSTM model for stock price prediction\n",
    "        st.write(\"Training LSTM model...\")\n",
    "\n",
    "        scaler = MinMaxScaler(feature_range=(0, 1))\n",
    "        df_scaled = scaler.fit_transform(df[['Close']])\n",
    "\n",
    "        X_train, y_train = [], []\n",
    "        for i in range(60, len(df_scaled)):\n",
    "            X_train.append(df_scaled[i-60:i, 0])\n",
    "            y_train.append(df_scaled[i, 0])\n",
    "\n",
    "        X_train, y_train = np.array(X_train), np.array(y_train)\n",
    "        X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))\n",
    "\n",
    "        model = Sequential([\n",
    "            Input(shape=(X_train.shape[1], 1)),\n",
    "            LSTM(units=50, return_sequences=True),\n",
    "            Dropout(0.2),\n",
    "            LSTM(units=50, return_sequences=False),\n",
    "            Dropout(0.2),\n",
    "            Dense(units=1)\n",
    "        ])\n",
    "\n",
    "        model.compile(optimizer='adam', loss='mean_squared_error')\n",
    "        model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=0)\n",
    "\n",
    "        # Predict future stock price\n",
    "        last_60_days = df_scaled[-60:]\n",
    "        X_test = np.reshape(last_60_days, (1, last_60_days.shape[0], 1))\n",
    "        predicted_price = model.predict(X_test)\n",
    "        predicted_price = scaler.inverse_transform(predicted_price)\n",
    "\n",
    "        st.subheader(\"Stock Price Prediction\")\n",
    "        st.write(f\"Predicted Closing Price: **{predicted_price[0][0]:.2f} MYR**\")\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
