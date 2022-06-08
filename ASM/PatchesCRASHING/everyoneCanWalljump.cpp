// By Pants64DS.
#include "SM64DS_2.h"

extern "C" bool ShouldNotWallSlide(Player& player)
{
	static short angle = 0;

	if (player.param1 & 1 &&  // if the player is Luigi or Yoshi
		(unsigned)player.currState == Player::ST_WALL_JUMP &&
		AngleDiff(player.ang.y, angle) < 22.5_deg)
	{
		player.ang.y += 180_deg;

		return true;
	}

	angle = player.ang.y;

	return false;
}

rlnk(0x020C1DBC, 2)
asm_func static void replWallSlideCheck()
{
    asm(R"(
        mov     r0, r5
        b 		ShouldNotWallSlide
    )");
}