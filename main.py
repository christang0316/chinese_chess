from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from const import unflipped_chess_look, BLACK, RED, PIECE_RANK
from utils import print_board, is_legal_move, is_edible, find_threatened_pieces, is_game_over, initialize_board, find_all_possible_eating_moves, find_all_possible_blank_moves

import logging
import random
import time
import os
import dotenv

logging.basicConfig(format='%(levelname)s - %(message)s')
logging.getLogger("my_bot").setLevel(logging.INFO)
logger = logging.getLogger("my_bot")


# Get token
dotenv.load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
logger.debug(f"{BOT_TOKEN=}")


async def update_button_board(message, update, context) -> None:
    text = f"Your chess are "
    if context.user_data["userColor"] == "black":
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
    if context.user_data["userColor"] == "black":
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
    # print_board(context.user_data["visibleBoard"])
    message += f" and get {context.user_data["visibleBoard"][row][col]}"
    await update_button_board(message, update, context)


async def eat_chess(predator_row, predator_col, prey_row, prey_col, who_eat, update, context) -> None:
    visible_board = context.user_data["visibleBoard"]
    predator_chess = visible_board[predator_row][predator_col]
    prey_chess = visible_board[prey_row][prey_col]
    context.user_data["visibleBoard"][prey_row][prey_col] = visible_board[predator_row][
        predator_col]
    context.user_data["visibleBoard"][predator_row][predator_col] = ' '
    await update_button_board(
        f"{who_eat} used {predator_chess}({predator_row},{predator_col}) to eat {prey_chess}({prey_row},{prey_col})",
        update, context)
    await check_game_over(update, context)


async def move_chess_to_blank(from_r, from_c, to_r, to_c, actor, update, context) -> None:
    """
    Executes the action of moving a piece to a blank space.
    
    WARNING: 
    This funciton only update the board. You should implement is_legal_move() to check if the move is valid if needed.
    
    """

    peice = context.user_data["visibleBoard"][from_r][from_c]

    # Update board state
    context.user_data["visibleBoard"][to_r][to_c] = peice
    context.user_data["visibleBoard"][from_r][from_c] = ' '
    await update_button_board(
        f"{actor} used {peice}({from_r}, {from_c}) to ({to_r}, {to_c})",
        update, context)


async def check_game_over(update, context, surrender=False) -> None:

    bot_color = "BLACK" if context.user_data["botColor"] == "black" else "RED"

    if not surrender:

        if is_game_over(context) == 1:
            win_color = "BLACK"
        elif is_game_over(context) == 2:
            win_color = "RED"
        else: # Game is not over
            return
        
    else:
        win_color = bot_color

    message = f"{win_color} (BOT) WINS!" if win_color == bot_color else f"{win_color} (YOU) WINS!"

    del context.user_data["turnAmount"]
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def start(update, context) -> None:
    # Create and initialize the user context dic
    # turnAmount: determine if this is User's first time
    # clickAmount: determine if this is User's second click ( for move and eat )

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Starting a new game...\n" \
                                   "You can surrender by enter /surrender . ")

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
        logger.info("User surrender")
        await check_game_over(update, context, surrender=True)

    except KeyError:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Please Start a new Game by enter /start !")


