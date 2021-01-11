import maya.cmds as cmds
import maya.OpenMaya as om
from functools import partial

def duplicateChain(scaleController, chainMenu, *args):

    global ogChain
    global chainLen
    global cosoLoc
    global side
    global controllerColor
    
    ogRootchain = cmds.ls(sl = True, type = "joint")[0]        
    ogChain = cmds.listRelatives(ogRootchain, ad = True, type = "joint")
    ogChain.append(ogRootchain)
    ogChain.reverse()
    side = ogRootchain[0:2]
    
    # Initialize input from UI
    scaleController = cmds.intField(scaleField_UI, q=1, v=1)
    blendCheckbox = cmds.checkBox(blendCheckbox_UI, q=1, v=1) 
    constraintCheckBox = cmds.checkBox(constraintCheckBox_UI, q=1, v=1) 
    
    chainMenu = cmds.optionMenu("chainMenu_UI", q=1, v=1)

    if side == "l_": controllerColor = rgb=(0, 0, 255)
    elif side == "r_": controllerColor = rgb=(255, 0, 0)

    if chainMenu == "Leg": chainLen = 5
    else: #this is totally unscalable but for now it's ok
        chainLen = 3

    #suffix for the new chains
    newJointList = ["_ik", "_fk"]
    for newJoint in newJointList:
        for i in range(chainLen):
            
            if blendCheckbox == 0 and constraintCheckBox == 0:
                cmds.error("pls, select one relation type")
                break

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
    cmds.move(0,0,-12, cosoLocGrp, r=1) #IMPROVE THIS SHIT
    cmds.parentConstraint(ogChain[1], cosoLocGrp, mo=1)
    
    #remove .t, .r, .s and .v from the channelbox
    for coord in ["X", "Y", "Z"]:
        cmds.setAttr(cosoLoc[0] + ".translate" + coord, k=0, l=1)
        cmds.setAttr(cosoLoc[0] + ".rotate" + coord, k=0, l=1)
        cmds.setAttr(cosoLoc[0] + ".scale" + coord, k=0, l=1)
    cmds.setAttr(cosoLoc[0] + ".visibility", k=0, l=1)

    if blendCheckbox == 1:
        blendNodeFunc(scaleController=scaleController, selectChain=chainMenu)
    
    if constraintCheckBox == 1:
        constraintFunc(scaleController=scaleController, selectChain=chainMenu)

def blendNodeFunc(scaleController, selectChain, *kekkeroni):

    # Create some blendColors node with the same name of the joint
    for x in range(chainLen):

        blendColorsNode = cmds.createNode("blendColors", n = ogChain[x] + "_blend")

        # Connect FK and IK chains into blendColors channels and then connect the output to the original joint chain
        cmds.connectAttr((ogChain[x] + "_ik.rotate"), blendColorsNode + ".color1")
        cmds.connectAttr((ogChain[x] + "_fk.rotate"), blendColorsNode + ".color2")
        cmds.connectAttr((blendColorsNode + ".output"), (ogChain[x] + ".rotate" ))
        cmds.connectAttr(cosoLoc[0]+".FKIK_Mode", blendColorsNode + ".blender")

    ikChainBuild(scaleIK=scaleController, HandleName=selectChain, masterIkHandle=kekkeroni)
    fkControllerCreator(fkSize=scaleController, legOrArm=selectChain)


def constraintFunc(scaleController, selectChain, *kekkeroni):

    # Create some blendColors node with the same name of the joint
    for x in range(chainLen):
        
        # Setup orient constraints        
        cmds.orientConstraint((ogChain[x] + "_ik"), ogChain[x])
        cmds.orientConstraint((ogChain[x] + "_fk"), ogChain[x])

        # Setup SDK naming convention
        sdkDriver = cosoLoc[0] + ".FKIK_Mode"
        ikSdkDriven = ogChain[x] + "_orientConstraint1." + ogChain[x] + "_ikW0"
        fkSdkDriven = ogChain[x] + "_orientConstraint1." + ogChain[x] + "_fkW1"

        # Setup SDK
        cmds.setAttr(sdkDriver, 0)
        cmds.setDrivenKeyframe(ikSdkDriven, cd=sdkDriver, v=0, dv=0)
        cmds.setDrivenKeyframe(fkSdkDriven, cd=sdkDriver, v=1, dv=0)

        cmds.setAttr(sdkDriver, 1)
        cmds.setDrivenKeyframe(ikSdkDriven, cd=sdkDriver, v=1, dv=1)
        cmds.setDrivenKeyframe(fkSdkDriven, cd=sdkDriver, v=0, dv=1)

    
    ikChainBuild(scaleIK=scaleController, HandleName=selectChain, masterIkHandle=kekkeroni)
    fkControllerCreator(fkSize=scaleController, legOrArm=selectChain)

    

