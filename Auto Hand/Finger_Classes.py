import maya.cmds as cmds

class Finger:
    def __init__(self, chainSel, fullLength):
        self.chainSel = chainSel
        self.fullLength = fullLength
        print (fullLength)

    def jointColor(self, colorR, colorG, colorB):
        self.colorR = colorR
        self.colorG = colorG
        self.colorB = colorB
        cmds.color(self.chainSel, rgb=(colorR, colorG, colorB))


chainSel = cmds.ls(sl=1)
jointsNumber = cmds.listRelatives(chainSel, ad=1)
jointsNumber.append(chainSel)
jointsNumber.reverse()
fullLength = len(jointsNumber)
colorOne = Finger(chainSel, fullLength)
colorOne.jointColor(0, 0, 255)

"""class Finger:
    def __init__(self, fullLength, chainSel):
        self.chainSel = chainSel
        jointsNumber = cmds.listRelatives(chainSel, ad=1)
        jointsNumber.append(chainSel)
        jointsNumber.reverse()
        self.fullLength = len(jointsNumber)
        print (fullLength)

    def jointColor(self, colorR, colorG, colorB):
        self.colorR = colorR
        self.colorG = colorG
        self.colorB = colorB
        cmds.color(self.chainSel, rgb=(colorR, colorG, colorB))


chainSel = cmds.ls(sl=1)
colorOne = Finger(0, chainSel)
colorOne.jointColor(0, 0, 255)"""