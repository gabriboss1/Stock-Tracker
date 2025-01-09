from flask import Flask, render_template, request, jsonify
import yfinance as yf  # yfinance (Yahoo Finance) for fetching stock data

app = Flask(__name__)

# Latest price and opening price
def get_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)  # Ticker for the given symbol
        data = stock.history(period="1d", interval="1m")  # Historical data for the last day with 1 minute intervals
        if data.empty:  # Check if there is data
            return None, None  # Return None if there is no data
        latest_price = data["Close"].iloc[-1]  # Latest closing price
        opening_price = data["Open"].iloc[0]  # Opening price
        return latest_price, opening_price  # Return latest price and opening price
    except Exception as e:  # Catch exceptions
        print(f"Error fetching stock price: {e}")  # Print error
        return None, None  # Return None if error occurs 

# Get the price change over the last 5 days
def get_stock_change(symbol):
    try:
        stock = yf.Ticker(symbol)  # Ticker for the given symbol
        data = stock.history(period="5d")  # Historical data for the last 5 days
        if data.empty or len(data) < 2:  # Check if the data is empty or has less than 2 entries
            return None, None, None  # Return None if no data is found
        latest_price = data["Close"].iloc[-1]  # Latest closing price
        previous_price = data["Close"].iloc[-2]  # Previous closing price
        change = latest_price - previous_price  # Calculate price change
        percentage_change = (change / previous_price) * 100  # Calculate percentage change
        direction = "up" if change > 0 else "down"  # Determine the direction of change
        return latest_price, direction, f"{percentage_change:.2f}%"  # Return latest price, direction change, percentage change
    except Exception as e:  # Catch exceptions
        print(f"Error fetching stock change: {e}")  # Print error
        return None, None, None  # Return None if error occurs

@app.route("/")  # Define the route for the home page
def index():
    return render_template("index.html")  # Render the index.html template

@app.route("/get_price", methods=["POST"])
def get_price():
    symbol = request.form.get("symbol")
    latest_price, opening_price = get_stock_price(symbol)
    if latest_price is None or opening_price is None:
        return jsonify({"error": "Error fetching stock price"}), 400
    return jsonify({"price": f"${latest_price:.2f}", "opening_price": f"${opening_price:.2f}"})

@app.route("/get_chart", methods=["POST"])  # Define the route for getting the stock chart, only allow POST
def get_chart():
    symbol = request.form.get("symbol")  # Get stock symbol
    timeframe = request.form.get("timeframe")  # Get timeframe
    try:
        stock = yf.Ticker(symbol)  # Create a Ticker the given symbol
        data = stock.history(period=timeframe)  # Get stock's historical data for the given timeframe
        if data.empty:  # Check if the data is empty
            return jsonify({"error": "No data found"}), 400  # Return an error message if no data is found
        chart_data = [{"date": str(date.date()), "close": row["Close"]} for date, row in data.iterrows()]  # Format chart data, list of dictionaries
        return jsonify(chart_data)  # Return chart data as JSON
    except Exception as e:  # Catch exceptions
        return jsonify({"error": str(e)}), 400  # Return an error message if an error occurs
        # Return the error message as JSON with status code 400 for terminal and debugging purposes

@app.route("/get_notable")  # Define the route for stocks for the slider
def get_notable():
    notable_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "JPM", "BRK-B","QQQ", "SPY"]
    notable_stocks = []  # Initialize list to store stocks
    for symbol in notable_symbols:  # Loop through each symbol
        price, direction, percentage = get_stock_change(symbol)  # Get stock change
        if price is not None:  # Check if price is not None
            notable_stocks.append({  # Append data to the stocks list (list of dictionaries)
                "symbol": symbol,
                "price": f"{price:.2f}",
                "direction": direction,
                "percentage": percentage
            })
    return jsonify(notable_stocks)  # Return notable stocks as JSON

if __name__ == "__main__":
    app.run(debug=True)  # Run app in debug mode
