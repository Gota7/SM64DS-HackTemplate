#include "SM64DS_2.h"

// Overlay init.
bool init = false;

//Initialization code.
void Initialize()
{

	//Load the MOM overlay.
	LoadOverlay(false, 155);

}

//Hooks every frame.
safe(0x0200DA0C)
void hook_0200da0c()
{

	//Initialize if needed.
	if (!init) {
		Initialize();
		init = true;
	}

}