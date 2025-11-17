from const import unflipped_chess_look, BLACKCHESS, REDCHESS, BLACK, RED, PIECE_RANK
import logging
import random

logger = logging.getLogger("my_bot")

def print_board(board) -> None:
    for r in range(8):
        for c in range(4):
            chess = board[r][c]
            
            # for better printing appearance
            if chess == unflipped_chess_look:
                chess += "　"  # for better print appearance
            elif chess == " ":
                chess = "　　"

            print(chess, end=" ")
        print()
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
    logger.debug(f"road chess amount = {count}")
    return count


def is_legal_move(from_r, from_c, to_r, to_c) -> bool:
    if abs(from_r - to_r) + abs(from_c - to_c) == 1:
        return True
    return False


def is_edible(board, from_r, from_c, to_r, to_c) -> bool:

    logger.debug(f"{from_r=}, {from_c=}, {to_r=}, {to_c=}")

    assert 0 <= from_r < 8 and 0 <= from_c < 4 and 0 <= to_r < 8 and 0 <= to_c < 4, "r, c out of board scope"
    
    attacker = board[from_r][from_c]
    target = board[to_r][to_c]

    # 砲/炮
    if attacker in [BLACKCHESS['cannon'], REDCHESS['cannon']]:

        # Has to be on the same row or col, and road chess amount == 1
        logger.debug(f"attacker({from_r},{from_c}), target({to_r},{to_c})")
        if ((from_r == to_r or from_c == to_c) and
                road_chess_amount(board, from_r, from_c, to_r, to_c) == 1):
            return True
        else:
            return False

    # Other chess need to move legally
    elif is_legal_move(from_r, from_c, to_r, to_c):

        # 卒/兵 eat 帥/將
        if PIECE_RANK.get(attacker) == 0 and PIECE_RANK.get(target) == 6:
            return True

        if PIECE_RANK.get(attacker) == 6 and PIECE_RANK.get(target) == 0:
            return False

        elif PIECE_RANK.get(attacker) >= PIECE_RANK.get(target):
            return True

        return False


def find_threatened_pieces(board, bot_pieces_coords, user_pieces_coords) -> list[tuple[int, int]]:
    
    """
        This function find the bot_chess that will be eaten (only return 1 chess at a time even though there's might be many)
    """
    threatened_pieces = []
    for (user_row, user_col) in user_pieces_coords:
        for (bot_row, bot_col) in bot_pieces_coords:
            if is_edible(board, user_row, user_col, bot_row, bot_col):
                threatened_pieces.append((bot_row, bot_col))

    return list(set(threatened_pieces))  # remove duplicates (if any))


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

    PIECE_COUNT = {
        'general': 1,
        'knight': 2,
        'elephant': 2,
        'car': 2,
        'horse': 2,
        'cannon': 2,
        'soldier': 5
    }

    RED_CHESS = [REDCHESS[key] for key, count in PIECE_COUNT.items() for _ in range(count)]
    BLACK_CHESS = [BLACKCHESS[key] for key, count in PIECE_COUNT.items() for _ in range(count)]


    whole_board = RED_CHESS + BLACK_CHESS

    # return a shuffled board
    random.shuffle(whole_board)

    board = [whole_board[i:i + 4] for i in range(0, 32, 4)]  # assign the 2D board
    return board


def find_all_possible_eating_moves(board, bot_pieces_coords, user_pieces_coords) -> list[tuple[int, int, int, int]]:
    """
    Find all possible eating moves that BOT can implement.
    
    @param board: 8x4 board
    @param bot_pieces_coords: Bot's chess list, e.g., [(0, 1), (2, 3)]
    @param user_pieces_coords: User's chess list, e.g., [(0, 1), (2, 3)]
    
    @return: list of tuples, e.g., [(from_r, from_c, to_r, to_c), ...]
    """
    eating_moves = []
    
    # Iterate through each of the Bot's pieces
    for (from_r, from_c) in bot_pieces_coords:
        
        # Iterate through each of the User's pieces (as target)
        for (to_r, to_c) in user_pieces_coords:
            
            # Call is_edible 
            if is_edible(board, from_r, from_c, to_r, to_c):
                eating_moves.append((from_r, from_c, to_r, to_c))
                
    return eating_moves


def find_all_possible_blank_moves(bot_pieces_coords, blank_coords):
    """
    Find all possible way to "move to blank" Bot can make.
    
    :param bot_pieces_coords: Bot's chess list, e.g., [(0, 1), (2, 3)]
    :param blank_coords: blank list, e.g., [(0, 1), (2, 3)]
    :return: list of tuples, e.g., [(from_r, from_c, to_r, to_c), ...]
    """
    blank_moves = []
    blank_set = set(blank_coords) # transform to set for better finding performance
    
    for (from_r, from_c) in bot_pieces_coords:
            
        # 檢查上下左右
        possible_targets = [
            (from_r - 1, from_c), # UP
            (from_r + 1, from_c), # Down
            (from_r, from_c - 1), # Left
            (from_r, from_c + 1)  # Right
        ]
        
        for (to_r, to_c) in possible_targets:
            
            # check if (to_r, to_c) is in the set of blank_set
            if (to_r, to_c) in blank_set:
                blank_moves.append((from_r, from_c, to_r, to_c))
                
    return blank_moves


