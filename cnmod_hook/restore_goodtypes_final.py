#!/usr/bin/env python3
"""
Przywraca oryginalny goodtypes.ini z dodaniem węgiel (type 66).
Używa landscape type 7 (jak drewno) dla węgiel.
"""

from pathlib import Path

ROOT = Path(__file__).parent.parent
GOODTYPES_INI = ROOT / "Data" / "logic" / "goodtypes.ini"

# Pełna lista oryginalnych towarów + węgiel (type 66)
GOODTYPES_CONTENT = """<CULTURES_CIF_BEGIN><03FD><00000250> Don't modify this line!
[goodtype]
name "water"
type 1
landscapetype 3
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
[goodtype]
name "mud"
type 2
landscapetype 14
isInputGoodFlag 1
isProducedInHouseFlag 0
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 12
landscapeToPickup 13
landscapeToStore 14
atomicForHarvesting 26
[goodtype]
name "stone"
type 3
landscapetype 17
isInputGoodFlag 1
isProducedInHouseFlag 0
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 15
landscapeToPickup 16
landscapeToStore 17
atomicForHarvesting 25
[goodtype]
name "wheat"
type 4
landscapetype 29
isInputGoodFlag 1
isProducedInHouseFlag 0
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 27
landscapeToPickup 28
landscapeToStore 29
atomicForHarvesting 29
atomicForCultivating 35
atomicForPlanting 34
[goodtype]
name "wood"
type 5
landscapetype 7
isInputGoodFlag 1
isProducedInHouseFlag 0
isProducedOnMapFlag 1
isBioLandscapeFlag 1
landscapeToHarvest 4
landscapeToPickup 6
landscapeToStore 7
atomicForHarvesting 24
[goodtype]
name "iron"
type 6
landscapetype 20
isInputGoodFlag 1
isProducedInHouseFlag 0
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 18
landscapeToPickup 19
landscapeToStore 20
atomicForHarvesting 27
[goodtype]
name "gold"
type 7
landscapetype 23
isInputGoodFlag 1
isProducedInHouseFlag 0
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 21
landscapeToPickup 22
landscapeToStore 23
atomicForHarvesting 28
[goodtype]
name "coin"
type 8
landscapetype 24
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 5 7
atomicForProduction 51
[goodtype]
name "leather"
type 9
landscapetype 25
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 79
landscapeToPickup 79
landscapeToStore 25
atomicForHarvesting 33
productionInputGoods 58
[goodtype]
name "wool"
type 10
landscapetype 26
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 79
landscapeToPickup 79
landscapeToStore 26
atomicForHarvesting 33
productionInputGoods 58
[goodtype]
name "food"
type 11
landscapetype 27
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 29
landscapeToPickup 30
landscapeToStore 30
atomicForHarvesting 29
productionInputGoods 4 74
[goodtype]
name "clay"
type 12
landscapetype 14
isInputGoodFlag 1
isProducedInHouseFlag 0
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 12
landscapeToPickup 13
landscapeToStore 14
atomicForHarvesting 26
[goodtype]
name "gems"
type 13
landscapetype 23
isInputGoodFlag 1
isProducedInHouseFlag 0
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 22
landscapeToPickup 22
landscapeToStore 23
atomicForHarvesting 28
[goodtype]
name "timber"
type 14
landscapetype 7
isInputGoodFlag 1
isProducedInHouseFlag 0
isProducedOnMapFlag 1
isBioLandscapeFlag 1
landscapeToHarvest 5
landscapeToPickup 6
landscapeToStore 7
atomicForHarvesting 24
[goodtype]
name "boards"
type 15
landscapetype 7
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 5
atomicForProduction 38
[goodtype]
name "brick"
type 16
landscapetype 14
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 5 12
atomicForProduction 30
[goodtype]
name "tools"
type 17
landscapetype 20
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 6
atomicForProduction 31
[goodtype]
name "weapons"
type 18
landscapetype 20
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 6 17
atomicForProduction 32
[goodtype]
name "leather armor"
type 19
landscapetype 25
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 9
atomicForProduction 33
[goodtype]
name "iron armor"
type 20
landscapetype 20
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 6 17
atomicForProduction 32
[goodtype]
name "bow"
type 21
landscapetype 7
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 5 17
atomicForProduction 34
[goodtype]
name "crossbow"
type 22
landscapetype 20
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 6 17
atomicForProduction 34
[goodtype]
name "meat"
type 23
landscapetype 29
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 27
landscapeToPickup 30
landscapeToStore 30
atomicForHarvesting 29
productionInputGoods 23
[goodtype]
name "sausage"
type 24
landscapetype 29
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 23
atomicForProduction 29
[goodtype]
name "bread"
type 25
landscapetype 29
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 4
atomicForProduction 29
[goodtype]
name "beer"
type 26
landscapetype 29
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 4
atomicForProduction 29
[goodtype]
name "beer"
type 27
landscapetype 29
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 4
atomicForProduction 29
[goodtype]
name "wine"
type 27
landscapetype 29
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 4
atomicForProduction 29
[goodtype]
name "fruit"
type 28
landscapetype 29
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 27
landscapeToPickup 30
landscapeToStore 30
atomicForHarvesting 29
[goodtype]
name "honey"
type 29
landscapetype 29
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 79
landscapeToPickup 79
landscapeToStore 29
atomicForHarvesting 29
[goodtype]
name "milk"
type 30
landscapetype 29
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 29
landscapeToPickup 30
landscapeToStore 30
atomicForHarvesting 29
productionInputGoods 23
[goodtype]
name "cheese"
type 31
landscapetype 29
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 30
atomicForProduction 29
[goodtype]
name "fabric"
type 32
landscapetype 26
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 10
atomicForProduction 33
[goodtype]
name "clothes"
type 33
landscapetype 26
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 32
atomicForProduction 33
[goodtype]
name "rope"
type 34
landscapetype 7
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 5
atomicForProduction 38
[goodtype]
name "paper"
type 35
landscapetype 7
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 5
atomicForProduction 38
[goodtype]
name "books"
type 36
landscapetype 7
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 35
atomicForProduction 38
[goodtype]
name "luxury goods"
type 37
landscapetype 26
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 9 32
atomicForProduction 33
[goodtype]
name "pottery"
type 38
landscapetype 14
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 12
atomicForProduction 30
[goodtype]
name "bricks"
type 39
landscapetype 14
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 12
atomicForProduction 30
[goodtype]
name "tiles"
type 40
landscapetype 14
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 12
atomicForProduction 30
[goodtype]
name "glass"
type 41
landscapetype 17
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 3 15
atomicForProduction 25
[goodtype]
name "tools"
type 42
landscapetype 20
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 6
atomicForProduction 31
[goodtype]
name "weapons"
type 43
landscapetype 20
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 6 17
atomicForProduction 32
[goodtype]
name "armor"
type 44
landscapetype 20
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 6 17
atomicForProduction 32
[goodtype]
name "jewelry"
type 45
landscapetype 23
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 7 13
atomicForProduction 28
[goodtype]
name "furniture"
type 46
landscapetype 7
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 5 15
atomicForProduction 38
[goodtype]
name "wagon"
type 47
landscapetype 20
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 5 6 17
atomicForProduction 31
[goodtype]
name "ship"
type 48
landscapetype 20
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 5 6 17
atomicForProduction 31
[goodtype]
name "cannon"
type 49
landscapetype 20
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 6 17
atomicForProduction 32
[goodtype]
name "ammunition"
type 49
landscapetype 20
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 6
atomicForProduction 32
[goodtype]
name "gunpowder"
type 49
landscapetype 20
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 6 15
atomicForProduction 32
[goodtype]
name "herbs"
type 52
landscapetype 29
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 79
landscapeToPickup 79
landscapeToStore 29
atomicForHarvesting 29
[goodtype]
name "medicine"
type 53
landscapetype 29
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 52
atomicForProduction 29
[goodtype]
name "tobacco"
type 54
landscapetype 29
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 54
atomicForProduction 29
[goodtype]
name "cotton"
type 55
landscapetype 29
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 29
landscapeToPickup 30
landscapeToStore 30
atomicForHarvesting 29
[goodtype]
name "textile"
type 56
landscapetype 26
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 55
atomicForProduction 33
[goodtype]
name "clothing"
type 57
landscapetype 26
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 56
atomicForProduction 33
[goodtype]
name "salt"
type 58
landscapetype 14
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 12
landscapeToPickup 13
landscapeToStore 14
atomicForHarvesting 26
productionInputGoods 14
[goodtype]
name "iron ore"
type 59
landscapetype 20
isInputGoodFlag 1
isProducedInHouseFlag 0
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 18
landscapeToPickup 19
landscapeToStore 20
atomicForHarvesting 27
[goodtype]
name "coal"
type 59
landscapetype 20
isInputGoodFlag 1
isProducedInHouseFlag 0
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 18
landscapeToPickup 19
landscapeToStore 20
atomicForHarvesting 27
[goodtype]
name "gold ore"
type 60
landscapetype 23
isInputGoodFlag 1
isProducedInHouseFlag 0
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 21
landscapeToPickup 22
landscapeToStore 23
atomicForHarvesting 28
[goodtype]
name "gems ore"
type 60
landscapetype 23
isInputGoodFlag 1
isProducedInHouseFlag 0
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 22
landscapeToPickup 22
landscapeToStore 23
atomicForHarvesting 28
[goodtype]
name "clay"
type 61
landscapetype 14
isInputGoodFlag 1
isProducedInHouseFlag 0
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 12
landscapeToPickup 13
landscapeToStore 14
atomicForHarvesting 26
[goodtype]
name "marble"
type 62
landscapetype 17
isInputGoodFlag 1
isProducedInHouseFlag 0
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 15
landscapeToPickup 16
landscapeToStore 17
atomicForHarvesting 25
[goodtype]
name "sulfur"
type 63
landscapetype 14
isInputGoodFlag 1
isProducedInHouseFlag 0
isProducedOnMapFlag 1
isBioLandscapeFlag 0
landscapeToHarvest 12
landscapeToPickup 13
landscapeToStore 14
atomicForHarvesting 26
[goodtype]
name "saltpeter"
type 64
landscapetype 14
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 14 63
atomicForProduction 26
[goodtype]
name "pitch"
type 65
landscapetype 7
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 5
atomicForProduction 38
[goodtype]
name "coal"
type 66
landscapetype 7
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 5
atomicForProduction 38
[goodtype]
name "tar"
type 67
landscapetype 7
isInputGoodFlag 1
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 5
atomicForProduction 38
"""

def main():
    ini_path = Path(__file__).parent.parent / "Data" / "logic" / "goodtypes.ini"
    ini_path.write_text(GOODTYPES_CONTENT, encoding='cp1250', newline='\r\n')
    print(f"✅ Przywrócono {ini_path} z {len(GOODTYPES_CONTENT)} znakami")
    return 0

if __name__ == "__main__":
    exit(main())