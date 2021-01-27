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
        
    attributeController = createHandCtrl(nome=jointSide + "fingers_controller_anim")
    attributeControllerGrp = cmds.group(em=1, n=attributeController + "_grp")
    cmds.parent(attributeController, attributeControllerGrp)
    cmds.delete(cmds.pointConstraint(completeHierarchy[0], attributeControllerGrp))

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
    
    # Create attributes
    cmds.addAttr(attributeController, ln = "Fingers_Shorcuts", k = 1, r = 1, s = 1, at = "enum", en = "------")
    cmds.addAttr(attributeController, ln = "Fist", k = 1, r = 1, s = 1, at = "float")
    cmds.addAttr(attributeController, ln = "Spread", k = 1, r = 1, s = 1, at = "float")

    selectAxis = cmds.optionMenu("axisMenu", q = 1, v = 1) 
    deleteVar = 0
    topAttribute = 1
    deleteVar += fingerChainLength
    for x in range(handJointCount):
        # Skip root hand joint
        if x == 0: 
            continue

        # Create "divider attribute" on the controller. 
        if x == topAttribute: 
            cmds.addAttr(attributeController, ln=completeHierarchy[x], k=1, s=1, r=1, at="enum", enumName = "------" )
            topAttribute += fingerChainLength
        
        # Delete last joint as attribute. Based on finger chain length. Usually I don't use it as transfom
        if x == deleteVar: 
            deleteVar += fingerChainLength
            continue

        # Create coords for every finger 
        for coord in ["X", "Y", "Z"]:
            cmds.addAttr(attributeController, ln=completeHierarchy[x] + coord, k=1, s=1, r=1)
            cmds.connectAttr(attributeController + "." + completeHierarchy[x] + coord, completeHierarchy[x] + "_LOC.rotate" + coord)
    
    deleteVar = 0
    deleteVar += fingerChainLength
    xyz = ["X", "Y", "Z"]
    for x in range(handJointCount):
        for coord in xyz:

            # Skip 0 index
            if x == 0:
                continue

            # Skip last joints based on finger chain length 
            if x == deleteVar:
                deleteVar += fingerChainLength
                continue


    # Setup controller attributes and space
    for coord in ["X", "Y", "Z"]:
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
            
    cmds.parent((completeHierarchy[0] + "_rig"), world = True)
 
    cmds.select(attributeController)

def showUI():
    global fingersCountField
    global fingersCheckBox
    global axisMenu

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
                                  #----------------------
                                  (execButton, "bottom", 5), (execButton, "right", 5), (execButton, "left", 5),
                                  ],

                    attachControl = [(fingersCheckBox, "left", 5, fingersCountField),
                                     (separator01, "top", 5, fingersCountField),
                                     (separator01, "top", 10, fingersCheckBox),
                                     (axisMenu, "top", 5, separator01),
                                     (separator02, "top", 5, axisMenu),
                                    ])

    cmds.showWindow(myWin)

showUI()