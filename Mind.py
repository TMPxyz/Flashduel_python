import random
import math

class Mind:
    "base class of AI/HumanPlayer"

    ACT_DEFEND = 'defend'
    ACT_RETREAT = 'retreat'
    ACT_BEHIT = 'behit'
    ACT_MOVE = 'move'
    ACT_ATTACK = 'attack'
    ACT_PUSH = 'push'
    ACT_DASH = 'dash'

    def Init(self, core, ctrl):
        self.core = core
        self.ctrl = ctrl

    def Think(self):
        pass

#############################################################
class HumanMind(Mind):
    "human player"

    def __init__(self):
        super().__init__()
        self.core = None
        self.ctrl = None

    def Think(self):
        if len(self.core.atkVector) == 0:
            cmd = input("{0}, input your cmd:".format(self.core.curPlayer().name))
            ret = self.ctrl.Handle(cmd)
        else:
            cmd = input("{0}, you're under attack, you cmd:".format(self.core.curPlayer().oppo.name))
            ret = self.ctrl.Handle(cmd)
        return ret           

#############################################################
class RNG_AIMind(Mind):
    "AI player which randomly make decision"

    def __init__(self):
        super().__init__()
        self.core = None
        self.ctrl = None
    
    def Think(self):
        if self.core.isDefenderPhase():
            if self.core.isDashAttack:
                self.chooseActionFrom(Mind.ACT_DEFEND, Mind.ACT_RETREAT, Mind.ACT_BEHIT)
            else:
                self.chooseActionFrom(Mind.ACT_DEFEND, Mind.ACT_BEHIT)
        else:
            self.chooseActionFrom(Mind.ACT_MOVE, Mind.ACT_ATTACK, Mind.ACT_PUSH, Mind.ACT_DASH)

    def chooseActionFrom(self, *actions):
        canDos = []
        for act in actions:
            if self.canExecute(act, canDos):
                canDos.append(act)

        act = random.choice(canDos)
        self.execute(act)

    def canExecute(self, act:str, canDos):

        dist = int(math.fabs(self.core.players[0].pos - self.core.players[1].pos))

        ############ defend
        if self.core.isDefenderPhase():
            p = self.core.curPlayer().oppo
            if act == Mind.ACT_DEFEND:
                cntDefCards = p.countCard(dist)
                needDefCards = len(self.core.atkVector)
                return cntDefCards >= needDefCards
            elif act == Mind.ACT_RETREAT:
                return p.pos != p.startPos
            elif act == Mind.ACT_BEHIT:
                return len(canDos) == 0 # only choose behit when nothing else can choose
        ############ attack
        else:
            p = self.core.curPlayer()
            if act == Mind.ACT_MOVE:
                return p.pos != p.startPos or p.pos + p.face != p.oppo.pos
            elif act == Mind.ACT_ATTACK:
                cntAtkCards = p.countCard(dist)
                return cntAtkCards > 0
            elif act == Mind.ACT_PUSH:
                return dist == 1 and p.oppo.pos != p.oppo.startPos
            elif act == Mind.ACT_DASH:
                hands = p.hands
                for i in range(len(hands)):
                    j = i+1
                    while j < len(hands):
                        if hands[i] + hands[j] == dist:
                            return True
                        j+=1
                return False
        
    def execute(self, act:str):
        dist = int(math.fabs(self.core.players[0].pos - self.core.players[1].pos))

        if self.core.isDefenderPhase():
            p = self.core.curPlayer().oppo
            if act == Mind.ACT_DEFEND:
                print("AI {0} defended attack {1}".format( p.name, self.core.atkVector) )
                self.core.cmd_defend(p, self.core.atkVector)
            elif act == Mind.ACT_RETREAT:
                c = random.choice(p.hands)
                print("AI {0} retreat with {1}".format( p.name, c) )
                self.core.cmd_retreat(p, c)
            elif act == Mind.ACT_BEHIT:
                print("~~~~~AI {0} is hit~~~~~".format(p.name))
                self.core.cmd_getHit(p)

        else:
            p = self.core.curPlayer()
            if act == Mind.ACT_MOVE:
                c = random.choice(p.hands)
                forward = random.random() < 0.5
                if forward and p.pos + p.face == p.oppo.pos:
                    forward = False
                if (not forward) and p.pos == p.startPos:
                    forward = True
                print("AI {0} moves {1} {2} cells".format(p.name, "forward" if forward else "backward", c))
                self.core.cmd_move(p, c, forward)                
            elif act == Mind.ACT_ATTACK:
                cntAtkCards = p.countCard(dist)
                maxC = min(cntAtkCards, 2)
                useC = random.randint(1, maxC)
                print("AI {0} attacks with {1} of {2}s".format(p.name, useC, dist))
                self.core.cmd_attack(p, [dist for _ in range(useC)] )
            elif act == Mind.ACT_PUSH:
                c = random.choice(p.hands)
                print("AI {0} pushes with {1}".format(p.name, c))
                self.core.cmd_push(p, c)
            elif act == Mind.ACT_DASH:
                hands = p.hands
                possibles = []
                for i in range(len(hands)):
                    mv = hands[i]
                    atk = dist - mv
                    hasAtk = p.countCard(atk)
                    if hasAtk >= 1:
                        if atk == mv:
                            canDouble = hasAtk >= 3
                        else:
                            canDouble = hasAtk >= 2
                        possibles.append( (mv, canDouble) )
                
                chosen = random.choice(possibles)
                mv = chosen[0]
                if chosen[1]:
                    if random.random() < 0.5:
                        atkCards = [dist-mv, dist-mv]
                    else:
                        atkCards = [dist-mv]
                else:
                    atkCards = [dist-mv]
                print("AI {0} dashes {1} cell and attacks with {2} of {3}".format(p.name, mv, len(atkCards), dist-mv))
                self.core.cmd_dashAttack(p, mv, atkCards)

