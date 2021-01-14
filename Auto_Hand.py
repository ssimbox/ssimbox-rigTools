import maya.cmds as cmds

def duplicateHandChain(*args):

    global fingersCountField
    global fingersCheckBox
    global axisMenu

    rootSel = cmds.ls(sl = True)[0]
    completeHierarchy = cmds.listRelatives(rootSel, ad = True)
    completeHierarchy.append(rootSel)
    completeHierarchy.reverse()
    jointSide = rootSel[0:2]

    handJointCount = len(completeHierarchy)
    #print("Chain length = ", handJointCount)

    fingerChainLength = cmds.intField(fingersCountField, q=1, v=1) #number of joints in a single finger
    supportJointCheckbox = cmds.checkBox(fingersCheckBox, q=1, value = True) 
    #attributeController = cmds.textField(controllerField, q = True, text=True)
    

    newListName = ["_rig"]
    handLocatorsName = ["_LOC"]

    #create top-down hierarchies

    #create _RIG hierarchy
    for name in newListName:
        for newJoint in range(handJointCount):
            newChain = completeHierarchy[newJoint] + name
            cmds.joint(n = newChain, radius = 1)
            cmds.matchTransform(newChain, completeHierarchy[newJoint])
            cmds.makeIdentity(newChain, a = 1, t = 0, r = 1, s = 0)

    # create locators to rotate fingers and freeze transform
    for nameLOC in handLocatorsName:
        for newLOC in range(handJointCount):
            handLocators = completeHierarchy[newLOC] + nameLOC
            cmds.spaceLocator(n = handLocators)
            cmds.matchTransform(handLocators, completeHierarchy[newLOC])
            cmds.makeIdentity(handLocators, a = 0, t = 0, r = 0, s = 0)
            cmds.setAttr(handLocators + ".scale", 0.1, 0.1, 0.1)
            
            #ikJointFingers = cmds.joint(n=str(completeHierarchy[newLOC]) + "_IK_start", radius = 0.1)


    # create group offsets for locators and parent it
    for x in range(handJointCount):
        anim_group = cmds.group(empty=True, name=completeHierarchy[x] + "_anim_grp")
        driver_group = cmds.group(empty=True, name=completeHierarchy[x] + "_driver_grp")
        cmds.matchTransform(anim_group, completeHierarchy[x])
        cmds.matchTransform(driver_group, completeHierarchy[x])
        cmds.parent(driver_group, anim_group)
        cmds.parent(completeHierarchy[x] + "_LOC", driver_group)
        

    # order locators & groups hierarchy like in top-down style
    
    for x in reversed(range(handJointCount)): 

        cmds.parent(completeHierarchy[x] + "_anim_grp", completeHierarchy[x-1] + "_LOC")
        #print (completeHierarchy[x], x)
        #break the operation on 1 because if hits 0 it'll search for '_fingers0' going to fuck up everything
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

    # hierarchy printed is in a top-down hierarchy so it's important parent all under hand

    for x in range(handJointCount):
        #print (x, hierarchyOrder)
        if x == hierarchyOrder:  #compares the index number to support_fingers joint 
            if supportJointCheckbox == 1:
                #print ("Check", supportJointCheckbox)
                cmds.parent((completeHierarchy[x] + "_rig"), (completeHierarchy[1] + "_rig"))
                cmds.parent(completeHierarchy[x] + "_anim_grp", completeHierarchy[1] + "_LOC")
                hierarchyOrder += fingerChainLength
                #cmds.joint(n=str(completeHierarchy[x]) + "_IK_start", radius = 0.1)
                
                if hierarchyOrder == handJointCount:
                    cmds.parent((completeHierarchy[x] + "_rig"), (completeHierarchy[0] + "_rig"))
                    cmds.parent(completeHierarchy[x] + "_anim_grp", completeHierarchy[0] + "_anim_grp")
                    
            else:
    
                cmds.parent((completeHierarchy[x] + "_rig"), (completeHierarchy[0] + "_rig"))
                cmds.parent(completeHierarchy[x] + "_anim_grp", completeHierarchy[0] + "_anim_grp")
                #cmds.joint(n="ciao", radius = 0.1)
                if x == 0:
                    continue
                hierarchyOrder += fingerChainLength
        
        # create connections between _rig hierachy and locators
        if x == 0:
            continue 
        # skip 0 index because hand joint it's not important into connections and orient constraints.
        # ONLY FINGERS  
        cmds.connectAttr((completeHierarchy[x] + "_rig.translate"), completeHierarchy[x] + ".translate") 
        cmds.connectAttr((completeHierarchy[x] + "_rig.rotate"), completeHierarchy[x] + ".rotate")
        cmds.orientConstraint((completeHierarchy[x] + "_LOC"), (completeHierarchy[x] + "_rig"))
            
    cmds.parent((completeHierarchy[0] + "_rig"), world = True)   
    
    # -----------------------------------------------------
    # create attribute on controller
    
    xyz = ["X", "Y", "Z"]
    fingers = ["thumb", "index", "mid", "ring", "pinkie"]
    numbers = []
    
    #create attributes based on the length of the single fingers chain
    for i in range(fingerChainLength):
        if i == 0:
            continue
        numbers.append(i) 
    

    attributeController = cmds.curve(d=1, p=[(61.39684755277148, 107.09833137762485, -7.9134744587261885),
                        (60.5014727013448, 104.69149073583574, -8.160753622601991),
                        (60.03541386899886, 104.04189931682629, -0.15053410167191128),
                        (58.365730593592026, 106.22898674786727, -0.07031874821935569),
                        (58.831789425937956, 106.87857816687672, -8.080538269149434),
                        (60.5014727013448, 104.69149073583574, -8.160753622601991),
                        (61.39684755277148, 107.09833137762485, -7.9134744587261885),
                        (58.831789425937956, 106.87857816687672, -8.080538269149434),
                        (58.365730593592026, 106.22898674786727, -0.07031874821935569),
                        (60.93078872042556, 106.44873995861535, 0.09674506220389012),
                        (60.03541386899886, 104.04189931682629, -0.15053410167191128),
                        (60.93078872042556, 106.44873995861535, 0.09674506220389012),
                        (61.39684755277148, 107.09833137762485, -7.9134744587261885)],
                            k=[0,1,2,3,4,5,6,7,8,9,10,11,12]
)


    cmds.addAttr(attributeController, ln = "Fingers_Shorcuts", k = 1, r = 1, s = 1, at = "enum", en = "------")
    cmds.addAttr(attributeController, ln = "Fist", k = 1, r = 1, s = 1, at = "float")
    cmds.addAttr(attributeController, ln = "Spread", k = 1, r = 1, s = 1, at = "float")
    
    for singleFinger in fingers:

        cmds.addAttr(attributeController, longName = singleFinger, keyable=True, readable = True, 
                        storable = True, attributeType = "enum", enumName = "------")
        cmds.setAttr(attributeController + "." + singleFinger, keyable = False, channelBox = 1)
        for n in numbers:
            for coord in xyz: #three ctrlAnims only for testing hehehehe
                #ctrlAnims =  jointSide + singleFinger + str(n) + "_noSupport_LOC.rotate"
                ctrlAnims =  jointSide + singleFinger + str(n) + "_LOC.rotate"
                #ctrlAnims =  jointSide + singleFinger + str(n) + "_fiveJNT_LOC.rotate"
                allNewAttr = singleFinger + str(n) + coord
                
                cmds.addAttr(attributeController, longName = allNewAttr, hidden = False, k = True, r = True, s = True)
                cmds.connectAttr(( attributeController + "." + allNewAttr), (ctrlAnims + coord ))

    # delete some attributes based on the bending axis
    selectAxis = cmds.optionMenu("axisMenu", q = 1, v = 1) 

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
    print (controllerField)

