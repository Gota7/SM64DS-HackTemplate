#include "BlueIceBlock.h"

namespace
{
	FixedSizeCLPS_Block<1> clpsBlock =
	{
		{'C', 'L', 'P', 'S'},
		8,
		1,
		{
        	CLPS(0x07, 0, 0x3f, 0x4, 0x8, 0x0E, 1, 0, 0, 0xff)
        }
	};
}

SharedFilePtr BlueIceBlock::modelFile;
SharedFilePtr BlueIceBlock::clsnFile;

SpawnInfo BlueIceBlock::spawnData =
{
	[]() -> ActorBase* { return new BlueIceBlock; },
	0x0034,
	0x0100,
	0x00000002,
	0x00000000_f,
	0x005dc000_f,
	0x01000000_f,
	0x01000000_f
};

BlueIceBlock* BlueIceBlock::Spawn()
{
	return new BlueIceBlock;
}

void BlueIceBlock::UpdateModelTransform()
{
	model.mat4x3 = model.mat4x3.RotationY(ang.y);
	model.mat4x3.c3 = pos >> 3;
}

int BlueIceBlock::InitResources()
{
	Model::LoadFile(modelFile);
	model.SetFile(modelFile.filePtr, 1, -1);

	MovingMeshCollider::LoadFile(clsnFile);
	clsn.SetFile(clsnFile.filePtr, clsnNextMat, 0x1000_f, ang.y, *(CLPS_Block*)&clpsBlock);

	UpdateModelTransform();
	UpdateClsnPosAndRot();
	return 1;
}

int BlueIceBlock::CleanupResources()
{
	clsn.Disable();
	clsnFile.Release();
	modelFile.Release();
	return 1;
}

int BlueIceBlock::Behavior()
{
	UpdateModelTransform();

	if(IsClsnInRange(0_f, 0_f))
		UpdateClsnPosAndRot();

	return 1;
}

int BlueIceBlock::Render()
{
	model.Render(nullptr);
	return 1;
}

BlueIceBlock::~BlueIceBlock() {}
