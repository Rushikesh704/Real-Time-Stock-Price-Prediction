import tkinter as tk  
import pandas as pd  
from tkinter import ttk, messagebox 
from matplotlib.figure import Figure  
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  
from statsmodels.tsa.statespace.sarimax import SARIMAX  # Importing SARIMAX model from statsmodels
from forex_python.converter import CurrencyRates  
from datetime import datetime  
import logging  
import os  
import matplotlib.pyplot as plt 
import yfinance as yf 

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,  # Setting logging level to DEBUG
    format="%(asctime)s - %(levelname)s: %(message)s",  # Setting format for log messages
    datefmt="%Y-%m-%d %H:%M:%S"  # Setting date format
)

def get_current_stock_price(symbol): 
    """Fetches the current stock price for the given symbol."""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")  # Fetch only today's data
        current_price = data['Close'].iloc[-1]  # Get the most recent closing price
        return current_price
    except Exception as e:
        raise ValueError(f"Error fetching current price for {symbol}: {str(e)}")

def train_model(symbol): # Training the model
    """Trains a SARIMAX model using historical stock data for the given symbol."""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1y")
        df = pd.DataFrame(data['Close'])
        model = SARIMAX(df, order=(1, 1, 1), seasonal_order=(1, 1, 1, 5))
        results = model.fit()
        return results
    except Exception as e:
        raise ValueError(f"Error training model for {symbol}: {str(e)}")

def predict_price(model, days=7): # Default prediction for 7 days 
    """Predicts the stock price for the given number of days using the trained model."""
    forecast = model.get_forecast(steps=days)
    predicted_price = forecast.predicted_mean.iloc[-1]
    return predicted_price

def plot_stock_data(stock_data, symbol, predicted_price_inr):
    """Plots the historical stock data along with the predicted price."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(stock_data, label=f'{symbol} Stock Price')
    ax.axhline(y=predicted_price_inr, color='r', linestyle='--', label='Predicted Price')
    ax.set_title(f'{symbol} Stock Price Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Stock Price (INR)')
    ax.legend()
    ax.grid(True)
    return fig

class StockPredictionApp:
    def __init__(self, root):
        """Initializes the GUI application."""
        self.root = root
        self.root.title("Stock Price Prediction")  # Setting title for the window

        # Creating GUI components
        self.symbol_label = ttk.Label(root, text="Enter Stock Symbol:")
        self.symbol_entry = ttk.Entry(root)
        self.predict_button = ttk.Button(root, text="Predict & Plot", command=self.show_plot)

        self.current_price_label = ttk.Label(root, text="Current Price:")
        self.predicted_price_label = ttk.Label(root, text="Predicted Price:")
        self.suggestion_label = ttk.Label(root, text="Suggestion: ")

        # Packing GUI components
        self.symbol_label.pack(pady=10)
        self.symbol_entry.pack(pady=10)
        self.predict_button.pack(pady=10)
        self.current_price_label.pack(pady=10)
        self.predicted_price_label.pack(pady=10)
        self.suggestion_label.pack(pady=10)

        # Creating canvas for plotting
        self.canvas_frame = ttk.Frame(root)
        self.canvas_frame.pack(expand=True, fill='both')

        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        self.canvas = tk.Canvas(self.canvas_frame, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", expand=True, fill="both")

        self.scrollbar.config(command=self.canvas.yview)

    def show_plot(self):
        """Handles the "Predict & Plot" button click event."""
        symbol = self.symbol_entry.get()
        try:
            # Fetching current stock price, training model, and predicting price
            current_price = get_current_stock_price(symbol)
            model = train_model(symbol)
            predicted_price_inr = predict_price(model, days=7)

            # Updating labels with current and predicted prices
            self.current_price_label.config(text=f"Current Price: ₹{current_price:.2f}")
            self.predicted_price_label.config(text=f"Predicted Price: ₹{predicted_price_inr:.2f}")

            # Determining suggestion (whether to buy, sell, or hold)
            suggestion = self.get_suggestion(current_price, predicted_price_inr)
            self.suggestion_label.config(text=f"Suggestion: {suggestion}")

            # Logging the prediction details
            logging.info(f"Symbol: {symbol}, Current Price: {current_price:.2f}, Predicted Price: {predicted_price_inr:.2f}, Suggestion: {suggestion}")

            # Plotting
            stock_data = yf.Ticker(symbol).history(period="1y")['Close']
            fig = plot_stock_data(stock_data, symbol, predicted_price_inr)

            canvas = FigureCanvasTkAgg(fig, master=self.canvas)
            canvas.draw()

            canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

            # Centering the plot
            self.canvas.create_window(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2, window=canvas.get_tk_widget(), anchor="center")

        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            # Logging the error
            logging.error(f"Error for symbol {symbol}: {str(ve)}")

    def get_suggestion(self, current_price, predicted_price):
        """Determines the suggestion (whether to buy, sell, or hold)."""
        # Add your suggestion logic here
        if predicted_price > current_price:
            logging.debug("Suggestion: Buy")
            return "Buy"
        elif predicted_price < current_price:
            logging.debug("Suggestion: Sell")
            return "Sell"
        else:
            logging.debug("Suggestion: Hold")
            return "Hold"

if __name__ == "__main__":
    # Creating the tkinter window and initializing the GUI application
    root = tk.Tk()
    app = StockPredictionApp(root)
    root.mainloop()  # Starting the GUI event loop
