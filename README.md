# Telegram 機器人：象棋（暗棋）

## 簡介

這是一個可以讓使用者在 Telegram 上玩象棋（暗棋）的 Telegram 機器人。

## 安裝與執行

本專案使用 [uv](https://github.com/astral-sh/uv) 進行環境管理與執行，並透過 `.env` 檔案管理 Token。

1.  **建立機器人與 `.env` 檔案：**

      * 在 Telegram 中搜尋 `@BotFather`，建立一個新的機器人並取得 `TOKEN`。
      * 複製專案中的 `.env.example` 檔案，並重新命名為 `.env`。
        ```bash
        # macOS / Linux
        cp .env.example .env

        # Windows (Command Prompt)
        copy .env.example .env
        ```
      * 開啟 `.env` 檔案，將你剛剛取得的 `TOKEN` 填入。

2.  **安裝 `uv` (如果尚未安裝)：**

      * `uv` 是一個極速的 Python 套件管理工具。請依據[官方文件](https://github.com/astral-sh/uv)安裝它（例如：`pip install uv`）。

3.  **執行專案：**

      * 在專案的根目錄下（有 `pyproject.toml` 的地方），直接執行：
        ```bash
        uv run python main.py
        ```
      * `uv` 會自動偵測 `pyproject.toml`，建立虛擬環境 (`.venv`)，安裝所有依賴套件，然後執行 `main.py`。

## 遊玩方式

1.  在聊天室中輸入 `/start`以開始新遊戲。
2.  使用按鈕進行移動或吃子。
3.  遊戲規則遵循官方象棋規則。
4.  若玩家想要中途投降，可輸入 `/surrender`。

## 致謝

本專案是基於 [truckski](https://hackmd.io/@truckski) 出的作業，雖然我不是他的學生。

## 聯絡我

如果你有任何問題或找到任何bugs，歡迎 建立Issues/PR 或 [聯絡我](https://linktr.ee/christang) 。

<br /><br />

---

<br /><br />

# Telegram Bot: Chinese Chess

## Description

This Telegram bot allows users to play Chinese chess within the Telegram messaging platform.

## Installation and Run

This project uses [uv](https://github.com/astral-sh/uv) for environment management and execution, and a `.env` file for token management.

1.  **Create Bot and `.env` File:**

      * In Telegram, find `@BotFather` to create a new bot and get your `TOKEN`.
      * Copy the `.env.example` file in this project to a new file named `.env`.
        ```bash
        # macOS / Linux
        cp .env.example .env

        # Windows (Command Prompt)
        copy .env.example .env
        ```
      * Open the new `.env` file and paste in your `TOKEN`.

2.  **Install `uv` (if you haven't):**

      * `uv` is an extremely fast Python package installer and resolver. Install it according to the [official documentation](https://github.com/astral-sh/uv) (e.g., `pip install uv`).

3.  **Run the Project:**

      * From the project's root directory (where `pyproject.toml` is located), simply run:
        ```bash
        uv run python main.py
        ```
      * `uv` will automatically detect the `pyproject.toml` file, create a virtual environment (`.venv`), install all dependencies, and then execute `main.py`.

## How to Play

1.  Enter `/start` in the chat with your Telegram bot to initiate a new game.
2.  Use buttons to make moves or capture chess pieces.
3.  The game follows the official Chinese chess rules.
4.  To surrender, enter `/surrender`.

## Credits

This project is based on the assignment of [truckski](https://hackmd.io/@truckski).

## Contact me

Feel free to create issues/ PR or [contact me](https://linktr.ee/christang) if you have any problems or find any bugs\!