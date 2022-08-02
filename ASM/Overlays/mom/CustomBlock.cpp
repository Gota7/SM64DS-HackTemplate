#include "CustomBlock.h"

namespace
{
	FixedSizeCLPS_Block<1> clpsBlock =
	{
		{'C', 'L', 'P', 'S'},
		8,
		1,
		{
        	CLPS(0x00, 0, 0x3f, 0x0, 0x6, 0x00, 1, 0, 0, 0xff)
        }
	};

	const int NUM_ITEMS = 14;

	constexpr unsigned ItemActor[NUM_ITEMS] = {0x00B2, 0x00B3, 0x0114, 0x0115, 0x0159, 0x0132, 0x011D, 0x011A, 0x011A, 0x011A, 0x011A, 0x011A, 0x011A, 0x022C};
	constexpr unsigned ItemParam[NUM_ITEMS] = {0x0040, 0x0010, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0001, 0x0002, 0x0003, 0x0004, 0x0005, 0x0000};
}

SharedFilePtr CustomBlock::modelFiles[3];
SharedFilePtr CustomBlock::clsnFile;
SharedFilePtr CustomBlock::animFiles[2];

SpawnInfo CustomBlock::spawnData =
{
	[]() -> ActorBase* { return new CustomBlock; },
	0x0034,
	0x0100,
	0x00000002,
	0x00000000_f,
	0x005dc000_f,
	0x01000000_f,
	0x01000000_f
};

CustomBlock* CustomBlock::Spawn()
{
	return new CustomBlock;
}

bool CustomBlock::CheckUnlock()
{
	if ((SAVE_DATA.miscStates1 & 1 << 7) == 0)
	{
		return false;
	}

	return true;
}

void CustomBlock::JumpedUnderBlock()
{
	stage = 1;
	return;
}

//Jiggles block up then down.
void CustomBlock::Jiggle()
{
	renderFrame = !renderFrame;

	switch (stage)
	{
		case 0:
			break;
		case 1:
			if (renderFrame)
			{
				stage = 2;
				Sound::PlayBank3(0, camSpacePos);
			}
			canBeHit =  false;
			pos.y += 30._f / 2;
			//modelAnim.mat4x3.c1 = originalScaleY * 0x1720_f;

			modelAnim.mat4x3.c1 = originalScaleY * 0x1720_f;
			break;
		case 2:
			if (renderFrame)
				stage = 3;
			pos.y += 20._f / 2;
			modelAnim.mat4x3.c1 = originalScaleY * 0x1720_f;
			modelAnim.mat4x3.c0 = originalScaleX * 0x1030_f;
			modelAnim.mat4x3.c2 = originalScaleZ * 0x1030_f;
			break;
		case 3:
			if (renderFrame)
				stage = 4;
			pos.y += 16._f / 2;
			modelAnim.mat4x3.c1 = originalScaleY * 0x0930_f;
			modelAnim.mat4x3.c0 = prevScaleX * 0x1400_f;
			modelAnim.mat4x3.c2 = prevScaleZ * 0x1400_f;
			break;
		case 4:
			if (renderFrame)
				stage = 5;
			hasClsn = false;
			pos.y += 9._f / 2;
			modelAnim.mat4x3.c1 = originalScaleY * 0x0910_f;
			modelAnim.mat4x3.c0 = prevScaleX * 0x1300_f;
			modelAnim.mat4x3.c2 = prevScaleZ * 0x1300_f;
			break;
		case 5:
			if (renderFrame)
				stage = 8;
			pos.y += 8._f / 2;
			modelAnim.mat4x3.c1 = originalScaleY * 0x0840_f;
			modelAnim.mat4x3.c0 = prevScaleX;
			modelAnim.mat4x3.c2 = prevScaleZ;
			break;
		case 6:
			if (renderFrame)
				stage = 7;
			modelAnim.mat4x3.c1 = originalScaleY;
			modelAnim.mat4x3.c0 = prevScaleX;
			modelAnim.mat4x3.c2 = prevScaleZ;
			break;
		case 7:
			if (renderFrame)
				stage = 8;
			modelAnim.mat4x3.c1 = originalScaleY;
			modelAnim.mat4x3.c0 = prevScaleX;
			modelAnim.mat4x3.c2 = prevScaleZ;

			//prevScaleYr0
			//prevScaleYr1
			//prevScaleYr2
			//
			//
			//
			//
			//
			//
			break;
		case 8:
			if (renderFrame)
			{
				stage = respawn ? 9 : 0;
				canRender = false;

				Particle::System::NewSimple(0x0b, pos.x, pos.y, pos.z);
				Particle::System::NewSimple(0x09, pos.x, pos.y, pos.z);
				Particle::System::NewSimple(0x0d, pos.x, pos.y, pos.z);

				if (spawnPowerUp && itemType != 0 && itemType != 2)
					Actor::Spawn(ItemActor[itemType - 1], ItemParam[itemType - 1], (itemType == 0xE ? oldPos : pos), nullptr, areaID, -1);

				if (itemType == 2)
				{
					UntrackStar();
					Actor* starMarker = Actor::Spawn(0xb4, 0x50, pos, nullptr, areaID, -1); //that was the star marker.
					Actor* silverStar = Actor::Spawn(0xb3, 0x10 + (starID), pos,         nullptr, areaID, -1);

					if(starMarker && silverStar)
					{
						*(int*)((char*)silverStar + 0x434) = starMarker->uniqueID;
						LinkSilverStarAndStarMarker(starMarker, silverStar);
						SpawnSoundObj(1);
					}
				}

				frameCounter = 0;
			}
			break;
		case 9:
			if (renderFrame)
				frameCounter++;
			if (frameCounter == 132)
				stage = 10;
			break;
		case 10:
			if (renderFrame)
				stage = 11;
			pos.y += 13._f / 2;
			//code
			//code
			canRender = true;
			frameCounter = 0;
			break;
		case 11:
			if (renderFrame)
				frameCounter++;
			pos.y -= 13._f / 2;
			if (frameCounter == 7)
				stage = 12;
			break;
		case 12:
			if (renderFrame)
				stage = 0;
			pos.y = oldPos.y;
			canBeHit = true;
			hasClsn = true;
			break;
	}

	prevScaleX = modelAnim.mat4x3.c0;
	prevScaleY = modelAnim.mat4x3.c1;
	prevScaleZ = modelAnim.mat4x3.c1;

	//prevScaleXr0
	//prevScaleXr1
	//prevScaleXr2
	//prevScaleYr0
	//prevScaleYr1
	//prevScaleYr2
	//prevScaleZr0
	//prevScaleZr1
	//prevScaleZr2

	//modelAnim.mat4x3.r0c0;
	//modelAnim.mat4x3.r1c0;
	//modelAnim.mat4x3.r2c0;
	//modelAnim.mat4x3.r0c1;
	//modelAnim.mat4x3.r1c1;
	//modelAnim.mat4x3.r2c1;
	//modelAnim.mat4x3.r0c2;
	//modelAnim.mat4x3.r1c2;
	//modelAnim.mat4x3.r2c2;
}

