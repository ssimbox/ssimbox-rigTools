#Helps automate game rig process
import maya.cmds as cmds


#Select bind joints

ogJoints = cmds.ls(sl=1)
#Make new '_game' joints, and position them in place.

cmds.select(d=1)
gameJoints = []
for i in ogJoints:
    jnt = cmds.joint(n=i+'_game')
    cmds.delete(cmds.parentConstraint(i,jnt,mo=0))
    gameJoints.append(jnt)
    cmds.select(d=1)
#Convert rotations of new joints to joint orient.
for i in gameJoints:
    cmds.makeIdentity(i, apply = True, t=0, r=1, s=0, n=0)


#Parent constraint from rig_jnts to game_jnts
def gameRig_constraints():
    for i in ogJoints:
        if cmds.objExists(i+'_game'):
            cmds.parentConstraint(i, i+'_game', mo=1)