import maya.cmds as cmds
from ctrlUI_lib import createHandCtrl

def duplicateHandChain(*args):

    global fingersCountField
    global fingersCheckBox
    global axisMenu

    rootSel = cmds.ls(sl = True)[0]
    completeHierarchy = cmds.listRelatives(rootSel, ad = True)
    completeHierarchy.append(rootSel)
    completeHierarchy.reverse()
    jointSide = rootSel[0:2]
    if jointSide == "l_": controllerColor = rgb=(0, 0, 255)
    elif jointSide == "r_": controllerColor = rgb=(255, 0, 0)

    handJointCount = len(completeHierarchy)

    fingerChainLength = cmds.intField(fingersCountField, q=1, v=1) #number of joints in a single finger
    supportJointCheckbox = cmds.checkBox(fingersCheckBox, q=1, value = True) 

    newListName = ["_rig"]
    handLocatorsName = ["_LOC"]

    # Create top-down hierarchies

    # Create _RIG hierarchy
    for name in newListName:
        for newJoint in range(handJointCount):
            newChain = completeHierarchy[newJoint] + name
            cmds.joint(n = newChain, radius = 1)
            cmds.matchTransform(newChain, completeHierarchy[newJoint])
            cmds.makeIdentity(newChain, a = 1, t = 0, r = 1, s = 0)

    # Create locators to rotate fingers and freeze transform
    for nameLOC in handLocatorsName:
        for newLOC in range(handJointCount):
            handLocators = completeHierarchy[newLOC] + nameLOC
            cmds.spaceLocator(n = handLocators)
            cmds.matchTransform(handLocators, completeHierarchy[newLOC])
            cmds.makeIdentity(handLocators, a = 1, t = 0, r = 0, s = 0)
            cmds.setAttr(handLocators + ".scale", 0.1, 0.1, 0.1)


    # Create group offsets for locators and parent it
    for x in range(handJointCount):
        anim_group = cmds.group(empty=True, name=completeHierarchy[x] + "_anim_grp")
        driver_group = cmds.group(empty=True, name=completeHierarchy[x] + "_driver_grp")
        cmds.matchTransform(anim_group, completeHierarchy[x])
        cmds.matchTransform(driver_group, completeHierarchy[x])
        cmds.parent(driver_group, anim_group)
        cmds.parent(completeHierarchy[x] + "_LOC", driver_group)

    # Order locators & groups hierarchy like in top-down style
    for x in reversed(range(handJointCount)): 

        cmds.parent(completeHierarchy[x] + "_anim_grp", completeHierarchy[x-1] + "_LOC")
        # Break the operation on 1 because if hits 0 it'll search for '_fingers0' going to fuck up everything
        if x == 1:
            cmds.parent(completeHierarchy[1] + "_anim_grp", completeHierarchy[0] + "_anim_grp")
            cmds.delete(completeHierarchy[0] + "_driver_grp")
            break
        

    # order the _RIG hierarchy with locators
    if supportJointCheckbox == 1:
        hierarchyOrder = 2 # if supportJoint exists, start the count from 2
    else:
        hierarchyOrder = 1 # if supportJoint exists, start the count from 1
    hierarchyOrder += fingerChainLength 

    # Hierarchy printed is in a top-down hierarchy so it's important parent all under hand
    for x in range(handJointCount):
        if x == hierarchyOrder:  #compares the index number to support_fingers joint 
            if supportJointCheckbox == 1:
                cmds.parent(completeHierarchy[x] + "_rig", completeHierarchy[1] + "_rig")
                cmds.parent(completeHierarchy[x] + "_anim_grp", completeHierarchy[1] + "_LOC")
                hierarchyOrder += fingerChainLength

                if hierarchyOrder == handJointCount:
                    cmds.parent(completeHierarchy[x] + "_rig", completeHierarchy[0] + "_rig")
                    cmds.parent(completeHierarchy[x] + "_anim_grp", completeHierarchy[0] + "_anim_grp")
                    
            else:
    
                cmds.parent(completeHierarchy[x] + "_rig", completeHierarchy[0] + "_rig")
                cmds.parent(completeHierarchy[x] + "_anim_grp", completeHierarchy[0] + "_anim_grp")
                if x == 0:
                    continue
                hierarchyOrder += fingerChainLength
        
        # create connections between _rig hierachy and locators
        if x == 0:
            continue 
        # Skip 0 index because hand root joint it's not important into connections and orient constraints.
        # ONLY FINGERS  
        cmds.connectAttr(completeHierarchy[x] + "_rig.translate", completeHierarchy[x] + ".translate") 
        cmds.connectAttr(completeHierarchy[x] + "_rig.rotate", completeHierarchy[x] + ".rotate")
        cmds.orientConstraint(completeHierarchy[x] + "_LOC", completeHierarchy[x] + "_rig")
            
    cmds.parent((completeHierarchy[0] + "_rig"), world = True)
    #cmds.rename(completeHierarchy[0] + "_anim_grp", jointSide + "fingers_grp")
    
    # -----------------------------------------------------
    # Create attribute on controller
    
    xyz = ["X", "Y", "Z"]
    fingers = []
    numbers = []
    
    # Create attributes based on the length of the single fingers chain. Skip 0
    for i in range(fingerChainLength):
        if i == 0:
            continue
        numbers.append(i) 

    thumbASD = cmds.checkBox(thumbCheckBox_UI, q=1, v=1)

    if thumbASD == 1:
        fingers.insert(0, "thumb")
    
    if cmds.radioButton(rd3, q=1, sl=1):
        fingers.append("index")
        fingers.append("mid")
        if thumbASD == 0: fingers.append("ring")
    if cmds.radioButton(rd4, q=1, sl=1):
        fingers.append("index")
        fingers.append("mid")
        fingers.append("ring")
        if thumbASD == 0: fingers.append("pinkie")
    """
    if cmds.radioButton(rd5, q=1, sl=1):
        fingers.append("index")
        fingers.append("mid")
        fingers.append("ring")
        fingers.append("pinkie")
    """
    print (fingers)
    
    # parallelepipedo tipo piramide
    attributeController = createHandCtrl(nome=jointSide + "fingers_controller_anim")

    attributeControllerGrp = cmds.group(em=1, n=attributeController + "_grp")
    cmds.parent(attributeController, attributeControllerGrp)
    cmds.delete(cmds.pointConstraint(completeHierarchy[0], attributeControllerGrp))
    #cmds.delete(cmds.pointConstraint(completeHierarchy[0], attributeController))
    #cmds.rotate(0,0,-30,attributeControllerGrp, r=1)
    cmds.color(attributeController, rgb=controllerColor)
    
    # Setup controller attributes and space
    for coord in xyz:
        cmds.setAttr(attributeController + ".translate" + coord, k=0, l=1)
        cmds.setAttr(attributeController + ".rotate" + coord, k=0, l=1)
        cmds.setAttr(attributeController + ".scale" + coord, k=0, l=1)
        cmds.setAttr(attributeController + ".visibility", k=0, l=1)
        cmds.scale(0.5,0.5,0.5, attributeControllerGrp)
    
    # Set controller spacing based on chain side
    if jointSide == "l_":
        cmds.rotate(0,0,-30,attributeControllerGrp, r=1)
        cmds.move(6,0,0, attributeControllerGrp, r=1)
    else:
        cmds.rotate(0,0,30,attributeControllerGrp, r=1)
        cmds.move(-6,0,0, attributeControllerGrp, r=1)

    cmds.parentConstraint(completeHierarchy[0], attributeControllerGrp, mo=1)

    # Create attributes
    cmds.addAttr(attributeController, ln = "Fingers_Shorcuts", k = 1, r = 1, s = 1, at = "enum", en = "------")
    cmds.addAttr(attributeController, ln = "Fist", k = 1, r = 1, s = 1, at = "float")
    cmds.addAttr(attributeController, ln = "Spread", k = 1, r = 1, s = 1, at = "float")
    
    for singleFinger in fingers:

        cmds.addAttr(attributeController, longName = singleFinger, k=True, readable = True, 
                        storable = True, attributeType = "enum", enumName = "------")
        cmds.setAttr(attributeController + "." + singleFinger, k=False, channelBox = 1)
        for n in numbers:
            for coord in xyz: # Three ctrlAnims only for testing hehehehe
                ctrlAnims =  jointSide + singleFinger + str(n) + "_LOC.rotate"
                allNewAttr = singleFinger + str(n) + coord
                
                cmds.addAttr(attributeController, longName = allNewAttr, hidden = False, k = True, r = True, s = True)
                cmds.connectAttr(( attributeController + "." + allNewAttr), (ctrlAnims + coord ))

    selectAxis = cmds.optionMenu("axisMenu", q = 1, v = 1) 

    # Delete some attributes based on the bending axis
    for removeFinger in fingers:
        for removeNumber in numbers[1:]:

            if selectAxis == "X":
                indexFirstAxis = 1
                indexSecondAxis = 2
            elif selectAxis == "Y":
                indexFirstAxis = 0
                indexSecondAxis = 2
            elif selectAxis == "Z":
                indexFirstAxis = 0
                indexSecondAxis = 1 
            
            deleteFirstAxis = removeFinger + str(removeNumber) + xyz[indexFirstAxis]
            deleteSecondAxis = removeFinger + str(removeNumber) + xyz[indexSecondAxis]
            
            cmds.deleteAttr(attributeController, attribute = deleteFirstAxis) 
            cmds.deleteAttr(attributeController, attribute = deleteSecondAxis)
    
    cmds.select(attributeController)

