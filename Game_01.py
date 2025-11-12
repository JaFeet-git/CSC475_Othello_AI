#-----------------------------------------------------------------------------------#
#-----------Name:John Feet----------------------------------------------------------#
#-----------------------------------------------------------------------------------#
#-----------Date: 11/9/25-----------------------------------------------------------#
#-----------------------------------------------------------------------------------#
#-----------Description: This is the game othello where the player can choose-------#
#-----------to play against an AI or another player. The player can also allow------#
#-----------the AI to make turns for them.------------------------------------------#
#-----------------------------------------------------------------------------------#

import pygame
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_WIDTH))
pygame.display.set_caption("Matrix Board")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 150, 50)
GREEN2 = (0, 100, 30)
GREY = (150, 150, 150)

# Cell dimensions and board size
buffer = 150 #is 1/2 of the boarder
COLS = 10
CELL_SIZE = (SCREEN_WIDTH-buffer) // (COLS-2)  # Always a square board

#Fonts for text
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 30)

#game stats and states
whiteTurn = True #White Player is moving
aiTurn = False #Player gives AI a turn
running = True #Game is running
prune = True #AI starts by pruning
vsAI = False #Player vs AI mode
gameState = "MainMenu" #Interface for player
mouseCoord = [0,0] #Mouse location
validMoves = [] #List of valid moves
maxDepth = 3 #how many play in the future

#DEBUGS
DEBUG = False #See history of game
DEBUGTREE = True #Show each decision tree
DEBUGNODES = False #See each node decision
DEBUGPRUNE = False #See pruning decisions

"""--------------Fundamential functions used through all lower functions--------------"""
def initializeGame(rows, cols):
    matrix = [] 
    debugMatrix = []

    for i in range(rows): #build board
        row = []
        debugRow = [] #debug row = [Coord, Corner, Side, Middle]
        for j in range(cols):
            """Make Normal Matrix"""
            if ((i==0 and j==0) or (i==0 and j==cols-1) or (i==rows-1 and j==0) or (i==rows-1 and j==cols-1)): row.append("#") #blank corners
            elif (i==0): row.append(str(chr(j+64)))
            elif (j==0): row.append(str(i))
            elif (i==rows-1): row.append(str(chr(j+64)))
            elif (j==cols-1): row.append(str(i))
            else: row.append("-")

            """Make Debug Matrix"""
            coord = str(str(chr(j+64))+str(i))
            if ((i==1 and j==1) or (i==rows-1 and j==1) or (i==1 and j==cols-1) or (i==rows-1 and j==cols-1)): debugRow.append([coord, True, False, False]) #Corner
            elif (i==0 or j==0): debugRow.append([coord, False, False, False]) #in the Coords
            elif ((i==1 or i==rows-1 or j==1 or j==cols-1)): debugRow.append([coord, False, True, False]) #Side
            else: debugRow.append([coord, False, False, True])

        matrix.append(row)  # adding rows to the matrix
        debugMatrix.append(debugRow)

    #Make starting point
    matrix[int(((rows+1)/2))][int(((cols+1)/2))] = "O"
    matrix[int(((rows-1)/2))][int(((cols+1)/2))] = "X"
    matrix[int(((rows+1)/2))][int(((cols-1)/2))] = "X"
    matrix[int(((rows-1)/2))][int(((cols-1)/2))] = "O"

    return (matrix, debugMatrix)

def toggleMove():
    global whiteTurn
    if whiteTurn:
        whiteTurn = False
    else:
        whiteTurn = True

def printSmall(matrix: list):
    rows = len(matrix)
    cols = len(matrix[0])
    for i in range(rows):
        for j in range(cols):
            print(matrix[i][j], end=" ")
        print()

def copyMatrix(matrix: list):
    copiedMatrix = []
    
    rows = len(matrix)
    cols = len(matrix[0])
    for i in range(rows):
        cRow =[]
        for j in range(cols):
            cRow.append(matrix [i][j])
        copiedMatrix.append(cRow)
    return (copiedMatrix)

def getScore(matrix: list):
    black = 0
    white = 0
    rows = len(matrix)
    cols = len(matrix[0])
    for i in range(1, rows):
        for j in range(1, cols):
            if (matrix[i][j] == "X"): black += 1
            elif (matrix[i][j] == "O"): white += 1
    
    return(white, black)

"""--------------Pygame Stuff (Researched from Pygame website but no copy-paste)--------------"""
def draw_text(text, font, color, surface, x, y): #Draws custom text easily
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def draw_button(text, textColor, buttonColor, x, y, xMax, yMax): #Function to draw buttons (just a square with text)
    pygame.draw.rect(screen, buttonColor, (x, y, xMax, yMax))
    pygame.draw.rect(screen, BLACK, (x, y, xMax, yMax), 1)
    draw_text(text, small_font, textColor, screen, x+xMax/2, y+yMax/2)

