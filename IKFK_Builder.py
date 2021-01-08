import maya.cmds as cmds
from functools import partial

def duplicateChain(scaleController, chainMenu, chainLen, *args):

    global ogChain
    global cosoLoc
    global side
    global modeCheckBox_UI
    
    ogRootchain = cmds.ls(sl = True, type = "joint")[0]        
    ogChain = cmds.listRelatives(ogRootchain, ad = True, type = "joint")
    ogChain.append(ogRootchain)
    ogChain.reverse()
    side = ogRootchain[0:2]
 
    scaleController = cmds.intField(scaleControllerField, q=1, v=1)
    
    chainMenu = cmds.optionMenu("chainMenu_UI", q=1, v=1)

    if chainMenu == "Leg": 
        chainLen = 5
    else: #this is totally unscalable but for now it's ok
        chainLen = 3

    #suffix for the new chains
    newJointList = ["_ik", "_fk"]
    for newJoint in newJointList:
        for i in range(chainLen):
            newJointName = ogChain[i] + newJoint

            #create a joint, copy their position and freeze transform
            cmds.joint(n = newJointName)
            cmds.matchTransform(newJointName, ogChain[i])
            cmds.makeIdentity(newJointName, a = 1, t = 0, r = 1, s = 0)
        
        #deselect to make the two different hierarchies
        cmds.select(cl = 1)

    cmds.parent((ogChain[0] + "_ik"), world = True)
    cmds.setAttr(ogChain[0] + "_ik.visibility", 0)
    cmds.setAttr(ogChain[0] + "_fk.visibility", 0)

    # Create a locator used for switching IK/FK mode and snap it between two joints
    cosoLoc = cmds.spaceLocator(n=side + chainMenu + "_ikfk_Switch")
    cosoLocGrp = cmds.group(em=1, n=cosoLoc[0] + "_grp")
    cmds.color(cosoLoc, rgb=(255, 255, 0)) #yellow
    cmds.delete(cmds.pointConstraint(cosoLoc, cosoLocGrp))
    cmds.parent(cosoLoc, cosoLocGrp)
    cmds.delete(cmds.pointConstraint(ogChain[1], ogChain[2], cosoLocGrp))
    cmds.addAttr(cosoLoc, ln="FKIK_Mode", at="short", min=0, max=1, k=1, r=1)
    cmds.move(0,0,-12, cosoLocGrp, r=1) #you must improve this shit
    cmds.parentConstraint(ogChain[1], cosoLocGrp, mo=1)
    
    #remove .t, .r, .s and .v from the channelbox
    axis = ["X", "Y", "Z"]
    for coord in axis:
        cmds.setAttr(cosoLoc[0] + ".translate" + coord, k=0, l=1)
        cmds.setAttr(cosoLoc[0] + ".rotate" + coord, k=0, l=1)
        cmds.setAttr(cosoLoc[0] + ".scale" + coord, k=0, l=1)
    cmds.setAttr(cosoLoc[0] + ".visibility", k=0, l=1)
    

    modeCheckBox = cmds.checkBox(modeCheckBox_UI, q=1, v=1) 

    if modeCheckBox == 0:
        blendNodeFunc(scaleController, selectChain=chainMenu, jointCount=chainLen)
        #print modeCheckBox
    else:
        constraintFunc(scaleController, selectChain=chainMenu, jointCount=chainLen)
        #print modeCheckBox


def blendNodeFunc(scaleController, selectChain, jointCount):

    #create some blendColors node with the same name of the joint
    for x in range(jointCount):

        blendColorsNode = cmds.createNode("blendColors", n = ogChain[x] + "_blend")

        # connect FK and IK chains into blendColors channels and then connect the output to the original joint chain
        cmds.connectAttr((ogChain[x] + "_ik.rotate"), blendColorsNode + ".color1")
        cmds.connectAttr((ogChain[x] + "_fk.rotate"), blendColorsNode + ".color2")
        cmds.connectAttr((blendColorsNode + ".output"), (ogChain[x] + ".rotate" ))
        cmds.connectAttr(cosoLoc[0]+".FKIK_Mode", blendColorsNode + ".blender")

    
    ikChainBuild(scaleIK=scaleController, HandleName=selectChain)
    fkControllerCreator(fkSize=scaleController, legOrArm=selectChain,jointCount=jointCount)


