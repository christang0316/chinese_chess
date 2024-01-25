from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from const import TOKEN, BLACK, RED, BLACKCHESS, REDCHESS
import random
import time

unflipped_chess_look = '⚪'


def print_board(board) -> None:
    for r in range(8):
        print(*board[r])
    print()


def road_chess_amount(board, row1, col1, row2, col2) -> int:
    count = 0
    # Different col
    if col1 != col2:
        for c in range(min(col1, col2) + 1, max(col1, col2)):
            if board[row1][c] != ' ':
                count += 1
    # Different row
    elif row1 != row2:
        for r in range(min(row1, row2) + 1, max(row1, row2)):
            if board[r][col1] != ' ':
                count += 1
    print(f"road chess amount = {count}")
    return count


def is_legal_move(pre_row, pre_col, row, col) -> bool:
    if abs(pre_row - row) + abs(pre_col - col) == 1:
        return True
    return False


def is_edible(board, predator_row, predator_col, prey_row, prey_col) -> bool:
    rank = {
        BLACKCHESS['general']: 6, BLACKCHESS['knight']: 5, BLACKCHESS['elephant']: 4, BLACKCHESS['car']: 3,
        BLACKCHESS['horse']: 2, BLACKCHESS['cannon']: 1, BLACKCHESS['soldier']: 0,
        REDCHESS['general']: 6, REDCHESS['knight']: 5, REDCHESS['elephant']: 4, REDCHESS['car']: 3,
        REDCHESS['horse']: 2, REDCHESS['cannon']: 1, REDCHESS['soldier']: 0
    }

    predator = board[predator_row][predator_col]
    prey = board[prey_row][prey_col]

    # 砲/炮
    if predator in [BLACKCHESS['cannon'], REDCHESS['cannon']]:

        # Has to be on the same row or col, and road chess amount == 1
        print(f"predator({predator_row},{predator_col}), prey({prey_row},{prey_col})")
        if ((predator_row == prey_row or predator_col == prey_col) and
                road_chess_amount(board, predator_row, predator_col, prey_row, prey_col) == 1):
            return True
        else:
            return False

    # Other chess need to move legally
    elif is_legal_move(predator_row, predator_col, prey_row, prey_col):

        # 卒/兵 eat 帥/將
        if rank.get(predator) == 0 and rank.get(prey) == 6:
            return True

        if rank.get(predator) == 6 and rank.get(prey) == 0:
            return False

        elif rank.get(predator) >= rank.get(prey):
            return True

        return False


def will_be_eaten(board, bot_chess, user_chess) -> int:  # Return -1 means won't be eaten

    for user_row, user_col in user_chess:
        for i, (bot_row, bot_col) in enumerate(bot_chess):
            if is_edible(board, user_row, user_col, bot_row, bot_col):
                return i

    return -1


def is_game_over(context) -> int:
    # return 0: not over
    # return 1: black win
    # return 2: red win

    # If there's unflipped chess, then game is not over (if flip, the hiddenBoard = ' ')
    for r in range(8):
        for c in range(4):
            if context.user_data["hiddenBoard"][r][c] != ' ':
                return 0

    # Check if the board has both black and red chess
    has_black_chess = False
    has_red_chess = False

    for r in range(8):
        for c in range(4):
            if context.user_data["visibleBoard"][r][c] in BLACK:
                has_black_chess = True
            elif context.user_data["visibleBoard"][r][c] in RED:
                has_red_chess = True

            if has_black_chess and has_red_chess:
                return 0

    # One side of the Chess is not on the board
    if not has_black_chess:
        return 2
    else:
        return 1


def initialize_board() -> list:
    # Sample
    whole_board = BLACK + RED

    # return a shuffled board
    random.shuffle(whole_board)

    board = [whole_board[i:i + 4] for i in range(0, 32, 4)]  # assign the 2D board
    return board


