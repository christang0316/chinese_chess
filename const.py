unflipped_chess_look = '⚪'

BLACKCHESS = {'general': '⚫將', 'knight': '⚫士', 'elephant': '⚫象', 'car': '⚫車', 'horse': '⚫馬', 'cannon': '⚫砲',
              'soldier': '⚫卒'}
REDCHESS = {'general': '🔴帥', 'knight': '🔴仕', 'elephant': '🔴相', 'car': '🔴俥', 'horse': '🔴傌', 'cannon': '🔴炮',
            'soldier': '🔴兵'}

# Use set for better searching
BLACK = set(BLACKCHESS.values())
RED = set(REDCHESS.values())

PIECE_RANK = {BLACKCHESS['general']: 6, BLACKCHESS['knight']: 5, BLACKCHESS['elephant']: 4, BLACKCHESS['car']: 3, BLACKCHESS['horse']: 2, 
              BLACKCHESS['cannon']: 1, BLACKCHESS['soldier']: 0, 

              REDCHESS['general']: 6, REDCHESS['knight']: 5, REDCHESS['elephant']: 4, REDCHESS['car']: 3, REDCHESS['horse']: 2, 
              REDCHESS['cannon']: 1, REDCHESS['soldier']: 0}