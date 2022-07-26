#include "SM64DS_2.h"
#include "../filenames/filenames.h"
#include "SilverCoin.h"

namespace {

	//Object IDs.
	enum ObjectIDs: short
	{
		GALAXY_SHRINKING_PLATFORM = 0x0200,
		SILVER_COIN,
		INVISIBLE_WALL,
		BERRY,
		YOSHI_RIDE,
		OBJECT_LIGHTING_MODIFIER,
		TWO_DEE_LEVEL,
		TWO_DEE_CAMERA_LIMITER,
		COLORED_GOOMBA_SMALL,
		COLORED_GOOMBA,
		COLORED_GOOMBA_LARGE,
		TOXIC_LEVEL,
		NOTEBLOCK,
		SHY_GUY,
		LAUNCH_STAR,
		KAMEK_SHOT,
		KAMEK, //210
		KAMELLA,
		SKYBOX_ROTATOR,
		FALLING_ICICLE,
		GRAVITY_MODIFIER,
		COLORED_GOOMBA_2_SMALL,
		COLORED_GOOMBA_2,
		COLORED_GOOMBA_2_LARGE,
		YOSHI_NPC,
		COLORED_PIPE,
		CHARACTER_BLOCK,
		TREE_SHADOW,
		SAVE_BLOCK,
		STAR_CHIP,
		DOOR_BLOCKER,
		COLORED_COIN,
		COLORED_TOAD_NPC, //220
		PEACH_NPC,
		BLUE_ICE_BLOCK,
		MEGA_BLOCK,
		CUTSCENE_LOADER,
		CUSTOM_BLOCK,
		TREASURE_CHEST,
		THWOMP,
		MAGMA_THWOMP,
		GIGA_THWOMP/*,
		TOX_BOX,
		PLAYER_TOX_BOX,
		TOX_BOX_FLOWER*/
	};

	//Modify the object and actor tables.
	void modTable(short int val, unsigned newFunc)
	{
		OBJ_TO_ACTOR_ID_TABLE[val] = val;
		ACTOR_SPAWN_TABLE[val] = newFunc;
	}

}

//Initialize the objects.
void init()
{

    //Silver coins.
	modTable(SILVER_COIN, (unsigned)&SilverCoin::spawnData);
	SilverCoin::modelFile.Construct(GetID("MOM/silverCoin.bmd"));

}