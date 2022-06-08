@ By Pants64DS
@ Make the player wall slide after long jumping into a wall
.hook(0x020C2098, 2)
nsub_020c2098_ov_02:
    bne 0x020c20f8
    b   0x020c209c