void CustomBlock::UpdateModelTransform()
{
	modelAnim.mat4x3 = modelAnim.mat4x3.RotationY(ang.y);
	modelAnim.mat4x3.c3 = pos >> 3;
	if (canRender)
		DropShadowScaleXYZ(shadow, modelAnim.mat4x3, 0x85000_f, 0x150000_f, 0x85000_f, 0xc);
}

int CustomBlock::InitResources()
{
	if ((param1 >> 12 & 0xf) == 1)
		blockType = BlockType::RED;
	else
		blockType = BlockType::YELLOW;

	itemType = param1 & 0xfff;
	starID = (ang.x >> 12 & 0xf) > 7 ? 0 : (ang.x >> 12 & 0xf);

	//Respawn block only after spawning power ups
	if (itemType == 0x4 || itemType == 0x5 || itemType == 0x6 || itemType == 0x7)
		respawn = true;
	else
		respawn = false;

	//Silver Star
	if (itemType == 2)
	{
		silverStarID = TrackStar(0xf, 1);
		LoadSilverStarAndNumber();
	}

	canRender = true;
	canBeHit = true;
	hasClsn = true;
	renderFrame = true;
	isUnlocked = CheckUnlock();
	spawnPowerUp = true;

	//Avoid particle glitches
	if (itemType == 3)
		Model::LoadFile(ONE_UP_MUSHROOM_MODEL_PTR);
	else if (itemType == 4)
		Model::LoadFile(SUPER_MUSHROOM_MODEL_PTR);
	else if (itemType == 5)
		Model::LoadFile(FEATHER_MODEL_PTR);
	else if (itemType == 6)
	{
		Model::LoadFile(POWER_FLOWER_OPEN_MODEL_PTR);
		Model::LoadFile(POWER_FLOWER_CLOSED_MODEL_PTR);
	}
	else if (itemType == 7)
		Model::LoadFile(SHELL_GREEN_MODEL_PTR);

	if (blockType == BlockType::YELLOW)
	{
		Model::LoadFile(modelFiles[0]);
		modelAnim.SetFile(modelFiles[0].filePtr, 1, -1);

		MovingMeshCollider::LoadFile(clsnFile);
		clsn.SetFile(clsnFile.filePtr, clsnNextMat, 0x190_f, ang.y, *(CLPS_Block*)&clpsBlock);

		Animation::LoadFile(animFiles[0]);
		modelAnim.SetAnim(animFiles[0].filePtr, Animation::NO_LOOP, 0x1000_f, 0);

		UpdateClsnPosAndRot();
	}
	else
	{
		if (isUnlocked)
		{
			Model::LoadFile(modelFiles[1]);
			modelAnim.SetFile(modelFiles[1].filePtr, 1, -1);

			MovingMeshCollider::LoadFile(clsnFile);
			clsn.SetFile(clsnFile.filePtr, clsnNextMat, 0x190_f, ang.y, *(CLPS_Block*)&clpsBlock);

			Animation::LoadFile(animFiles[0]);
			modelAnim.SetAnim(animFiles[0].filePtr, Animation::NO_LOOP, 0x1000_f, 0);

			UpdateClsnPosAndRot();
		}
		else
		{
			Model::LoadFile(modelFiles[2]);
			modelAnim.SetFile(modelFiles[2].filePtr, 1, -1);

			Animation::LoadFile(animFiles[1]);
			modelAnim.SetAnim(animFiles[1].filePtr, Animation::LOOP, 0x1000_f, 0);
		}
	}

	shadow.InitCuboid();
	UpdateModelTransform();

	shadowMat = model.mat4x3 * Matrix4x3::IDENTITY;
	shadowMat.c3.y -= 0x14000_f >> 3;

	stage = 0;
	oldPos = pos;

	originalScaleX = modelAnim.mat4x3.c0;
	originalScaleY = modelAnim.mat4x3.c1;
	originalScaleZ = modelAnim.mat4x3.c2;

	return 1;
}

