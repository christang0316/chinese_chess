# Telegram Bot: Chinese Chess

## Description

This Telegram bot allows users to play Chinese chess within the Telegram messaging platform.

## Installation

1. **Create a Telegram Bot:**
   - In Telegram, find `@BotFather` to apply for a Telegram Bot.

2. **Install Python-telegram-bot:**
   - Use pip to install `python-telegram-bot`:
     ```bash
     pip3 install python-telegram-bot
      ```
   - macOS users may encounter a `CERTIFICATE_VERIFY_FAILED` error. To resolve, execute:
     ```bash
     /Applications/Python\ 3.10/Install\ Certificates.command
     ```

3. **Configure Token:**
   - In `const.py`, change the `TOKEN` to your Telegram Bot token.

4. **Run the Code:**
   - Execute the `main.py` code.

For more detailed instructions, refer to [Building and Registering Handlers](https://hackmd.io/@truckski/SJkxm2gV3#%E5%BB%BA%E7%AB%8B%E5%8F%8A%E8%A8%BB%E5%86%8A-Handler).

## How to Play

1. Enter `/start` in the chat with your Telegram bot to initiate a new game.
2. Use buttons to make moves or capture chess pieces.
3. The game follows the official Chinese chess rules.
4. To surrender, enter `/surrender`.

## Credits

This project is based on the assignment of [truckski](https://hackmd.io/@truckski).

## Contact me

Feel free to [contact me](christang426859@gmail.com) if you have any problems or find any bugs! 

