#include "filenames.h"
#include "SM64DS_2.h"

// Load OV0 IDs from custom filename list instead of normal overlay. DO NOT MOVE THIS FUNCTION, IT HAS TO BE DEFINED FIRST IN THE OVERLAY!!!
void loadFiles()
{
    uint32_t uVar2 = FUN_0201a9ec(&DAT_0209d574);
    int numFiles = sizeof(filenameList) / sizeof(filenameList[0]);
    FUN_02018a58(numFiles);
    void* thr = thread;
    uint32_t pri = OS_GetThreadPriority(thread);
    OS_SetThreadPriority(thr, 0x1f);
    for (int i = 0; i < numFiles; i++)
    {
        uint16_t fileId = FUN_020189f0(filenameList[i]);
        if (fileId)
        {
            FUN_02018a40(i, fileId);
        }
    }
    OS_SetThreadPriority(thr, pri);
    FUN_0201a9fc(&DAT_0209d574);
    FUN_0201a96c(&DAT_0209d574, uVar2);
}

// Empty static initializer.
void init()
{
}