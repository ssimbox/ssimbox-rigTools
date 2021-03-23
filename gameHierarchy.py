import maya.cmds as cmds

#Simple tool useful in building a single hierarchy exportable in Unity 

#Select bind joints
ogChain = cmds.ls(sl=1, type="joint")

#Make new 'game' joints, and position them in place.
cmds.select(d=1)
gameChain = []
for i in ogChain:
    jnt = cmds.joint(n=i+"_game")
    cmds.delete(cmds.parentConstraint(i,jnt,mo=0))
    gameChain.append(jnt)
    cmds.select(d=1)
    
#Convert rotations of new joints to joint orient.
for i in gameChain:
    cmds.makeIdentity(i, apply = True, t=0, r=1, s=0, n=0)
    
for i in ogChain:
    if cmds.objExists(i+"_game"):
        cmds.parentConstraint(i,i+"_game", mo=1)