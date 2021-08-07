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

    def joint_side(self):
        left_or_right = self.hierarchy[0][0:2]
        print("This chain is on the --> {}".format(left_or_right))
        return left_or_right

class DriverChain(BaseChain):

    def __init__(self, hierarchy, hierarchyDrv):
        super(DriverChain, self).__init__(hierarchy)
        self.hierarchyDrv = hierarchyDrv

    # Directly connect driver chain with the base one
    def connect_to_baseFinger(self):
        for bone, boneDrv in zip(self.hierarchy, self.hierarchyDrv):
            cmds.parentConstraint(boneDrv, bone)

class Locators(DriverChain):
    def __init__(self, hierarchy, hierarchyDrv):
        super(DriverChain, self).__init__(hierarchy, hierarchyDrv)
        pass

def chain_definition():
    
    # Chain definition
    metacarp = cmds.ls(sl=1)[0]
    hierarchy = cmds.listRelatives(metacarp, ad=1, typ="joint")
    hierarchy.append(metacarp)
    hierarchy.reverse()

    return hierarchy


def make_driver_chain(*args):

    hierarchy = chain_definition()
    
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

    return driver_hierarchy

def make_ik_chain(*args):

    hierarchy = chain_definition()

    # Creating a two-joint chain where gonna apply "reverse-hand" ik-handles
    ikStart = cmds.joint(n=hierarchy[0] + "_ikStart", rad=3)
    ikEnd = cmds.joint(n=hierarchy[-1] + "_ikEnd", rad=3)

    # Parent this chain to the world using the original chain attributes
    cmds.parent(ikStart, w=1)
    cmds.matchTransform(ikStart, hierarchy[0])
    cmds.matchTransform(ikEnd, hierarchy[-1])

    # single chain ik handle build and parenting in a single grp
    finger_ikHandle = cmds.ikHandle(sj=ikStart, ee=ikEnd, sol="ikSCsolver", n=hierarchy[0] + "_ikHandle")[0]
    cmds.parent(finger_ikHandle, ik_hand_grp)

# group automatically generating at the startup where parent fingers ik_handles
ik_hand_grp = cmds.group(n= "fingers_ik", em=1, w=1)


def make_locators_attributes(*args):
    
    hierarchy = chain_definition()
    hierarchyDrv = make_driver_chain()
    print(hierarchyDrv)

    fingerLOCS = []

    for bone in hierarchy:
        boneLOC = cmds.spaceLocator(n=bone + "_LOC")
        fingerLOCS.append(boneLOC)
        cmds.matchTransform(boneLOC, bone)
        cmds.orientConstraint(boneLOC, hierarchyDrv)

    for x in range(len(hierarchy[:-1])):
            cmds.parent(fingerLOCS[x+1], fingerLOCS[x])

# User Interface
def showUI():

    if cmds.window("switchModeUI", ex = 1): cmds.deleteUI("switchModeUI")
    myWin = cmds.window("switchModeUI", t="sbx-autohand", w=300, h=300, s=1)
    mainLayout = cmds.formLayout(nd=50)

    separator01 = cmds.separator(h=5)
    separator02 = cmds.separator(h=5)
    driver_chain_Button = cmds.button(l="make driver chain", c=make_driver_chain)
    ik_chain_Button = cmds.button(l="make ik chain", c=make_ik_chain)
    locators_Button = cmds.button(l="create locators", c=make_locators_attributes)

    cmds.formLayout(mainLayout, e=1,
                    attachForm = [
                        (driver_chain_Button, "left", 8), (driver_chain_Button, "top", 5), (driver_chain_Button, "right", 8),
                        (separator01, "left", 1), (separator01, "right", 2),
                        (separator02, "left", 1), (separator02, "right", 2),
                        (ik_chain_Button, "left", 8), (ik_chain_Button, "top", 5), (ik_chain_Button, "right", 8),
                        (locators_Button, "left", 8), (locators_Button, "top", 5), (locators_Button, "right", 8)
                        ],
                    attachControl = [
                        (separator01, "top", 5, driver_chain_Button),
                        (ik_chain_Button, "top", 5, separator01),
                        (separator02, "top", 5, ik_chain_Button),
                        (locators_Button, "top", 5, separator02),
                        ],
                    #attachPosition = [(driver_chain_Button, "right", 0, 0)
                        #]
                        )
    
    cmds.showWindow(myWin)

showUI()