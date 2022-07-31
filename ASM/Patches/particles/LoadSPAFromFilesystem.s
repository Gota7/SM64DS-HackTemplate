@ these get called when loading a level
.hook(0x02022FF8)
nsub_02022ff8:
	push {r14}
	ldr r0, =0x80a			@ this is the ov0 ID of your SPA file
	bl 0x0201816c			@ LoadFile()
	ldr r1, =0x020230D8		@ this was used as a fixed offset to the embedded SPA file
	str r0, [r1]			@ now its used as a pointer to the SPA file
	pop {r14}
	b 0x02022ffc

.hook(0x0202300C)
nsub_0202300c:
	ldr r0, =0x020230D8
	ldr r0, [r0]
	b 0x02023010

.hook(0x02023018)
nsub_02023018:
	ldr r6, =0x020230D8
	ldr r6, [r6]
	b 0x0202301c

.hook(0x02023074)
nsub_02023074:
	ldr r0, =0x020230D8
	ldr r0, [r0]
	b 0x02023078

@ gets called when leaving a level
.hook(0x020231D0)
nsub_020231d0:
	ldr r1, =0x020230D8
	push {r0, r2-r8, r14}
	ldr r0, [r1]
	ldr r1, [r1]
	push {r1}
	bl 0x0203c1b4			@ Memory::Deallocate
	pop {r0-r8, r14}
	b 0x020231d4