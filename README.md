**Repository Name:** Real Time Stock Price Prediction App

**Description:**

 This project is a Python-based application that leverages data analysis, time series modeling, and a graphical user interface (GUI) to predict future stock prices and provide valuable insights for decision-making.

**Key Features:**
- **Data Retrieval:** Utilizes the `yfinance` library to fetch historical stock data for the chosen symbol.
- **Model Training:** Employs the SARIMA (Seasonal AutoRegressive Integrated Moving Average) model from the `statsmodels` library to train and predict stock prices.
- **GUI Interface:** Built with Tkinter, the GUI allows users to input a stock symbol, triggering the prediction and visualization process.
- **Plotting:** Utilizes Matplotlib to create interactive plots displaying historical stock prices and predicted future values.
- **Suggestion Logic:** Offers practical suggestions – whether to buy, sell, or hold the stock – based on predicted and current prices.

**How to Use:**
1. Clone the repository to your local machine.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Run the script (`stock_prediction.py`) and enter the stock symbol when prompted.
4. Go to yahoo finance website to get stock symbols and try indian stocks as the default currency is INR.{ex - MRF,TATA} 
5. Explore the visualized historical and predicted stock prices along with actionable suggestions.

**Dependencies:**
- `tkinter`
- `matplotlib`
- `statsmodels`
- `forex_python`
- `yfinance`
- `pandas`

**Note:** Ensure you have Python installed on your machine.

Feel free to contribute, open issues, or suggest improvements. Happy predicting!
