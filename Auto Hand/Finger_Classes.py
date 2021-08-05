import maya.cmds as cmds

class Finger(object):
    def __init__(self, metacarp, distal, fullLength):
        self.metacarp = metacarp #Metacarp -> First bone in a finger
        self.distal = distal #Distal -> Last bone in a finger
        self.fullLength = fullLength #Entire chain

class DriverFinger(Finger):
    def __init__(self, metacarp, distal, fullLength, metacarpDrv, distalDrv, hierarchyDrv):
        super(DriverFinger, self).__init__(metacarp, distal, fullLength)
                
        self.metacarpDrv = metacarpDrv
        self.distalDrv = distalDrv
        self.hierarchyDrv = hierarchyDrv
    
    def connectToOrigin(self):
        for boneDrv, bone in zip(self.hierarchyDrv,self.fullLength):
            cmds.parentConstraint(boneDrv, bone)

    """def ikHandles(self):
        fingerIKH = cmds.ikHandle(sj=self.ikStart, ee=self.ikEnd, sol="ikSCsolver", n=self.metacarp + "_ikHandle")[0]
        return fingerIKH"""

class ControllerFinger(DriverFinger):

    def __init__(self, metacarp, distal, fullLength, metacarpDrv, distalDrv, hierarchyDrv):
        super(ControllerFinger, self).__init__(metacarp, distal, fullLength, metacarpDrv, distalDrv, hierarchyDrv)

    def makeController(self):
        self.fingerLOCS = []
        
        for x in range(len(self.fullLength)):
            boneLOC = cmds.spaceLocator(n=self.fullLength[x] + "_LOC")
            self.fingerLOCS.append(boneLOC)
            cmds.matchTransform(boneLOC, self.fullLength[x])
        
        for x in range(len(self.fullLength[:-1])):
            cmds.parent(self.fingerLOCS[x+1], self.fingerLOCS[x])
            pass

    def jointColor(self, colorR, colorG, colorB):
        for LOC in self.fingerLOCS:
            cmds.color(LOC, rgb=(colorR, colorG, colorB))

def basic_finger():
    ### Selection definition and the original chain hierarchy
    startJoint = cmds.ls(sl=1)[0]
    entireFinger = cmds.listRelatives(startJoint, ad=1, typ="joint")
    entireFinger.append(startJoint)
    entireFinger.reverse()

    baseMetacarp = entireFinger[0] #First bone in a finger
    baseDistal = entireFinger[-1] #Last bone in a finger

    # baseMetacarp = first joint selected -> metacarp
    # baseDistal = last joint in the chain -> distal
    firstFinger = Finger(baseMetacarp, baseDistal, entireFinger)
    return entireFinger

def make_driver_chain():

    fingerHierarchyDrv = []

    entireFinger = basic_finger()
    print("ciao --> ", entireFinger)

    for bone in entireFinger:
        boneDrv = cmds.joint(n=bone + "__nuovo")
        fingerHierarchyDrv.append(boneDrv) 
        cmds.matchTransform(boneDrv, bone)
                
    driverFinger = DriverFinger(baseMetacarp, baseDistal, entireFinger, 
                                baseMetacarp + "__nuovo", baseDistal + "__nuovo", fingerHierarchyDrv)
    cmds.parent(fingerHierarchyDrv[0], w=1) #Parent into world the driver chain
    cmds.select(cl=1) #Maya automatically selects the new chain but I don't want
    
    driverFinger.connectToOrigin()

    ikStart = cmds.joint(n=baseMetacarp + "_ikStart", rad=3)
    ikEnd = cmds.joint(n=baseDistal + "_ikEnd", rad=3)

    cmds.matchTransform(ikStart, baseMetacarp)
    cmds.matchTransform(ikEnd, baseDistal)

# Create ikHandle
#finger_ikHandles = driverFinger.ikHandles()

# Group ikHandles 
"""finger_ikHandles_grp = cmds.group(n="ik_grp", em=1)
cmds.parent(finger_ikHandles, "ik_grp")
if finger_ikHandles_grp == "ik_grp1":
    cmds.delete(finger_ikHandles_grp)"""

createCtrl = ControllerFinger(baseMetacarp, baseDistal, entireFinger, 
                            baseMetacarp + "__nuovo", baseDistal + "__nuovo", fingerHierarchyDrv)
createCtrl.makeController()

# Change color based on side
if startJoint[0:2] == "l_":
    createCtrl.jointColor(0, 0, 255)
elif startJoint[0:2] == "r_":
    createCtrl.jointColor(255, 0, 0)

make_driver_chain()