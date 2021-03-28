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