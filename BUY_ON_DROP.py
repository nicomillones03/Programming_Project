from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies import Strategy


class BuyOnDrop(Strategy):
    def initialize(self):
        self.sleeptime = "1D"  # Trading once a day
        self.symbol = "NVDA"
        self.last_close_price = None  # To store the last day's closing price
        self.entry_price = 0
        self.drop_threshold = 0.02  # 2% drop
        self.rise_threshold = 0.025  # 2.5% rise

    def on_start(self):
        # Fetch the initial closing price for the first trading day
        self.last_close_price = self.get_last_price(self.symbol)

    def on_trading_iteration(self):
        current_price = self.get_last_price(self.symbol)

        # Check if the last closing price is available
        if self.last_close_price:
            if not self.entry_price:
                # Check for a 2% drop from the last close price
                if current_price <= self.last_close_price * (1 - self.drop_threshold):
                    # Buy the asset
                    symbol = "NVDA"
                    price = self.get_last_price(symbol)
                    quantity = self.cash // price  # Assuming a fixed quantity for simplicity
                    order = self.create_order(self.symbol, quantity, "buy")
                    self.submit_order(order)
                    self.entry_price = current_price
            else:
                # Check for a 2.5% rise from the entry price
                if current_price >= self.entry_price * (1 + self.rise_threshold):
                    # Sell the asset
                    quantity = self.get_position(self.symbol).quantity
                    if quantity > 0:
                        order = self.create_order(self.symbol, quantity, "sell")
                        self.submit_order(order)
                        self.entry_price = 0  # Reset the entry price after selling

        # Update the last closing price for the next day
        self.last_close_price = current_price


if __name__ == "__main__":
    # Define the backtesting period
    start = datetime(2020, 1, 1)
    end = datetime(2020, 12, 31)

    # Assuming your backtesting setup here; make sure it's adjusted as per the framework's requirements
    BuyOnDrop.backtest(
        YahooDataBacktesting,
        start,
        end
    )
