import maya.cmds as cmds

class Finger:
    def __init__(self, metacarp, distal, fullLength):
        self.metacarp = metacarp #Metacarp -> First bone in a finger
        self.distal = distal #Distal -> Last bone in a finger
        self.fullLength = fullLength #Entire chain
        
    def jointColor(self, colorR, colorG, colorB):
        cmds.color(self.metacarp, rgb=(colorR, colorG, colorB))

    def ikHandles(self, nomone):
        cmds.ikHandle(sj=self.metacarpDup, ee=self.distalDup, sol="ikRPsolver", n=nomone)
    
    def duplFinger(self, metacarpDup, distalDup, hierarchyDup):

        self.metacarpDup = metacarpDup
        self.distalDup = distalDup
        self.hierarchyDup = hierarchyDup

        """devo ancora capire se tenere questo processo qui dentro oppure portarlo fuori, ancora non ne ho ben capito l'utilità
        che poi sotto viene comunuque richiamato in maniera altamente barbara"""

        for i in fullFinger:
            asd = cmds.joint(n= i + rigJoint)
            newJoint.append(asd)
            cmds.matchTransform(asd, i)

        cmds.parent(newJoint[0], w=1)
        pass
    
    # Connect Translate and Rotate attributes from duplicated hierarchy to the original
    def connectToOrigin(self):
        for x in range(len(self.fullLength)):
            cmds.parentConstraint(self.hierarchyDup[x], self.fullLength[x])

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
# fullFinger[0] = first joint selected and so first into the chain 
# fullFinger[-1] = it is the last joint in the chain
firstFinger = Finger(fullFinger[0], fullFinger[-1], fullFinger)


# richiamo il metodo della classe dichiarando chi è cosa
rigJoint = "__nuovo"
newJoint = []
dupFinger = firstFinger.duplFinger(fullFinger[0] + rigJoint, (fullFinger[-1] + rigJoint), newJoint)

"""
rigChain = ["_rig"]
for y in rigChain:
    for x in range(len(fullFinger)):
        asd = cmds.joint(n=fullFinger[x] + y, rad=.7)
        cmds.matchTransform(fullFinger[x] + y, fullFinger[x])
"""
firstFinger.connectToOrigin()
# Create ikHandle
firstFinger.ikHandles(startJoint + "_ikHandle")

# Change color based on side
if startJoint[0:2] == "l_":
    firstFinger.jointColor(0, 0, 255)
elif startJoint[0:2] == "r_":
    firstFinger.jointColor(255, 0, 0)