def constraintFunc(scaleController, selectChain, jointCount):

    #create some blendColors node with the same name of the joint
    for x in range(jointCount):
        
        #setup orient constraints        
        cmds.orientConstraint((ogChain[x] + "_ik"), ogChain[x])
        cmds.orientConstraint((ogChain[x] + "_fk"), ogChain[x])

        #setup SDK naming convention
        sdkDriver = cosoLoc[0] + ".FKIK_Mode"
        ikSdkDriven = ogChain[x] + "_orientConstraint1." + ogChain[x] + "_ikW0"
        fkSdkDriven = ogChain[x] + "_orientConstraint1." + ogChain[x] + "_fkW1"

        #setup SDK
        cmds.setAttr(sdkDriver, 0)
        cmds.setDrivenKeyframe(ikSdkDriven, cd=sdkDriver, v=0, dv=0)
        cmds.setDrivenKeyframe(fkSdkDriven, cd=sdkDriver, v=1, dv=0)

        cmds.setAttr(sdkDriver, 1)
        cmds.setDrivenKeyframe(ikSdkDriven, cd=sdkDriver, v=1, dv=1)
        cmds.setDrivenKeyframe(fkSdkDriven, cd=sdkDriver, v=0, dv=1)

    
    ikChainBuild(scaleIK=scaleController, HandleName=selectChain)
    fkControllerCreator(fkSize=scaleController, legOrArm=selectChain, jointCount=jointCount)

    

def fkControllerCreator(fkSize, legOrArm, jointCount):
    
    orientController = cmds.optionMenu("UI_orientControllerMenu", q=1, v=1)

    #create controllers and group offsets
    #change rotation, color
    for y in range(jointCount):
        anim_group = cmds.group(em=1, n=ogChain[y] + "_anim_grp")
        fk_controller = cmds.circle(n=ogChain[y] + "_anim")[0] #if not [0] it'll warn some stuff related to Maya underworld
        
        cmds.setAttr(fk_controller + ".scaleX", fkSize)
        cmds.setAttr(fk_controller + ".scaleY", fkSize)
        cmds.setAttr(fk_controller + ".scaleZ", fkSize)

        cmds.matchTransform(anim_group, ogChain[y])
        cmds.delete(cmds.parentConstraint(ogChain[y], fk_controller))
        cmds.parent(fk_controller, anim_group)

        if orientController == "x": cmds.rotate(90,0,0, fk_controller)
        if orientController == "y": cmds.rotate(0,90,0, fk_controller)
        if orientController == "z": cmds.rotate(0,0,90, fk_controller)
        
        cmds.makeIdentity(fk_controller, a = 1, t = 1, r = 1, s = 0)
        cmds.delete(fk_controller, ch = 1)


        if side == "l_": 
            cmds.color(fk_controller, rgb=(0, 0, 255))
        else:
            cmds.color(fk_controller, rgb=(255, 0, 0))
        
        #set SDK visibility

        sdkDriver = cosoLoc[0] + ".FKIK_Mode"
        cmds.setAttr(sdkDriver, 0)
        cmds.setDrivenKeyframe(ogChain[0] + "_anim_grp.visibility", cd=sdkDriver, v=0, dv=1)
        cmds.setAttr(sdkDriver, 1)
        cmds.setDrivenKeyframe(ogChain[0] + "_anim_grp.visibility", cd=sdkDriver, v=1, dv=0)

    # Create ordered hierarchy
    for x in reversed(range(jointCount)):
        if x == 0:
            continue
        cmds.parent(ogChain[x] + "_anim_grp", ogChain[x-1] + "_anim")

    
    # Orient Constraint _anim controllers with _fk hierarchy
    for x in range(jointCount):
        cmds.orientConstraint(ogChain[x] + "_anim", ogChain[x] + "_fk")
        # If leg chain is selected delete toe controller, else not
        if legOrArm == "Leg":
            if x == (jointCount-1):
                cmds.delete(ogChain[jointCount-1] + "_anim_grp")
        else:
            pass
    
    print ("first", fkSize)
    

