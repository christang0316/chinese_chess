# Telegram 機器人：象棋（暗棋）

## 簡介

這是一個可以讓使用者在 Telegram 上玩象棋（暗棋）的 Telegram 機器人。

## 安裝

1. **建立 Telegram 機器人：**
   - 在 Telegram 中搜尋 `@BotFather`，並申請一個 Telegram 機器人。

2. **安裝 Python-telegram-bot：**
   - 使用 pip 安裝 `python-telegram-bot`：
     ```bash
     pip3 install python-telegram-bot
     ```
   - macOS 使用者可能會遇到 `CERTIFICATE_VERIFY_FAILED` 錯誤。解決方法是執行以下程式碼：
     ```bash
     /Applications/Python\ 3.10/Install\ Certificates.command
     ```

3. **設定 Token：**
   - 在 `const.py` 中，將 `TOKEN` 更改為你的 Telegram 機器人的 token。

4. **執行程式：**
   - 執行 `main.py` 程式碼。

如需更詳細的說明，請參閱 [建立和註冊 Python Telegram Bot](https://hackmd.io/@truckski/SJkxm2gV3#%E5%BB%BA%E7%AB%8B%E5%8F%8A%E8%A8%BB%E5%86%8A-Handler)。

## 遊玩方式

1. 在聊天室中輸入 `/start`以開始新遊戲。
2. 使用按鈕進行移動或吃子。
3. 遊戲規則遵循官方象棋規則。
4. 若玩家想要中途投降，請輸入 `/surrender`。

## 致謝

本專案是基於 [truckski](https://hackmd.io/@truckski) 出的作業，雖然我不是他的學生（我是幫交大的高中同學寫的，他程式太爛）。

## 聯絡我

如果你有任何問題或找到任何bugs，歡迎 [聯絡我](christang426859@gmail.com) 。

<br /><br />

---

<br /><br />

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

