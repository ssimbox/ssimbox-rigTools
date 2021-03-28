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