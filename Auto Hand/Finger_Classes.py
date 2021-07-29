import maya.cmds as cmds

class Finger:
    def __init__(self, metacarp, distal, fullLength):
        self.metacarp = metacarp #Metacarp -> First bone in a finger
        self.distal = distal #Distal -> Last bone in a finger
        self.fullLength = fullLength #Entire chain

    def jointColor(self, colorR, colorG, colorB):
        cmds.color(self.metacarp, rgb=(colorR, colorG, colorB))

    def ikHandles(self, nomone):
        cmds.ikHandle(sj=self.metacarpDup, ee=self.distalDup, sol="ikSCsolver", n=nomone)
    
    def duplFinger(self, metacarpDup, distalDup):
        self.metacarpDup = metacarpDup
        self.distalDup = distalDup
        pass
    
    """potrei dichiarare le variabili di classe di duplFinger dentro __init__ e, nel metodo appena citato 
        eseguo il processo con cui si creano i duplicati??? boh ci devo provare"""

    """
    def duplicateFingerChain(self, firstDup, endDup): 
        
        self.firstDup = firstDup
        self.endDup = endDup
        firstDup = [] #dichiaro chain come una lista
        suffix = ["_rig"]
        
        for y in suffix:

            #carico la lista ad ogni giro del ciclo per poter effettuare tutte le operazioni sulle liste    
            for x in range(len(fullFinger)):
                
                firstDup.append(fullFinger[x])
                cmds.joint(n = firstDup[x] + y, radius = 1)
                cmds.matchTransform(firstDup[x] + y, fullFinger[x])
                #cmds.makeIdentity(chain[x] + y, a = 1, t = 0, r = 1, s = 0)
        
        cmds.parent((firstDup[0] + "_rig"), world = True)
    """
class Hand:
    def __init__(self, carpal):
        self.carpal = carpal 
        pass


startJoint = cmds.ls(sl=1)[0]
fullFinger = cmds.listRelatives(startJoint, ad=1, typ="joint")
fullFinger.append(startJoint)
fullFinger.reverse()
# print("fullFinger --> ", fullFinger)

# call Finger class
# startJoint[0] = first joint selected and so first into the chain 
# fullFinger[-1] = it is the last joint in the chain
firstFinger = Finger(fullFinger[0], fullFinger[-1], len(fullFinger))

# duplicate the finger base chain with a new one
#firstFinger.duplicateFingerChain(startJoint[0] + "_rig")

newJoint = []
for i in fullFinger:
    asd = cmds.joint(n=i+"__nuovo")
    newJoint.append(asd)
    cmds.matchTransform(asd, i)
    #print(newJoint[i])
print(newJoint)
cmds.parent(newJoint[0], w=1)

# richiamo il metodo della classe dichiarando chi è cosa
dupFinger = firstFinger.duplFinger(newJoint[0], newJoint[-1])

"""
rigChain = ["_rig"]
for y in rigChain:
    for x in range(len(fullFinger)):
        asd = cmds.joint(n=fullFinger[x] + y, rad=.7)
        cmds.matchTransform(fullFinger[x] + y, fullFinger[x])
"""

# Create ikHandle
firstFinger.ikHandles(startJoint + "_ikHandle")

# Change color based on side
if startJoint[0:2] == "l_":
    firstFinger.jointColor(0, 0, 255)
elif startJoint[0:2] == "r_":
    firstFinger.jointColor(255, 0, 0)