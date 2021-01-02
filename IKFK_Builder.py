import maya.cmds as cmds

def duplicateChain(*args):

    global chainMenu
    global jointCount
    global ogChain
    global cosoLoc
    global side
    global selectChain
    
    ogRootchain = cmds.ls(sl = True, type = "joint")[0]        
    ogChain = cmds.listRelatives(ogRootchain, ad = True, type = "joint")
    ogChain.append(ogRootchain)
    ogChain.reverse()
    side = ogRootchain[0:2]

    #how many joints to select?
    """ testing on selecting the entire chain
    lengthSelection = cmds.ls(sl=1)
    for x in enumerate(lengthSelection):
        jointCount += 1
    """ 
    selectChain = cmds.optionMenu("chainMenu", q=1, v=1)
    if selectChain == "Leg": 
        jointCount = 5
    else: 
        jointCount = 3
    #suffix for the new chains
    newJointList = ["_ik", "_fk"]
    for newJoint in newJointList:
        for i in range(jointCount):
            newJointName = ogChain[i] + newJoint

            #create a joint, copy their position and freeze transform
            cmds.joint(n = newJointName)
            cmds.matchTransform(newJointName, ogChain[i])
            cmds.makeIdentity(newJointName, a = 1, t = 0, r = 1, s = 0)
        
        #deselect to make the two different hierarchies
        cmds.select(cl = 1)

    cmds.parent((ogChain[0] + "_ik"), world = True)
    #cmds.parent((ogChain[0] + "_fk"), world = True)
    cmds.setAttr(ogChain[0] + "_ik.visibility", 0)
    cmds.setAttr(ogChain[0] + "_fk.visibility", 0)

    # Create a locator used for switching IK/FK mode
    cosoLoc = cmds.spaceLocator(n=side + selectChain + "_ikfk_Switch")
    cosoLocGrp = cmds.group(em=1, n=cosoLoc[0] + "_grp")
    cmds.color(cosoLoc, rgb=(255, 255, 0))
    cmds.delete(cmds.pointConstraint(cosoLoc, cosoLocGrp))
    cmds.parent(cosoLoc, cosoLocGrp)
    #cmds.delete(cmds.parentConstraint(ogChain[1], ogChain[2], cosoLoc))
    cmds.addAttr(cosoLoc, ln="FKIK_Mode", at="short", min=0, max=1, k=1, r=1)
    cmds.move(0,0,-11, cosoLocGrp, r=1)
    
    axis = ["X", "Y", "Z"]
    for coord in axis:
        cmds.setAttr(cosoLoc[0] + ".translate" + coord, k=0, l=1)
        cmds.setAttr(cosoLoc[0] + ".rotate" + coord, k=0, l=1)
        cmds.setAttr(cosoLoc[0] + ".scale" + coord, k=0, l=1)
    
    cmds.setAttr(cosoLoc[0] + ".visibility", k=0, l=1)

def blendNodeFunc(*args):
    
    duplicateChain(*args)
    #create some blendColors node with the same name of the joint
    for x in range(jointCount):

        blendColorsNode = cmds.createNode("blendColors", n = ogChain[x] + "_blend" )

        # connect FK and IK chains into blendColors channels and then connect the output to the original joint chain
        cmds.connectAttr((ogChain[x] + "_ik.rotate"), blendColorsNode + ".color1")
        cmds.connectAttr((ogChain[x] + "_fk.rotate"), blendColorsNode + ".color2")
        cmds.connectAttr((blendColorsNode + ".output"), (ogChain[x] + ".rotate" ))
        cmds.connectAttr(cosoLoc[0]+".FKIK_Mode", blendColorsNode + ".blender")

    fkControllerCreator()


def constraintFunc(*args):

    duplicateChain(*args)

    #create some blendColors node with the same name of the joint
    for x in range(jointCount):

        #blendColorsNode = cmds.createNode("blendColors", n = ogChain[x] + "_blend" )
        # connect FK and IK chains into blendColors channels and then connect the output to the original joint chain
        cmds.orientConstraint((ogChain[x] + "_ik"), ogChain[x])
        cmds.orientConstraint((ogChain[x] + "_fk"), ogChain[x])

    fkControllerCreator()

    

def fkControllerCreator():
    #create controllers and group offsets
    #change rotation, color
    for y in range(jointCount):
        anim_group = cmds.group(em=1, n=ogChain[y] + "_anim_grp")
        fk_controller = cmds.circle(n=ogChain[y] + "_anim", r=7)[0]
        cmds.matchTransform(anim_group, ogChain[y])
        cmds.delete(cmds.parentConstraint(ogChain[y], fk_controller))
        cmds.parent(fk_controller, anim_group)
        cmds.rotate(0, 90, 0, fk_controller)
        cmds.makeIdentity(fk_controller, a = 1, t = 1, r = 1, s = 1)
        cmds.delete(fk_controller, ch = 1)
        cmds
        if side == "l_": 
            cmds.color(fk_controller, rgb=(0, 0, 255))
        else:
            cmds.color(fk_controller, rgb=(255, 0, 0))
    
    # Create ordered hierarchy
    for x in reversed(range(jointCount)):
        if x == 0:
            continue
        cmds.parent(ogChain[x] + "_anim_grp", ogChain[x-1] + "_anim" )

    # Orient Constraint _anim controllers with _fk hierarchy
    for x in range(jointCount):
        cmds.orientConstraint(ogChain[x] + "_anim", ogChain[x] + "_fk")
        # If leg chain is selected delete toe controller, else not
        if selectChain == "Leg":
            if x == (jointCount-1):
                cmds.delete(ogChain[jointCount-1] + "_anim_grp")
        else:
            pass


def showUI():
    
    global chainMenu
    
    if cmds.window("switchModeUI", ex = 1): cmds.deleteUI("switchModeUI")
    myWin = cmds.window("switchModeUI", t="IKFK Builder", w=300, h=300, s=1)
    #mainLayout = cmds.rowColumnLayout(nc=3)
    mainLayout = cmds.formLayout(nd=50)
    
    chainMenu = cmds.optionMenu("chainMenu", l="Which chain?")
    cmds.menuItem(l="Leg")
    cmds.menuItem(l="Arm")
    
    modeSwitcherText = cmds.text(l="Select IKFK switcher", al="left")
    #cmds.textField()
    #cmds.button(l="<<<")

    scaleControllerField = cmds.textField(en=10)
    
    separator01 = cmds.separator(h=5)

    execButton = cmds.button(l="blendColors Mode", c=blendNodeFunc)
    parentButton = cmds.button(l="Constraint Mode", c=constraintFunc)
    
    cmds.formLayout(mainLayout, e=1,
                    attachForm = [
                        (chainMenu, "left", 8), (chainMenu, "top", 5),
                        (separator01, "left", 1), (separator01, "right", 2),
                        #--------------------
                        (scaleControllerField, "right", 5), (scaleControllerField, "left", 150),
                        
                        #--------------------
                        (execButton, "bottom", 5), (execButton, "left", 5), (execButton, "right", 5),
                        (parentButton, "bottom", 5), (parentButton, "left", 5), (parentButton, "right", 5)
                    ],
                    attachControl = [(separator01, "top", 5, chainMenu),
                                     (modeSwitcherText, "top", 5, separator01),
                                     (scaleControllerField, "top", 5, separator01),
                    
                    ],

                    attachPosition = [(execButton, "left", 0, 26),
                                      (parentButton, "right", 0, 24)

                    ]
    
    
    )
    
    cmds.showWindow(myWin)
    
showUI()