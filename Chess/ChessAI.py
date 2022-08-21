import random

pieceScore = {'K': 0, 'Q': 9, 'R': 5, 'N': 3, 'B': 3, 'p': 1}
CHECKMATE = 100
STALEMATE = 0
DEPTH = 4

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]

def findBestMove(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    findNegaMaxAB(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    returnQueue.put(nextMove)

# def findMinMax(gs, validMoves, depth, whiteToMove):
#     global nextMove
#     if depth == 0:
#         return scoreMaterial(gs.board)
#
#     if whiteToMove:
#         maxScore = -CHECKMATE
#         for move in validMoves:
#             gs.makeMove(move)
#             nextMoves = gs.getValidMoves()
#             score = findMinMax(gs, nextMoves, depth - 1, False)
#             if score > maxScore:
#                 maxScore = score
#                 if depth == DEPTH:
#                     nextMove = move
#             gs.undoMove()
#         return maxScore
#     else:
#         minScore = CHECKMATE
#         for move in validMoves:
#             gs.makeMove(move)
#             nextMoves = gs.getValidMoves()
#             score = findMinMax(gs, nextMoves, depth - 1, True)
#             if score < minScore:
#                 minScore = score
#                 if depth == DEPTH:
#                     nextMove = move
#             gs.undoMove()
#         return minScore

# def findNegaMax(gs, validMoves, depth, turnMultiplier):
#     global nextMove
#     if depth == 0:
#         return turnMultiplier * scoreBoard(gs)
#
#     maxScore = -CHECKMATE
#     for move in validMoves:
#         gs.makeMove(move)
#         nextMoves = gs.getValidMoves()
#         score = -findNegaMax(gs, nextMoves, depth - 1, -turnMultiplier)
#         if score > maxScore:
#             maxScore = score
#             if depth == DEPTH:
#                 nextMove = move
#         gs.undoMove()
#     return maxScore

def findNegaMaxAB(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findNegaMaxAB(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore
'''
Scores the overall position of both players. 
A positive score is good for white.
A negative score is good for black.
'''
def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.checkmate:
        return STALEMATE

    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score