async def update_button_board(message, update, context) -> None:
    text = f"Your chess are "
    if context.user_data["playerColor"] == "black":
        text += "⚫: 將, 士, 象, 車, 馬, 砲, 卒"
    else:
        text += "🔴: 帥, 仕, 相, 俥, 傌, 炮, 兵"
    text += f"\n{message}"

    board = context.user_data["visibleBoard"]
    button_board = [[InlineKeyboardButton(board[r][c], callback_data=f"{r},{c}") for c in range(4)] for r in range(8)]
    await context.bot.edit_message_text(text, reply_markup=InlineKeyboardMarkup(button_board),
                                        chat_id=update.callback_query.message.chat_id,
                                        message_id=update.callback_query.message.message_id)


async def update_button_board_4_callback_ver(message, pre_row, pre_col, update, context) -> None:
    text = f"Your chess are "
    if context.user_data["playerColor"] == "black":
        text += "⚫: 將, 士, 象, 車, 馬, 砲, 卒"
    else:
        text += "🔴: 帥, 仕, 相, 俥, 傌, 炮, 兵"
    text += f"\n{message}"

    board = context.user_data["visibleBoard"]
    button_board = [[InlineKeyboardButton(board[r][c], callback_data=f"{pre_row},{pre_col},{r},{c}") for c in range(4)]
                    for r in range(8)]
    await context.bot.edit_message_text(text, reply_markup=InlineKeyboardMarkup(button_board),
                                        chat_id=update.callback_query.message.chat_id,
                                        message_id=update.callback_query.message.message_id)


async def flip_chess(row, col, message, update, context) -> None:
    context.user_data["visibleBoard"][row][col] = context.user_data["hiddenBoard"][row][col]
    context.user_data["hiddenBoard"][row][col] = ' '
    # print_board(context.user_data["hiddenBoard"])
    print_board(context.user_data["visibleBoard"])
    message += f" and get {context.user_data["visibleBoard"][row][col]}"
    await update_button_board(message, update, context)


async def eat_chess(predator_row, predator_col, prey_row, prey_col, who_eat, update, context) -> None:
    predator_chess = context.user_data["visibleBoard"][predator_row][predator_col]
    prey_chess = context.user_data["visibleBoard"][prey_row][prey_col]
    context.user_data["visibleBoard"][prey_row][prey_col] = context.user_data["visibleBoard"][predator_row][
        predator_col]
    context.user_data["visibleBoard"][predator_row][predator_col] = ' '
    await update_button_board(
        f"{who_eat} used {predator_chess}({predator_row},{predator_col}) to eat {prey_chess}({prey_row},{prey_col})",
        update, context)
    await check_game_over(update, context)


async def check_game_over(update, context) -> None:
    if is_game_over(context) == 1:
        message = "BLACK WINS!"
    elif is_game_over(context) == 2:
        message = "RED WINS!"
    else:
        return

    del context.user_data["turnAmount"]
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def start(update, context) -> None:
    # Create and initialize the user context dic
    # turnAmount: determine if this is User's first time
    # clickAmount: determine if this is User's second click ( for move and eat )

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Starting a new game...\nYou can surrender by enter /surrender . ")

    context.user_data["turnAmount"] = 0
    context.user_data["clickAmount"] = 0

    # Initialize the board and save it to the user_data
    context.user_data["hiddenBoard"] = initialize_board()
    context.user_data["visibleBoard"] = [[unflipped_chess_look for _ in range(4)] for _ in range(8)]

    print_board(context.user_data["hiddenBoard"])

    # Show visible board
    board = context.user_data["visibleBoard"]
    context.user_data["button_board"] = [[InlineKeyboardButton(board[r][c], callback_data=f"{r},{c}") for c in range(4)]
                                         for r in range(8)]
    await update.message.reply_text("You go first!",
                                    reply_markup=InlineKeyboardMarkup(context.user_data["button_board"]))


