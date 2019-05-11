import numpy as np
import random
import math

from . import Player

class EndException(Exception):
    pass

class Core:
    """
    in charge of manage and alter game states, 
    it doesn't handle UI and input errors
    """

    def __init__(self, minds=[]):
        assert len(minds) == 2, "Core.__init__: expect has 2 minds, get {0}".format(len(minds))
        self.players = [Player.Player(self, "Player1", minds[0]), Player.Player(self, "Player2", minds[1])]
        self.curPlayerIdx = 0
        self.deck = [ 1, 2, 3, 4, 5 ] * 5
        self.atkVector = []
        self.beHitPlayer = None # the player who is hit
        self.isDashAttack = False
        self.winner = None
        self.playedCards = [0, 0, 0, 0, 0]
        self.endReason = ""

    def isDefenderPhase(self):
        return len(self.atkVector) > 0

    def prepareGame(self):
        self.atkVector.clear()
        self.beHitPlayer = None

        random.shuffle(self.deck)
        p = self.players[0]
        p.pos = 1
        p.startPos = 1
        p.face=1
        p.oppo = self.players[1]
        p.drawFull()

        p = self.players[1]
        p.pos = 18
        p.startPos = 18
        p.face=-1
        p.oppo = self.players[0]
        p.drawFull()

    def isAtkPhase(self):
        return len(self.atkVector) == 0

    def switchSide(self):
        if len(self.deck) == 0:
            self.endGame()
        else:
            self.curPlayerIdx = 1 - self.curPlayerIdx

    def endGame(self):
        if self.beHitPlayer != None:
            self.winner = next( x for x in self.players if x != self.beHitPlayer )
            self.endReason = "Hit opponent"
        else:
            dist = int(math.fabs(self.players[0].pos - self.players[1].pos))
            card0 = self.players[0].countCard(dist)
            card1 = self.players[1].countCard(dist)
            if card0 > card1:
                self.winner = self.players[0] 
                self.endReason = "Has more cards matching distance"
            elif card0 < card1:
                self.winner = self.players[1]
                self.endReason = "Has more cards matching distance"
            else:
                forward0 = int(math.fabs(self.players[0].pos - self.players[0].startPos))
                forward1 = int(math.fabs(self.players[1].pos - self.players[1].startPos))
                if forward0 > forward1:
                    self.winner = self.players[0]
                    self.endReason = "Going further than opponent"
                elif forward0 < forward1:
                    self.winner = self.players[1]
                    self.endReason = "Going further than opponent"
                else:
                    self.winner = None
        raise EndException()

    def curPlayer(self):
        return self.players[self.curPlayerIdx]

    def _doMove(self, p:Player, card:int, forward:bool):
        p.setNewPos(p.pos + (p.face if forward else -p.face) * card)

    # def cmd_drawFull(self, p:Player):
    #     p.drawFull()
    #     self.switchSide()

    def cmd_move(self, p:Player, card:int, forward:bool=True):
        p.hands.remove(card)
        self.playedCards[card-1]+=1
        self._doMove(p, card, forward)
        p.drawFull()
        self.switchSide()

    def cmd_push(self, p:Player, card:int):
        p.hands.remove(card)
        self.playedCards[card-1]+=1
        op = p.oppo
        op.setNewPos( op.pos + p.face * card )
        p.drawFull()
        self.switchSide()

    def cmd_attack(self, p:Player, atkCards=[]):
        for c in atkCards:
            p.hands.remove(c)
            self.playedCards[c-1]+=1
        self.atkVector.extend(atkCards)

    def cmd_dashAttack(self, p:Player, moveCard:int, atkCards=[]):
        self.isDashAttack = True
        p.hands.remove(moveCard)
        self.playedCards[moveCard-1]+=1
        self._doMove(p, moveCard, forward=True)
        self.cmd_attack(p, atkCards)

    def cmd_getHit(self, p:Player):
        self.beHitPlayer = p
        self.endGame()

    def cmd_defend(self, p:Player, defCards=[]):
        for c in defCards:
            p.hands.remove(c)
            self.playedCards[c-1]+=1
        p.oppo.drawFull() # oppo draws full hand
        self.atkVector.clear()
        self.switchSide()
        self.isDashAttack = False

    def cmd_retreat(self, p:Player, moveCard:int):
        p.hands.remove(moveCard)
        self.playedCards[moveCard-1]+=1
        self._doMove(p, moveCard, forward=False)
        self.atkVector.clear()

        p.oppo.drawFull()
        self.switchSide()

        print("{0} pass his turn due to retreat".format(p.name))

        p.drawFull()
        self.switchSide()
        self.isDashAttack = False
