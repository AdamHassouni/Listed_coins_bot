# NewCoinListings Bot

## Overview

NewCoinListings Bot is an automated trading bot that listens for new coin listings on the Binance exchange using Websockets. When a new coin is listed in the USDT market, the bot automatically places a buy order and then sets a sell order based on the configured profit and stop-loss settings.

## Features

- Listens for new coin listings in the USDT market.
- Automatically places buy orders when a new coin is detected.
- Sets sell orders based on configured profit and stop-loss percentages.
- Sends notifications when trades are executed.

## Requirements

- Python 3.6 or higher
- Binance API key and secret
- Required Python libraries (see `requirements.txt`)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/AdamHassouni/Listed_coins_bot
    cd Listed_coins_bot
    ```

2. Install the required Python libraries:

    ```bash
    pip install -r requirements.txt
    ```

3. Configure your Binance API credentials and trading settings in `config.py`:

    ```python
    # config.py
    credentials = {
        'api': 'YOUR_BINANCE_API_KEY',
        'sec': 'YOUR_BINANCE_SECRET_KEY',
        'usdt': 100,  # Amount of USDT to use for each trade
        'profit': 1.05,  # Target profit multiplier (e.g., 1.05 for 5% profit)
        'sloss': 0.95  # Stop-loss multiplier (e.g., 0.95 for 5% loss)
    }
    ```

## Usage

To run the bot, execute the following command:

    ```bash
    python main.py
    ```

## Code Structure

- `main.py`: The main entry point of the bot. Sets up logging, validates configuration, and starts the WebSocket listener.
- `detect.py`: Contains functions to start the WebSocket and detect new listings.
- `order_making.py`: Contains functions to load trading information, calculate trade quantity, and place buy/sell orders.
- `validate.py`: Contains functions to validate the bot's configuration.
- `Notification.py`: Module for sending notifications.

## Main Functions

### `handle_new_listing(data)`

Handles new coin listings detected by the WebSocket. It performs the following steps:
1. Logs the new symbol and its price.
2. Loads trading information for the new symbol.
3. Calculates the trade quantity based on the available USDT.
4. Places a buy order.
5. Calculates the average buy price.
6. Places a sell order based on the configured profit and stop-loss.
7. Sends a notification of the executed buy order.

### `start_ws()`

Starts the WebSocket listener to detect new coin listings.

## Logging

The bot uses the Python `logging` module to log information and errors. Logs are printed to the console with different log levels (INFO and ERROR).

## Notifications

The bot sends notifications when a trade is executed using the `Notification` module. Customize this module to integrate with your preferred notification service (e.g., email, SMS, push notifications).

## Contributing

Feel free to submit issues or pull requests if you have any suggestions or improvements.
