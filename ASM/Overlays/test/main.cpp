#include "SM64DS_2.h"

// Defined in the patches folder.
void ChangeGravity(uint16_t scale, bool isUp);

// Just test changing gravity.
void init()
{
    ChangeGravity(0x800, false);
    FALL_DAMAGE_SMALL = FALL_DAMAGE_BIG = 0x7FFFFFFF_f;
}