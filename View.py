import math

from . import Player
from . import Core

class View:

    # self.view.deckState()
    # self.view.trackState()
    # self.view.playerState()
    # self.view.atkState()

    def __init__(self, core:Core):
        self.core = core

    def _playedCardState(self, card):
        cnt = self.core.playedCards[card-1]
        return '*'*(5-cnt) + '_'*cnt

    def playedCardState(self):
        "output deckState"
        print ("\n============================")
        print ("Played: 1:{0}, 2:{1}, 3:{2}, 4:{3}, 5:{4},   LEFT:{5}".format(
            self._playedCardState(1),
            self._playedCardState(2),
            self._playedCardState(3),
            self._playedCardState(4),
            self._playedCardState(5),
            len(self.core.deck)
        ))

    def trackState(self):
        "output track state"
        pos1 = self.core.players[0].pos
        pos2 = self.core.players[1].pos
        s = [ "A " if x == pos1 else "B " if x == pos2 else "_ " for x in range(1, 19)]
        print("{0}         Dist={1}".format(''.join(s), int(math.fabs(pos1-pos2))) )

    def playerState(self):
        for i in range(2):
            p = self.core.players[i]
            s = "{0} hands:{1}".format(self._getPlayerStateSymbol(p), p.hands)
            print(s)

    def _getPlayerStateSymbol(self, p:Player):
        if self.core.curPlayer() == p:
            if len(self.core.atkVector) == 0:
                return "A"
            else:
                return " "
        else:
            if len(self.core.atkVector) == 0:
                return " "
            else:
                return "D"
