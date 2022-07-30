#include "SM64DS_2.h"
#include "../filenames/filenames.h"
#include "Berry.h"
#include "GalaxyShrinkingPlatform.h"
#include "SaveBlock.h"
#include "ShyGuy.h"
#include "SkyboxRotator.h"
#include "SilverCoin.h"
#include "StarChip.h"
#include "Thwomp.h"
#include "ToxicLevel.h"
#include "TreasureChest.h"
#include "TreeShadow.h"
#include "YoshiRide.h"

namespace {

	// Object IDs.
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

	// Modify the object and actor tables.
	void modTable(short int val, unsigned newFunc)
	{
		OBJ_TO_ACTOR_ID_TABLE[val] = val;
		ACTOR_SPAWN_TABLE[val] = newFunc;
	}

}

// Initialize the objects.
void init()
{

	// Galaxy platforms.
	modTable(GALAXY_SHRINKING_PLATFORM, (unsigned)&GalaxyShrinkingPlatform::spawnData);
	GalaxyShrinkingPlatform::modelFile.Construct(GetID("MOM/galaxyShrinkPlatform.bmd"));
    GalaxyShrinkingPlatform::clsnFile.Construct(GetID("MOM/galaxyShrinkPlatform.kcl"));
    GalaxyShrinkingPlatform::frameModelFile.Construct(GetID("MOM/galaxyShrinkPlatformFrame.bmd"));

    // Silver coins.
	modTable(SILVER_COIN, (unsigned)&SilverCoin::spawnData);
	SilverCoin::modelFile.Construct(GetID("MOM/silverCoin.bmd"));

	// Berries.
	modTable(BERRY, (unsigned)&Berry::spawnData);
	Berry::modelFile.Construct(GetID("MOM/berry.bmd"));
	Berry::stemFile.Construct(GetID("MOM/berryStem.bmd"));

	// Rideable yoshis.
	modTable(YOSHI_RIDE, (unsigned)&YoshiRide::spawnData);
	YoshiRide::ridingAnim.Construct(GetID("MOM/yoshiRide.bca"));

	// Toxic level.
	modTable(TOXIC_LEVEL, (unsigned)&ToxicLevel::spawnData);

	// Shy guys.
	modTable(SHY_GUY, (unsigned)&ShyGuy::spawnData);
	ShyGuy::modelFile.Construct(GetID("MOM/shyGuy.bmd"));
	ShyGuy::animFiles[0].Construct(GetID("MOM/shyGuyWait.bca"));
	ShyGuy::animFiles[1].Construct(GetID("MOM/shyGuyWalk.bca"));
	ShyGuy::animFiles[2].Construct(GetID("MOM/shyGuyRun.bca"));
	ShyGuy::animFiles[3].Construct(GetID("MOM/shyGuyFreeze.bca"));

	// Skybox rotator.
	modTable(SKYBOX_ROTATOR, (unsigned)&SkyboxRotator::spawnData);

	// Tree shadows.
	modTable(TREE_SHADOW, (unsigned)&TreeShadow::spawnData);
	TreeShadow::modelFile.Construct(GetID("MOM/characterBlockTransWario.bmd"));

	//Save Blocks.
	modTable(SAVE_BLOCK, (unsigned)&SaveBlock::spawnData);
	SaveBlock::modelFile.Construct(GetID("MOM/saveBlock.bmd"));
	SaveBlock::texSeqFile.Construct(GetID("MOM/saveBlock.btp"));
	SaveBlock::clsnFile.Construct(GetID("MOM/saveBlock.kcl"));

	// Star Chips.
	modTable(STAR_CHIP, (unsigned)&StarChip::spawnData);
	StarChip::modelFile.Construct(GetID("MOM/starChip.bmd"));

	// Treasure chest.
	modTable(TREASURE_CHEST, (unsigned)&TreasureChest::spawnData);
	TreasureChest::modelFile.Construct(GetID("MOM/t_box.bmd"));
	TreasureChest::animFiles[0].Construct(GetID("MOM/t_box_open.bca"));

	// Thwomp, Magma Thwomp and Giga Thwomp
	modTable(THWOMP, (unsigned)&Thwomp::spawnData);
	modTable(MAGMA_THWOMP, (unsigned)&Thwomp::spawnData);
	modTable(GIGA_THWOMP, (unsigned)&Thwomp::spawnData);
	Thwomp::modelFiles[0].Construct(GetID("MOM/thwomp.bmd"));
	Thwomp::modelFiles[1].Construct(GetID("MOM/thwompMagma.bmd"));
	Thwomp::modelFiles[2].Construct(GetID("MOM/thwompGiga.bmd"));
	Thwomp::texSeqFile.Construct(GetID("MOM/thwomp.btp"));
	Thwomp::clsnFile.Construct(GetID("MOM/thwomp.kcl"));

}