#ifndef BERRY_INCLUDED
#define BERRY_INCLUDED

#include "SM64DS_2.h"

struct Berry : public Actor
{
	Model model;
	Model stem;
	MovingCylinderClsn cylClsn;
	ShadowModel shadow;
	Vector3 origPos;
	bool groundFound;
	bool killed;

	void UpdateModelTransform();
	void Kill();

	static Berry* Spawn();
	virtual int InitResources() override;
	virtual int CleanupResources() override;
	virtual int Behavior() override;
	virtual int Render() override;
	virtual ~Berry() override;
	virtual unsigned OnYoshiTryEat() override;
	virtual void OnTurnIntoEgg(Player& player) override;

	static SpawnInfo spawnData;

	static SharedFilePtr modelFile;
	static SharedFilePtr stemFile;

	static unsigned berryCount;
	static unsigned berryMaxCount;

};

#endif