async def surrender(update, context) -> None:
    try:
        color = "BLACK" if context.user_data["botColor"] == "black" else "RED"
        del context.user_data["turnAmount"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{color} WINS!")

    except KeyError:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Please Start a new Game by enter /start !")


async def bot_turn(update, context) -> None:
    time.sleep(1)
    print("bot' s turn")
    bot_color = context.user_data["botColor"]
    print(bot_color)

    # Get the current board state
    hidden_chess = []
    blank_chess = []
    bot_chess = []
    user_chess = []

    for r in range(8):
        for c in range(4):
            if context.user_data["visibleBoard"][r][c] == unflipped_chess_look:
                hidden_chess.append((r, c))
            elif context.user_data["visibleBoard"][r][c] == ' ':
                blank_chess.append((r, c))
            else:
                if context.user_data["botColor"] == "black" and context.user_data["visibleBoard"][r][c] in BLACK:
                    bot_chess.append((r, c))
                elif context.user_data["botColor"] == "red" and context.user_data["visibleBoard"][r][c] in RED:
                    bot_chess.append((r, c))
                else:
                    user_chess.append((r, c))

    while True:

        # botChoice is random between "move" and "flip" if there's hiddenChess, else botChoice is "move"
        # "move" contains moving chess or eating chess

        will_be_eaten_chess = will_be_eaten(context.user_data["visibleBoard"], bot_chess, user_chess)
        print(will_be_eaten_chess)

        # There's chess will be eaten, move the chess
        if will_be_eaten_chess != -1:
            bot_choice = "move_certain_chess"

        # No chess to play, then flip
        elif not bot_chess:
            bot_choice = "flip"

        # No chess to flip or will be eaten, then move
        elif not hidden_chess:
            bot_choice = "move"

        # random move or flip
        else:
            [bot_choice] = random.choices(["move", "flip"], weights=(50, 50), k=1)

        print(bot_choice)

        if bot_choice == "flip":
            row, col = random.choice(hidden_chess)
            await flip_chess(row, col, f"Bot flop ({row},{col})", update, context)
            return

        # Move certain chess or random eat/move
        else:

            if will_be_eaten_chess != -1:
                row, col = bot_chess[will_be_eaten_chess]
            else:
                row, col = random.choice(bot_chess)

            move_chess = context.user_data["visibleBoard"][row][col]
            print(f"moveChess = {move_chess}({row}, {col})")

            # Consider 炮/砲 eating
            if move_chess in [BLACKCHESS['cannon'], REDCHESS['cannon']]:
                for r in range(8):
                    for c in range(4):
                        # If the target is blank, hidden, or bot chess (use visibleBoard to check since botBoard
                        # items might be deleted), then skip
                        if ((r, c) in blank_chess) or ((r, c) in hidden_chess) or (
                                context.user_data["visibleBoard"][r][c] in BLACK if bot_color == "black" else RED):
                            continue

                        # If edible
                        elif is_edible(context.user_data["visibleBoard"], row, col, r, c):
                            await eat_chess(row, col, r, c, "Bot", update, context)
                            return
            # Consider other chess' eating
            else:
                # check the 9 square ### Need optimize
                for r in range(max(row - 1, 0), min(row + 2, 8)):
                    for c in range(max(col - 1, 0), min(col + 2, 4)):
                        print(f"Checking{(r, c)}")
                        # target is blankChess, hiddenChess or botChess, then skip
                        if ((r, c) in blank_chess) or ((r, c) in hidden_chess) or (
                                context.user_data["visibleBoard"][r][c] in (BLACK if bot_color == "black" else RED)):
                            continue
                        else:
                            print(F"consider{(r, c)}")
                            if is_edible(context.user_data["visibleBoard"], row, col, r, c):
                                print("edible")
                                await eat_chess(row, col, r, c, "Bot", update, context)
                                return

            # Can't eat, then consider move in up, down, left, right
            if (row - 1, col) in blank_chess:
                r, c = row - 1, col
            elif (row + 1, col) in blank_chess:
                r, c = row + 1, col
            elif (row, col - 1) in blank_chess:
                r, c = row, col - 1
            elif (row, col + 1) in blank_chess:
                r, c = row, col + 1
            else:
                # No way to move or eat, delete this chess and continue the while loop to choose another chess
                bot_chess.remove((row, col))
                continue

            # move
            context.user_data["visibleBoard"][r][c] = context.user_data["visibleBoard"][row][col]
            context.user_data["visibleBoard"][row][col] = ' '
            await update_button_board(
                f"Bot moved {context.user_data["visibleBoard"][r][c]} from ({row},{col}) to ({r}, {c})", update,
                context)
            return


async def main_func(update, context) -> None:
    try:
        context.user_data["turnAmount"] += 1
        # print(context.user_data["turnAmount"])
        # print(context.user_data["clickAmount"])
        # print(update.callback_query.data)

        if len(update.callback_query.data.split(",")) == 2:
            pre_row, pre_col = -1, -1
            now_row, now_col = map(int, update.callback_query.data.split(","))
        else:
            pre_row, pre_col, now_row, now_col = map(int, update.callback_query.data.split(","))

        # For the first time (need to determine the color)
        if context.user_data["turnAmount"] == 1:

            if context.user_data["hiddenBoard"][now_row][now_col] in BLACK:
                context.user_data["playerColor"] = "black"
                context.user_data["botColor"] = "red"
            else:
                context.user_data["playerColor"] = "red"
                context.user_data["botColor"] = "black"

            await flip_chess(now_row, now_col, f"You flop ({now_row},{now_col})", update, context)

            await bot_turn(update, context)

        # Player chose unflipped chess
        elif context.user_data["visibleBoard"][now_row][now_col] == unflipped_chess_look:

            await flip_chess(now_row, now_col, f"You flop ({now_row},{now_col})", update, context)

            await bot_turn(update, context)

        # Player's first click and not unflipped chess
        elif len(update.callback_query.data.split(",")) == 2:

            # Player chose on his own chess
            if context.user_data["visibleBoard"][now_row][now_col] in (
                    BLACK if context.user_data["playerColor"] == "black" else RED):
                chess = context.user_data["visibleBoard"][now_row][now_col]
                await update_button_board_4_callback_ver(f"You chose {chess}({now_row},{now_col})", now_row, now_col,
                                                         update, context)

            # Player chose on opponent's chess or blank space
            else:
                chess = context.user_data["visibleBoard"][now_row][now_col]
                await update_button_board(f"Illegal choice{chess}({now_row},{now_col})", update, context)

        # Player's second click (first click is his own chess)
        else:
            # Choose the same chess
            if pre_row == now_row and pre_col == now_col:
                return

            # Player chose on his own chess again
            elif context.user_data["visibleBoard"][now_row][now_col] in (
                    BLACK if context.user_data["playerColor"] == "black" else RED):
                chess = context.user_data["visibleBoard"][now_row][now_col]
                await update_button_board_4_callback_ver(f"You chose {chess}({now_row}, {now_col})", now_row, now_col,
                                                         update, context)

            # Want to move and legal
            elif (context.user_data["visibleBoard"][now_row][now_col] == ' ' and
                  is_legal_move(pre_row, pre_col, now_row, now_col)):
                print("Legal move")
                chess = context.user_data["visibleBoard"][pre_row][pre_col]
                context.user_data["visibleBoard"][now_row][now_col] = \
                    context.user_data["visibleBoard"][pre_row][pre_col]
                context.user_data["visibleBoard"][pre_row][pre_col] = ' '
                await update_button_board(
                    f"You move {chess} from ({pre_row},{pre_col}) to ({now_row},{now_col})", update, context)

                await bot_turn(update, context)

            # Want to eat and legal
            elif (context.user_data["visibleBoard"][now_row][now_col] in (
                    BLACK if context.user_data["botColor"] == "black" else RED) and
                  is_edible(context.user_data["visibleBoard"], pre_row, pre_col, now_row, now_col)):
                print("Want to eat")
                await eat_chess(pre_row, pre_col, now_row, now_col, "You", update, context)
                await bot_turn(update, context)

            # Illegal choice to move (chose blank space) or eat (chose opponent's chess)
            else:
                chess = context.user_data["visibleBoard"][pre_row][pre_col]
                await update_button_board_4_callback_ver(
                    f"Illegal move/eat\nNow choosing: {chess}({pre_row},{pre_col})",
                    pre_row, pre_col, update, context)

    except KeyError:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Please Start a new Game by enter /start !")


def main():
    """Start the bot."""
    # Create the Application and pass token to your bot
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # Player choose to surrender
    application.add_handler(CommandHandler("surrender", surrender))

    # whenever the button is pushed
    application.add_handler(CallbackQueryHandler(main_func))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
