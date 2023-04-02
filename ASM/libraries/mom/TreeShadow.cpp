#include "TreeShadow.h"

namespace {}

SharedFilePtr TreeShadow::modelFile;

SpawnInfo TreeShadow::spawnData =
{
	[]() -> ActorBase* { return new TreeShadow; },
	0x0034,
	0x0100,
	0x00000002,
	0x00000000_f,
	0x005dc000_f,
	0x01000000_f,
	0x01000000_f
};

TreeShadow* TreeShadow::Spawn()
{
	return new TreeShadow;
}

void TreeShadow::UpdateModelTransform()
{
	model.mat4x3 = model.mat4x3.RotationY(ang.y);
	model.mat4x3.c3 = pos >> 3;
	DropShadowRadHeight(shadow, model.mat4x3, 0x150000_f, 0x137000_f, 0xc);
}

int TreeShadow::InitResources()
{
	opacity = param1 & 0xf;

	Model::LoadFile(modelFile);
	model.SetFile(modelFile.filePtr, 1, -1);

	shadow.InitCylinder();

	UpdateModelTransform();

	shadowMat = model.mat4x3 * Matrix4x3::IDENTITY;
	shadowMat.c3.y -= 0x14000_f >> 3;

	return 1;
}

int TreeShadow::CleanupResources()
{
	modelFile.Release();
	return 1;
}

int TreeShadow::Behavior()
{
	UpdateModelTransform();
	return 1;
}

int TreeShadow::Render()
{
	//model.Render(nullptr);
	return 1;
}

TreeShadow::~TreeShadow() {}
