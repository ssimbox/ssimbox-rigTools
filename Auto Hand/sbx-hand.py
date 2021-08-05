import maya.cmds as cmds

class BaseFinger(object):
    
    def hierarchy_definition(self):
        self.metacarp = cmds.ls(sl=1)[0]
        self.hierarchy = cmds.listRelatives(self.metacarp, ad=1, typ="joint")
        self.hierarchy.append(self.metacarp)
        self.hierarchy.reverse()

        return self.hierarchy

    def countBones(self):

        count = 0
        for x in self.hierarchy:
            count += 1
        return count

class DriverFinger(BaseFinger):
    # Directly connect driver chain with the base one
    def connect_to_baseFinger(self):
        for bone, boneDrv in zip(self.hierarchy, self.hierarchyDrv):
            cmds.parentConstraint(boneDrv, bone)

def make_driver_chain(*args):

    original_finger = BaseFinger()
    original_hierarchy = original_finger.hierarchy_definition()

    driver_hierarchy = []

    for bone in original_hierarchy:
        boneDrv = cmds.joint(n=bone + "__rig")
        driver_hierarchy.append(boneDrv)
        cmds.matchTransform(boneDrv, bone)

    cmds.parent(driver_hierarchy[0], w=1)

    driver_finger = DriverFinger()
    driver_to_origin_connection = driver_finger.connect_to_baseFinger()


def showUI():

    if cmds.window("switchModeUI", ex = 1): cmds.deleteUI("switchModeUI")
    myWin = cmds.window("switchModeUI", t="IKFK Builder", w=300, h=300, s=1)
    mainLayout = cmds.formLayout(nd=50)

    execButton = cmds.button(l="make driver chain", c=make_driver_chain)

    
    cmds.showWindow(myWin)

showUI()

#ogFinger = BaseFinger()
#numBones = ogFinger.countBones()