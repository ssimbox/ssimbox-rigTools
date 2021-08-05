import maya.cmds as cmds

# Try to write classes as more generic as possible so you would re-use them in other scripts 
#  
class BaseChain(object):

    def __init__(self, hierarchy):
        self.hierarchy = hierarchy

    def bone_count(self):
        count = 0
        for x in self.hierarchy:
            count += 1    
        print("Joints in this chain --> {}".format(count))
        return count

class DriverChain(BaseChain):

    def __init__(self, hierarchy, hierarchyDrv):
        super(DriverChain, self).__init__(hierarchy)
        self.hierarchyDrv = hierarchyDrv

    # Directly connect driver chain with the base one
    def connect_to_baseFinger(self):
        for bone, boneDrv in zip(self.hierarchy, self.hierarchyDrv):
            cmds.parentConstraint(boneDrv, bone)

# Chain definition
metacarp = cmds.ls(sl=1)[0]
hierarchy = cmds.listRelatives(metacarp, ad=1, typ="joint")
hierarchy.append(metacarp)
hierarchy.reverse()

def make_driver_chain(*args):

    # Istantiating BaseChain and printing number of joint in every single chain
    original_chain = BaseChain(hierarchy)
    original_chain.bone_count()
    
    # Building up the driver hierarchy
    driver_hierarchy = []

    for bone in hierarchy:
        boneDrv = cmds.joint(n=bone + "__rig")
        driver_hierarchy.append(boneDrv)
        cmds.matchTransform(boneDrv, bone)

    cmds.parent(driver_hierarchy[0], w=1)

    # Intantiating DriverChain and parentConstraint every driver joint with the relative original 
    driver_finger = DriverChain(hierarchy, driver_hierarchy)
    driver_finger.connect_to_baseFinger()

def make_ik_chain(*args):

    ikStart = cmds.joint(n=hierarchy[0] + "_ikStart", rad=3)
    ikEnd = cmds.joint(n=hierarchy[-1] + "_ikEnd", rad=3)

    cmds.parent(ikStart, w=1)

    cmds.matchTransform(ikStart, hierarchy[0])
    cmds.matchTransform(ikEnd, hierarchy[-1])

    finger_ikHandle = cmds.ikHandle(sj=ikStart, ee=ikEnd, sol="ikSCsolver", n=hierarchy[0] + "_ikHandle")[0]

# User Interface
def showUI():

    if cmds.window("switchModeUI", ex = 1): cmds.deleteUI("switchModeUI")
    myWin = cmds.window("switchModeUI", t="sbx-autohand", w=300, h=300, s=1)
    mainLayout = cmds.formLayout(nd=50)

    separator01 = cmds.separator(h=5)
    driver_chain_Button = cmds.button(l="make driver chain", c=make_driver_chain)
    ik_chain_Button = cmds.button(l="make ik chain", c=make_ik_chain)

    cmds.formLayout(mainLayout, e=1,
                    attachForm = [
                        (driver_chain_Button, "left", 8), (driver_chain_Button, "top", 5), (driver_chain_Button, "right", 8),
                        (separator01, "left", 1), (separator01, "right", 2),
                        (ik_chain_Button, "left", 8), (ik_chain_Button, "top", 5), (ik_chain_Button, "right", 8)
                        ],
                    attachControl = [
                        (separator01, "top", 5, driver_chain_Button),
                        (ik_chain_Button, "top", 5, separator01)
                        ],
                    #attachPosition = [(driver_chain_Button, "right", 0, 0)
                        #]
                        )
    
    cmds.showWindow(myWin)

showUI()