def fkControllerCreator(fkSize, legOrArm):
    
    orientController = cmds.optionMenu("UI_orientControllerMenu", q=1, v=1)

    # Create controllers and group offsets
    # Change rotation, color
    for y in range(chainLen):
        anim_group = cmds.group(em=1, n=ogChain[y] + "_anim_grp")
        fk_controller = cmds.circle(n=ogChain[y] + "_anim")[0] # If not [0] it'll warn some stuff related to Maya underworld
        
        for x in ["X", "Y", "Z"]:
            cmds.setAttr(fk_controller + ".scale" + x, fkSize)
            
        cmds.matchTransform(anim_group, ogChain[y])
        cmds.delete(cmds.parentConstraint(ogChain[y], fk_controller))
        cmds.parent(fk_controller, anim_group)

        if orientController == "x": cmds.rotate(90,0,0, fk_controller)
        if orientController == "y": cmds.rotate(0,90,0, fk_controller)
        if orientController == "z": cmds.rotate(0,0,90, fk_controller)
        
        cmds.makeIdentity(fk_controller, a = 1, t = 1, r = 1, s = 0)
        cmds.delete(fk_controller, ch = 1)
        
        cmds.color(fk_controller, rgb=controllerColor)
        
        # Set SDK visibility
        sdkDriver = cosoLoc[0] + ".FKIK_Mode"
        cmds.setAttr(sdkDriver, 1)
        cmds.setDrivenKeyframe(ogChain[0] + "_anim_grp.visibility", cd=sdkDriver, v=1, dv=0)
        cmds.setAttr(sdkDriver, 0)
        cmds.setDrivenKeyframe(ogChain[0] + "_anim_grp.visibility", cd=sdkDriver, v=0, dv=1)

    # Create ordered hierarchy
    for x in reversed(range(chainLen)):
        if x == 0:
            continue
        cmds.parent(ogChain[x] + "_anim_grp", ogChain[x-1] + "_anim")

    
    # Orient Constraint _anim controllers with _fk hierarchy
    for x in range(chainLen):
        cmds.orientConstraint(ogChain[x] + "_anim", ogChain[x] + "_fk")
        # If leg chain is selected delete toe controller, else not
        if legOrArm == "Leg":
            if x == (chainLen-1):
                cmds.delete(ogChain[chainLen-1] + "_anim_grp")
        else:
            pass
    

def ikChainBuild(scaleIK, HandleName, masterIkHandle):
    
    masterIkHandle = cmds.ikHandle(sj=ogChain[0] + "_ik", ee=ogChain[2] + "_ik", sol="ikRPsolver", n=side + HandleName + "_ikHandle")
    cmds.setAttr(masterIkHandle[0] + ".visibility", 0)
    
    if HandleName == "Arm": 
        #print ("scaleController", scaleField_UI)
        armIk(armIkScale=scaleIK, armikHandle=masterIkHandle, pvName=HandleName)
    else:   
        #print ("scaleController", scaleField_UI)
        legIK(ikFootScale=scaleIK, legikHandle=masterIkHandle, pvName=HandleName)


