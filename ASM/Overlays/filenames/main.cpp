#include "filenames.h"

// Load OV0 IDs from custom filename list instead of normal overlay.
void init()
{
    /*
        Below is the code from OV0:

        OSThread *pOVar1;
        undefined4 uVar2;
        uint uVar3;
        int iVar4;
        int i;

        uVar2 = FUN_0201a9ec(&DAT_0209d574);
        FUN_02018a58(0x80a);
        pOVar1 = thread;
        uVar3 = OS_GetThreadPriority(thread);
        OS_SetThreadPriority(pOVar1,0x1f);
        i = 0;
        do {
            iVar4 = FUN_020189f0(nameTable[i]);
            if (iVar4 != 0) {
            FUN_02018a40(i);
            }
            i = i + 1;
        } while (i < 0x80a);
        OS_SetThreadPriority(pOVar1,uVar3);
        FUN_0201a9fc(&DAT_0209d574);
        FUN_0201a96c(&DAT_0209d574,uVar2);
        return;
    */
}