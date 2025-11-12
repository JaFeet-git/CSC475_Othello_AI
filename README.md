# CSC475_Othello_AI (My grade was 108/100)
This assignment will give you experience implementing a classical two player game, Othello, along with an AI opponent driven by the mini-max heuristic search algorithm.

The assignment can be broken down into two relatively separate tasks:

Implement the mechanics of the game Othello. This includes representing the board, initilizing play, accepting player moves (including rejecting illegal moves), computing the discs that should be flipped, displaying the board after each move (ASCII graphics are acceptable), score keeping, and recognition of when the game is complete.

Implement the Mini-Max algorithm, with alphabeta pruning and a reasonable heuristic.

Language of implemention is up to you. Python is a reasonable choice.

This assignment provides the opportunity for 110 out of 100 points (10 bonus points).

[20 pts] Your program is appropriately commented. Be sure to place comments/documentation in every class and function. This includes a README.md file or a comment block at the beginning of your main program with your name, the date, and a full description of the game. If you plan to put this in your Github portfolio, I suggest a README.md file.

[40 pts] Your program implements the rules of the Othello game accurately. In other words, two humans can use your program to successfully play Othello.

[20 pts] Your program properly implements the Mini-Max algorithm. To demonstrate that mini-max is implemented properly, you should have a debug mode that can be switched on, on a move by move basis. The debug mode should show all the sequences of moves considered from the current state along with the heuristic value associated with each move sequence. By default, the debug mode should be OFF.

Additionally, search depth should be easily adjustable, and your program should display the total number of game states examined prior to making a move. Your program should also support computer playing either white or black, that is, if the player wants to have the computer make a move for them, they can choose to do so.

[20 pts] Your program properly implements alpha-beta pruning. You will provide the ability to easily switch on/off alpha-beta pruning on a move by move basis. You should be able to demonstrate that alpha-beta pruning is operating properly by observing the total number of game states when it is enabled versus when it is disabled.

[10 pts] Awarded if your program is able to beat a human that is really trying to win. This will be demonstrated by a recorded program trace of an entire game.
