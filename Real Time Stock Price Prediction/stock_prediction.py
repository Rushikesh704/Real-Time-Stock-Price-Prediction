import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from statsmodels.tsa.statespace.sarimax import SARIMAX
from forex_python.converter import CurrencyRates
from datetime import datetime
import logging
import os
import matplotlib.pyplot as plt
from tkinter import ttk
import yfinance as yf
import pandas as pd

# Set up logging
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
log_file = os.path.join(log_folder, "stock_prediction.log")

logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1y")
        return data['Close']
    except Exception as e:
        raise ValueError(f"Error fetching data for {symbol}: {str(e)}")

def get_exchange_rate():
    c = CurrencyRates()
    exchange_rate = c.get_rate('USD', 'INR')
    return exchange_rate

def train_model(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1y")
        df = pd.DataFrame(data['Close'])
        model = SARIMAX(df, order=(1, 1, 1), seasonal_order=(1, 1, 1, 5))
        results = model.fit()
        return results
    except Exception as e:
        raise ValueError(f"Error training model for {symbol}: {str(e)}")

def predict_price(model, days=1):
    forecast = model.get_forecast(steps=days)
    predicted_price = forecast.predicted_mean.iloc[-1]
    return predicted_price

def plot_stock_data(stock_data, symbol, predicted_price_inr):
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
        self.root = root
        self.root.title("Stock Price Prediction")

        self.symbol_label = ttk.Label(root, text="Enter Stock Symbol:")
        self.symbol_entry = ttk.Entry(root)
        self.predict_button = ttk.Button(root, text="Predict & Plot", command=self.show_plot)

        self.current_price_label = ttk.Label(root, text="Current Price:")
        self.predicted_price_label = ttk.Label(root, text="Predicted Price:")
        self.suggestion_label = ttk.Label(root, text="Suggestion: ")

        self.symbol_label.pack(pady=10)
        self.symbol_entry.pack(pady=10)
        self.predict_button.pack(pady=10)
        self.current_price_label.pack(pady=10)
        self.predicted_price_label.pack(pady=10)
        self.suggestion_label.pack(pady=10)

        self.canvas_frame = ttk.Frame(root)
        self.canvas_frame.pack(expand=True, fill='both')

        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        self.canvas = tk.Canvas(self.canvas_frame, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", expand=True, fill="both")

        self.scrollbar.config(command=self.canvas.yview)

    def show_plot(self):
        symbol = self.symbol_entry.get()
        try:
            stock_data = get_stock_data(symbol)
            model = train_model(symbol)
            predicted_price_usd = predict_price(model, days=7)

            exchange_rate = get_exchange_rate()
            stock_data_inr = stock_data * exchange_rate
            predicted_price_inr = predicted_price_usd * exchange_rate

            # Update labels
            current_price = stock_data_inr.iloc[-1]
            self.current_price_label.config(text=f"Current Price: ₹{current_price:.2f}")
            self.predicted_price_label.config(text=f"Predicted Price: ₹{predicted_price_inr:.2f}")

            # Determine the suggestion
            suggestion = self.get_suggestion(current_price, predicted_price_inr)
            self.suggestion_label.config(text=f"Suggestion: {suggestion}")

            # Log the prediction details
            logging.info(f"Symbol: {symbol}, Current Price: {current_price:.2f}, Predicted Price: {predicted_price_inr:.2f}, Suggestion: {suggestion}")

            # Plotting
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(stock_data_inr, label=f'{symbol} Stock Price')
            ax.axhline(y=predicted_price_inr, color='r', linestyle='--', label='Predicted Price')

            # Include date, time, and data in the title
            now = datetime.now()
            plot_date = now.strftime("%Y-%m-%d %H:%M:%S")
            ax.set_title(f'{symbol} Stock Price Over Time\nAs of {plot_date}')

            ax.set_xlabel('Date')
            ax.set_ylabel('Stock Price (INR)')
            ax.legend()
            ax.grid(True)

            canvas = FigureCanvasTkAgg(fig, master=self.canvas)
            canvas.draw()

            canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

            # Center the plot
            self.canvas.create_window(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2, window=canvas.get_tk_widget(), anchor="center")

        except ValueError as ve:
            tk.messagebox.showerror("Error", str(ve))
            # Log the error
            logging.error(f"Error for symbol {symbol}: {str(ve)}")

    def get_suggestion(self, current_price, predicted_price):
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
    root = tk.Tk()
    app = StockPredictionApp(root)
    root.mainloop()
