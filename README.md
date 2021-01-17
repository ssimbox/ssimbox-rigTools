# sbx-autorig
Welcome to my repo, first in my life.

I'm currently working on controllers and relationships maker of my own rigs and I would like to share my entire work, free for all.
Actually I developed a simple IKFK-builder for legs and arms and an auto hand maker (I really hate make fingers rigs, really boriiiing)

This is just a start, I want to build always better tools to help my own works and, hopefully, speed up yours

Actually there a simple rule to remember using my tools **naming convention**. 
I use this type of joint naming: *side_jointName* ---> *l_upperleg* or *r_knee*
Suffixes are ok but I need a this kind of prefix.


# IKFK-Builder
## Features

Oh well, you know...simple stuff

* Support arm and leg chains.
    * Arm = 3 joint length
    * Leg = 5 joint length
* Create an _ik chain and _fk chain using, by your choice, blendColors node connections or orientConstraint + Set Driven Key
* Create fk controllers and ik-handles for legs and arms

## TODO list

Lots of stuff

* Clavicle support
* Tweak about pole vectors
* Complex leg and arm chain 
* Add Squash and Stretch option
* Color choice (by your own)
* Better controllers


# AutoHand
## Features 

* Duplicate hand chain
* Fingers controller creation with attributes to control them

## TODO list

* IK Hand - Actually it started all for this, to create automatically an IK Hand. This is my main goal