def ikChainBuild(scaleIK, HandleName):

    global masterIkHandle
    
    masterIkHandle = cmds.ikHandle(sj=ogChain[0] + "_ik", ee=ogChain[2] + "_ik", sol="ikRPsolver", n=side + HandleName + "_ikHandle")
    cmds.setAttr(masterIkHandle[0] + ".visibility", 0)
    """
    pvController = cmds.curve( d=1, p=[( 0, 1, 0 ), ( 0, 0.92388, 0.382683 ), ( 0, 0.707107, 0.707107 ), 
                                        ( 0, 0.382683, 0.92388 ), ( 0, 0, 1 ), ( 0, -0.382683, 0.92388 ), ( 0, -0.707107, 0.707107 ), ( 0, -0.92388, 0.382683 ), 
                                        ( 0, -1, 0 ), ( 0, -0.92388, -0.382683 ), ( 0, -0.707107, -0.707107 ), ( 0, -0.382683, -0.92388 ), 
                                        ( 0, 0, -1 ), ( 0, 0.382683, -0.92388 ), ( 0, 0.707107, -0.707107 ), ( 0, 0.92388, -0.382683 ), ( 0, 1, 0 ), 
                                        ( 0.382683, 0.92388, 0 ), ( 0.707107, 0.707107, 0 ), ( 0.92388, 0.382683, 0 ), ( 1, 0, 0 ), ( 0.92388, -0.382683, 0 ), 
                                        ( 0.707107, -0.707107, 0 ), ( 0.382683, -0.92388, 0 ), ( 0, -1, 0 ), ( -0.382683, -0.92388, 0 ), ( -0.707107, -0.707107, 0 ), 
                                        ( -0.92388, -0.382683, 0 ), ( -1, 0, 0 ), ( -0.92388, 0.382683, 0 ), ( -0.707107, 0.707107, 0 ), ( -0.382683, 0.92388, 0 ), 
                                        ( 0, 1, 0 ), ( 0, 0.92388, -0.382683, ), ( 0, 0.707107, -0.707107, ), ( 0, 0.382683, -0.92388, ), ( 0, 0, -1 ), 
                                        ( -0.382683, 0, -0.92388 ), ( -0.707107, 0, -0.707107 ), ( -0.92388, 0, -0.382683 ), ( -1, 0, 0 ), ( -0.92388, 0, 0.382683 ), 
                                        ( -0.707107, 0, 0.707107 ), ( -0.382683, 0, 0.92388 ), ( 0, 0, 1 ), ( 0.382683, 0, 0.92388 ), ( 0.707107, 0, 0.707107 ), 
                                        ( 0.92388, 0, 0.382683 ), ( 1, 0, 0 ), ( 0.92388, 0, -0.382683 ), ( 0.707107, 0, -0.707107 ), ( 0.382683, 0, -0.92388 ), 
                                        ( 0, 0, -1)], 
                                        k= [0 , 1 , 2 , 3 , 4 , 5 , 6 , 7 , 8 , 9 , 10 , 11 , 12 , 13 , 14 , 15 , 16 , 17 , 18 , 19 , 20 , 21 , 22 , 23 , 24 , 25 , 26 , 27 , 28 , 29 , 30 , 31 , 32 , 33 , 34 , 35 , 36 , 37 , 38 , 39 , 40 , 41 , 42 , 43 , 44 , 45 , 46 , 47 , 48 , 49 , 50 , 51 , 52])
    """
    
    if HandleName == "Arm": 
        #print ("scaleController", scaleControllerField)
        armIk(armIkScale=scaleIK)
    else:   
        #print ("scaleController", scaleControllerField)
        legIK(ikFootScale=scaleIK)
    


