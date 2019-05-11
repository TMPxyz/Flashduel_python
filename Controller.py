import numpy as np
import math
import os

from .Core import Core
from .Core import EndException
from .View import View
from .Mind import HumanMind
from .Mind import RNG_AIMind

class Controller:
    """
    take care of input check, and view
    """

    def __init__(self):
        self.core = Core( [HumanMind(), RNG_AIMind()] )
        for p in self.core.players:
            p.mind.Init(self.core, self)
        self.view = View(self.core)

        self.dispatch = {
            "help" :    {'mtd':self.onHelp,         'doc':": get command list"},
            "exit" :    {'mtd':self.onExit,         'doc':": quit command mode"},
            "forward":  {'mtd':self.onForward,      'doc':" <X>: move forward X cell"},
            "back":     {'mtd':self.onBackward,     'doc':" <X>: move backward X cell"},
            "push":     {'mtd':self.onPush,         'doc':" <X>: push opponent X cell"},
            "attack":   {'mtd':self.onAttack,       'doc':" [2]: attack opponent"},
            "dash":     {'mtd':self.onDashAttack,   'doc':" <mX> [2]: first move mX, then attack opponent"},
            "defend":   {'mtd':self.onDefend,       'doc':": defend opponent's attack"},
            "retreat":  {'mtd':self.onRetreat,      'doc':" <X>: retreat with X cell"},
            "behit":    {'mtd':self.onBehit,        'doc':": get hit by opponent"}
        }

        self.core.prepareGame()
        self.clearScreen()

    def clearScreen(self):
        os.system('cls')

    def tick(self):
        "return false to end"
        self.view.playedCardState()
        self.view.trackState()
        self.view.playerState()

        try:
            if len(self.core.atkVector) == 0:
                ret = self.core.curPlayer().mind.Think()
            else:
                ret = self.core.curPlayer().oppo.mind.Think()
            return ret
        except EndException:
            self.view.playedCardState()
            self.view.trackState()
            self.view.playerState()
            if self.core.winner != None:
                print ("Winner is " + self.core.winner.name)
                print ("Winning Reason is: " + self.core.endReason)
            else:
                print ("It's a draw game!")
            return False

    def Handle(self, inp:str):
        splited = inp.split()
        if len(splited) > 1:
            cmd = splited[0]
            args = splited[1:]
        elif len(splited) == 1:
            cmd = splited[0]
            args = []
        else:
            cmd = ""
            args = []
        return self.dispatch.get(cmd, {'mtd':self.onHelp})['mtd'](args)
        
    def onHelp(self, args=[]):
        s = "Available cmds:\n"
        for k, v in self.dispatch.items():
            s += '\t'+ k + v['doc'] + '\n'
        print(s)
        return True

    def onExit(self, args=[]):
        return False

    def onForward(self, args=[]):
        if not self.core.isAtkPhase():
            print("You can only input cmd of def phase!")
            return
        if len(args) != 1:
            self.onHelp()
            return
        curP = self.core.curPlayer()
        card = int(args[0])
        if not curP.hasCard(card):
            print("!!! {0} doesn't have a card of {1}".format(curP.name, card))
            return
        else:
            self.core.cmd_move(curP, card, forward=True)
            self.clearScreen()
            return
    
    def onBackward(self, args=[]):
        if not self.core.isAtkPhase():
            print("You can only input cmd of def phase!")
            return
        if len(args) != 1:
            self.onHelp()
            return
        curP = self.core.curPlayer()
        card = int(args[0])
        if not curP.hasCard(card):
            print("!!! {0} doesn't have a card of {1}".format(curP.name, card))
            return
        else:
            self.core.cmd_move(curP, card, forward=False)
            self.clearScreen()
            return

    def onPush(self, args=[]):
        if not self.core.isAtkPhase():
            print("You can only input cmd of def phase!")
            return
        if len(args) != 1:
            self.onHelp()
            return
        curP = self.core.curPlayer()
        card = int(args[0])
        if not curP.hasCard(card):
            print("!!! {0} doesn't have a card of {1}".format(curP.name, card))
            return
        else:
            self.core.cmd_push(curP, card)
            self.clearScreen()


    def onAttack(self, args=[]):
        if not self.core.isAtkPhase():
            print("You can only input cmd of def phase!")
            return
        needCard = 1
        if len(args) > 1:
            self.onHelp()
            return
        if len(args) == 1 and args[0] == "2":
            needCard = 2
        
        curP = self.core.curPlayer()
        oppo = curP.oppo
        card = int(math.fabs(oppo.pos - curP.pos))
        cntCard = curP.countCard(card)
        if cntCard < needCard:
            print ("!!! {0} needs {1} of {2}, but only has {3}".format(curP.name, needCard, card, cntCard))
        else:
            self.core.cmd_attack(curP, [card for _ in range(needCard)] )
            self.clearScreen()


    def onDashAttack(self, args=[]):
        if not self.core.isAtkPhase():
            print("You can only input cmd of def phase!")
            return
        needAtkCard = 1
        if len(args) < 1 or len(args) > 2:
            self.onHelp()
            return
        if len(args) == 2 and args[1] == "2":
            needAtkCard = 2

        curP = self.core.curPlayer()
        oppo = curP.oppo

        mvCard = int(args[0])
        if not curP.hasCard(mvCard):
            print("!!! {0} doesn't have a card of {1} for moving".format(curP.name, mvCard))
            return
        
        dist = int(math.fabs(oppo.pos-curP.pos))
        if dist <= 1:
            print("!!! Distance must be larger than 1 to dash attack")
            return

        afterDist = max(1, dist - mvCard)
        cntAtkCard = curP.countCard(afterDist)
        if cntAtkCard < needAtkCard:
            print("!!! {0} needs {1} of {2}, but only has {3}".format(curP.name, needAtkCard, afterDist, cntAtkCard))
            return
        else:
            self.core.cmd_dashAttack(curP, mvCard, [afterDist for _ in range(needAtkCard)])
            self.clearScreen()


    def onDefend(self, args=[]):
        if self.core.isAtkPhase():
            print("You can only input cmd of atk phase!")
            return
        curP = self.core.curPlayer()
        oppo = curP.oppo
        dist = int(math.fabs(curP.pos - oppo.pos))
        needDefCard = len(self.core.atkVector)
        cntDefCard = oppo.countCard(dist)
        if cntDefCard < needDefCard:
            print("!!! {0} needs {1} of {2} to defend, but only has {3}".format(oppo.name, needDefCard, dist, cntDefCard))
            return
        else:
            self.core.cmd_defend(oppo, [dist for _ in range(needDefCard)])
            self.clearScreen()


    def onRetreat(self, args=[]):
        if self.core.isAtkPhase():
            print("You can only input cmd of atk phase!")
            return
        if not self.core.isDashAttack:
            print("You can only retreat on dashAttack")
            return
        if len(args) != 1:
            self.onHelp()
            return
        mvCard = int(args[0])
        curP = self.core.curPlayer()
        oppo = curP.oppo

        if oppo.pos == oppo.startPos:
            print("!!! {0} cannot retreat any further".format(oppo.name))
            return

        if not oppo.hasCard(mvCard):
            print("!!! {0} doesn't have a card of {1}".format(oppo.name, mvCard))
            return
        else:
            self.core.cmd_retreat(oppo, mvCard)
            self.clearScreen()


    def onBehit(self, args=[]):
        if self.core.isAtkPhase():
            print("You can only input cmmd of atk phase!")
            return
        
        curP = self.core.curPlayer()
        oppo = curP.oppo
        self.core.cmd_getHit(oppo)
        

