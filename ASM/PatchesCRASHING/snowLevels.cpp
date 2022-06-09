#include "SM64DS_2.h"

// Add what levels you want to have snow here.
char snowLevels[] =
{
    1,
    10, // Cool cool mountain.
    19 // Snow man's land.
};

// Custom snow partical code by Gota7.
bool isSnow;
hook(0x0200E0E4)
void nsub_0200E0E4()
{
    isSnow = false;
    int numSnowLevels = sizeof(snowLevels) / sizeof(snowLevels[0]);
    for (int i = 0; i < numSnowLevels; i++)
    {
        if (LEVEL_ID == snowLevels[i])
        {
            isSnow = true;
            break;
        }
    }
    asm
    (
        "ldr r1, =isSnow\n\t"
        "b 0x0200e0f4\n\t"
    );
}