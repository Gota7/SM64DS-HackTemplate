@ enables loading particle textures outside of the SPA file

.hook(0x0204A408)
nsub_0204a408:
	ldrb r2, [r10, #0x26]
	b 0x0204a40c

.hook(0x0204A420)
nsub_0204a420:
	ldrb r0, [r10, #0x27]
	b 0x0204a424

.hook(0x204A490)
nsub_0204a490:
	ldrb r2, [r10, #0x27]
	b 0x0204a494

.hook(0x0204A0F0)
nsub_0204a0f0:
	ldrb r0, [r10, #0x27]
	b 0x0204a0f4

.hook(0x0204A154)
nsub_0204a154:
	ldrb r0, [r10, #0x27]
	b 0x0204a158

.hook(0x0204A03C)
nsub_0204a03c:
	ldrb r0, [r10, #0x27]
	b 0x0204a040

.hook(0x0204A0B4)
nsub_0204a0b4:
	ldrb r0, [r10, #0x27]
	b 0x0204a0b8