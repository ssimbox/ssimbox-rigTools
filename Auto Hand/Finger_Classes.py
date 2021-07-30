import maya.cmds as cmds

class Finger(object):
    def __init__(self, metacarp, distal, fullLength):
        self.metacarp = metacarp #Metacarp -> First bone in a finger
        self.distal = distal #Distal -> Last bone in a finger
        self.fullLength = fullLength #Entire chain
        
    def jointColor(self, colorR, colorG, colorB):
        cmds.color(self.metacarp, rgb=(colorR, colorG, colorB))

class DriverFinger(Finger):
    def __init__(self, metacarp, distal, fullLength):
        super(DriverFinger, self).__init__(metacarp, distal, fullLength)

    def duplicateChain(self, metacarpDrv, distalDrv, hierarchyDrv):
        
        self.metacarpDrv = metacarpDrv
        self.distalDrv = distalDrv
        self.hierarchyDrv = hierarchyDrv

        for x in range(len(self.fullLength)):
            boneDrv = cmds.joint(n=self.fullLength[x] + "__nuovo")
            fingerHierarchyDrv.append(boneDrv) 
            cmds.matchTransform(boneDrv, self.fullLength[x])
               
        cmds.parent(metacarpDrv, w=1)
    
    def ikHandles(self):
        fingerIKH = cmds.ikHandle(sj=self.metacarpDrv, ee=self.distalDrv, sol="ikSCsolver", n=self.metacarp + "_ikHandle")[0]
        return fingerIKH

    def connectToOrigin(self):
        for x in range(len(self.fullLength)):
            cmds.parentConstraint(self.hierarchyDrv[x], self.fullLength[x])


class ControllerFinger(Finger):

    def __init__(self, metacarp, distal, fullLength):
        super(ControllerFinger, self).__init__(metacarp, distal, fullLength)

    def makeController(self):
        for x in range(len(self.fullLength)):
            fingerLOCs = cmds.spaceLocator(n=self.fullLength[x] + "_LOC")
            cmds.matchTransform(fingerLOCs, self.fullLength[x])


### Selection definition and the original chain hierarchy
startJoint = cmds.ls(sl=1)[0]
fullFinger = cmds.listRelatives(startJoint, ad=1, typ="joint")
fullFinger.append(startJoint)
fullFinger.reverse()

# fullFinger[0] = first joint selected and so first into the chain 
# fullFinger[-1] = it is the last joint in the chain
firstFinger = Finger(fullFinger[0], fullFinger[-1], fullFinger)

fingerHierarchyDrv = []

driverFinger = DriverFinger(fullFinger[0], fullFinger[-1], fullFinger)
driverFinger.duplicateChain(fullFinger[0] + "__nuovo", fullFinger[-1] + "__nuovo", fingerHierarchyDrv)

driverFinger.connectToOrigin()

# Create ikHandle
"""asd = firstFinger.ikHandles()
# Queste tre righe qua sotto sono la morte della programmazione
asdGrp = cmds.group(n="ik_grp", em=1)
cmds.parent(asd, "ik_grp")
if cmds.objExists("ik_grp1"):
    cmds.delete("ik_grp1")"""

# Change color based on side
if startJoint[0:2] == "l_":
    firstFinger.jointColor(0, 0, 255)
elif startJoint[0:2] == "r_":
    firstFinger.jointColor(255, 0, 0)

createCtrl = ControllerFinger(fullFinger[0], fullFinger[-1], fullFinger)
createCtrl.makeController()