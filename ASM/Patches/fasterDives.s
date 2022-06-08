@ By Pants64DS
@ Make diving 1.3 times faster
.hook(0x020DD1EC, 2)
nsub_020dd1ec:
    add   r0, r0, #0x1e000 @ = 2 * 0xf000
    b     0x020dd1f0

.hook(0x020DD1FC, 2)
nsub_020dd1fc:
    cmp   r0, #0x50000 @ = 2 * 0x28000
    movgt r0, #0x50000 @ = 2 * 0x28000
    b     0x020dd204