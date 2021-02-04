import maya.cmds as cmds
from ctrlUI_lib import createHandCtrl

def duplicateHandChain(*args):

    global completeHierarchy

    rootSel = cmds.ls(sl = True, type = "joint")[0]
    completeHierarchy = cmds.listRelatives(rootSel, ad = True, type = "joint")
    completeHierarchy.append(rootSel)
    completeHierarchy.reverse()
    jointSide = rootSel[0:2]
    
    controllerColor = None
    if jointSide == "l_": controllerColor = rgb=(0, 0, 255)
    elif jointSide == "r_": controllerColor = rgb=(255, 0, 0)

    handJointCount = len(completeHierarchy)

    fingerChainLength = cmds.intField(fingersCountField_UI, q=1, v=1) #number of joints in a single finger
    supportJointCheckbox = cmds.checkBox(fingersCheckBox_UI, q=1, v=0) 

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
        
    attributeController = createHandCtrl(nome=completeHierarchy[0] + "_fingers_ctrl_anim")
    attributeControllerGrp = cmds.group(em=1, n=attributeController + "_grp")
    cmds.parent(attributeController, attributeControllerGrp)
    cmds.delete(cmds.pointConstraint(completeHierarchy[0], attributeControllerGrp))

    # order the _RIG hierarchy with locators
    if supportJointCheckbox == 1:
        hierarchyOrder = 2 # if supportJoint exists, start the count from 2
        attributeCount = 1 + fingerChainLength
        fingerBoneCount = 2
    else:
        hierarchyOrder = 1 # if supportJoint exists, start the count from 1
        attributeCount = fingerChainLength
        fingerBoneCount = 1

    xyz = ["X", "Y", "Z"]

    # Create attributes
    cmds.addAttr(attributeController, ln = "Fingers_Shorcuts", k = 1, r = 1, s = 1, at = "enum", en = "------")
    cmds.addAttr(attributeController, ln = "Fist", k = 1, r = 1, s = 1, at = "float")
    cmds.addAttr(attributeController, ln = "Spread", k = 1, r = 1, s = 1, at = "float")
    
    hierarchyOrder += fingerChainLength
    # Hierarchy printed is in a top-down hierarchy so it's important parent all under hand
    for x in range(handJointCount):
        
        attributeName = syntaxFix(jointSide, x)
        if x == 1: cmds.addAttr(attributeController, ln=attributeName, k=1, s=1, r=1, at="enum", enumName = "------" )
        
        if x == hierarchyOrder:  #compares the index number to support_fingers joint 
            if supportJointCheckbox == 1:
    
                cmds.parent(completeHierarchy[x] + "_rig", completeHierarchy[1] + "_rig")
                cmds.parent(completeHierarchy[x] + "_anim_grp", completeHierarchy[1] + "_LOC")
                
                cmds.addAttr(attributeController, ln=attributeName, k=1, s=1, r=1, at="enum", enumName = "------" )
                
                hierarchyOrder += fingerChainLength

                if hierarchyOrder == handJointCount:
                    cmds.parent(completeHierarchy[x] + "_rig", completeHierarchy[0] + "_rig")
                    cmds.parent(completeHierarchy[x] + "_anim_grp", completeHierarchy[0] + "_anim_grp")
                    
            else:
                cmds.addAttr(attributeController, ln=attributeName, k=1, s=1, r=1, at="enum", enumName = "------" )
                cmds.parent(completeHierarchy[x] + "_rig", completeHierarchy[0] + "_rig")
                cmds.parent(completeHierarchy[x] + "_anim_grp", completeHierarchy[0] + "_anim_grp")
                
                # Skin hand root joint
                if x == 0:
                    continue
                hierarchyOrder += fingerChainLength
        
        # create connections between _rig hierachy and locators
        
        # Skip 0 index because hand root joint it's not important into connections and orient constraints.
        if x == 0:
            continue 
        cmds.connectAttr(completeHierarchy[x] + "_rig.translate", completeHierarchy[x] + ".translate") 
        cmds.connectAttr(completeHierarchy[x] + "_rig.rotate", completeHierarchy[x] + ".rotate")
        cmds.orientConstraint(completeHierarchy[x] + "_LOC", completeHierarchy[x] + "_rig")
        
        # Create attributes
        
        # Skip supportJoint attribute
        if supportJointCheckbox == 1:
            if x == 1:
                continue
        
        for coord in xyz:
            if x == attributeCount:
                continue
            cmds.addAttr(attributeController, ln=(attributeName + coord), k=1, s=1, r=1)
            cmds.connectAttr(attributeController + "." + attributeName + coord, completeHierarchy[x] + "_LOC.rotate" + coord)
        
        if x == attributeCount:
            attributeCount += fingerChainLength

    global startik
    fingersGRP = cmds.group(em=1, n=jointSide + "fingers_grp")

    for x in range(handJointCount):
        # Start joint
        # fingerBoneCount is useful to understand the first finger bone for each finger
        if x == fingerBoneCount:
            startik = cmds.joint(n=completeHierarchy[x] + "_ik_start")
            cmds.delete(cmds.parentConstraint(completeHierarchy[x], startik))
            cmds.parent(startik, w=1)
        # end joint
        # fingerBoneCount + (fingerChainLength-1) is useful to understand the last finger bone for each finger
        if x == fingerBoneCount + (fingerChainLength-1):
            endik = cmds.joint(n=completeHierarchy[x] + "_ik_end")
            cmds.delete(cmds.parentConstraint(completeHierarchy[x], endik))
            cmds.parent(endik, w=1)
            cmds.parent(endik, startik)
            fingerikHandle = cmds.ikHandle(sj=startik, ee=endik, sol="ikSCsolver", n=completeHierarchy[fingerBoneCount] + "_ikHandle")[0]
            cmds.parent(fingerikHandle, fingersGRP)
            cmds.parent(completeHierarchy[fingerBoneCount] + "_anim_grp", completeHierarchy[fingerBoneCount] + "_ik_start")
            cmds.parent(completeHierarchy[fingerBoneCount] + "_ik_start", completeHierarchy[0] + "_rig")
            fingerBoneCount += fingerChainLength

    # Delete hand root joint
    cmds.delete(completeHierarchy[0] + "_anim_grp")

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
        cmds.color(attributeController, rgb=controllerColor)
    else:
        cmds.rotate(0,0,30,attributeControllerGrp, r=1)
        cmds.move(-6,0,0, attributeControllerGrp, r=1)
        cmds.color(attributeController, rgb=controllerColor)

    cmds.parentConstraint(completeHierarchy[0], attributeControllerGrp, mo=1)
            
    cmds.parent((completeHierarchy[0] + "_rig"), world = True)
 
    cmds.select(attributeController)