def armIk(armIkScale, armikHandle, pvName):

    ikHandJoint = cmds.joint(n=side + "hand_ik")
    cmds.delete(cmds.parentConstraint(ogChain[2] + "_ik", ikHandJoint))
    cmds.makeIdentity(ikHandJoint, a = 1, t = 1, r = 1, s = 0)
    cmds.move(10,0,0, ikHandJoint, r=1, os=1)
    cmds.parent(ikHandJoint, ogChain[2] + "_ik")
    handikHandle = cmds.ikHandle(sj=ogChain[2] + "_ik", ee=ikHandJoint, n=side + "hand_ikHandle", sol="ikSCsolver")
    cmds.parent(handikHandle[0], armikHandle[0])
    
    #create IK controller ---> CUBE
    crvIkCube = cmds.curve(d=1, p=[(-1, 1, -1), (1, 1, -1), (1, 1, 1),
                                    (-1, 1, 1), (-1, -1, 1), (-1, -1, -1),
                                    (-1, 1, -1), (-1, 1, 1), (-1, -1, 1),
                                    (1, -1, 1), (1, 1, 1), (1, 1, -1),
                                    (1, -1, -1), (1, -1, 1), (1, -1, -1), (-1, -1, -1)], 
                                    k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5], n=side + "hand_ik_anim" )
    crvIkCubeGrp = cmds.group(n=crvIkCube + "_grp")
    cmds.delete(cmds.parentConstraint(ogChain[2] + "_ik", crvIkCubeGrp))

    cmds.color(crvIkCube, rgb=controllerColor)
    
    for coord in ["X", "Y", "Z"]:
        cmds.setAttr(crvIkCubeGrp + ".scale" + coord, armIkScale)

    cmds.parent(armikHandle[0], crvIkCube)

    pvController = cmds.curve(n=side + pvName + "_PV", d=1, p=[
                                                            ( 0, 1, 0 ), ( 0, 0.92388, 0.382683 ), ( 0, 0.707107, 0.707107 ), 
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

    findPoleVector(loc=pvController, targetHandle=armikHandle[0])
    
    #set SDK visibility
    sdkDriver = cosoLoc[0] + ".FKIK_Mode"
    cmds.setAttr(sdkDriver, 0)
    cmds.setDrivenKeyframe(crvIkCubeGrp + ".visibility", cd=sdkDriver, v=0, dv=0)
    cmds.setAttr(sdkDriver, 1)
    cmds.setDrivenKeyframe(crvIkCubeGrp + ".visibility", cd=sdkDriver, v=1, dv=1)

def legIK(ikFootScale, legikHandle, pvName):

    ballikHandle = cmds.ikHandle(sj=ogChain[2] + "_ik", ee=ogChain[3] + "_ik", sol="ikSCsolver", n=side + "ball_ikHandle")
    toeikHandle = cmds.ikHandle(sj=ogChain[3] + "_ik", ee=ogChain[4] + "_ik", sol="ikSCsolver", n=side + "toe_ikHandle")
    
    # Create and place ik controller
    ikFootControl = cmds.circle(n=side + "leg_anim_ik")
    ikFootControlGrp = cmds.group(n=ikFootControl[0] + "_grp")
    
    for coord in ["X", "Y", "Z"]:
        cmds.setAttr(ikFootControlGrp + ".scale" + coord, ikFootScale)

    cmds.rotate(90,0,0, ikFootControl)
    cmds.move(0,-3.2,0, ikFootControl, r=1)
    cmds.makeIdentity(ikFootControl, a = 1, t = 1, r = 1, s = 0)
    cmds.delete(ikFootControl[0], ch = 1)
    cmds.delete(cmds.pointConstraint(ogChain[3] + "_ik", ikFootControlGrp))
    
    cmds.color(ikFootControl[0], rgb=controllerColor) 
    
    # pivot snapping on ankle joint
    piv = cmds.xform(ogChain[2], q=True, ws=True, t=True)
    cmds.xform(ikFootControl[0], ws=True, piv=piv)

    cmds.parent(ballikHandle[0], toeikHandle[0], legikHandle[0], ikFootControl[0])
    
    # Pole Vector controller ---> Sphere
    pvController = cmds.curve(n=side + pvName + "_PV", d=1, p=[
                                                            ( 0, 1, 0 ), ( 0, 0.92388, 0.382683 ), ( 0, 0.707107, 0.707107 ), 
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

    findPoleVector(loc=pvController, targetHandle=legikHandle[0])


    # Set SDK visibility
    sdkDriver = cosoLoc[0] + ".FKIK_Mode"
    cmds.setAttr(sdkDriver, 0)
    cmds.setDrivenKeyframe(ikFootControlGrp + ".visibility", cd=sdkDriver, v=0, dv=0)
    cmds.setDrivenKeyframe(pvController + "_grp.visibility", cd=sdkDriver, v=0, dv=0)
    cmds.setAttr(sdkDriver, 1)
    cmds.setDrivenKeyframe(ikFootControlGrp + ".visibility", cd=sdkDriver, v=1, dv=1)
    cmds.setDrivenKeyframe(pvController + "_grp.visibility", cd=sdkDriver, v=1, dv=1)
    
def findPoleVector(loc, targetHandle):

    # This func is kinda black magic

    start = cmds.xform(ogChain[0], q=1, ws=1, t=1)
    mid = cmds.xform(ogChain[1], q=1, ws=1, t=1)
    end = cmds.xform(ogChain[2], q=1, ws=1, t=1)

    startV = om.MVector(start[0], start[1], start[2])
    midV = om.MVector(mid[0], mid[1], mid[2])
    endV = om.MVector(end[0], end[1], end[2])

    startEnd = endV - startV
    startMid = midV - startV

    dotP = startMid * startEnd
    proj = float(dotP) / float(startEnd.length())
    startEndN = startEnd.normal()
    projV = startEndN * proj

    arrowV = startMid - projV
    arrowV*= 10 #distance from joint
    finalV = arrowV + midV
    
    cmds.xform(loc, ws=1, t=(finalV.x, finalV.y ,finalV.z))

    locGrp = cmds.group(em=1, n=loc + "_grp")

    cmds.delete(cmds.pointConstraint(loc, locGrp))
    cmds.parent(loc, locGrp)
    cmds.makeIdentity(loc, a=1, t=1, r=1, s=1)
    cmds.color(loc, rgb=controllerColor)

    cmds.poleVectorConstraint(loc, targetHandle)



def showUI():
    
    global chainMenu_UI
    global scaleField_UI
    global orientControllerMenu
    global constraintCheckBox_UI
    global blendCheckbox_UI
    
    if cmds.window("switchModeUI", ex = 1): cmds.deleteUI("switchModeUI")
    myWin = cmds.window("switchModeUI", t="IKFK Builder", w=300, h=300, s=1)
    mainLayout = cmds.formLayout(nd=50)
    
    # Useful in selecting which chain: Leg or Arm? 
    chainMenu_UI = cmds.optionMenu("chainMenu_UI", l="Which chain?")
    cmds.menuItem(l="Leg")
    cmds.menuItem(l="Arm")

    constraintCheckBox_UI = cmds.checkBox(label = "orientConsts+SDK Mode", v=0, 
                                          cc= lambda state: (cmds.checkBox(blendCheckbox_UI, e=1, en=state-1)))
    blendCheckbox_UI = cmds.checkBox(label = "blendColor Mode", v=0, 
                                     cc= lambda state: (cmds.checkBox(constraintCheckBox_UI, e=1, en=state-1)))

    # Useful in orienting FK controllers as the user wishes. Maybe this can be improved
    orientControllerMenu = cmds.optionMenu("UI_orientControllerMenu", l="What's the secondary axis")
    cmds.menuItem(l="x")
    cmds.menuItem(l="y")
    cmds.menuItem(l="z")

    # Scale the UI becase you'll never know
    scaleControllerText = cmds.text(l="FK Controllers size")
    scaleField_UI = cmds.intField(en=10, v=5, min=1)
    
    separator01 = cmds.separator(h=5)
    separator02 = cmds.separator(h=5)

    #
    execButton = cmds.button(l="Duplicate Chain", c=partial(duplicateChain, blendNodeFunc, constraintFunc))
    #parent_execButton = cmds.button(l="Constraint + SDK Mode", c=duplicateChain)
    
    cmds.formLayout(mainLayout, e=1,
                    attachForm = [
                        (chainMenu_UI, "left", 8), (chainMenu_UI, "top", 5), (chainMenu_UI, "right", 8),
                        (constraintCheckBox_UI, "left", 8),
                        (blendCheckbox_UI, "left", 5),
                        (separator01, "left", 1), (separator01, "right", 2),
                        #--------------------
                        
                        (scaleField_UI, "right", 5), (scaleField_UI, "left", 5),
                        (scaleControllerText, "left", 5),
                        (separator02, "left", 1), (separator02, "right", 2),
                        #--------------------
                        
                        (orientControllerMenu, "left", 8), (orientControllerMenu, "top", 5),
                        #--------------------
                        
                        (execButton, "bottom", 5), (execButton, "left", 5), (execButton, "right", 5),
                        #(parent_execButton, "bottom", 5), (parent_execButton, "left", 5), (parent_execButton, "right", 5)
                    ],
                    attachControl = [(constraintCheckBox_UI, "top", 5, chainMenu_UI),
                                     (blendCheckbox_UI, "top", 5, chainMenu_UI),
                                     (separator01, "top", 5, constraintCheckBox_UI),
                                     (scaleField_UI, "top", 5, separator01),
                                     (scaleControllerText, "top", 8, separator01),
                                     (separator02, "top", 6, scaleField_UI),
                                     (orientControllerMenu, "top", 6, separator02)
                    
                    ],
                    
                    attachPosition = [(constraintCheckBox_UI, "left", 0, 26), (blendCheckbox_UI, "right", 10, 24),
                                      (scaleControllerText, "left", 5, 0), (scaleField_UI, "left", 110, 0)
                    ]
    
    
    )
    
    cmds.showWindow(myWin)
    
showUI()