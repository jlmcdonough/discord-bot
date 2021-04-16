import discord
from discord.utils import get
from discord.ext import commands
import random
import sqlite3
from datetime import datetime
from datetime import date
import asyncio

class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.broyosServerID = 573599118035910677
        self.broyosChannelID = 711330308728946718   #channelID for gambling text channel
        self.vaultChannelID = 739560506595082300
        self.last_player = None
        self.blackjackPlayerCards = []
        self.blackjackDealerCards = []
        self.blackjackCardDeck = [2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,9,9,9,9,10,10,10,10,"J","J","J","J","Q","Q","Q","Q","K","K","K","K","A","A","A","A"]
        self.blackjackPlayerSum = int(0)
        self.blackjackDealerSum = int(0)
        self.wager = int(0)
        self.rollHostID = None
        self.rollChallengerID = None
        self.rollWager = int(0)
        self.rouletteOwner = None
        self.rouletteBets = []
        self.rouletteWinners = []

    # DATABASE STUFF
    def connectToDB(self):  # returns database and cursor pointer to games database
        db = sqlite3.connect("C:/Users/Joseph/PycharmProjects/discordBot/casino.sqlite")
        cursor = db.cursor()
        return db, cursor

    def closeDB(self, db, cursor):  # commits changes and closes database and cursor
        db.commit()
        cursor.close()
        db.close()

    def checkWager(self, playerID):
        db, cursor = self.connectToDB()
        cursor.execute("""SELECT moneyAmount
                          FROM players
                          WHERE playerID = ?""", (int(playerID),))
        result = cursor.fetchall()
        result = result[0][0]
        return result

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        print("Casino Cog is being read")
        db, cursor = self.connectToDB()
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS blackjack(
                    date DATETIME,
                    playerID INT,
                    playerSum INT,
                    dealerSum INT,
                    amountWagered INT,
                    wagerResult INT)
                """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS diceGame(
                    date DATETIME,
                    hostID INT,
                    challengerID INT,
                    hostRoll INT,
                    challengerRoll INT,
                    wager INT)
                """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS roulette(
                    date DATETIME,
                    betCount INT,
                    winnerCount INT,
                    winningNumber INT,
                    winningColor INT,
                    totalWagered INT,
                    totalPaidOut INT)
                """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS roulettePlay(
                    date DATETIME,
                    playerID INT,
                    color TEXT,
                    wager INT)
                """)

        now = datetime.now()

    #Commands
    @commands.command(hidden = True)
    async def test(self, ctx):
        await ctx.send("hi")

    #DONATE
    @commands.command(hidden = True)
    async def poor(self, ctx):
        if (ctx.message.channel.id == self.broyosChannelID or ctx.message.channel.id == self.vaultChannelID):
            db,cursor = self.connectToDB()
            cursor.execute("""UPDATE players
                              SET moneyAmount = 1000000
                              WHERE playerID = ?""", (ctx.author.id,))
            self.closeDB(db, cursor)
            print("read")
        else:
            await ctx.send("Keep all casino related commands in the gambling text channel")


    #ALLOWANCE
    @commands.command(name = "allowance", help="Gives daily allowance", description="")
    async def allowance(self,ctx):
        if (ctx.message.channel.id == self.broyosChannelID or ctx.message.channel.id == self.vaultChannelID):
            db, cursor = self.connectToDB()
            cursor.execute("""SELECT lastAllowance, moneyAmount
                                FROM players
                                WHERE playerID = ?""", (ctx.author.id,))
            result = cursor.fetchall()
            dayLastAllowance = (result[0][0])
            currMoney = result[0][1]
            today = (date.today())
            today = today.strftime("%Y-%m-%d")

            if(today == dayLastAllowance):
                print("Today")
                await ctx.send("You have already redeemed your daily allowance for today. Come back tomorrow")

            elif(today != dayLastAllowance):
                print("Not today")
                newMoney = currMoney + 5000
                cursor.execute("""UPDATE players
                                  SET moneyAmount = ?, lastAllowance = ?
                                  WHERE playerID = ?""", (newMoney, today, ctx.author.id,))
                self.closeDB(db, cursor)
                await ctx.send("Your daily allowance has been added to your balance")
        else:
            await ctx.send("Keep all casino related commands in the gambling text channel")

    #LEADERBOARD
    @commands.command(name = "leaderboard", help = "Brings up the casino leaderboard, sorted by money", description = "")
    async def leaderboard(self, ctx):
        if (ctx.message.channel.id == self.broyosChannelID or ctx.message.channel.id == self.vaultChannelID):
            db, cursor = self.connectToDB()
            query = cursor.execute("""SELECT playerName, moneyAmount, winCount, lossCount
                                        FROM players
                                        ORDER BY moneyAmount DESC, playerName ASC""")
            result = cursor.fetchall()
            response = ("```" +
                        "\n{:<20s}{:^10s}{:>10s}{:>10s}".format("PLAYER", "MONEY", "WINS", "LOSSES"))
            for i in range(len(result)):
                name = str(result[i][0])
                money = str(result[i][1])
                winCount = str(result[i][2])
                lossCount = str(result[i][3])
                response += ("\n{:<20s}{:^10s}{:>10s}{:>10s}".format(name, money, winCount, lossCount))
            response += "```"
            await ctx.channel.send(response)
        else:
            await ctx.send("Keep all casino related commands in the gambling text channel")

    @commands.command(name = "balance", help = "Gets current casino money balance", description = "")
    async def balance(self, ctx):
        if (ctx.message.channel.id == self.broyosChannelID or ctx.message.channel.id == self.vaultChannelID):
            db, cursor = self.connectToDB()
            cursor.execute("""SELECT moneyAmount
                              FROM players
                              WHERE playerID = ?""", (ctx.author.id,))
            result = cursor.fetchall()
            result = result[0][0]
            await ctx.send("Your balance is " + str(result))
        else:
            await ctx.send("Keep all casino related commands in the gambling text channel")

    #DICE GAME
    @commands.command(name = "roll", help = "Challenge another member to dice 1v1", description = "")
    async def roll(self, ctx, challenger, wager):
        if (ctx.message.channel.id == self.broyosChannelID or ctx.message.channel.id == self.vaultChannelID):
            print(ctx.author.id)
            db = sqlite3.connect("C:/Users/Joseph/PycharmProjects/discordBot/casino.sqlite")
            cursor = db.cursor()
            challenger = challenger.split("!")[1]
            challenger = challenger.split(">")[0]
            self.rollHostID = int(ctx.author.id)
            self.rollChallengerID = int(challenger)
            self.rollWager = int(wager)
            db, cursor = self.connectToDB()
            cursor.execute("""SELECT playerName
                                FROM players
                                WHERE playerID = ?""", (challenger,))
            playerName = cursor.fetchall()
            print(playerName)
            await ctx.send("Waiting for " + playerName[0][0] + " to accept!")
        else:
            await ctx.send("Keep all casino related commands in the gambling text channel")

    @commands.command(name = "acceptRoll", help = "Accept roll 1v1 challenge. @host", description = "")
    async def acceptRoll(self, ctx, host):
        if (ctx.message.channel.id == self.broyosChannelID or ctx.message.channel.id == self.vaultChannelID):
            db, cursor = self.connectToDB()
            cursor.execute("""SELECT playerName
                              FROM players
                              WHERE playerID = ?""", (self.rollChallengerID,))
            challengerName = cursor.fetchall()
            challengerName = challengerName[0][0]
            cursor.execute("""SELECT playerName
                              FROM players
                              WHERE playerID = ?""", (self.rollHostID,))
            hostName = cursor.fetchall()
            hostName = hostName[0][0]
            hostMoney = self.checkWager(self.rollHostID)
            challengerMoney = self.checkWager(self.rollChallengerID)
            if(int(hostMoney) >= int(self.rollWager)):
                if(int(challengerMoney) >= int(self.rollWager)):
                    winnings = int(self.rollWager) * 2
                    roll1 = random.randint(1, 6)
                    roll2 = random.randint(1, 6)
                    roll3 = random.randint(1, 6)
                    total1 = roll1 + roll2 + roll3
                    roll4 = random.randint(1, 6)
                    roll5 = random.randint(1, 6)
                    roll6 = random.randint(1, 6)
                    total2 = roll4 + roll5 + roll6
                    response = hostName + "'s Roll: " + str(roll1) + ", " + str(roll2) + ", " + str(roll3) + " TOTAL: " + str(total1)
                    response += "\n" + challengerName + "'s Roll: " + str(roll4) + ", " + str(roll5) + ", " + str(roll6) + " TOTAL: " + str(total2)
                    if(total1>total2):
                        print("HOST WINNER")
                        winner = hostName
                        response += "\n" + hostName + " has won the game and " + str(winnings)
                        cursor.execute("""SELECT winCount, moneyAmount
                                            FROM players
                                            WHERE playerID = ?""", (self.rollHostID,))
                        result = cursor.fetchall()
                        winCount = result[0][0]
                        hostMoney = result[0][1]
                        hostMoney += int(self.rollWager)
                        winCount += 1
                        cursor.execute("""UPDATE players
                                             SET winCount = ?, moneyAmount = ?
                                             WHERE playerID = ?""", (winCount, hostMoney, self.rollHostID,))

                        cursor.execute("""SELECT lossCount, moneyAmount
                                            FROM players
                                            WHERE playerID = ?""", (self.rollChallengerID,))
                        result = cursor.fetchall()
                        lossCount = result[0][0]
                        lossCount += 1
                        challengerMoney = result[0][1]
                        challengerMoney -= int(self.rollWager)
                        cursor.execute("""UPDATE players
                                             SET lossCount = ?, moneyAmount = ?
                                             WHERE playerID = ?""", (lossCount, challengerMoney, self.rollChallengerID,))
                        self.closeDB(db, cursor)
                    elif(total2 > total1):
                        print("CHALLENGER WINNER")
                        winner = challengerName
                        response += "\n" + challengerName + " has won the game and " + str(winnings)
                        cursor.execute("""SELECT winCount, moneyAmount
                                                    FROM players
                                                    WHERE playerID = ?""", (self.rollChallengerID,))
                        result = cursor.fetchall()
                        winCount = result[0][0]
                        winCount += 1
                        challengerMoney = result[0][1]
                        challengerMoney += int(self.rollWager)
                        cursor.execute("""UPDATE players
                                          SET winCount = ?, moneyAmount = ?
                                          WHERE playerID = ?""", (winCount, challengerMoney, self.rollChallengerID,))

                        cursor.execute("""SELECT lossCount, moneyAmount
                                          FROM players
                                          WHERE playerID = ?""", (self.rollHostID,))
                        result = cursor.fetchall()
                        lossCount = result[0][0]
                        lossCount += 1
                        hostMoney = result[0][1]
                        hostMoney -= int(self.rollWager)
                        cursor.execute("""UPDATE players
                                          SET lossCount = ?, moneyAmount = ?
                                          WHERE playerID = ?""", (lossCount, hostMoney, self.rollHostID,))
                        self.closeDB(db,cursor)
                    elif(total1 == total2):
                        print("NO WINNER")
                        response += "\nGame has ended in a draw and all money returned!"

                    db, cursor = self.connectToDB()
                    now = datetime.now()
                    sql = "INSERT INTO diceGame VALUES (?,?,?,?,?,?)"
                    val = now, self.rollHostID, self.rollChallengerID, total1, total2, self.rollWager
                    print(val)
                    cursor.execute(sql, val)
                    self.closeDB(db, cursor)
                else:
                    response = challengerName + " does not have that kind of money"
            else:
                response = "You do not even have that kind of dough " + hostName
            await ctx.send(response)
        else:
            await ctx.send("Keep all casino related commands in the gambling text channel")

    @commands.command(name = "declineRoll", help = "Decline roll 1v1 challenge. @host", description = "")
    async def declineRoll(self, ctx, host):
        if (ctx.message.channel.id == self.broyosChannelID or ctx.message.channel.id == self.vaultChannelID):
            if(ctx.author.id == self.rollChallengerID):
                host = host.split("!")[1]
                host = host.split(">")[0]
                print("HOST", host, "HOSTID", self.rollHostID)
                if(host == self.rollHostID):
                    self.rollHostID = None
                    self.rollChallengerID = None
                    self.rollWager = int(0)
                    await ctx.send("Roll has been declined!")
                    print("HOST", host, "HOSTID", self.rollHostID)
                else:
                    await ctx.send("That is not the player that challenged you")
                    print("HOST", host, "HOSTID", self.rollHostID)
            else:
                await ctx.send("You were never challenged!")
        else:
            await ctx.send("Keep all casino related commands in the gambling text channel")

    #BLACKJACK
    def blackjackSum(self, cardHand):
        total = 0
        acePresent = False
        aceCount = 0
        for card in cardHand:
            if(card == "J" or card == "Q" or card == "K"):
                total += 10
                #print("Total: ", total)
            elif(card == "A"):
                acePresent = True
                aceCount +=1
                #print("Ace Count: ", aceCount)
            else:
                total += int(card)
                #print("Total: ", total)
        if(total < 11 and acePresent and aceCount == 1):  #One Ace and an 11 value ace wont put over 21
            total += 11
            #print("Ace Scenario 1a: ", total)
        elif(total >= 11 and acePresent and aceCount == 1):  #One Ace and an 11 value ace would put over 21
            total += 1
            #print("Ace Scenario 1b: ", total)
        elif(total < 10 and acePresent and aceCount == 2):   #draws 2 Aces, one must be 1 and the other will be 11
            total += 12
            #print("Ace Scenario 2a: ", total)
        elif(total >=10 and acePresent and aceCount == 2):  #one ace being 11 would put over, so both set to 1
            total +=2
            #print("Ace Scenario 2b: ", total)
        elif(total < 9 and acePresent and aceCount == 3):  #draws 3 Aces, then two must be 1 and the other can 11
            total += 13
            #print("Ace Scenario 3a: ", total)
        elif(total >= 9 and acePresent and aceCount == 3):  #one ace being 11 would put over, so all three set to 1
            total += 3
            #print("Ace Scenario 3b: ", total)
        elif(total < 8 and acePresent and aceCount == 4):  #draw 4 aces, one can be 11 and the others 1
            total += 14
            #print("Ace Scenario 4a: ", total)
        elif(total >= 8 and acePresent and aceCount == 4):  #draw 4 aces and one being 11 would put over, so all 1s
            total += 4
            #print("Ace Scenario 4b: ", total)
        return total

    def drawCard(self):
        cardIndexNum = random.randint(0, (len(self.blackjackCardDeck)-1))
        drawnCard = self.blackjackCardDeck[cardIndexNum]
        del self.blackjackCardDeck[cardIndexNum]
        return drawnCard

    def blackjackEndGame(self, winner):
        db, cursor = self.connectToDB()

        stats = """SELECT *
                    FROM players
                    WHERE playerID = ?"""
        data = int(self.last_player)
        cursor.execute("""SELECT *
                    FROM players
                    WHERE playerID = ?""", (data,))
        result = cursor.fetchall()
        print(result)

        winCount = result[0][3]
        lossCount = result[0][4]

        if(winner == "player"):
            print(self.wager)
            winnings = int(self.wager)
            winCount += 1
            cursor.execute("""UPDATE players
                                 SET winCount = ?
                                 WHERE playerID = ?""", (winCount, self.last_player,))
        elif(winner == "dealer"):
            winnings = 0 - int(self.wager)
            lossCount += 1
            cursor.execute("""UPDATE players
                                 SET lossCount = ?
                                 WHERE playerID = ?""", (lossCount, self.last_player,))
        elif(winner == "none"):
            winnings = 0
        print(winnings)
        newAmount = result[0][2] + winnings
        print(newAmount)

        now = datetime.now()
        sql = "INSERT INTO blackjack VALUES (?,?,?,?,?,?)"
        val = now, self.last_player, self.blackjackPlayerSum, self.blackjackDealerSum, self.wager, winnings
        cursor.execute(sql, val)


        print(newAmount)
        newMoney = """UPDATE players
                      SET moneyAmount = ?
                      WHERE playerID = ?"""
        cursor.execute("""UPDATE players
                      SET moneyAmount = ?
                      WHERE playerID = ?""", (newAmount,self.last_player,))


        self.closeDB(db, cursor)

        self.blackjackPlayerCards = []
        self.blackjackDealerCards = []
        self.blackjackPlayerSum = int(0)
        self.blackjackDealerSum = int(0)
        self.blackjackCardDeck = [2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,9,9,9,9,10,10,10,10,"J","J","J","J","Q","Q","Q","Q","K","K","K","K","A","A","A","A"]
        self.last_player = None
        self.wager = 0

    @commands.command(name = "blackjack", help = "Start a game of blackjack", description = "")
    async def blackjack(self, ctx, wager):
        if (ctx.message.channel.id == self.broyosChannelID or ctx.message.channel.id == self.vaultChannelID):
            if(self.last_player == None):
                self.last_player = ctx.message.author.id
                self.wager = int(wager)
                db, cursor = self.connectToDB()
                cursor.execute("""SELECT moneyAmount
                                            FROM players
                                            WHERE playerID = ?""", (int(self.last_player),))
                result = cursor.fetchall()
                result = result[0][0]
                if(result >= self.wager):
                    card1 = self.drawCard()
                    self.blackjackPlayerCards.append(card1)
                    card2 = self.drawCard()
                    self.blackjackPlayerCards.append(card2)
                    card3 = self.drawCard()
                    self.blackjackDealerCards.append(card3)
                    self.blackjackDealerSum = self.blackjackSum( self.blackjackDealerCards)
                    while self.blackjackDealerSum < 17:
                        nextCard = self.drawCard()
                        self.blackjackDealerCards.append(nextCard)
                        self.blackjackDealerSum = self.blackjackSum( self.blackjackDealerCards)
                        #print("DCards: ",self.blackjackDealerCards, " SUM:", self.blackjackDealerSum)
                    playerID = ctx.message.author.id
                    self.blackjackPlayerSum = self.blackjackSum(self.blackjackPlayerCards)
                    if (self.blackjackPlayerSum == 21):
                        await ctx.send("YOUR CARDS: " + str(self.blackjackPlayerCards) +
                                       "\nYou hit blackjack, congrats!")
                        halfWager = int(self.wager)/2
                        self.wager = int(self.wager) + halfWager  #winnings = winnings + winnings --> natural blackjack pays out 3-to-2, and 1.5+1=2.5
                        self.blackjackEndGame("player")
                    else:
                        await ctx.send("YOUR CARDS: " + str(card1) + " " + str(card2) +
                                       "\nDEALERS CARDS: " + str(card3) + " ? ")
                        #print("PCards: ",self.blackjackPlayerCards, " SUM:", self.blackjackPlayerSum)
                else:
                    await ctx.send("Yeah you don't have that kind of money pleb, nice try :clown:")
                    self.last_player = None
            else:
                await ctx.send("One player at a time :monkey_face:")
        else:
            await ctx.send("Keep all casino related commands in the gambling text channel")

    @commands.command(name = "hit", help = "BLACKJACK: Draw another card", description = "")
    async def hit(self, ctx):
        if (ctx.message.channel.id == self.broyosChannelID or ctx.message.channel.id == self.vaultChannelID):
            if(ctx.message.author.id == self.last_player):
                #print("Player Hit")
                hitCard = self.drawCard()
                self.blackjackPlayerCards.append(hitCard)
                self.blackjackPlayerSum = self.blackjackSum(self.blackjackPlayerCards)
                if (self.blackjackPlayerSum < 21):
                    overMessage = ("YOUR CARDS: " + str(self.blackjackPlayerCards) +
                                   "\nDEALERS CARDS: " + str(self.blackjackDealerCards[0]) + " ?")
                if (self.blackjackPlayerSum == 21):
                    overMessage = ("YOUR CARDS: " + str(self.blackjackPlayerCards) +
                                    "\nYou hit 21, congrats!")
                    self.blackjackEndGame("player")
                elif (self.blackjackPlayerSum > 21):
                    overMessage = ("YOUR CARDS: " + str(self.blackjackPlayerCards) +
                                    "\nYou went over, feelsbadman")
                    self.blackjackEndGame("dealer")
                await ctx.send(overMessage)
            elif(ctx.message.author.id != self.last_player):
                await ctx.send("One player at a time please and thank you!")
            else:
                await ctx.send("No active game!")
        else:
            await ctx.send("Keep all casino related commands in the gambling text channel")

    @commands.command(name = "doubleDown", help = "BLACKJACK: Double wager and only get one hit. Can only be used on first turn", description = "")
    async def doubleDown(self, ctx):
        if (ctx.message.channel.id == self.broyosChannelID or ctx.message.channel.id == self.vaultChannelID):
            if(ctx.message.author.id == self.last_player):
                #print("Player Double Down")
                self.wager = int(self.wager) * 2
                hitCard = self.drawCard()
                self.blackjackPlayerCards.append(hitCard)
                self.blackjackPlayerSum = self.blackjackSum(self.blackjackPlayerCards)
                if (self.blackjackPlayerSum < 21 and self.blackjackDealerSum<=21 and self.blackjackDealerSum<self.blackjackPlayerSum):
                    overMessage = ("YOUR CARDS: " + str(self.blackjackPlayerCards) +
                                   "\nDEALERS CARDS: " + str(self.blackjackDealerCards) +
                                   "\nYou beat the dealer, well played!")
                    self.blackjackEndGame("player")
                elif (self.blackjackPlayerSum < 21 and self.blackjackDealerSum <= 21 and self.blackjackDealerSum > self.blackjackPlayerSum):
                        overMessage = ("YOUR CARDS: " + str(self.blackjackPlayerCards) +
                                       "\nDEALERS CARDS: " + str(self.blackjackDealerCards) +
                                       "\nDealer wins")
                        self.blackjackEndGame("dealer")
                elif (self.blackjackPlayerSum < 21 and self.blackjackDealerSum>21):
                    overMessage = ("YOUR CARDS: " + str(self.blackjackPlayerCards) +
                                   "\nDEALERS CARDS: " + str(self.blackjackDealerCards) +
                                   "\nYou beat the dealer, well played!")
                    self.blackjackEndGame("player")
                elif (self.blackjackPlayerSum == 21):
                    overMessage = ("YOUR CARDS: " + str(self.blackjackPlayerCards) +
                                    "\nYou hit 21, congrats!")
                    self.blackjackEndGame("player")
                elif (self.blackjackPlayerSum > 21):
                    overMessage = ("YOUR CARDS: " + str(self.blackjackPlayerCards) +
                                    "\nYou went over, feelsbadman")
                    self.blackjackEndGame("dealer")
                elif (self.blackjackPlayerSum == self.blackjackDealerSum):
                    overMessage = ("YOUR CARDS: " + str(self.blackjackPlayerCards) +
                                   "\nDEALERS CARDS: " + str(self.blackjackDealerCards) +
                                   "\nDRAW!")
                    self.blackjackEndGame("none")
                await ctx.send(overMessage)
            elif(ctx.message.author.id != self.last_player):
                await ctx.send("One player at a time please and thank you!")
            else:
                await ctx.send("No active game!")
        else:
            await ctx.send("Keep all casino related commands in the gambling text channel")

    @commands.command(name = "stand", help = "BLACKJACK: Stay with current cards", description = "")
    async def stand(self, ctx):
        if (ctx.message.channel.id == self.broyosChannelID or ctx.message.channel.id == self.vaultChannelID):
            if(ctx.message.author.id == self.last_player):
                #print("Player Stand")
                #print("Player Sum: ", self.blackjackPlayerSum)
                #print("Dealer Sum: ", self.blackjackDealerSum)
                if (self.blackjackPlayerSum == 21):
                    overMessage = ("YOUR CARDS: " + str(self.blackjackPlayerCards) +
                                   "\nYou hit 21, congrats!")
                    winner = "player"
                elif (self.blackjackPlayerSum > 21):
                    overMessage = ("YOUR CARDS: " + str(self.blackjackPlayerCards) +
                                   "\nYou went over, feelsbadman")
                    winner = "dealer"
                elif (self.blackjackDealerSum > 21):
                    overMessage = ("YOUR CARDS: " + str(self.blackjackPlayerCards) +
                                   "\nDEALERS CARDS: " + str(self.blackjackDealerCards) +
                                   "\nDealer went over, congrats!")
                    winner = "player"
                elif (self.blackjackDealerSum == 21):
                    overMessage = ("YOUR CARDS: " + str(self.blackjackPlayerCards) +
                                   "\nDEALERS CARDS: " + str(self.blackjackDealerCards) +
                                   "\nDealer hit 21, better luck next time")
                    winner = "dealer"
                elif (self.blackjackDealerSum < self.blackjackPlayerSum):
                    overMessage = ("YOUR CARDS: " + str(self.blackjackPlayerCards) +
                                   "\nDEALERS CARDS: " + str(self.blackjackDealerCards) +
                                   "\nYou beat the dealer, well played!")
                    winner = "player"
                elif (self.blackjackDealerSum > self.blackjackPlayerSum):
                    overMessage = ("YOUR CARDS: " + str(self.blackjackPlayerCards) +
                                   "\nDEALERS CARDS: " + str(self.blackjackDealerCards) +
                                   "\nDealer beat you, unlucko")
                    winner = "dealer"
                elif (self.blackjackDealerSum == self.blackjackPlayerSum):
                    overMessage = ("YOUR CARDS: " + str(self.blackjackPlayerCards) +
                                   "\nDEALERS CARDS: " + str(self.blackjackDealerCards) +
                                   "\nDraw")
                    winner = "none"
                await ctx.send(overMessage)
                self.blackjackEndGame(winner)
            elif (ctx.message.author.id != self.last_player):
                await ctx.send("One player at a time please and thank you!")
            else:
                await ctx.send("No active game!")
        else:
            await ctx.send("Keep all casino related commands in the gambling text channel")

    #ROULETTE
    def rouletteEndGame(self):
        self.rouletteOwner = None
        self.rouletteBets = []
        self.rouletteWinners = []

    def rouletteResults(self, color, number):
        response = ("```" +
                    "\nOUTCOME: " + str(number) + " (" + color + ")" +
                    "\n{:<15s}{:<10s}".format("PLAYER", "WINNINGS"))
        for winners in self.rouletteWinners:
            response += ("\n{:<15s}{:<10s}".format(str(winners[0]), str(winners[1])))
        response += ("```")
        return response

    @commands.command(name = "rouletteOpen", help = "Starts a roulette game", description = "")
    async def rouletteOpen(self, ctx):
        if (ctx.message.channel.id == self.broyosChannelID or ctx.message.channel.id == self.vaultChannelID):
            if(self.rouletteOwner != None):
                await ctx.send("There is already a roulette game open")
            elif(self.rouletteOwner == None):
                self.rouletteOwner = ctx.message.author.id
                self.rouletteBets = []
                await ctx.send("Roulette game now open! ~rouletteBet to enter")
        else:
            await ctx.send("Keep all casino related commands in the gambling text channel")

    @commands.command(name = "rouletteBet", help = "Place a bet on one color (green/red/black) per command. Can place multiple bets per match, but one command per bet", description = "")
    async def rouletteBet(self, ctx, color, wager):
        if (ctx.message.channel.id == self.broyosChannelID or ctx.message.channel.id == self.vaultChannelID):
            if(self.rouletteOwner != None):
                if(color.lower() == "green" or color.lower() == "red" or color.lower() == "black"):
                    if(self.checkWager(ctx.message.author.id) >= int(wager)):
                        self.rouletteBets.append((ctx.message.author.id, color.lower(), int(wager)))
                        db, cursor = self.connectToDB()
                        cursor.execute("""SELECT moneyAmount
                                          FROM players
                                          WHERE playerID = ?""", (ctx.author.id,))
                        currMoney = cursor.fetchall()[0][0]
                        newMoney = currMoney - int(wager)
                        cursor.execute("""UPDATE players
                                          SET moneyAmount = ?
                                          WHERE playerID = ?""", (newMoney, ctx.author.id,))
                        print(currMoney, newMoney)
                        self.closeDB(db, cursor)
                        print(self.rouletteBets)
                        await ctx.send("Successful bet placed on " + color + " for " + str(wager), delete_after=2)
                    else:
                        await ctx.send("You do not have that amount available to bet")
                else:
                    await ctx.send("Please choose a valid color - green, red, or black")
            else:
                await ctx.send("There is no roulette game open at the moment. ~rouletteOpen to begin one")
        else:
            await ctx.send("Keep all casino related commands in the gambling text channel")

    @commands.command(name = "rouletteSpin", help = "Triggers the roulette game to begin", description = "")
    async def rouletteSpin(self, ctx):
        if (ctx.message.channel.id == self.broyosChannelID or ctx.message.channel.id == self.vaultChannelID):
            if(self.rouletteOwner == ctx.message.author.id):
                spinNum = random.randint(0,14)
                fileNum = "rouletteGifs/roulette" + str(spinNum) + ".gif"
                await ctx.channel.send(file=discord.File(fileNum))
                await asyncio.sleep(9)
                db, cursor = self.connectToDB()
                color = ""
                if(spinNum == 0):
                    #print("In Green")
                    for i in self.rouletteBets:
                        if(i[1] == "green"):
                            cursor.execute("""SELECT moneyAmount, playerName
                                              FROM players
                                              WHERE playerID = ?""", (i[0],))
                            results = cursor.fetchall()
                            currMoney = results[0][0]
                            winnings = int(i[2]) * 14
                            newMoney = currMoney + winnings
                            cursor.execute("""UPDATE players
                                              SET moneyAmount = ?
                                              WHERE playerID = ?""", (newMoney, i[0],))
                            print(results)
                            self.rouletteWinners.append(((results[0][1]), winnings))
                    color = "GREEN"
                elif(spinNum >= 1 and spinNum <= 7):  #red
                    #print("In Red")
                    for i in self.rouletteBets:
                        if(i[1] == "red"):
                            cursor.execute("""SELECT moneyAmount, playerName
                                              FROM players
                                              WHERE playerID = ?""", (i[0],))
                            results = cursor.fetchall()
                            currMoney = results[0][0]
                            winnings = int(i[2]) * 2
                            newMoney = currMoney + winnings
                            cursor.execute("""UPDATE players
                                              SET moneyAmount = ?
                                              WHERE playerID = ?""", (newMoney, i[0],))
                            print(results)
                            self.rouletteWinners.append(((results[0][1]), winnings))
                    color = "RED"
                elif(spinNum >= 8 and spinNum <= 14):  #black
                    #print("In Black")
                    for i in self.rouletteBets:
                        if(i[1] == "black"):
                            cursor.execute("""SELECT moneyAmount, playerName
                                              FROM players
                                              WHERE playerID = ?""", (i[0],))
                            results = cursor.fetchall()
                            currMoney = results[0][0]
                            winnings = int(i[2]) * 2
                            newMoney = currMoney + winnings
                            cursor.execute("""UPDATE players
                                              SET moneyAmount = ?
                                              WHERE playerID = ?""", (newMoney, i[0],))
                            print(results)
                            self.rouletteWinners.append(((results[0][1]), winnings))
                    color = "BLACK"

                wagerTotal = 0
                payTotal = 0
                for j in self.rouletteBets:
                    wagerTotal += j[2]
                for k in self.rouletteWinners:
                    payTotal += k[1]
                now = datetime.now()
                sql = "INSERT INTO roulette VALUES (?,?,?,?,?,?,?)"
                val = now, len(self.rouletteBets), len(self.rouletteWinners), spinNum, color, wagerTotal, payTotal
                cursor.execute(sql, val)

                sql2 = "INSERT INTO roulettePlay VALUES (?,?,?,?)"
                for x in self.rouletteBets:
                    val2 = now, x[0], x[1], x[2]
                    cursor.execute(sql2,val2)

                self.closeDB(db, cursor)
                await ctx.send(self.rouletteResults(color, spinNum))
                self.rouletteEndGame()

            else:
                await ctx.send("Only the person who opened the roulette can start it!")
        else:
            await ctx.send("Keep all casino related commands in the gambling text channel")

    def flipCoin(self):
        result = random.randint(1, 2)
        if(result == 1):
            side = "HEADS"
        elif(result == 2):
            side = "TAILS"
        return side

    @commands.command(name="heads", help="Coin flip choosing heads", description="")
    async def heads(self, ctx):
        await ctx.channel.send(file=discord.File("coinFlipping.gif"),delete_after=3)
        side = self.flipCoin()
        response = "RESULT: " + side + "\n"
        if(side == "HEADS"):
            response += "WINNER WINNER!"
        else:
            response += "Wow you are bad at this!"
        await asyncio.sleep(2.2)
        await ctx.send(response)

    @commands.command(name="tails", help="Coin flip choosing tails", description="")
    async def tails(self, ctx):
        await ctx.channel.send(file=discord.File("coinFlipping.gif"), delete_after=3)
        side = self.flipCoin()
        response = "RESULT: " + side + "\n"
        if(side == "TAILS"):
            response += "WINNER WINNER!"
        else:
            response += "Wow you are bad at this!"
        await asyncio.sleep(2.2)
        await ctx.send(response)
        
def setup(bot):
    bot.add_cog(Casino(bot))
