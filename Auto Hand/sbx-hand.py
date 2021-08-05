import maya.cmds as cmds

# Try to write classes as more generic as possible so you would re-use them in other scripts 
#  
class BaseChain(object):

    def __init__(self, hierarchy):
        self.hierarchy = hierarchy

    def countBones(self):
        count = 0
        for x in self.hierarchy:
            count += 1
        return count

class DriverChain(BaseChain):

    def __init__(self, hierarchy, hierarchyDrv):
        super(DriverChain, self).__init__(hierarchy)
        self.hierarchyDrv = hierarchyDrv

    # Directly connect driver chain with the base one
    def connect_to_baseFinger(self):
        for bone, boneDrv in zip(self.hierarchy, self.hierarchyDrv):
            cmds.parentConstraint(boneDrv, bone)

def make_driver_chain(*args):

    metacarp = cmds.ls(sl=1)[0]
    hierarchy = cmds.listRelatives(metacarp, ad=1, typ="joint")
    hierarchy.append(metacarp)
    hierarchy.reverse()
    
    driver_hierarchy = []

    for bone in hierarchy:
        boneDrv = cmds.joint(n=bone + "__rig")
        driver_hierarchy.append(boneDrv)
        cmds.matchTransform(boneDrv, bone)

    cmds.parent(driver_hierarchy[0], w=1)

    driver_finger = DriverChain(hierarchy, driver_hierarchy)
    driver_to_origin_connection = driver_finger.connect_to_baseFinger()


def showUI():

    if cmds.window("switchModeUI", ex = 1): cmds.deleteUI("switchModeUI")
    myWin = cmds.window("switchModeUI", t="IKFK Builder", w=300, h=300, s=1)
    mainLayout = cmds.formLayout(nd=50)

    execButton = cmds.button(l="make driver chain", c=make_driver_chain)

    
    cmds.showWindow(myWin)

showUI()

#ogFinger = BaseChain()
#numBones = ogFinger.countBones()