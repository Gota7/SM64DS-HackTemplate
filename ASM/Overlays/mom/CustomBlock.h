#ifndef POWER_UP_BLOCK_INCLUDED
#define POWER_UP_BLOCK_INCLUDED

#include "SM64DS_2.h"

struct CustomBlock : public Platform
{
	enum BlockType
	{
		YELLOW = 0,
		RED = 1
	};

	void UpdateModelTransform();

	static CustomBlock* Spawn();
	virtual void Jiggle();
	virtual void JumpedUnderBlock();
	virtual bool CheckUnlock();
	virtual int InitResources() override;
	virtual int CleanupResources() override;
	virtual int Behavior() override;
	virtual int Render() override;
	virtual void OnGroundPounded(Actor& groundPounder) override;
	virtual void OnAttacked1(Actor& attacker) override;
	virtual void OnAttacked2(Actor& attacker) override;
	virtual void OnKicked(Actor& kicker) override;
	virtual void OnHitByMegaChar(Player& megaChar) override;
	virtual ~CustomBlock();

	int stage;
	bool canRender;
	bool hasClsn;
	bool canBeHit;
	bool spawnPowerUp;
	bool renderFrame;
	bool respawn;
	int frameCounter;
	Vector3 oldPos;
	ModelAnim modelAnim;
	ShadowModel shadow;
	Matrix4x3 shadowMat;

	Vector3 originalScaleX;
	Vector3 originalScaleY;
	Vector3 originalScaleZ;

	Vector3 prevScaleX;
	Vector3 prevScaleY;
	Vector3 prevScaleZ;

	char silverStarID;
	unsigned starID;
	unsigned blockType;
	unsigned itemType;
	unsigned myParticle;
	bool isUnlocked;

	static SpawnInfo spawnData;

	static SharedFilePtr modelFiles[3];
	static SharedFilePtr clsnFile;
	static SharedFilePtr animFiles[2];
};

#endif