def armIk(armIkScale):

    ikHandJoint = cmds.joint(n=side + "hand_ik")
    cmds.delete(cmds.parentConstraint(ogChain[2] + "_ik", ikHandJoint))
    cmds.makeIdentity(ikHandJoint, a = 1, t = 1, r = 1, s = 0)
    cmds.move(10,0,0, ikHandJoint, r=1, os=1)
    cmds.parent(ikHandJoint, ogChain[2] + "_ik")
    handikHandle = cmds.ikHandle(sj=ogChain[2] + "_ik", ee=ikHandJoint, n=side + "hand_ikHandle", sol="ikSCsolver")
    cmds.parent(handikHandle[0], masterIkHandle[0])
    
    #create IK controller
    crvIkCube = cmds.curve(d=1, p=[(-1, 1, -1), (1, 1, -1), (1, 1, 1),
                                    (-1, 1, 1), (-1, -1, 1), (-1, -1, -1),
                                    (-1, 1, -1), (-1, 1, 1), (-1, -1, 1),
                                    (1, -1, 1), (1, 1, 1), (1, 1, -1),
                                    (1, -1, -1), (1, -1, 1), (1, -1, -1), (-1, -1, -1)], 
                                    k=[0 , 1, 2, 3, 4, 5, 6, 7, 8, 9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5], n=side + "hand_ik_anim" )
    crvIkCubeGrp = cmds.group(n=crvIkCube + "_grp")
    cmds.delete(cmds.parentConstraint(ogChain[2] + "_ik", crvIkCubeGrp))
    print("arms", armIkScale)
    cmds.setAttr(crvIkCubeGrp + ".scaleX", armIkScale)
    cmds.setAttr(crvIkCubeGrp + ".scaleY", armIkScale)
    cmds.setAttr(crvIkCubeGrp + ".scaleZ", armIkScale)

    cmds.parent(masterIkHandle[0], crvIkCube)
    
    #set SDK visibility
    sdkDriver = cosoLoc[0] + ".FKIK_Mode"
    cmds.setAttr(sdkDriver, 0)
    cmds.setDrivenKeyframe(crvIkCubeGrp + ".visibility", cd=sdkDriver, v=0, dv=0)
    cmds.setAttr(sdkDriver, 1)
    cmds.setDrivenKeyframe(crvIkCubeGrp + ".visibility", cd=sdkDriver, v=1, dv=1)

def legIK(ikFootScale):

    ballikHandle = cmds.ikHandle(sj=ogChain[2] + "_ik", ee=ogChain[3] + "_ik", sol="ikSCsolver", n=side + "ball_ikHandle")
    toeikHandle = cmds.ikHandle(sj=ogChain[3] + "_ik", ee=ogChain[4] + "_ik", sol="ikSCsolver", n=side + "toe_ikHandle")
    
    # Create and place ik controller
    ikFootControl = cmds.circle(n=side + "leg_anim_ik")
    ikFootControlGrp = cmds.group(n=ikFootControl[0] + "_grp")
    cmds.setAttr(ikFootControlGrp + ".scaleX", ikFootScale)
    cmds.setAttr(ikFootControlGrp + ".scaleY", ikFootScale)
    cmds.setAttr(ikFootControlGrp + ".scaleZ", ikFootScale)
    cmds.rotate(90,0,0, ikFootControl)
    cmds.move(0,-3.2,0, ikFootControl, r=1)
    cmds.makeIdentity(ikFootControl, a = 1, t = 1, r = 1, s = 0)
    cmds.delete(ikFootControl[0], ch = 1)
    cmds.delete(cmds.pointConstraint(ogChain[3] + "_ik", ikFootControlGrp))
    
    # pivot snapping on ankle joint
    piv = cmds.xform(ogChain[2], q=True, ws=True, t=True)
    cmds.xform(ikFootControl[0], ws=True, piv=piv)

    cmds.parent(ballikHandle[0], toeikHandle[0], masterIkHandle[0], ikFootControl[0])

    #set SDK visibility
    sdkDriver = cosoLoc[0] + ".FKIK_Mode"
    cmds.setAttr(sdkDriver, 0)
    cmds.setDrivenKeyframe(ikFootControlGrp + ".visibility", cd=sdkDriver, v=0, dv=0)
    cmds.setAttr(sdkDriver, 1)
    cmds.setDrivenKeyframe(ikFootControlGrp + ".visibility", cd=sdkDriver, v=1, dv=1)
    

