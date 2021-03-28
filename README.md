# ssimbox-rigTools
Welcome to my repo, first in my life.

Here I'm going to upload scripts I develop in my free time. I'm a character rigger and I found very useful write my own scripts. 

Actually I developed two simple scripts
* IKFK-Builder - Tool useful in building linear IKFK chain. I use it when I need to rig legs and arms
* Autohand - Hand maker. Make constraints, controller and attributes on it. Save a lot of tedious work
* Game Hierarchy Maker - I found necessary use a hiearchy to export in Unity so this tool helps you in make new joints and constraint rapidly 


I'm currently working on controllers and relationships maker of my own rigs and I would like to share my entire work, free for all.
Actually I developed a simple IKFK-builder for legs and arms and an auto hand maker (I really hate make fingers rigs, really tedious)

Actually there is a simple rule to remember using my tools **naming convention**. 
I use this type of joint naming: *side_jointName* ---> *l_upperleg* or *r_knee*. Suffixes are ok but I need this kind of prefix.

This is just a start, I want to build always better tools to help my own works and, hopefully, speed up yours.
These things is what I achieved in one full month of study, I'm totally new to coding, there's much more to do.
Any suggestion will be appreciated and, if you want to contribute feel free, I just want some of this in Maya world :)

# IKFK-Builder

![Alt Text](https://media.giphy.com/media/9oNiWOptNcUAJlf9cG/giphy.gif)
## Features

Oh well, you know...

* Support arm and leg chains.
    * Arm = 3 joint length
    * Leg = 5 joint length
* Create an _ik chain and _fk chain using, by your choice, blendColors node connections or orientConstraint + Set Driven Key
* Create fk controllers and ik-handles for legs and arms

## To-Do list

Lots of stuff

- [ ] Better foot attributes
- [x] Clavicle support
- [ ] Tweaks about pole vectors
- [ ] More complex leg and arm chains
- [ ] Add Squash and Stretch option
- [ ] Color choice (by your own)
- [ ] Better controllers
- [ ] Auto hierarchy in outliner

## How to install
Save *IKFK_Builder* in your maya scripts folder with *ctrlUI_lib*
Then, write and save this lines into your shelf

```
import IKFK_Builder
IKFK_Builder.showUI()
```

# AutoHand
![Alt Text](https://media.giphy.com/media/NYyDRYhQClclSwf4Fh/giphy.gif)
## Features 

For now very simple stuff but it could be very useful to create an usable hand with fingers control.

- Various length fingers
- Fingers controller creation with attributes to control them

P.S. Another rule: if you use what I call _supportJoint_ (watch gif second shot) please use this hierarchy

- Hand
    - Thumb
    - SupportJoint
        - other fingers

## To-Do list

- [x] IK Hand - Actually it started all for this, to create automatically an IK Hand. This is my main goal
- [x] Various hand builds - My objective was to build the human hand (five fingers) but could be useful have three, four or six fingers.
- [ ] Change attribute order
- [ ] Delete some useless attributes

## How to install
Save *Auto_Hand* in your maya scripts folder
Then, write and save this lines into your shelf

```
import Auto_Hand
Auto_Hand.showUI()
```