int CustomBlock::CleanupResources()
{
	clsn.Disable();
	clsnFile.Release();

	modelFiles[0].Release();
	modelFiles[1].Release();
	modelFiles[2].Release();

	animFiles[0].Release();
	animFiles[1].Release();

	//Avoid particle glitches
	if (itemType == 3)
		ONE_UP_MUSHROOM_MODEL_PTR.Release();
	else if (itemType == 4)
		SUPER_MUSHROOM_MODEL_PTR.Release();
	else if (itemType == 5)
		FEATHER_MODEL_PTR.Release();
	else if (itemType == 6)
	{
		POWER_FLOWER_OPEN_MODEL_PTR.Release();
		POWER_FLOWER_CLOSED_MODEL_PTR.Release();
	}
	else if (itemType == 7)
		SHELL_GREEN_MODEL_PTR.Release();

	if (itemType == 2)
		UnloadSilverStarAndNumber();

	return 1;
}

int CustomBlock::Behavior()
{
	UpdateModelTransform();

	if (isUnlocked || blockType == BlockType::YELLOW)
	{
		if (IsClsnInRange(0_f, 0_f))
		{
			Player* player = ClosestPlayer();

			if (BumpedUnderneathByPlayer(*player) && player->pos.x < pos.x + 0x53500_f && player->pos.x > pos.x - 0x53500_f && player->pos.z < pos.z + 0x53500_f && player->pos.z > pos.z - 0x53500_f && stage == 0 && canBeHit)
			{
				JumpedUnderBlock();
			}

			UpdateClsnPosAndRot();

			spawnPowerUp = true;

			if ((ang.x >> 8 & 0xf) == 1 && SAVE_DATA.currentCharacter != 0)
				spawnPowerUp = false;
			else if ((ang.x >> 8 & 0xf) == 2 && SAVE_DATA.currentCharacter != 1)
				spawnPowerUp = false;
			else if ((ang.x >> 8 & 0xf) == 3 && SAVE_DATA.currentCharacter != 2)
				spawnPowerUp = false;
			else if ((ang.x >> 8 & 0xf) == 4 && SAVE_DATA.currentCharacter != 3)
				spawnPowerUp = false;
		}

		Jiggle();
	}
	else
	{
		isUnlocked = CheckUnlock();
		if (isUnlocked)
		{
			Model::LoadFile(modelFiles[1]);
			modelAnim.SetFile(modelFiles[1].filePtr, 1, -1);

			MovingMeshCollider::LoadFile(clsnFile);
			clsn.SetFile(clsnFile.filePtr, clsnNextMat, 0x190_f, ang.y, *(CLPS_Block*)&clpsBlock);

			Animation::LoadFile(animFiles[0]);
			modelAnim.SetAnim(animFiles[0].filePtr, Animation::NO_LOOP, 0x1000_f, 0);

			UpdateClsnPosAndRot();
		}
		else
		{
			modelAnim.Advance();
		}
	}

	if (!hasClsn)
		clsn.Disable();

	return 1;
}

int CustomBlock::Render()
{
	if (canRender)
		modelAnim.Render(nullptr);

	return 1;
}

void CustomBlock::OnGroundPounded(Actor& groundPounder)
{
	if (canBeHit)
		JumpedUnderBlock();
}

void CustomBlock::OnAttacked1(Actor& attacker)
{
	if (canBeHit)
		JumpedUnderBlock();
}

void CustomBlock::OnAttacked2(Actor& attacker)
{
	if (canBeHit)
		JumpedUnderBlock();
}

void CustomBlock::OnKicked(Actor& kicker)
{
	if (canBeHit)
		JumpedUnderBlock();
}

void CustomBlock::OnHitByMegaChar(Player& megaChar)
{
	if (canBeHit)
	{
		megaChar.IncMegaKillCount();
		JumpedUnderBlock();
	}
}

CustomBlock::~CustomBlock() {}