def controllerAttributes(*args):
    global controllerField

    nurbsSelection = cmds.ls(sl=1)
    #print nurbsSelection
    cmds.textField(controllerField, edit = 1, text = nurbsSelection[0])

def showUI():
    global fingersCountField
    global fingersCheckBox
    global axisMenu
    global controllerField

    # close the previous window
    if cmds.window("HandUI", ex = 1): cmds.deleteUI("HandUI")
    
    myWin = cmds.window("HandUI", title="Hand script")
    mainLayout = cmds.formLayout(nd = 100)
    #mainLayout = cmds.rowColumnLayout(nc=3)

    # Input field for finger length
    
    txtFingersChain = cmds.text("Joint per finger")
    fingersCountField = cmds.intField(minValue=3, w = 20)
    
    # Checkbox 
    fingersCheckBox = cmds.checkBox(label = "Support joint?", value = False)

    
    # Input field for attribute controller
    controllerText = cmds.text(l="Controller")
    controllerField = cmds.textField(en=0)
    controllerButton = cmds.button(label="<<<", w=55, h=22, c=controllerAttributes)

    # create an optionMenu for fingers bending 
    axisMenu = cmds.optionMenu("axisMenu", l = "Bending Axis") 
    cmds.menuItem(l="X")
    cmds.menuItem(l="Y")
    cmds.menuItem(l="Z")
    
    # Separat
    separator01 = cmds.separator(h=5)
    separator02 = cmds.separator(h=5)
    
    # Button to execute
    
    execButton = cmds.button(label="Duplicate hand chain", command=duplicateHandChain)
  
    
    #formlayout test
    cmds.formLayout(mainLayout, e=1,
                    attachForm = [(txtFingersChain, "top", 8),(txtFingersChain, "left", 5),
                                  (fingersCountField, "top", 6), (fingersCountField, "right", 115), (fingersCountField, "left", 90),
                                  (fingersCheckBox, "top", 8), (fingersCheckBox, "right", 5),
                                  (separator01, "left", 5), (separator01, "right", 5),
                                  #---------------------
                                  (separator02, "left", 5), (separator02, "right", 5),
                                  (controllerText, "left", 5),
                                  (controllerField, "right", 70), (controllerField, "left", 70),
                                  (controllerButton, "right", 5),
                                  (axisMenu, "left", 10),
                                  #----------------------
                                  (execButton, "bottom", 10), (execButton, "right", 5), (execButton, "left", 5),
                                  ],

                    attachControl = [(separator01, "top", 5, fingersCountField),
                                     (separator01, "top", 10, fingersCheckBox),
                                     (axisMenu, "top", 5, separator01),
                                     (separator02, "top", 5, axisMenu),
                                     (controllerField, "top", 5, separator02),
                                     (controllerButton, "top", 5, separator02),
                                     (controllerText, "top", 7, separator02)
                                    ],
                    
                    attachPosition = [(axisMenu, "left", 100, 0)
                                      
                                     ]
    
                    )
   
    cmds.showWindow(myWin)

showUI()