import maya.cmds as cmds

class Finger(object):
    def __init__(self, metacarp, distal, fullLength):
        self.metacarp = metacarp #Metacarp -> First bone in a finger
        self.distal = distal #Distal -> Last bone in a finger
        self.fullLength = fullLength #Entire chain

class DriverFinger(Finger):
    def __init__(self, metacarp, distal, fullLength):
        super(DriverFinger, self).__init__(metacarp, distal, fullLength)

    def duplicateChain(self, metacarpDrv, distalDrv):
        
        self.metacarpDrv = metacarpDrv
        self.distalDrv = distalDrv
        self.hierarchyDrv = []

        for x in range(len(self.fullLength)):
            boneDrv = cmds.joint(n=self.fullLength[x] + "__nuovo")
            self.hierarchyDrv.append(boneDrv) 
            cmds.matchTransform(boneDrv, self.fullLength[x])
               
        cmds.parent(metacarpDrv, w=1) #Parent into world the driver chain
        cmds.select(cl=1) #Maya automatically selects the new chain but I don't want
    
    def connectToOrigin(self):
        for x in range(len(self.fullLength)):
            cmds.parentConstraint(self.hierarchyDrv[x], self.fullLength[x])

    def ikChain(self):
        self.ikStart = cmds.joint(n=self.metacarp + "_ikStart", rad=3)
        self.ikEnd = cmds.joint(n=self.distal + "_ikEnd", rad=3)

        cmds.matchTransform(self.ikStart, self.metacarp)
        #cmds.makeIdentity(ikStart, self.metacarp)
        cmds.matchTransform(self.ikEnd, self.distal)

    def ikHandles(self):
        fingerIKH = cmds.ikHandle(sj=self.ikStart, ee=self.ikEnd, sol="ikSCsolver", n=self.metacarp + "_ikHandle")[0]
        return fingerIKH

class ControllerFinger(Finger):

    def __init__(self, metacarp, distal, fullLength):
        super(ControllerFinger, self).__init__(metacarp, distal, fullLength)


    def makeController(self):
        self.fingerLOCS = []
        
        for x in range(len(self.fullLength)):
            boneLOC = cmds.spaceLocator(n=self.fullLength[x] + "_LOC")
            self.fingerLOCS.append(boneLOC)
            cmds.matchTransform(boneLOC, self.fullLength[x])
        
        for x in range(len(self.fullLength[:-1])):
            #print(x)
            cmds.parent(self.fingerLOCS[x+1], self.fingerLOCS[x])
            pass

    def jointColor(self, colorR, colorG, colorB):
        for LOC in self.fingerLOCS:
            cmds.color(LOC, rgb=(colorR, colorG, colorB))

### Selection definition and the original chain hierarchy
startJoint = cmds.ls(sl=1)[0]
fullFinger = cmds.listRelatives(startJoint, ad=1, typ="joint")
fullFinger.append(startJoint)
fullFinger.reverse()

# fullFinger[0] = first joint selected -> metacarp
# fullFinger[-1] = last joint in the chain -> distal
firstFinger = Finger(fullFinger[0], fullFinger[-1], fullFinger)

driverFinger = DriverFinger(fullFinger[0], fullFinger[-1], fullFinger)
driverFinger.duplicateChain(fullFinger[0] + "__nuovo", fullFinger[-1] + "__nuovo")

driverFinger.connectToOrigin()

# Create ikHandle
ikChain = driverFinger.ikChain()
finger_ikHandles = driverFinger.ikHandles()
# Queste tre righe qua sotto sono la morte della programmazione
finger_ikHandles_grp = cmds.group(n="ik_grp", em=1)
cmds.parent(finger_ikHandles, "ik_grp")
if finger_ikHandles_grp == "ik_grp1":
    cmds.delete(finger_ikHandles_grp)

createCtrl = ControllerFinger(fullFinger[0], fullFinger[-1], fullFinger)
createCtrl.makeController()

# Change color based on side
if startJoint[0:2] == "l_":
    createCtrl.jointColor(0, 0, 255)
elif startJoint[0:2] == "r_":
    createCtrl.jointColor(255, 0, 0)
