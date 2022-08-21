'''
Main driver file. Handles user input and displays GameState object.
'''

import pygame as p
import ChessEngine, ChessAI
from multiprocessing import Process, Queue

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

'''
Initializes a global dictionary of images. This will be called exactly once in the main.
'''

def load_images():
    pieces = ['wp', 'wR', 'wB', 'wN', 'wQ', 'wK', 'bp', 'bR', 'bB', 'bN', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

'''
Main driver. Handles user input and updates the graphics.
'''

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT), p.NOFRAME)
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False

    load_images()
    running = True
    sqSelected = ()
    playerClicks = []

    gameOver = False

    playerOne = True
    playerTwo = False

    AIthinking = False
    moveFinderProcess = None
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                pieceNote = ''
                                if move.pieceMoved[1] != "p":
                                    pieceNote = move.pieceMoved[1]
                                print(pieceNote + move.getChessNotation())
                                gs.makeMove(validMoves[i])
                                playSound(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False

                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    moveMade = False
                    animate = False
                    gameOver = False

        #AI Logic
        if not gameOver and not humanTurn:
            if not AIthinking:
                AIthinking = True
                returnQueue = Queue()
                moveFinderProcess = Process(target = ChessAI.findBestMove,
                                            args = (gs, validMoves, returnQueue))
                moveFinderProcess.start()
            if not moveFinderProcess.is_alive():
                AImove = returnQueue.get()
                if AImove is None:
                    AImove = ChessAI.findRandomMove(validMoves)
                gs.makeMove(AImove)
                playSound(AImove)
                moveMade = True
                animate = True
                AIthinking = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkmate or gs.stalemate:
            gameOver = True

        clock.tick(MAX_FPS)
        p.display.flip()

def playSound(move):
    if move.pieceCaptured != '--' or move.enPassant:
        p.mixer.Sound.play(p.mixer.Sound("sounds/capture.wav"))
    elif move.castle:
        p.mixer.Sound.play(p.mixer.Sound("sounds/castle.wav"))
    else:
        p.mixer.Sound.play(p.mixer.Sound("sounds/move-self.wav"))

def highlightSquares(screen, gs, validMoves, sqSelected):
    s = p.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(200)

    if gs.inCheck:
        if gs.whiteToMove:
            r, c = gs.whiteKingLocation
        else:
            r, c = gs.blackKingLocation
        screen.blit(p.transform.scale(p.image.load("images/cm.png"), (SQ_SIZE, SQ_SIZE)),
                    p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s.fill(p.Color((206,210,107)))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            colors = [p.Color((240,217,181)), p.Color((181,136,99))]
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    if gs.board[move.endRow][move.endCol] != "--":
                        color = colors[(move.endRow+move.endCol)%2]
                        screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))
                        # p.draw.polygon(screen, color, [(SQ_SIZE*move.endCol, SQ_SIZE*move.endRow + 42.6), (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow + 21.3),
                        #                                (SQ_SIZE*move.endCol + 21.3, SQ_SIZE*move.endRow), (SQ_SIZE*move.endCol + 42.6, SQ_SIZE*move.endRow),
                        #                                (SQ_SIZE*move.endCol + 64, SQ_SIZE*move.endRow + 21.3), (SQ_SIZE*move.endCol + 64, SQ_SIZE*move.endRow + 42.6),
                        #                                (SQ_SIZE*move.endCol + 42.6, SQ_SIZE*move.endRow + 64), (SQ_SIZE*move.endCol + 21.3, SQ_SIZE*move.endRow + 64)])
                        p.draw.circle(screen, color, (SQ_SIZE*move.endCol + 32, SQ_SIZE*move.endRow + 32), 32)

                    else:
                        p.draw.circle(screen, p.Color((206,210,107)), (SQ_SIZE*move.endCol + 32, SQ_SIZE*move.endRow + 32), 10)


def highlightMoveMade(screen, gs):
    s = p.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(150)
    s.fill(p.Color("gray")) #(206,210,107)
    if gs.moveLog:
        lastMove = gs.moveLog[-1]
        screen.blit(s, (SQ_SIZE*lastMove.startCol, SQ_SIZE*lastMove.startRow))
        screen.blit(s, (SQ_SIZE*lastMove.endCol, SQ_SIZE*lastMove.endRow))


'''
Responsible for all graphic in the current game state.
'''

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightMoveMade(screen, gs)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)

'''
Responsible for drawing the 8 by 8 board 
'''

def drawBoard(screen):
    global colors
    colors = [p.Color((240,217,181)), p.Color((181,136,99))]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c)%2]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Responsible for placing the pieces on their corresponding squares.
'''

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = ((move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount))
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != "--" and frame < frameCount:
            if move.enPassant:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                screen.blit(IMAGES[move.pieceCaptured], endSquare)
            else:
                screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(200)

if __name__ == '__main__':
    main()
