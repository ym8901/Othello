import numpy as np
SIZE = 4

def test():
    board = np.zeros((SIZE, SIZE), dtype=int)
    for y in range(SIZE):
        for x in range(SIZE):
            if(not(y*10+x in range(1, 21))):
                break
            board[y][x] = y*10+x
    print(board)
    return 0

test()
