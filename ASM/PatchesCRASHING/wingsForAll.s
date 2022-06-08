@ Originally by Gota7, ported by Pants64DS.
@ Spawn a feather instead of a Power Flower
.hook(0x020DD1EC, 6)
nsub_02149ab0_ov_66:
	mov	 r4, #0
	b    0x02149ac4

@ Don't despawn the feather even if the player isn't Mario
.hook(0x020DD1EC, 2)
nsub_020b2ed0_ov_02:
	b    0x020b2ed8

@ Give the player wings if the feather is collected
.hook(0x020DD1EC, 2)
nsub_020e03e4_ov_02:
	b    0x020e03e8