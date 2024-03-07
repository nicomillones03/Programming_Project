from config import ALPACA_CONFIG
from lumibot.brokers import Alpaca
from lumibot.strategies import Strategy
from lumibot.traders import Trader


class BuyOnDrop(Strategy):
    def initialize(self):
        self.sleeptime = "10S"  # Trading once a day
        self.symbol = "NVDA"
        self.last_close_price = None  # To store the last day's closing price
        self.entry_price = 0
        self.drop_threshold = 0.0002  # .02% drop
        self.rise_threshold = 0.00025  # .025% rise

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
    broker = Alpaca(ALPACA_CONFIG)
    strategy = BuyOnDrop(broker=broker)
    trader = Trader()
    trader.add_strategy(strategy)
    trader.run_all()