def drawGameBoard(matrix):
    if (whiteTurn): #Change the title of who's turn at bottom of board
        draw_text("White Turn", font, WHITE, screen, SCREEN_WIDTH//2, SCREEN_WIDTH-40)
        if aiTurn: draw_text("AI White", font, WHITE, screen, SCREEN_WIDTH//2, SCREEN_WIDTH-40)
    elif (vsAI):
        draw_text("PogFish Turn", font, BLACK, screen, SCREEN_WIDTH//2, SCREEN_WIDTH-40) #Yes im calling the AI PogFish
    else:
        draw_text("Black Turn", font, BLACK, screen, SCREEN_WIDTH//2, SCREEN_WIDTH-40)
        if aiTurn: draw_text("AI Black", font, WHITE, screen, SCREEN_WIDTH//2, SCREEN_WIDTH-40)

    for row_index, row in enumerate(matrix[1:COLS-1]):
        for col_index, cell_value in enumerate(row[1:COLS-1]):
            # Calculate position for each cell
            x = col_index * CELL_SIZE +buffer/2
            y = row_index * CELL_SIZE +buffer/2
            
            # Draw the cell rectangle
            pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1) # Border
            
            # Fill the cell based on its value in the matrix
            if cell_value == "X":
                pygame.draw.circle(screen, BLACK, (x+CELL_SIZE/2, y+CELL_SIZE/2), ((CELL_SIZE/2)-3))
            elif cell_value == "O":
                pygame.draw.circle(screen, WHITE, (x+CELL_SIZE/2, y+CELL_SIZE/2), ((CELL_SIZE/2)-3))
            elif cell_value == "+": #Shows possible moves (will do this if im board) Yeah not doing this
                pygame.draw.circle(screen, RED, (x+CELL_SIZE/2, y+CELL_SIZE/2), ((CELL_SIZE/2)-3))
                pygame.draw.circle(screen, GREEN, (x+CELL_SIZE/2, y+CELL_SIZE/2), ((CELL_SIZE/2)-5))

"""--------------Logic moves to maintain and change board--------------"""
def updateBoard(updateMatrix: list, placeRow, placeCol): #change the rest of the pieces

    rows = len(updateMatrix) #get borders of matrix
    cols = len(updateMatrix[0]) #get borders of matrix
    
    if (updateMatrix[placeRow][placeCol]=="X"): #black's turn
        found = False
        p = 1
        while ((placeRow+p) < rows): #Find another X
            if (updateMatrix[placeRow+p][placeCol] == "-"): break
            elif( updateMatrix[placeRow+p][placeCol] == "X"): found = True
            p+=1
        if found:
            p = 1
            while ((placeRow+p) < rows): #replace all down O's
                if (updateMatrix[placeRow+p][placeCol] == "O"):
                    updateMatrix[placeRow+p][placeCol] = "X"
                else: break
                p+=1
        
        found = False
        p = 1
        while ((placeRow-p) > 0): #Find another X
            if (updateMatrix[placeRow-p][placeCol] == "-"): break
            elif( updateMatrix[placeRow-p][placeCol] == "X"): found = True
            p+=1
        if found:
            p = 1
            while ((placeRow-p) > 0): #replace all upper O's
                if (updateMatrix[placeRow-p][placeCol] == "O"):
                    updateMatrix[placeRow-p][placeCol] = "X"
                else: break
                p+=1
        
        found = False
        p = 1
        while ((placeCol+p) < cols): #Find another X
            if (updateMatrix[placeRow][placeCol+p] == "-"): break
            elif(updateMatrix[placeRow][placeCol+p] == "X"): found = True
            p+=1
        if found:
            p = 1
            while ((placeCol+p) < cols): #replace all right O's
                if (updateMatrix[placeRow][placeCol+p] == "O"):
                    updateMatrix[placeRow][placeCol+p] = "X"
                else: break
                p+=1
        
        found = False
        p = 1
        while ((placeCol-p) > 0): #Find another X
            if (updateMatrix[placeRow][placeCol-p] == "-"): break
            elif(updateMatrix[placeRow][placeCol-p] == "X"): found = True
            p+=1
        if found:
            p=1
            while ((placeCol-p) > 0): #replace all left O's
                if (updateMatrix[placeRow][placeCol-p] == "O"):
                    updateMatrix[placeRow][placeCol-p] = "X"
                else: break
                p+=1
        
        found = False
        p = 1
        while (((placeRow+p) < rows) and ((placeCol+p) < cols)): #Find another X
            if (updateMatrix[placeRow+p][placeCol+p] == "-"): break
            elif(updateMatrix[placeRow+p][placeCol+p] == "X"): found = True
            p+=1
        if found:
            p=1
            while (((placeRow+p) < rows) and ((placeCol+p) < cols)): #replace all DownRight O's
                if (updateMatrix[placeRow+p][placeCol+p] == "O"):
                    updateMatrix[placeRow+p][placeCol+p] = "X"
                else: break
                p+=1
        
        found = False
        p = 1
        while (((placeRow+p) < rows) and ((placeCol-p) > 0)): #Find another X
            if (updateMatrix[placeRow+p][placeCol-p] == "-"): break
            elif(updateMatrix[placeRow+p][placeCol-p] == "X"): found = True
            p+=1
        if found:
            p=1
            while (((placeRow+p) < rows) and ((placeCol-p) > 0)): #replace all DownLeft O's
                if (updateMatrix[placeRow+p][placeCol-p] == "O"):
                    updateMatrix[placeRow+p][placeCol-p] = "X"
                else: break
                p+=1
        
        found = False
        p = 1
        while (((placeRow-p) > 0) and ((placeCol+p) < cols)): #Find another X
            if (updateMatrix[placeRow-p][placeCol+p] == "-"): break
            elif(updateMatrix[placeRow-p][placeCol+p] == "X"): found = True
            p+=1
        if found:
            p=1
            while (((placeRow-p) > 0) and ((placeCol+p) < cols)): #replace all UpRight O's
                if (updateMatrix[placeRow-p][placeCol+p] == "O"):
                    updateMatrix[placeRow-p][placeCol+p] = "X"
                else: break
                p+=1
        
        found = False
        p = 1
        while (((placeRow-p) > 0) and ((placeCol-p) > 0)): #Find another X
            if (updateMatrix[placeRow-p][placeCol-p] == "-"): break
            elif(updateMatrix[placeRow-p][placeCol-p] == "X"): found = True
            p+=1
        if found:
            p=1
            while (((placeRow-p) > 0) and ((placeCol-p) > 0)): #replace all UpLeft O's
                if (updateMatrix[placeRow-p][placeCol-p] == "O"):
                    updateMatrix[placeRow-p][placeCol-p] = "X"
                else: break
                p+=1

    #--------------------------------- Look for O's ---------------------------------#
    elif (updateMatrix[placeRow][placeCol]=="O"): #white's turn
        found = False
        p = 1
        while ((placeRow+p) < rows): #Find another O
            if (updateMatrix[placeRow+p][placeCol] == "-"): break
            elif( updateMatrix[placeRow+p][placeCol] == "O"): found = True
            p+=1
        if found:
            p = 1
            while ((placeRow+p) < rows): #replace all down X's
                if (updateMatrix[placeRow+p][placeCol] == "X"):
                    updateMatrix[placeRow+p][placeCol] = "O"
                else: break
                p+=1
        
        found = False
        p = 1
        while ((placeRow-p) > 0): #Find another O
            if (updateMatrix[placeRow-p][placeCol] == "-"): break
            elif( updateMatrix[placeRow-p][placeCol] == "O"): found = True
            p+=1
        if found:
            p = 1
            while ((placeRow-p) > 0): #replace all upper X's
                if (updateMatrix[placeRow-p][placeCol] == "X"):
                    updateMatrix[placeRow-p][placeCol] = "O"
                else: break
                p+=1
        
        found = False
        p = 1
        while ((placeCol+p) < cols): #Find another O
            if (updateMatrix[placeRow][placeCol+p] == "-"): break
            elif(updateMatrix[placeRow][placeCol+p] == "O"): found = True
            p+=1
        if found:
            p = 1
            while ((placeCol+p) < cols): #replace all right X's
                if (updateMatrix[placeRow][placeCol+p] == "X"):
                    updateMatrix[placeRow][placeCol+p] = "O"
                else: break
                p+=1
        
        found = False
        p = 1
        while ((placeCol-p) > 0): #Find another O
            if (updateMatrix[placeRow][placeCol-p] == "-"): break
            elif(updateMatrix[placeRow][placeCol-p] == "O"): found = True
            p+=1
        if found:
            p=1
            while ((placeCol-p) > 0): #replace all left X's
                if (updateMatrix[placeRow][placeCol-p] == "X"):
                    updateMatrix[placeRow][placeCol-p] = "O"
                else: break
                p+=1
        
        found = False
        p = 1
        while (((placeRow+p) < rows) and ((placeCol+p) < cols)): #Find another O
            if (updateMatrix[placeRow+p][placeCol+p] == "-"): break
            elif(updateMatrix[placeRow+p][placeCol+p] == "O"): found = True
            p+=1
        if found:
            p=1
            while (((placeRow+p) < rows) and ((placeCol+p) < cols)): #replace all DownRight X's
                if (updateMatrix[placeRow+p][placeCol+p] == "X"):
                    updateMatrix[placeRow+p][placeCol+p] = "O"
                else: break
                p+=1
        
        found = False
        p = 1
        while (((placeRow+p) < rows) and ((placeCol-p) > 0)): #Find another O
            if (updateMatrix[placeRow+p][placeCol-p] == "-"): break
            elif(updateMatrix[placeRow+p][placeCol-p] == "O"): found = True
            p+=1
        if found:
            p=1
            while (((placeRow+p) < rows) and ((placeCol-p) > 0)): #replace all DownLeft X's
                if (updateMatrix[placeRow+p][placeCol-p] == "X"):
                    updateMatrix[placeRow+p][placeCol-p] = "O"
                else: break
                p+=1
        
        found = False
        p = 1
        while (((placeRow-p) > 0) and ((placeCol+p) < cols)): #Find another O
            if (updateMatrix[placeRow-p][placeCol+p] == "-"): break
            elif(updateMatrix[placeRow-p][placeCol+p] == "O"): found = True
            p+=1
        if found:
            p=1
            while (((placeRow-p) > 0) and ((placeCol+p) < cols)): #replace all UpRight X's
                if (updateMatrix[placeRow-p][placeCol+p] == "X"):
                    updateMatrix[placeRow-p][placeCol+p] = "O"
                else: break
                p+=1
        
        found = False
        p = 1
        while (((placeRow-p) > 0) and ((placeCol-p) > 0)): #Find another O
            if (updateMatrix[placeRow-p][placeCol-p] == "-"): break
            elif(updateMatrix[placeRow-p][placeCol-p] == "O"): found = True
            p+=1
        if found:
            p=1
            while (((placeRow-p) > 0) and ((placeCol-p) > 0)): #replace all UpLeft X's
                if (updateMatrix[placeRow-p][placeCol-p] == "X"):
                    updateMatrix[placeRow-p][placeCol-p] = "O"
                else: break
                p+=1

    return(updateMatrix)

def placeMarker(placeMatrix: list, reqRow, reqCol): #Place the requested piece if possible
    global whiteTurn

    if whiteTurn:
        placeMatrix[reqRow][reqCol] = "O"
        whiteTurn = False 

    else:
        placeMatrix[reqRow][reqCol] = "X"
        whiteTurn = True 
        
    return(placeMatrix)

def checkValidMove(matrix, reqRow, reqCol):
    global whiteTurn

    ogWhite, ogBlack = getScore(matrix)
    testMatrix = copyMatrix(matrix)

    if ((matrix[reqRow][reqCol] != "-")):#make sure spot is not taken
            return False
    #elif ((matrix[reqRow+1][reqCol] not in ["X", "O"]) and (matrix[reqRow-1][reqCol] not in ["X", "O"]) and (matrix[reqRow][reqCol+1] not in ["X", "O"]) and (matrix[reqRow][reqCol-1] not in ["X", "O"])):
            #return False
    
    newWhite, newBlack = getScore(updateBoard(placeMarker(testMatrix, reqRow, reqCol), reqRow, reqCol))

    #toggle turn back bc place toggle turn forward
    toggleMove()

    if ((whiteTurn) and ((newWhite - ogWhite) > 1)): #make sure that a piece is captured
        return True
    elif ((not whiteTurn) and ((newBlack - ogBlack) > 1)): #make sure that a piece is captured
        return True
    else:
        #print("False")
        return False

def checkFull(matrix: list): #check if matrix is full
    rows = len(matrix)
    cols = len(matrix[0])
    for i in range(1, rows):
        for j in range(1, cols):
            if ((matrix[i][j] == "-")):
                return False
    return True

def validMoves(matrix): #count the number of valid moves
    rows = len(matrix)
    validCount = 0
    for i in range(1,rows):
        for j in range(1,rows):
            if checkValidMove(matrix, i, j):
                validCount += 1
    
    return validCount

def showValidMoves(matrix): #show any/all possible moves
    rows = len(matrix)
    for i in range(1,rows):
        for j in range(1,rows):
            if checkValidMove(matrix, i, j):
                matrix[i][j] = "+"

def anyPossibleMoves(matrix): #check if Black or White can move
    if (validMoves(matrix) == 0):
        toggleMove() #check if other player can move
        print("Toggle")
        if (validMoves(matrix) == 0):
            toggleMove() #turn back for end of game
            return False

    return True #There are moves for the other person

"""--------------Tree for MinMax function--------------"""
class TreeNode: #Tree to decide next best move
    def __init__(self, move, treeMatrix, localWhiteTurn, isMaxing): #Initialize a tree to decide best moves 
        self.move = move #everything in here was modified from sample code
        self.parent = None
        self.children = []
        self.maxing = isMaxing
        self.localWhite = localWhiteTurn
        self.gameMatrix = copyMatrix(treeMatrix)
        self.nextMatrix = copyMatrix(treeMatrix)
        self.opponentMoves = 0
        self.value = 0 #value based on score, position, and possible moves

        #get possible opponent moves value
        possibleMoves = validMoves(self.gameMatrix)
        self.possibleMoves = validMoves(self.gameMatrix)

        #get position value
        positionValue = 0 
        oppScore = 0 
        if (self.move != "None"):
            coordList = self.move.split(',') 
            row = int(coordList[0])
            col = int(coordList[1])
            if (debugMatrix[row][col][1]): #corner
                positionValue = 20
            elif (debugMatrix[row][col][2]): #side
                positionValue = 15

            #get opponent moves and score
            tempMatrix = updateBoard(placeMarker(copyMatrix(self.nextMatrix), row, col), row, col)
            self.opponentMoves = validMoves(tempMatrix)
            #get current score value
            white, black = getScore(tempMatrix) 
            if whiteTurn: #set score based on turn
                oppScore = white - black
            else:
                oppScore = black - white
            toggleMove()

            if (self.opponentMoves == 0):
                if (oppScore > 0):
                    positionValue = -9999
                else:
                    positionValue = 9999

        #get current score value
        scoreDiff = 0 
        white, black = getScore(self.gameMatrix) 
        if whiteTurn: #set score based on turn
            scoreDiff = white - black
        else:
            scoreDiff = black - white
        
        self.value = scoreDiff + possibleMoves + positionValue - oppScore - (self.opponentMoves*2)

        if self.parent: 
            self.value = self.value + self.parent.value #add the parents value

    def add_child(self, child_node): #add a child node (from sample code)
        child_node.parent = self
        self.children.append(child_node)
        
    def get_level(self): #get the level of the node (Also from gemini sample code)
        level = 0
        p = self.parent
        while p:
            level += 1
            p = p.parent
        return level
    
    def makeChildren(self): #make all prossible children up to depth
        rows = len(self.gameMatrix)
        for i in range(1,rows): #Check the whole board
            for j in range(1,rows):
                if (whiteTurn != self.localWhite): #make sure turn matches
                    toggleMove() 

                if checkValidMove(self.gameMatrix, i, j): #only add valid moves to the node
                    Name = str(i) + "," + str(j)
                    tempMatrix = updateBoard(placeMarker(copyMatrix(self.gameMatrix), i, j), i, j)
                    toggleMove()
                    if self.localWhite:
                        if self.maxing:
                            self.add_child(TreeNode(Name, tempMatrix, False, False)) #Is now black Turn and Min node
                        else:
                            self.add_child(TreeNode(Name, tempMatrix, False, True)) #Is now black turn and Max node
                    else:
                        if self.maxing:
                            self.add_child(TreeNode(Name, tempMatrix, True, False)) #Is now white Turn and Min node
                        else:
                            self.add_child(TreeNode(Name, tempMatrix, True, True)) #Is now white turn and Max node
                
        if (self.get_level() < (maxDepth-1)): #have children spread
            if self.children:
                for child in self.children: #Make first set of children only does first layer
                    child.makeChildren()
                    if (child.get_level() < (maxDepth-1)):
                        if child.children: #children to make children and this goes infinitely
                            for child2 in child.children:
                                child2.makeChildren()

    def print_tree(self): #Print the tree (I Got this when I looked up tree classes on google. I got this from the top search AI [ig gemini])
        spaces = ' ' * self.get_level() * 4
        prefix = spaces + "|__" if self.parent else ""
        print(prefix + str(self.move) + ": " + str(self.value) + " MAX? " + str(self.maxing))
        if self.children:
            for child in self.children:
                child.print_tree()
    
    def setMinMax(self): #set the values for min and maxing
        if self is None:
            return
        if(self.maxing and self.children): #max-ing
            self.value = -99999 
        elif ((not self.maxing) and self.children): #min-ing
            self.value = 99999
        for child in self.children: #Do this for every node
            child.setMinMax()

    def searchMinMax(self): #Do the MinMax Search
        if self is None:
            return
        
        compVal = self.value #Set base value (-9999 or 9999)

        for child in self.children:
            #Depth First
            child.searchMinMax()

            #Set child values
            compVal = child.value
            compMove = child.move

            #DEBUGing nodes
            if self.parent:
                if DEBUGNODES:
                    print("Node:\t\t Grand\t\tParent\t\tChild".format(self.parent.move, self.move, compMove))
                    print("Position\t {} \t\t {} \t\t {}".format(self.parent.move, self.move, compMove))
                    print("Value\t\t {} \t\t {} \t\t {}".format(self.parent.value, self.value, compVal))
                    print("")
            
            #DEBUGing nodes
            elif DEBUGNODES:
                    print("Node:\t\t Grand\t\tParent\t\tChild".format("None", self.move, compMove))
                    print("Position\t {} \t\t {} \t\t {}".format("None", self.move, compMove))
                    print("Value\t\t {} \t\t {} \t\t {}".format("None", self.value, compVal))
                    print("")

            if ((prune) and (self.parent)): #if pruning and node has a parent (grandparent)
                if DEBUGPRUNE: #This is for Debuging if a branch is pruned
                    print("Node:\t\t Grand\t\tParent\t\tChild".format(self.parent.move, self.move, compMove))
                    print("Position\t {} \t\t {} \t\t {}".format(self.parent.move, self.move, compMove))
                    print("Value\t\t {} \t\t {} \t\t {}".format(self.parent.value, self.value, compVal))
                    print("")

                if ((self.parent.maxing) and (not self.maxing) and (self.parent.value > self.value)): #if grandparent is max and parent is min
                    if DEBUGPRUNE: print("----------------prune by MAX----------------\n")
                    child.value = "Prune" #Show a prune in the tree 
                    break #prune branch
                elif ((not self.parent.maxing) and (self.maxing) and (self.parent.value < self.value)): #grandparent is min and parent is max
                    if DEBUGPRUNE: print("----------------prune by MIN----------------\n")
                    child.value = "Prune" #Show a prune in the tree
                    break #prune branch

            if ((self.maxing) and (self.value < compVal)): #set parent node if maxing and childe > parent
                self.value = compVal
                if (child.get_level() == 1):
                    self.move = compMove
            elif ((not self.maxing) and (self.value > compVal)): #set parent node if mining and child < parent
                self.value = compVal
                if (child.get_level() == 1):
                    self.move = compMove
        
        if self.parent: #set grandparent node
            if ((self.parent.maxing) and (self.parent.value < compVal)): #same as last function
                self.parent.value = self.value
                if (self.get_level() == 1):
                    self.parent.move = self.move
            elif ((not self.parent.maxing) and (self.parent.value > compVal)): #same as last function
                self.parent.value = self.value
                if (self.get_level() == 1):
                    self.parent.move = self.move

    def setOneNode(self): #Set movement node so our first options isnt NULL <- will crash code if NULL
        self.move = self.children[0].move
                
"""--------------Begin Main Code--------------"""
matrix, debugMatrix = initializeGame(COLS, COLS)
wFinal = 0
bFinal = 0

#Get time for thinking delay
currentTime = time.time()
delayTime = time.time()

while (running):
    currentTime = time.time() #update time
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #Be able to leave
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN: #See any Click
            if event.button == 1:
                mouseCoord = event.pos
                if DEBUG: #Simple Debug to track the board
                    print("--Player Move--")
                    printSmall(matrix)
                    print("--Player Move--")
                #print(mouseCoord)

    screen.fill(GREEN) # Clear the screen
    draw_text("--OTHELLO--", font, WHITE, screen, SCREEN_WIDTH//2, 40) #Title of Game
    
    if (gameState == "Game"): #Game is active
        if (not checkFull(matrix) and anyPossibleMoves(matrix)): #make sure there are valid moves
            drawGameBoard(matrix) # Draw the board
            draw_button("AI turn", WHITE, GREEN2, SCREEN_WIDTH-150, ((SCREEN_WIDTH-buffer/2)+10), 100, 60) #Draw AI Turn Button
            if prune:
                draw_button("Prune on", WHITE, GREEN2, 80, ((SCREEN_WIDTH-buffer/2)+10), 100, 60) #Draw Alpha Toggle Button
            else:
                draw_button("Prune off", WHITE, RED, 80, ((SCREEN_WIDTH-buffer/2)+10), 100, 60) #Draw Alpha Toggle Button
            draw_button("End Game", WHITE, GREEN2, SCREEN_WIDTH-150, 10, 110, 60) #Draw End Game Button

            """ GET Button Actions """
            #Get button actions
            if ((mouseCoord[0] > (SCREEN_WIDTH-150)) and (mouseCoord[0] < SCREEN_WIDTH-150+110) and (mouseCoord[1] > 10) and (mouseCoord[1] < 10+60)): #Within End Button Coords
                gameState = "EndMenu"

            #AI turn
            elif ((mouseCoord[0] > (SCREEN_WIDTH-150) and (mouseCoord[0] < ((SCREEN_WIDTH-150)+100)) and (mouseCoord[1] > ((SCREEN_WIDTH-buffer/2)+10)) and (mouseCoord[1] < ((SCREEN_WIDTH-buffer/2)+10)+60))): #Within AI Button Coords
                aiTurn = True
                #print("AI Mode")

            #Pruning Toggle
            elif ((mouseCoord[0] > (80) and (mouseCoord[0] < (180) ) and (mouseCoord[1] > ((SCREEN_WIDTH-buffer/2)+10)) and (mouseCoord[1] < ((SCREEN_WIDTH-buffer/2)+10)+60))): #Within AI Button Coords
                if prune: #toggle alpha AI mode
                    prune = False

                elif (not prune):
                    prune = True

            """ GET MOVE """
            #vsAI mode (AI Turn from gamemode)
            if ((not whiteTurn) and (vsAI)): #it is the AI's turn in PvE

                if ((delayTime-currentTime) < 0):
                    #do AI Action
                    root = TreeNode("None", matrix, whiteTurn, True) #Init Decision Tree
                    root.makeChildren() #Grow the tree with possible moves
                    if DEBUGTREE: #Show diffrence in trees
                        print("-------------Pre Search-------------")
                        root.print_tree()
                    root.setOneNode() #Set default move
                    root.setMinMax() #Set the min and max values
                    root.searchMinMax() #Search the tree for best move
                    if DEBUGTREE: #Show diffrence in trees
                        print("-------------Post Search-------------")
                        root.print_tree()

                    aiMove = root.move.split(',') #get best move
                    row = int(aiMove[0]) #make best move
                    col = int(aiMove[1]) #make best move

                    if (root.localWhite != whiteTurn): #make sure turns are aligned
                        toggleMove()

                    matrix = placeMarker(matrix, row, col) #Make the move
                    matrix = updateBoard(matrix, row, col) #Make the move

                    if DEBUG: #Track Board the move
                        print("--AI Move--")
                        printSmall(matrix)
                        print("--AI Move--")
            
            #AI's Turn (From a Player)
            elif (aiTurn): #Same comments from 712
                #do AI action
                root = TreeNode("None", matrix, whiteTurn, True) 
                root.makeChildren()
                if DEBUGTREE:
                    print("-------------Pre Search-------------")
                    root.print_tree()
                root.setOneNode()
                root.setMinMax()
                root.searchMinMax()
                if DEBUGTREE:
                    print("-------------Post Search-------------")
                    root.print_tree()

                aiMove = root.move.split(',') #get best move
                row = int(aiMove[0])
                col = int(aiMove[1])

                if (root.localWhite != whiteTurn): #make sure turns are aligned
                    toggleMove()

                matrix = placeMarker(matrix, row, col)
                matrix = updateBoard(matrix, row, col)

                delayTime = currentTime + 1

                if DEBUG:
                    print("--AI Move--")
                    printSmall(matrix)
                    print("--AI Move--")

                aiTurn = False  

            #Place piece (a Player is placing a piece)
            elif ((mouseCoord[0] > (buffer/2)) and (mouseCoord[0] < ((SCREEN_WIDTH-(buffer/2)))) and (mouseCoord[1] > (buffer/2)) and (mouseCoord[1] < ((SCREEN_WIDTH-(buffer/2))))): #Within Button Coords
                reqX = int((mouseCoord[1]-(buffer/2))/CELL_SIZE)+1 #shrink board from screen size to number of tiles for coords
                reqY = int((mouseCoord[0]-(buffer/2))/CELL_SIZE)+1 #shrink board from screen size to number of tiles for coords
                if (checkValidMove(matrix, reqX, reqY)): #Make sure move is valid
                    matrix = placeMarker(matrix, reqX, reqY) #Allow move if valid
                    matrix = updateBoard(matrix, reqX, reqY) #Allow move if valid
                    delayTime = currentTime + 0.5 #Start move delay so there is no instant response           

        else: gameState = "EndMenu" #protect from crashing and end game automatically

    elif (gameState == "MainMenu"): #Main Menu 
        draw_button("Player Vs Player", WHITE, GREEN2, 100, 100, 200, 60) #Draw vsPlayer Button
        draw_button("Player Vs AI", WHITE, GREEN2, SCREEN_WIDTH-300, 100, 200, 60) #Draw vsAI Button

        if ((mouseCoord[0] > (100)) and (mouseCoord[0] < 300) and (mouseCoord[1] > 100) and (mouseCoord[1] < 160)): #Within PvP Coords
            matrix, debugMatrix = initializeGame(COLS, COLS) #restart game
            vsAI = False
            gameState = "Game" #Start game in PvP mode
            
        elif ((mouseCoord[0] > (SCREEN_WIDTH-300)) and (mouseCoord[0] < SCREEN_WIDTH-300+200) and (mouseCoord[1] > 100) and (mouseCoord[1] < 100+60)): #Within PvAI Coords
            matrix, debugMatrix = initializeGame(COLS, COLS) #restart game
            vsAI = True
            gameState = "Game" #Start game in PvE mode

    elif (gameState == "EndMenu"): #The game's ending menu
        wFinal, bFinal = getScore(matrix)
        
        draw_button("Return to Main Menu", WHITE, GREEN2, (SCREEN_WIDTH/2)-150, ((SCREEN_WIDTH/2)+50), 300, 60) #Draw Return Button
        draw_button("See Board", WHITE, GREEN2, SCREEN_WIDTH-150, 10, 110, 60) #Draw Return Button
        draw_text("--White--", font, WHITE, screen, ((SCREEN_WIDTH//2)-150), ((SCREEN_WIDTH/2)-150)) #White Cards of Game
        draw_text((str(wFinal)), font, WHITE, screen, ((SCREEN_WIDTH//2)-150), ((SCREEN_WIDTH/2)-100)) #White Score of Game
        draw_text("--Black--", font, BLACK, screen, ((SCREEN_WIDTH//2)+150), ((SCREEN_WIDTH/2)-150)) #Black Cards of Game
        draw_text((str(bFinal)), font, BLACK, screen, ((SCREEN_WIDTH//2)+150), ((SCREEN_WIDTH/2)-100)) #Black Cards of Game
        
        if (wFinal > bFinal):
            draw_text("White Wins!", font, WHITE, screen, ((SCREEN_WIDTH//2)), ((SCREEN_WIDTH/2)-230)) #White wins
        elif (wFinal < bFinal):
            draw_text("Black Wins!", font, BLACK, screen, ((SCREEN_WIDTH//2)), ((SCREEN_WIDTH/2)-230)) #Black Wins
        else:
            draw_text("It's a Tie!", font, RED, screen, ((SCREEN_WIDTH//2)), ((SCREEN_WIDTH/2)-230)) #Tie
        if ((mouseCoord[0] > ((SCREEN_WIDTH/2)-150)) and (mouseCoord[0] < (((SCREEN_WIDTH/2)-150)+300)) and (mouseCoord[1] > (((SCREEN_WIDTH/2)+50))) and (mouseCoord[1] < (((SCREEN_WIDTH/2)+50)+60))): #Within PvP Coords
            gameState = "MainMenu" #Go back to start new game
        elif ((mouseCoord[0] > (SCREEN_WIDTH-150)) and (mouseCoord[0] < SCREEN_WIDTH-150+110) and (mouseCoord[1] > 10) and (mouseCoord[1] < 10+60)): #Within End Button Coords
            gameState = "SeeBoard" #Allow player to see how they lost
        
    elif (gameState == "SeeBoard"): #See how the game ended
        drawGameBoard(matrix) 
        pygame.draw.rect(screen, GREEN, (0, (SCREEN_WIDTH-buffer/2), SCREEN_WIDTH, buffer/2))
        draw_button("End Menu", WHITE, GREEN2, SCREEN_WIDTH-150, 10, 110, 60) #Draw End Game Button
        wFinal, bFinal = getScore(matrix)
        draw_text("--White--", small_font, WHITE, screen, ((SCREEN_WIDTH)-150), ((SCREEN_WIDTH)-45)) #White Cards of Game
        draw_text((str(wFinal)), small_font, WHITE, screen, ((SCREEN_WIDTH)-150), ((SCREEN_WIDTH)-25)) #White Score of Game
        draw_text("--Black--", small_font, BLACK, screen, (150), ((SCREEN_WIDTH)-45)) #Black Cards of Game
        draw_text((str(bFinal)), small_font, BLACK, screen, (150), ((SCREEN_WIDTH)-25)) #Black Cards of Game
        #Get button actions
        if ((mouseCoord[0] > (SCREEN_WIDTH-150)) and (mouseCoord[0] < SCREEN_WIDTH-150+110) and (mouseCoord[1] > 10) and (mouseCoord[1] < 10+60)): #Within End Button Coords
            gameState = "EndMenu"
        
    mouseCoord = [0,0] #reset selection coords

    # Update the display
    pygame.display.flip()

pygame.quit()

#whiteScore, blackScore = getScore(matrix)
#print("White Score: " + str(whiteScore) + " Black Score: " + str(blackScore))
