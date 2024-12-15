#driver file (responsible for handling user input and displaying the current game state object)
import pygame as p
import ChessEngine 
import ChessAI
import random

width = height = 512 #512x512
dimension = 8 #8x8 dimensions
sq_size = height // dimension #square size = height / dimension
max_fps = 15 #for animations
images = {} 

#main driver : handles input n updating the graph
def main():
    p.init()
    screen = p.display.set_mode((width, height))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validmoves = gs.getvalidmoves()
    movemade = False #flag variable when a move is made
    animate = False  # flag for when we should animate a move
    loadimages() # only do this once before while loop
    gameOver = False
    playerOne = True  # True if human is playing white
    playerTwo = False  # False if AI is playing black

    running = True
    sqselected = () #no square is selected initially, keep track with the last click of the user (tuple : row, column)
    playerclicks = [] #keep track of the player clicks (2 tuples : r6, c4)

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                
            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    if humanTurn:
                        location = p.mouse.get_pos() #(x,y) location of the mouse
                        col = location[0]//sq_size
                        row = location[1]//sq_size
                        
                        if sqselected == (row,col): #user clicked the same square twice
                            sqselected = () #deselect
                            playerclicks = [] #clear clicks
                        else:
                            sqselected = (row,col)
                            playerclicks.append(sqselected) #append for both 1st and 2nd clicks
                        if len(playerclicks) == 2: #after 2nd click
                            move = ChessEngine.move(playerclicks[0], playerclicks[1], gs.board)
                            for i in range(len(validmoves)):
                                if move == validmoves[i]:
                                    gs.makemove(validmoves[i])
                                    movemade = True
                                    animate = True
                                    sqselected = () #reset user clicks
                                    playerclicks = []
                            if not movemade:
                                playerclicks = [sqselected]
                else:  # Game is over, any click resets
                    gs = ChessEngine.GameState()
                    validmoves = gs.getvalidmoves()
                    sqselected = ()
                    playerclicks = []
                    movemade = False
                    animate = False
                    gameOver = False

            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when z is pressed
                    gs.undomove()
                    movemade = True
                    animate = False
                    gameOver = False
                elif e.key == p.K_r:  # reset the game when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validmoves = gs.getvalidmoves()
                    sqselected = ()
                    playerclicks = []
                    movemade = False
                    animate = False
                    gameOver = False
        
        # AI move finder
        if not gameOver and not humanTurn:
            ai_move = ChessAI.find_best_move(gs)
            if ai_move is None:
                ai_move = random.choice(validmoves)
            gs.makemove(ai_move)
            movemade = True
            animate = True

        if movemade:
            if animate:
                animatemove(gs.moveLog[-1], screen, gs.board, clock)
            validmoves = gs.getvalidmoves()
            movemade = False
            animate = False

        drawGameState(screen, gs, sqselected, validmoves)

        # Check for checkmate or stalemate
        if not gameOver and len(validmoves) == 0:
            gameOver = True
            drawGameState(screen, gs, sqselected, validmoves)  # Redraw final position
            if gs.is_in_check():
                if gs.whiteToMove:
                    drawEndGameText(screen, "Black Wins!")
                else:
                    drawEndGameText(screen, "White Wins!")
            else:
                drawEndGameText(screen, "Stalemate!")
            p.display.flip()  # Update the display with the final position and message
            # Wait for player input to reset
            waiting = True
            while waiting and running:
                for event in p.event.get():
                    if event.type == p.QUIT:
                        running = False
                        waiting = False
                    elif event.type == p.MOUSEBUTTONDOWN or event.type == p.KEYDOWN:
                        waiting = False
                        gs = ChessEngine.GameState()
                        validmoves = gs.getvalidmoves()
                        sqselected = ()
                        playerclicks = []
                        movemade = False
                        animate = False
                        gameOver = False
            continue  # Skip the rest of the game loop after reset

        clock.tick(max_fps)
        p.display.flip()

def drawEndGameText(screen, text):
    font = p.font.SysFont("Arial", 32, True, False)
    textObject = font.render(text, False, p.Color("Black"))
    textLocation = p.Rect(0, 0, width, height).move(width/2 - textObject.get_width()/2, height/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    
    # Add "Click to reset" message
    resetFont = p.font.SysFont("Arial", 24, True, False)
    resetText = resetFont.render("Click to reset", False, p.Color("Black"))
    resetLocation = textLocation.move(0, textObject.get_height() + 10)
    screen.blit(resetText, resetLocation)

def animatemove(move, screen, board, clock):
    global colors
    coords = []  # list of coords that the animation will move through
    dR = move.endrow - move.startrow
    dC = move.endcol - move.startcol
    framesPerSquare = 10  # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r = move.startrow + dR*frame/frameCount
        c = move.startcol + dC*frame/frameCount
        drawboard(screen)
        drawpieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.endrow + move.endcol) % 2]
        endSquare = p.Rect(move.endcol*sq_size, move.endrow*sq_size, sq_size, sq_size)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle
        if move.piececaptured != "- -":
            if move.isenpassantmove:
                enpassantRow = move.endrow + 1 if move.piececaptured[0] == 'b' else move.endrow - 1
                endSquare = p.Rect(move.endcol*sq_size, enpassantRow*sq_size, sq_size, sq_size)
            screen.blit(images[move.piececaptured], endSquare)
        # draw moving piece
        screen.blit(images[move.piecemoved], p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))
        p.display.flip()
        clock.tick(60)

#initialize global dictionary of images, will be called exactly once in the main
def loadimages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        images[piece] = p.image.load("chess/images/" + piece + ".png")

def drawGameState(screen, gs, selectedsquare, validmoves):
    drawboard(screen)  # draw squares on the board
    highlightSquares(screen, gs, selectedsquare, validmoves)  # highlight selected square and valid moves
    drawpieces(screen, gs.board)  # draw pieces on top

def highlightSquares(screen, gs, selectedsquare, validmoves):
    if selectedsquare != ():
        r, c = selectedsquare
        # highlight selected square
        s = p.Surface((sq_size, sq_size))
        s.set_alpha(100)  # transparency value -> 0 transparent; 255 opaque
        s.fill(p.Color('blue'))
        screen.blit(s, (c*sq_size, r*sq_size))
        # highlight valid moves
        s.fill(p.Color('yellow'))
        for move in validmoves:
            if move.startrow == r and move.startcol == c:
                screen.blit(s, (move.endcol*sq_size, move.endrow*sq_size))

colors = [p.Color('white'), p.Color('gray')]
def drawboard(screen):
    for r in range(dimension):
        for c in range(dimension):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))

def drawpieces(screen, board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece != "- -": #not empty squares
                screen.blit(images[piece], p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))

if __name__ == "__main__":
    main()
