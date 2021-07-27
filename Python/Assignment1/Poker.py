#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: sis24
"""
#Imported to make shuffling available
import random
'''
This function initialises variables to help maintain the amount of times the 
hand vaue prints as well as how many times the player has folded. This function
is initialised only once per game
'''
def globalV():
    global j # global variable to keep track of folds
    j=0 # starts at zero because the user has not folded yet
    global k # global variable to help hinder multiple prints of winner
    k=0 
    global name # helps keep track of the users name, to print and write
'''
Global variables that keep track of the hands, and flop indexes (i) and the 
deck index (deckI) to make sure that each player and the flop get the correct 
amount of cards and that the cards are not the same. This function is called
for each new deck that the user needs.
'''
def globalVdeck():
    global i # Variable to help keep track of the card in the deck is next
    i=0 
    global deckI # Variable to keep track of how many cards have been delt
    deckI = 0 
'''
Starting function that prompts the user for a name (default name is sis24) and 
asks the user to start (interpteting any form of start and asking to re-enter 
if not start) as well as offering the user to quit
TASK 1 a
'''
def start(): 
    begin = input("Please type start to play or quit to exit\n").lower() #Waits for user input to either start or exit the game 
    if begin == "start":  # if the input is start, start the game
        play() # calls the play function
    elif begin == "quit": # if the input is quit then quits the game
        exit() # closses the program
    else: # If the input is neither start nor quit then recall the function till an apropriate input is put in
        print("Invalid input, please type start to start or quit to quit") # Print out to inform user what to do
        start() # calls the start function
'''
Initialisation functiontion to start a new game, if user folds.
TASK 1 a
'''
def initialise():
    globalVdeck() # Calls to set the global deck variables to zero to deal out new hands
    start() # goes to the start function to ask for user input
'''
This function creates a deck and goes through the game, creating the hands, 
asking to fold and then evaluating the hands.
TASK 1 b
'''    
def play():
    global k, j  # global variables to keep track of folds and printing instances
    deck = {"Cards":['Ac', '2c', '3c', '4c', '5c', '6c', '7c', '8c', '9c', 
                     '10c', 'Jc', 'Qc', 'Kc', 'Ah', '2h', '3h', '4h', '5h',
                     '6h', '7h', '8h', '9h', '10h', 'Jh', 'Qh', 'Kh', 'Ad',
                     '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d', '10d',
                     'Jd', 'Qd', 'Kd', 'As', '2s', '3s', '4s', '5s', '6s',
                     '7s', '8s', '9s', '10s', 'Js', 'Qs', 'Ks']} # initialises deck as a dictionary of cards
    nDeck = list(deck['Cards']) # creates a new deck of type list
    random.shuffle(nDeck) # shuffles the new list deck
    hand = playHand(nDeck) # creates the hand by calling the function to deal out the user hand and passing in the new deck
    flop = flops(nDeck) # creates the flop 
    oHand = aiHand(nDeck) # creates the ai hand
    print(writeHands(hand, oHand, flop)) # writes the hands to the file and prints out a return message
    if j<5: # chrecks if the user has any folds left and if so, goes to fold function
        fold() 
    if k==0: # makes sure that this function is only called once
        handValue(hand, oHand, flop) 
        k=k+1  # once this function has been called, increments k to make repeat impossible
'''
The fold function asks the user if they want to fold and keeps track of how 
many times the user has folded with "j". The funtion also prints the amount of 
folds remaining as well as interpreting any form of "yes" and "no" and only 
accepts those answers.
TASK 4
'''        
def fold():
    global j # Variable to keep track of folds
    option = input("Would you like to fold?\n").lower() # asks user if they want to fold
    if option == "yes" and j<5: # if yes then print remaining folds and initialise a new game
        j=j+1 # incrments fold count
        print("You have "+str(5-j)+" folds remaining") # prints ramining folds
        if j==5: # check if the fold amount is five 
            print("\nYou  have exceeded  the upper limit") # if the fold count is greater print message to inform user
            print("This hand will be played") # inform user that the next hand will be played
        initialise() # calls the initialisasion function for a game
    elif option == "no": # if no then play the hand
        print("You had "+str(5-j)+" folds remining") # informs user how many folds they had remaining
    elif option != "yes" or option != "no": # if the input is not yes or no then ask for a walid input
        print("Please input either 'yes' or 'no'") # prints to user to type either yes or no
        fold() # calls fold again
'''
This function writes the hands of the player, the AI and the
    global userWin, aiWin flop to a file 
called "pokerhandhistory.txt". The function knows about the name so that it can
 write the new name (or the standard name) into the file.
TASK 2 d
'''
def writeHands(hand, oHand, flop):
    global name # global variable to print the input name of the user
    f = open("pokerhandhistory.txt","a") # opens and appends the file (creates one if there is none)
    f.write(str(name)+" hand:"+str(hand)+". AI hand:"+str(oHand)+". Flop:"+
            str(flop)+"\n") # writes the user name, hand, ai hand and flop to the file
    f.close() # saves and closes the file
    confirm = "\nHands were saved to file" # a conformation that the writting has happened
    return confirm # returns the message to inform user
'''
This function deal out the players hand. it does not follow the normal rule in 
Texas Hold'em regarding discarding every other card from the deck, but rather 
takes one after the other.
TASK 2 a
'''
def playHand(nDeck):
    print("\nYour hand") # information on which hand this is
    global deckI, i # global variables to keep track of the indexes and amount of cards taken from the deck
    hand=[] # initialises a list for the user hand
    while deckI<2: # loops two times
        hand.append(nDeck[i]) # adds the card at place i into the list
        i=i+1 # increments i
        deckI=deckI+1 # incrments deckI to move over and not take same card
    print(hand) # prints the hand for the user
    return hand # returns the hand for the program
'''
This function deal out the flop. it does not follow the normal rule in Texas 
Hold'em regarding discarding every other card from the deck, but rather takes 
one after the other. Also all hands are usually dealt before the flop, that is
not the case here.
TASK 2 b
'''
def flops(nDeck):
    print("\nFlop") # 
    global deckI, i # global variables to keep track of the indexes and amount of cards taken from the deck
    flop=[] # initialises a list for the flop
    while deckI<5: # loops 3 times as deckI is now 2 after dealing out the hand to the user
        flop.append(nDeck[i]) # adds the card at place i into the list
        i=i+1 # increments i
        deckI=deckI+1 # incrments deckI to move over and not take same card
    print(flop) # print flop for user to see
    return flop # return flop for the program 
'''
This function deal out the AI's hand. it does not follow the normal rule in 
Texas Hold'em regarding discarding every other card from the deck, but rather
takes one after the other.
TASK 2 c
'''
def aiHand(nDeck):
    global deckI, i # global variables to keep track of the indexes and amount of cards taken from the deck
    oHand=[] # initialises a list for the ai hand
    while deckI<7: # loops 2 times as deckI is now 5 after dealing out the hand to the user and the flop
        oHand.append(nDeck[i]) # adds the card at place i into the list
        i=i+1 # increments i
        deckI=deckI+1 # incrments deckI to move over and not take same card
    return oHand # returns the hand for the program
'''
This function takes in the scores assigned in calcValue() and compares them 
together to ditermine who the winner is and then prints that out.
TASK 3 b+c
'''        
def compareScores(userScore, aiScore): #  compares the score of the user and ai
    if userScore>aiScore: # if the user has a higher score 
        print(name +" is the winner") # print the user as the winner
    elif aiScore>userScore: # if the ai has a higher score
        print("AI  is the winner") # print the ai as winner
    elif userScore==aiScore: # if both are equal
        print(name +" and the AI are equal this time") # print message to say no one won
'''
Here the function takes in the lists containing just the suits and just the 
ranks and ditermines the score that the player and ai get with the flop.
TASK 3 a
'''    
def calcValue(valueRank, valueSuits):
    if valueRank.count(valueRank[0])==4: # counts the rank of cards to see if it is 4 of a kind
        score=6 # if it is assign score to 6
        return score # return the score
    elif valueRank.count(valueRank[1])==4: # makes sure that if the last 4 are the same that it gets evaluated as well
        score=6
        return score
    elif valueRank.count(valueRank[0])==3 and valueRank.count(valueRank[3])==2: # counts the ranks to check if it is a full house
        score=5 # assigns a score of 5
        return score # returns score
    elif valueRank.count(valueRank[0])==2 and valueRank.count(valueRank[2])==3: # makes sure that if there are 2 cards first to count that as well
        score=5
        return score
    elif valueSuits.count(valueSuits[0])==5: # counts the suits to check for a flush
        score=4 # if there is a flush then assign the score to 4
        return score # return score
    elif valueRank.count(valueRank[0])==3: # counts the rank values to see if there is a three of a kind 
        score=3 # if three of a kind assign score to 3
        return score # return score
    elif valueRank.count(valueRank[1])==3: # check if the middle three are the same
        score=3
        return score
    elif valueRank.count(valueRank[2])==3: # check if the last three are the same
        score=3
        return score
    elif (valueRank.count(valueRank[0])==2 
          and (valueRank.count(valueRank[2])==2
                         or valueRank.count(valueRank[3])==2)): # check the ranks to see if there are two pairs, checks first two with third+fourth and fourth+fifth
        score=2 # if two pair then assign score to 2
        return score # return score
    elif valueRank.count(valueRank[1])==2 and valueRank.count(valueRank[3])==2: # check the second+third with fourth+fifth
        score=2
        return score
    elif (valueRank.count(valueRank[0])==2 or valueRank.count(valueRank[1])==2 
    or valueRank.count(valueRank[2])==2 or valueRank.count(valueRank[3])==2): # check the ranks to see if there is one pair at any point in the hand + flop
        score=1 # if there is ine pair then assign score of 1
        return score # return score
    else: # if none of the above
        score=0 # assign the score to zero
        return score # return score
'''
This function takes in both hands and the flop and splits each hand (with the 
flop) into lists of ranks and suits, so that a value for the hand can be 
calculated.
TASK 3 a
'''  
def handValue(hand, oHand, flop):
    # initialises lists for user hand with flop and for the user suits and ranks for evaluation
    userTable = [] # 
    userValueSuits = [] # 
    userValueRank = [] # 
    # initialises lists for ai hand with flop and for the user suits and ranks for evaluation
    aiTable = [] # 
    aiValueSuits = [] # 
    aiValueRank = [] # 
    
    # creates the table for the user out of user hand and the flop then sorts it
    userTable = (hand+flop) # 
    userTable.sort() # 

    #Split the users hand (with the flop) into just suits and ranks
    for i in userTable: # while there are cards in the table hand
        if i[1] == '0': # if the table has a 10 in make the suit the 2 index of the list
            userValueSuits.append(i[2])
        else: # else make the 1 index the suit
            userValueSuits.append(i[1])
        userValueRank.append(i[0]) # make the 0 index the rank value
    #Sets the user score by calling the calcValue function and passing in the
    #two lists.    
    userScore = calcValue(userValueRank, userValueSuits)

    aiTable = (oHand+flop) # 
    aiTable.sort() # 

    #Split the users hand (with the flop) into just suits and ranks
    for i in aiTable: # while there are cards in the table hand
        if i[1]=='0': # if the table has a 10 in make the suit the 2 index of the list
            aiValueSuits.append(i[2]) # 
        else: # else make the 1 index the suit
            aiValueSuits.append(i[1]) # 
        aiValueRank.append(i[0]) # make the 0 index the rank value
    #Sets the ai score by calling the calcValue function and passing in the
    #two lists. 
    aiScore = calcValue(aiValueRank, aiValueSuits) # 
    
    return compareScores(userScore, aiScore) # 
'''
Starting function for the program. Initialises the values that need only be 
initialised once and then starts the game.
TASK 1 a
'''
if __name__ == "__main__":
    globalV() # initialises the fold and print variables
    global name # global variable for name
    name = input("Please input name\n(enter for sis24)\n") # assigns the name to the user input
    if name == "": # if the user does not input name 
        name = "sis24" # assign name to sis24
    initialise() # initialises the game