def syntaxFix(jointSide, count):
    if jointSide in completeHierarchy[count]:
        attributeName = completeHierarchy[count].replace(jointSide,"")
        return attributeName

def showUI():
    global fingersCountField_UI
    global fingersCheckBox_UI
    #global axisMenu_UI

    # Close the previous window
    if cmds.window("HandUI", ex = 1): cmds.deleteUI("HandUI")
    
    myWin = cmds.window("HandUI", title="Hand script")
    mainLayout = cmds.formLayout(nd = 100)

    # Input field for finger length
    txtFingersChain = cmds.text("Joint per finger")
    fingersCountField_UI = cmds.intField(minValue=3, w = 20)
    
    # Checkbox 
    fingersCheckBox_UI = cmds.checkBox(label = "Support joint?", value = False)

    # create an optionMenu for fingers bending 
    """axisMenu_UI = cmds.optionMenu("axisMenu_UI", l = "Bending Axis") 
    cmds.menuItem(l="X")
    cmds.menuItem(l="Y")
    cmds.menuItem(l="Z")"""
    
    # Separators
    separator01 = cmds.separator(h=5)
    #separator02 = cmds.separator(h=5)
    
    # Button to execute
    execButton = cmds.button(label="Duplicate hand chain", command=duplicateHandChain)
  
    
    #formlayout test
    cmds.formLayout(mainLayout, e=1,
                    attachForm = [(txtFingersChain, "top", 8), (txtFingersChain, "left", 5),
                                  (fingersCountField_UI, "top", 6), (fingersCountField_UI, "right", 105), (fingersCountField_UI, "left", 90),
                                  (fingersCheckBox_UI, "top", 8), (fingersCheckBox_UI, "right", 40),
                                  (separator01, "left", 5), (separator01, "right", 5), 
                                  #(separator02, "left", 5), (separator02, "right", 5), 
                                  #---------------------
                                  #(axisMenu_UI, "left", 10),
                                  #----------------------
                                  (execButton, "bottom", 5), (execButton, "right", 5), (execButton, "left", 5),
                                  ],

                    attachControl = [(fingersCheckBox_UI, "left", 5, fingersCountField_UI),
                                     (separator01, "top", 5, fingersCountField_UI),
                                     (separator01, "top", 10, fingersCheckBox_UI),
                                     #(axisMenu_UI, "top", 5, separator01),
                                     #(separator02, "top", 5, axisMenu_UI),
                                    ])

    cmds.showWindow(myWin)

showUI()