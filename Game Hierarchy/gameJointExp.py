import maya.cmds as cmds

def jointMaker(*args):

    global suffix_UI
    global mainJoints

    mainJoints = cmds.ls(sl=1, typ="joint")
    suffix = cmds.textField(suffix_UI, q=1, text=True)
    #cmds.textScrollList('listJointUI',e=1, ra=1)
    #cmds.textScrollList('listJointUI', e=1, append=[""+str(mainJoints)+""])
    
    #Make new '_game' joints, and position them in place.
    gameExpGrp = cmds.group(n="gameExp_grp", em=1)
    
    cmds.select(d=1)
    gameJoints = []
    
    
    for i in mainJoints:
        jnt = cmds.joint(n=i+'_game', rad=0.65)
        cmds.delete(cmds.parentConstraint(i, jnt, mo=0))
        # remove suffix on user input
        if suffix in jnt:
            new = str(jnt).replace(suffix, "")
            jnt = cmds.rename(jnt, new) 
            cmds.select(cl=1)
            print("jnt in if-->", jnt)
        gameJoints.append(jnt)
        cmds.select(d=1)

    #Convert rotations of new joints to joint orient.
    for i in gameJoints:
        cmds.makeIdentity(i, apply = True, t=0, r=1, s=0, n=0)
        cmds.parent(i, gameExpGrp)


    #Parent constraint from rig_jnts to game_jnts
def makeConstraint(*args):
    for i in mainJoints:
        if cmds.objExists(i+'_game'):
            cmds.parentConstraint(i, i+'_game', mo=1)


def showUI():

    global suffix_UI

    if cmds.window("gameExportUI", ex = 1): cmds.deleteUI("gameExportUI")
    myWin = cmds.window("gameExportUI", t="gameExportUI", w=300, h=300, s=1)
    mainLayout = cmds.formLayout(nd=50)

    suffix_UI = cmds.textField(w=100, tx="_")
    jointMaker_btn = cmds.button(l="build joint", c=jointMaker)
    constraintMaker_btn = cmds.button(l="make constraints", c=makeConstraint)
    #listJointUI = cmds.textScrollList("listJointUI",numberOfRows=8)

    cmds.formLayout(mainLayout, e=1,
                    attachForm = [
                                #(listJointUI, "left", 8),
                                (jointMaker_btn, "right", 8), (jointMaker_btn, "top", 8),
                                (constraintMaker_btn, "right", 8), (constraintMaker_btn, "top", 40),
                                (suffix_UI, "top", 8), (suffix_UI, "left", 5)
                                ]
                                )

    cmds.showWindow(myWin)

showUI()