def showUI():
    global fingersCountField
    global fingersCheckBox
    global axisMenu
    global rd3, rd4, rd5, rd6
    global thumbCheckBox_UI

    # Close the previous window
    if cmds.window("HandUI", ex = 1): cmds.deleteUI("HandUI")
    
    myWin = cmds.window("HandUI", title="Hand script")
    mainLayout = cmds.formLayout(nd = 100)

    # Input field for finger length
    txtFingersChain = cmds.text("Joint per finger")
    fingersCountField = cmds.intField(minValue=4, w = 20)
    
    # Checkbox 
    fingersCheckBox = cmds.checkBox(label = "Support joint?", value = False)

    # create an optionMenu for fingers bending 
    axisMenu = cmds.optionMenu("axisMenu", l = "Bending Axis") 
    cmds.menuItem(l="X")
    cmds.menuItem(l="Y")
    cmds.menuItem(l="Z")
    
    # Separators
    separator01 = cmds.separator(h=5)
    separator02 = cmds.separator(h=5)
    
    # Radiobutton
    fingerNumber = cmds.radioCollection()
    rd3 = cmds.radioButton(label='Three')
    rd4 = cmds.radioButton(label='Four')
    rd5 = cmds.radioButton(label='Five', sl=1)
    rd6 = cmds.radioButton(label='Six')

    thumbCheckBox_UI = cmds.checkBox("thumb?",v=0)
    
    # Button to execute
    execButton = cmds.button(label="Duplicate hand chain", command=duplicateHandChain)
  
    
    #formlayout test
    cmds.formLayout(mainLayout, e=1,
                    attachForm = [(txtFingersChain, "top", 8), (txtFingersChain, "left", 5),
                                  (fingersCountField, "top", 6), (fingersCountField, "right", 105), (fingersCountField, "left", 90),
                                  (fingersCheckBox, "top", 8), (fingersCheckBox, "right", 40),
                                  (separator01, "left", 5), (separator01, "right", 5), 
                                  (separator02, "left", 5), (separator02, "right", 5), 
                                  #---------------------
                                  (axisMenu, "left", 10),
                                  (rd3, "left", 10),
                                  (rd4, "left", 10),
                                  (rd5, "left", 10),
                                  (rd6, "left", 10),
                                  #----------------------
                                  (execButton, "bottom", 5), (execButton, "right", 5), (execButton, "left", 5),
                                  ],

                    attachControl = [(fingersCheckBox, "left", 5, fingersCountField),
                                     (separator01, "top", 5, fingersCountField),
                                     (separator01, "top", 10, fingersCheckBox),
                                     (axisMenu, "top", 5, separator01),
                                     (separator02, "top", 5, axisMenu),
                                     (rd3, "top", 5, separator02),
                                     (rd4, "top", 5, separator02), (rd4, "left", 5, rd3),
                                     (rd5, "top", 5, separator02), (rd5, "left", 5, rd4),
                                     (rd6, "top", 5, separator02), (rd6, "left", 5, rd5),
                                     (thumbCheckBox_UI, "left", 10, rd6), (thumbCheckBox_UI, "top", 5, separator02),
                                    ]
                                    )

    cmds.showWindow(myWin)

showUI()