def showUI():
    
    global chainMenu_UI
    global scaleControllerField
    global orientControllerMenu
    global modeCheckBox_UI
    
    if cmds.window("switchModeUI", ex = 1): cmds.deleteUI("switchModeUI")
    myWin = cmds.window("switchModeUI", t="IKFK Builder", w=300, h=300, s=1)
    mainLayout = cmds.formLayout(nd=50)
    
    # Useful in selecting which chain: Leg or Arm? 
    chainMenu_UI = cmds.optionMenu("chainMenu_UI", l="Which chain?")
    cmds.menuItem(l="Leg")
    cmds.menuItem(l="Arm")

    modeCheckBox_UI = cmds.checkBox(label = "orientConstraint+SDK Mode", v=0)

    # Useful in orienting FK controllers as the user wishes. Maybe this can be improved
    orientControllerMenu = cmds.optionMenu("UI_orientControllerMenu", l="What's the secondary axis")
    cmds.menuItem(l="x")
    cmds.menuItem(l="y")
    cmds.menuItem(l="z")

    # Scale the UI becase you'll never know
    scaleControllerText = cmds.text(l="FK Controllers size")
    scaleControllerField = cmds.intField(en=10, v=5, min=1)
    
    separator01 = cmds.separator(h=5)
    separator02 = cmds.separator(h=5)

    #
    execButton = cmds.button(l="Duplicate Chain", c=partial(duplicateChain, blendNodeFunc, constraintFunc))
    #parent_execButton = cmds.button(l="Constraint + SDK Mode", c=duplicateChain)
    
    cmds.formLayout(mainLayout, e=1,
                    attachForm = [
                        (chainMenu_UI, "left", 8), (chainMenu_UI, "top", 5),
                        (modeCheckBox_UI, "right", 5), (modeCheckBox_UI, "top", 5),
                        (separator01, "left", 1), (separator01, "right", 2),
                        #--------------------
                        
                        (scaleControllerField, "right", 5), (scaleControllerField, "left", 150),
                        (scaleControllerText, "left", 5),
                        (separator02, "left", 1), (separator02, "right", 2),
                        #--------------------
                        
                        (orientControllerMenu, "left", 8), (orientControllerMenu, "top", 5),
                        #--------------------
                        
                        (execButton, "bottom", 5), (execButton, "left", 5), (execButton, "right", 5),
                        #(parent_execButton, "bottom", 5), (parent_execButton, "left", 5), (parent_execButton, "right", 5)
                    ],
                    attachControl = [(separator01, "top", 5, chainMenu_UI),
                                     (scaleControllerField, "top", 5, separator01),
                                     (scaleControllerText, "top", 6, separator01),
                                     (separator02, "top", 6, scaleControllerField),
                                     (orientControllerMenu, "top", 6, separator02)
                    
                    ],
                    
                    #attachPosition = [(execButton, "left", 0, 26), (parent_execButton, "right", 0, 24)]
    
    
    )
    
    cmds.showWindow(myWin)
    
showUI()