async def bot_turn(update, context) -> None:
    time.sleep(0.5)
    logger.info("Bot' s turn")

    bot_color = context.user_data["botColor"]
    visible_board = context.user_data["visibleBoard"]
    
    logger.debug(f"{bot_color=}")

    # --- Get the current board state (gather info) ---
    hidden_chess: list[tuple[int, int]] = []
    blank_chess: list[tuple[int, int]] = []
    bot_chess: list[tuple[int, int]] = []
    user_chess: list[tuple[int, int]] = []

    for r in range(8):
        for c in range(4):
            piece = visible_board[r][c]

            if piece == unflipped_chess_look:
                hidden_chess.append((r, c))
            elif piece == ' ':
                blank_chess.append((r, c))
            else:
                if context.user_data["botColor"] == "black" and piece in BLACK:
                    bot_chess.append((r, c))
                elif context.user_data["botColor"] == "red" and piece in RED:
                    bot_chess.append((r, c))
                else:
                    user_chess.append((r, c))
    
    logger.debug(f"{bot_chess=}")
    logger.debug(f"{user_chess=}")

    all_eating_moves = find_all_possible_eating_moves(visible_board, bot_chess, user_chess)
    threatened_pieces_coords = find_threatened_pieces(visible_board, bot_chess, user_chess)
    all_blank_moves = find_all_possible_blank_moves(bot_chess, blank_chess)
    
    can_flip = bool(hidden_chess)
    can_move = bool(all_blank_moves)

    logger.debug(f"{all_eating_moves=}")
    logger.debug(f"{threatened_pieces_coords=}")
    logger.debug(f"{all_blank_moves=}")

    # --- Bot's Decision Making ---
    """
        Bot's decision priority:
        
        P1 (attack): Are there any way to eat user's piece?
            yes -> eat and end turn
        
        P2 (defend): Are there any of my pieces are in danger of being captured?
            yes -> try moving the threatened piece to a blank spot.
                If successfully moved to a blank spot -> End turn
                If no blank spot to escape (blocked) -> Give up defense and proceed to P3
        
        P3 (move): Can I move any peice to a blank spot?
        P4 (Flip): Are there any hidden pieces to flip?
                - Both possible -> Randomly select one (prefer flip, weight=(65, 35)).
                
                - Move only -> Perform "Random Move".
                - Flip Piece only -> Perform "Flip Piece".
               
                - Neither possible: The bot is stuck; end the turn. (rarely happens)

    """

    # P1 (attack)
    if all_eating_moves:
        logger.info("Bot Decision: P1 - Eat")
        from_r, from_c, to_r, to_c = random.choice(all_eating_moves)
        await eat_chess(from_r, from_c, to_r, to_c, "Bot", update, context)
        return

    # P2 (defend)
    if threatened_pieces_coords:
        logger.info(f"Bot Decision: P2 - Defend (Threatened pieces: {threatened_pieces_coords})")

        # Find all "saving moves" (moves to a blank spot originating from a threatened piece)
        # move: (from_r, from_c, to_r, to_c)
        # (move[0], move[1]) is the threatened piece's coordinate
        saving_moves = [
            move for move in all_blank_moves 
            if (move[0], move[1]) in threatened_pieces_coords
        ]
        
        if saving_moves:
            logger.info("Bot: Found a safe spot! prioritizing high-rank pieces.")

            # 1. Get the current board state
            board = context.user_data["visibleBoard"] 
            
            # 2. Find the highest rank among all pieces that can be saved.
            #    We iterate through all possible saving moves,
            #    get the piece being moved (move[0], move[1]),
            #    and find its rank from the PIECE_RANK dictionary.
            try:
                highest_rank_to_save = max(
                    PIECE_RANK[board[move[0]][move[1]]] for move in saving_moves
                )
                logger.debug(f"Highest rank threatened and savable: {highest_rank_to_save}")

                # 3. Filter the moves: Keep only those that save a piece with that highest rank.
                #    (This handles cases where two '車' are threatened; both are valid)
                best_saving_moves = [
                    move for move in saving_moves
                    if PIECE_RANK[board[move[0]][move[1]]] == highest_rank_to_save
                ]

                # 4. Choose randomly from the best moves
                #    (e.g., if one '車' has 3 escape routes, pick one randomly)
                from_r, from_c, to_r, to_c = random.choice(best_saving_moves)
            
            except (KeyError, ValueError) as e:
                # Fallback in case PIECE_RANK lookup fails (e.g., piece is BLANK, which shouldn't happen)
                logger.error(f"Error in P2 logic: {e}. Falling back to random save.")
                from_r, from_c, to_r, to_c = random.choice(saving_moves) # Fallback
            
            # Execute move
            await move_chess_to_blank(from_r, from_c, to_r, to_c, "Bot", update, context)
            return # End bot's turn
        
        # If no saving_moves, the piece is trapped.
        # Logic automatically proceeds to P3/P4.
        logger.info("Bot: Piece is threatened but has no escape. Proceeding to P3/P4.")

    # P3 & P4: REGULAR MOVE or FLIP (Lowest Priority)
    if can_move and can_flip:
        logger.info("Bot Decision: P3/P4 - Random Move/Flip")
        [bot_choice] = random.choices(["flip", "move"], cum_weights=[75, 100], k=1)
    
    elif can_move:
        logger.info("Bot Decision: P3 - Forced Move (No pieces to flip)")
        bot_choice = "move"
        
    elif can_flip:
        # This handles the case where all pieces are blocked, but flipping is possible
        logger.info("Bot Decision: P4 - Forced Flip (No possible moves)")
        bot_choice = "flip"
        
    else:
        # This handles cases like 'not bot_chess' or all pieces are blocked and no hidden pieces are left.
        logger.info("Bot is stuck. No actions available.")
        return # End bot's turn (Pass)

    # --- 3. EXECUTE P3 or P4 ACTION ---

    if bot_choice == "flip":
        logger.info("Bot: Executing Flip")
        row, col = random.choice(hidden_chess)
        
        # Execute flip (Assumes you have this async function)
        await flip_chess(row, col, f"Bot flop ({row},{col})", update, context)
        return # End bot's turn

    if bot_choice == "move":
        logger.info("Bot: Executing Random Move")
        # Pick a random move from *all* possible blank moves
        from_r, from_c, to_r, to_c = random.choice(all_blank_moves)
        
        # Execute move
        await move_chess_to_blank(from_r, from_c, to_r, to_c, "Bot", update, context)
        return # End bot's turn
    
    raise RuntimeError("Bot's decision logic error")


