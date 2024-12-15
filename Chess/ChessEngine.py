#store allat data storing allat info abt the state in the chess game also b responsbile for determining the valid moves at the current state and also move logs

class GameState ():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],  #the order of the chessboard (1st row)
            ["bp","bp","bp","bp","bp","bp","bp","bp"], #pawn row
            ["- -","- -","- -","- -","- -","- -","- -","- -"], #blank space
            ["- -","- -","- -","- -","- -","- -","- -","- -"],
            ["- -","- -","- -","- -","- -","- -","- -","- -"],
            ["- -","- -","- -","- -","- -","- -","- -","- -"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"], #pawn row (white)
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],]
        self.whiteToMove = True
        self.moveLog = []
        # Keep track of kings' positions
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        # For castling
        self.whiteCastleKingside = True
        self.whiteCastleQueenside = True
        self.blackCastleKingside = True
        self.blackCastleQueenside = True
        # For en passant
        self.enpassantPossible = () # coordinates for the square where en passant capture is possible
        
    def makemove(self, move): 
        self.board[move.startrow][move.startcol] = "- -"
        self.board[move.endrow][move.endcol] = move.piecemoved 
        self.moveLog.append(move) #log the move so can undo later
        self.whiteToMove = not self.whiteToMove #take turns
        
        # Update king's position
        if move.piecemoved == "wK":
            self.whiteKingLocation = (move.endrow, move.endcol)
        elif move.piecemoved == "bK":
            self.blackKingLocation = (move.endrow, move.endcol)
            
        # Pawn promotion
        if move.ispawnpromotion:
            promotedpiece = "Q" # auto-promote to queen for now
            self.board[move.endrow][move.endcol] = move.piecemoved[0] + promotedpiece
            
        # En passant
        if move.isenpassantmove:
            self.board[move.startrow][move.endcol] = "- -" # capturing the pawn
            
        # Update enpassantPossible
        if move.piecemoved[1] == "p" and abs(move.startrow - move.endrow) == 2:
            self.enpassantPossible = ((move.startrow + move.endrow)//2, move.startcol)
        else:
            self.enpassantPossible = ()
            
        # Castle move
        if move.iscastlemove:
            if move.endcol - move.startcol == 2: # Kingside castle
                self.board[move.endrow][move.endcol-1] = self.board[move.endrow][move.endcol+1]
                self.board[move.endrow][move.endcol+1] = "- -"
            else: # Queenside castle
                self.board[move.endrow][move.endcol+1] = self.board[move.endrow][move.endcol-2]
                self.board[move.endrow][move.endcol-2] = "- -"
                
        # Update castling rights
        self.updatecastlerights(move)
        
        # Check if a king was captured
        if move.piececaptured == "wK" or move.piececaptured == "bK":
            self.checkmate = True
            
    def undomove(self):
        if len(self.moveLog) != 0:  # make sure there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startrow][move.startcol] = move.piecemoved
            self.board[move.endrow][move.endcol] = move.piececaptured
            self.whiteToMove = not self.whiteToMove  # switch turns back
            
            # Update king's position if needed
            if move.piecemoved == "wK":
                self.whiteKingLocation = (move.startrow, move.startcol)
            elif move.piecemoved == "bK":
                self.blackKingLocation = (move.startrow, move.startcol)
                
            # Undo en passant move
            if move.isenpassantmove:
                self.board[move.endrow][move.endcol] = "- -"  # leave landing square blank
                self.board[move.startrow][move.endcol] = move.piececaptured
                self.enpassantPossible = (move.endrow, move.endcol)
            
            # Undo a 2 square pawn advance
            if move.piecemoved[1] == "p" and abs(move.startrow - move.endrow) == 2:
                self.enpassantPossible = ()

    def updatecastlerights(self, move):
        if move.piecemoved == "wK":
            self.whiteCastleKingside = False
            self.whiteCastleQueenside = False
        elif move.piecemoved == "bK":
            self.blackCastleKingside = False
            self.blackCastleQueenside = False
        elif move.piecemoved == "wR":
            if move.startrow == 7:
                if move.startcol == 0:
                    self.whiteCastleQueenside = False
                elif move.startcol == 7:
                    self.whiteCastleKingside = False
        elif move.piecemoved == "bR":
            if move.startrow == 0:
                if move.startcol == 0:
                    self.blackCastleQueenside = False
                elif move.startcol == 7:
                    self.blackCastleKingside = False

    def getvalidmoves(self):
        """
        Get all valid moves considering checks
        """
        temp_enpassant_possible = self.enpassantPossible
        temp_castle_rights = CastleRights(self.whiteCastleKingside, self.blackCastleKingside,
                                        self.whiteCastleQueenside, self.blackCastleQueenside)
        # Get all possible moves
        moves = self.getallpossiblemoves()
        
        # For each move, make it and see if it leaves king in check
        for i in range(len(moves) - 1, -1, -1):
            self.makemove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.is_in_check():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undomove()
            
        # Restore the enpassant and castle rights
        self.enpassantPossible = temp_enpassant_possible
        self.whiteCastleKingside = temp_castle_rights.wks
        self.blackCastleKingside = temp_castle_rights.bks
        self.whiteCastleQueenside = temp_castle_rights.wqs
        self.blackCastleQueenside = temp_castle_rights.bqs
        
        return moves

    def getallpossiblemoves(self):
        moves = []  # start with an empty list instead of a hardcoded move
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of columns in given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    if piece == 'p':
                        self.getpawnmoves(r,c,moves)
                    elif piece == 'R':
                        self.getrookmoves(r,c,moves)
                    elif piece == 'N':
                        self.getknightmoves(r,c,moves)
                    elif piece == 'B':
                        self.getbishopmoves(r,c,moves)
                    elif piece == 'Q':
                        self.getqueenmoves(r,c,moves)
                    elif piece == 'K':
                        self.getkingmoves(r,c,moves)
        return moves

#get all the pawn moves for the pawn located at row,col n add these moves to the list
    def getpawnmoves(self,r,c,moves):
        if self.whiteToMove:  # white pawn moves
            if r > 0 and self.board[r-1][c] == "- -":  # 1 square pawn advance
                moves.append(move((r,c), (r-1,c), self.board))
                if r == 6 and self.board[r-2][c] == "- -":  # 2 square pawn advance
                    moves.append(move((r,c), (r-2,c), self.board))
            # captures
            if r > 0 and c-1 >= 0 and self.board[r-1][c-1][0] == 'b':  # capture to left
                moves.append(move((r,c), (r-1,c-1), self.board))
            if r > 0 and c+1 <= 7 and self.board[r-1][c+1][0] == 'b':  # capture to right
                moves.append(move((r,c), (r-1,c+1), self.board))
            # En passant
            if (r-1, c-1) == self.enpassantPossible:
                attackingpiece = blockingpiece = False
                if self.whiteToMove:  # white to move
                    attackingpiece = self.board[r][c-1][0] == 'b'  # enemy piece to capture
                    blockingpiece = self.board[r-1][c-1] == "- -"  # blocking piece
                    if attackingpiece and blockingpiece:
                        m = move((r,c), (r-1,c-1), self.board)
                        m.isenpassantmove = True
                        moves.append(m)
            if (r-1, c+1) == self.enpassantPossible:
                attackingpiece = blockingpiece = False
                if self.whiteToMove:  # white to move
                    attackingpiece = self.board[r][c+1][0] == 'b'  # enemy piece to capture
                    blockingpiece = self.board[r-1][c+1] == "- -"  # blocking piece
                    if attackingpiece and blockingpiece:
                        m = move((r,c), (r-1,c+1), self.board)
                        m.isenpassantmove = True
                        moves.append(m)
        
        else:  # black pawn moves
            if r < 7 and self.board[r+1][c] == "- -":  # 1 square pawn advance
                moves.append(move((r,c), (r+1,c), self.board))
                if r == 1 and self.board[r+2][c] == "- -":  # 2 square pawn advance
                    moves.append(move((r,c), (r+2,c), self.board))
            # captures
            if r < 7 and c-1 >= 0 and self.board[r+1][c-1][0] == 'w':  # capture to left
                moves.append(move((r,c), (r+1,c-1), self.board))
            if r < 7 and c+1 <= 7 and self.board[r+1][c+1][0] == 'w':  # capture to right
                moves.append(move((r,c), (r+1,c+1), self.board))
            # En passant
            if (r+1, c-1) == self.enpassantPossible:
                attackingpiece = blockingpiece = False
                if not self.whiteToMove:  # black to move
                    attackingpiece = self.board[r][c-1][0] == 'w'  # enemy piece to capture
                    blockingpiece = self.board[r+1][c-1] == "- -"  # blocking piece
                    if attackingpiece and blockingpiece:
                        m = move((r,c), (r+1,c-1), self.board)
                        m.isenpassantmove = True
                        moves.append(m)
            if (r+1, c+1) == self.enpassantPossible:
                attackingpiece = blockingpiece = False
                if not self.whiteToMove:  # black to move
                    attackingpiece = self.board[r][c+1][0] == 'w'  # enemy piece to capture
                    blockingpiece = self.board[r+1][c+1] == "- -"  # blocking piece
                    if attackingpiece and blockingpiece:
                        m = move((r,c), (r+1,c+1), self.board)
                        m.isenpassantmove = True
                        moves.append(m)

    def getrookmoves(self,r,c,moves):
        directions = [(-1,0), (0,-1), (1,0), (0,1)]  # up, left, down, right
        enemy_color = 'b' if self.whiteToMove else 'w'
        
        for d in directions:
            for i in range(1,8):
                endrow = r + d[0] * i
                endcol = c + d[1] * i
                if 0 <= endrow < 8 and 0 <= endcol < 8:  # check if on board
                    endpiece = self.board[endrow][endcol]
                    if endpiece == "- -":  # empty space is valid
                        moves.append(move((r,c), (endrow,endcol), self.board))
                    elif endpiece[0] == enemy_color:  # capture enemy piece
                        moves.append(move((r,c), (endrow,endcol), self.board))
                        break
                    else:  # friendly piece
                        break
                else:  # off board
                    break

    def getknightmoves(self,r,c,moves):
        knight_moves = [(-2,-1), (-2,1), (-1,-2), (-1,2), 
                       (1,-2), (1,2), (2,-1), (2,1)]
        ally_color = 'w' if self.whiteToMove else 'b'
        
        for m in knight_moves:
            endrow = r + m[0]
            endcol = c + m[1]
            if 0 <= endrow < 8 and 0 <= endcol < 8:
                endpiece = self.board[endrow][endcol]
                if endpiece[0] != ally_color:  # not an ally piece (empty or enemy)
                    moves.append(move((r,c), (endrow,endcol), self.board))

    def getbishopmoves(self,r,c,moves):
        directions = [(-1,-1), (-1,1), (1,-1), (1,1)]  # diagonals
        enemy_color = 'b' if self.whiteToMove else 'w'
        
        for d in directions:
            for i in range(1,8):
                endrow = r + d[0] * i
                endcol = c + d[1] * i
                if 0 <= endrow < 8 and 0 <= endcol < 8:
                    endpiece = self.board[endrow][endcol]
                    if endpiece == "- -":
                        moves.append(move((r,c), (endrow,endcol), self.board))
                    elif endpiece[0] == enemy_color:
                        moves.append(move((r,c), (endrow,endcol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getqueenmoves(self,r,c,moves):
        self.getrookmoves(r,c,moves)  # Queen combines rook
        self.getbishopmoves(r,c,moves)  # and bishop moves

    def getkingmoves(self,r,c,moves):
        king_moves = [(-1,-1), (-1,0), (-1,1), (0,-1), 
                     (0,1), (1,-1), (1,0), (1,1)]
        ally_color = 'w' if self.whiteToMove else 'b'
        
        for i in range(8):
            endrow = r + king_moves[i][0]
            endcol = c + king_moves[i][1]
            if 0 <= endrow < 8 and 0 <= endcol < 8:
                endpiece = self.board[endrow][endcol]
                if endpiece[0] != ally_color:  # not an ally piece
                    # Check for castling
                    if endpiece == "- -" and abs(endcol - c) == 2:
                        if endcol - c == 2: # Kingside castle
                            if self.whiteToMove and self.whiteCastleKingside:
                                moves.append(move((r,c), (endrow,endcol), self.board))
                            elif not self.whiteToMove and self.blackCastleKingside:
                                moves.append(move((r,c), (endrow,endcol), self.board))
                        else: # Queenside castle
                            if self.whiteToMove and self.whiteCastleQueenside:
                                moves.append(move((r,c), (endrow,endcol), self.board))
                            elif not self.whiteToMove and self.blackCastleQueenside:
                                moves.append(move((r,c), (endrow,endcol), self.board))
                    else:
                        moves.append(move((r,c), (endrow,endcol), self.board))

    def is_in_check(self):
        """
        Determine if the current player is in check
        """
        if self.whiteToMove:
            return self.square_under_attack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.square_under_attack(self.blackKingLocation[0], self.blackKingLocation[1])

    def square_under_attack(self, r, c):
        """
        Determine if the square (r, c) is under attack by enemy pieces
        """
        self.whiteToMove = not self.whiteToMove  # Switch to opponent's perspective
        opp_moves = self.getallpossiblemoves()
        self.whiteToMove = not self.whiteToMove  # Switch back
        for move in opp_moves:
            if move.endrow == r and move.endcol == c:  # Square is under attack
                return True
        return False

    def check_checkmate_stalemate(self):
        """
        Check if the current position is checkmate or stalemate
        """
        if len(self.getvalidmoves()) == 0:  # No valid moves
            if self.is_in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class move():
    #maps keys to values where key : value
    #align the chess coordinates with the python based coordinates (0,0 in py is a8 in chess) goes down by matrix
    rankstorows = {"1" : 7, "2" : 6, "3" : 5, "4" : 4, "5" : 3, "6" : 2, "7" : 1, "8" : 0}
    rowstoranks = {v : k for k, v in rankstorows.items()} #reverse vk kv
    filestocols = {"a" : 0, "b" : 1, "c" : 2, "d" : 3, "e" : 4, "f" : 5, "g" : 6, "h" : 7}
    colstofiles = {v : k for k, v in filestocols.items()}

    def __init__(self, startsq, endsq, board): 
        self.startrow = startsq[0] #move from startcol0 to start col1 (pieces moving)
        self.startcol = startsq[1]
        self.endrow = endsq[0]
        self.endcol = endsq[1]
        self.piecemoved = board[self.startrow][self.startcol]
        self.piececaptured = board[self.endrow][self.endcol] #information of all a move in 1 place
        # Pawn promotion
        self.ispawnpromotion = (self.piecemoved == "wp" and self.endrow == 0) or \
                              (self.piecemoved == "bp" and self.endrow == 7)
        # En passant
        self.isenpassantmove = False
        # Castle move
        self.iscastlemove = False
        self.moveid = self.startrow * 1000 + self.startcol * 100 + self.endrow * 10 + self.endcol #move tht number into the thousands' place, gives a unique move id between 0-7777
        print(self.moveid)
    
    #overriding the equals method
    def __eq__(self, other):
        if isinstance(other, move):
            return self.moveid == other.moveid
        return False

    
    def getchessnotation(self) :
        #making real chess notations
        return self.getrankfile(self.startrow, self.startcol) + self.getrankfile(self.endrow, self.endcol)
    
    def getrankfile(self, r, c) : #row column
        return self.colstofiles[c] + self.rowstoranks[r]
    
    



      