#include "SM64DS_2.h"

// Overlay init.
bool init = false;

//Initialization code.
void Initialize()
{

	// Load the test overlay.
	// LoadOverlay(false, 155);

	// Load the MOM overlay.
	LoadOverlay(false, 156);

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

	// Test for level select shortcut.
	if (INPUT_ARR[0].buttonsHeld & Input::Buttons::START && INPUT_ARR[0].buttonsHeld & Input::Buttons::SELECT)
	{
		LEVEL_SELECT = 2;
	}

}