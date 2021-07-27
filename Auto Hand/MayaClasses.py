import maya.cmds as cmds

class createSphere():
    def __init__(self, nomone):
        self.newSphere = cmds.polySphere(n=nomone)

    def translateValue(self, tx, ty, tz):
        self.tx = cmds.setAttr(self.newSphere[0] + ".translateX", tx)
        self.ty = cmds.setAttr(self.newSphere[0] + ".translateY", ty)
        self.tz = cmds.setAttr(self.newSphere[0] + ".translateZ", tz)
    
    def freezeTrans(self, state):
        cmds.makeIdentity(self.newSphere[0], a=1, t=state)
        cmds.delete(self.newSphere[0], ch=state)

sphere1 = createSphere("ichiban")
sphere2 = createSphere("kasuga")
firstTrans = sphere1.translateValue(6, 0, 0)
secondTrans = sphere2.translateValue(-6, 0, 0)
sphere1.freezeTrans(True)
sphere2.freezeTrans(True)

#print(createSphere())

"""
import maya.cmds as p
class soSphere():

    def __init__(self, name):
        self.sphere = p.sphere(n=name)
        
    def setTranslateX(self, value):		
        p.setAttr(self.sphere[0] + '.tx', value)

    def getTranslateX(self):
        return p.getAttr(self.sphere[0] + '.tx')


sp = soSphere('nameOftheSphere')
print (sp.getTranslateX())
sp.setTranslateX(5.0)
print (sp.getTranslateX())
"""