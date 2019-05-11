import numpy as np

from . import Core

class Player:
    """
    The player data
    act as a data holder and simple calc
    """

    def __init__(self, core:Core, name:str, mind:"mind"):
        self.name = name
        self.mind = mind
        self.pos = -1
        self.startPos = -1
        self.oppo = None
        self.face = 0

        self.hands = []
        self.core = core

    def hasCard(self, card):
        return next( (x for x in self.hands if x == card), False) != False

    def countCard(self, card):
        return len( [x for x in self.hands if x == card] )

    def setNewPos(self, pos):
        if self.startPos == 1:
            min = 1
            max = self.oppo.pos-1
        else:
            min = self.oppo.pos+1
            max = 18

        self.pos = np.clip(pos, min, max)

    def drawCard(self, cnt):
        assert len(self.hands) + cnt <= 5, "Player.DrawCard: hands({0}), draw({1})".format(len(self.hands), cnt)

        cnt = min(len(self.core.deck), cnt)
        self.hands.extend(self.core.deck[:cnt])
        del self.core.deck[:cnt] #remove

    def drawFull(self):
        self.drawCard(5-len(self.hands))

