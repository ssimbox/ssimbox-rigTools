import maya.cmds as cmds

class Finger:
    def __init__(self, chainSel, fullLength):
        self.chainSel = chainSel #primo elemento della catena
        self.fullLength = fullLength #l'intera catena

    def jointColor(self, colorR, colorG, colorB):
        cmds.color(self.chainSel, rgb=(colorR, colorG, colorB))

    def ikHandles(self, endJoint, nomone):
        cmds.ikHandle(sj=self.chainSel, ee=endJoint, sol="ikSCsolver", n=nomone)

    def duplicateFingerChain(self): 
        chain = [] #dichiaro chain come una lista
        suffix = ["_rig"]
        # print("immediate after append --> ", chain)
        for y in suffix:
            #carico la lista ad ogni giro del ciclo per poter effettuare tutte le operazioni sulle liste
            
            for x in range(len(fullFinger)):
                chain.append(fullFinger[x])
                cmds.joint(n = chain[x] + y, radius = 1)
                cmds.matchTransform(chain[x] + y, fullFinger[x])
                #cmds.makeIdentity(chain[x] + y, a = 1, t = 0, r = 1, s = 0)
        
        cmds.parent((chain[0] + "_rig"), world = True)

startJoint = cmds.ls(sl=1)[0]
fullFinger = cmds.listRelatives(startJoint, ad=1, typ="joint")
fullFinger.append(startJoint)
fullFinger.reverse()
# print("fullFinger --> ", fullFinger)

# call Finger class
firstFinger = Finger(startJoint, len(fullFinger))

# duplicate the finger base chain with a new one
firstFinger.duplicateFingerChain()

# Create ikHandle
firstFinger.ikHandles(fullFinger[-1], startJoint + "_ikHandle")

# Change color based on side
if startJoint[0:2] == "l_":
    firstFinger.jointColor(0, 0, 255)
elif startJoint[0:2] == "r_":
    firstFinger.jointColor(255, 0, 0)


"""class Finger:
    def __init__(self, fullLength, chainSel):
        self.chainSel = cmds.ls(sl=1)
        jointsNumber = cmds.listRelatives(self.chainSel, ad=1)
        jointsNumber.append(chainSel)
        jointsNumber.reverse()
        self.fullLength = len(jointsNumber)
        print (fullLength)

    def jointColor(self, colorR, colorG, colorB):
        self.colorR = colorR
        self.colorG = colorG
        self.colorB = colorB
        cmds.color(self.chainSel, rgb=(colorR, colorG, colorB))


# chainSel = cmds.ls(sl=1)
colorOne = Finger(0, chainSel)
colorOne.jointColor(0, 0, 255)"""