async def main_func(update, context) -> None:
    
    visible_board = context.user_data["visibleBoard"]
    try:
        context.user_data["turnAmount"] += 1
        logger.debug(f"{context.user_data['turnAmount']=}")

        if len(update.callback_query.data.split(",")) == 2:
            pre_row, pre_col = -1, -1
            now_row, now_col = map(int, update.callback_query.data.split(","))
        else:
            pre_row, pre_col, now_row, now_col = map(int, update.callback_query.data.split(","))

        # For the first time (need to determine the color)
        if context.user_data["turnAmount"] == 1:

            if context.user_data["hiddenBoard"][now_row][now_col] in BLACK:
                context.user_data["userColor"] = "black"
                context.user_data["botColor"] = "red"
            else:
                context.user_data["userColor"] = "red"
                context.user_data["botColor"] = "black"

            await flip_chess(now_row, now_col, f"You flop ({now_row},{now_col})", update, context)

            await bot_turn(update, context)

        # Player chose unflipped chess -> flip chess
        elif visible_board[now_row][now_col] == unflipped_chess_look:
            
            logger.info("User chose unflipped chess")

            await flip_chess(now_row, now_col, f"You flop ({now_row},{now_col})", update, context)
            await bot_turn(update, context)

        # Player's first click at an not-unflipped chess
        elif len(update.callback_query.data.split(",")) == 2:

            # Player chose on his own chess
            if visible_board[now_row][now_col] in (
                    BLACK if context.user_data["userColor"] == "black" else RED):
                
                logger.info("User chose on his chess")
                chess = visible_board[now_row][now_col]

                await update_button_board_4_callback_ver(f"You chose {chess}({now_row},{now_col})", now_row, now_col,
                                                         update, context)

            # Player chose on opponent's chess or blank space
            else:
                chess = visible_board[now_row][now_col]
                await update_button_board(f"Illegal choice{chess}({now_row},{now_col})", update, context)

        # Player's second click (first click on his own chess)
        else:
            # Choose the same chess
            if pre_row == now_row and pre_col == now_col:
                return

            # Player chose on his own chess again
            elif visible_board[now_row][now_col] in (
                    BLACK if context.user_data["userColor"] == "black" else RED):
                
                logger.info("User chose on his chess")
                chess = visible_board[now_row][now_col]

                await update_button_board_4_callback_ver(f"You chose {chess}({now_row}, {now_col})", now_row, now_col,
                                                         update, context)

            # Want to move and legal
            elif (visible_board[now_row][now_col] == ' ' and
                  is_legal_move(pre_row, pre_col, now_row, now_col)):
                
                logger.info("User: legal move")
                
                await move_chess_to_blank(pre_row, pre_col, now_row, now_col, "You", update, context)
                await bot_turn(update, context)

            # Want to eat and legal
            elif (visible_board[now_row][now_col] in (
                    BLACK if context.user_data["botColor"] == "black" else RED) and
                  is_edible(visible_board, pre_row, pre_col, now_row, now_col)):
                
                logger.info("User: want to eat")

                await eat_chess(pre_row, pre_col, now_row, now_col, "You", update, context)
                await bot_turn(update, context)

            # Illegal choice to move (chose blank space) or eat (chose opponent's chess)
            else:
                chess = visible_board[pre_row][pre_col]

                logger.info("User: illegal move/eat")

                await update_button_board_4_callback_ver(
                    f"Illegal move/eat\nNow choosing: {chess}({pre_row},{pre_col})",
                    pre_row, pre_col, update, context)

    except KeyError:
        logger.warning("KeyError: Ask user to start a new game")
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Please Start a new Game by enter /start !")


def main():
    """Start the bot."""
    # Create the Application and pass token to your bot
    application = Application.builder().token(BOT_TOKEN).build()

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
