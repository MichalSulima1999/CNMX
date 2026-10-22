# Goods Mechanism Analysis - CN.PLMOD.exe

## Executive Summary

After extensive reverse engineering, the goods system in CN.PLMOD.exe is **extensible but requires patching at multiple layers**. The engine loads goods from `Data/logic/goodtypes.ini` (override for `goodtypes.cif`), but runtime production and UI loops have hardcoded 66-goods limits that must be patched. The production pipeline works, but **tribe house initialization was the critical missing link**.

---

## 1. Data Layer - Goods Definition

### 1.1 File Format
- **Source**: `Data/logic/goodtypes.ini` (overrides `goodtypes.cif`)
- **Format**: `<CULTURES_CIF_BEGIN><03FD><NNNNNNNN>` header + `[goodtype]` blocks + `<CULTURES_CIF_END>`
- **Encoding**: CP1250, CRLF
- **Transform**: `%01%goodtype` → `[goodtype]`, `%02%` stripped

### 1.2 Good Record Structure (stride 0xD0)
| Offset | Field | Description |
|--------|-------|-------------|
| +0x00 | name | string (e.g., "coal") |
| +0x20 | landscapetype | terrain type for map generation |
| +0x30 | isProducedOnMapFlag | 1 = generated on map |
| +0x31 | isProducedInHouseFlag | 1 = produced in buildings |
| +0x32 | isBioLandscapeFlag | 1 = biological |
| +0x50 | productionInputGoods | input goods (space-separated IDs) |
| +0x54 | atomicForProduction | production atomic type |

### 1.3 Loader (VA 0x41592E)
- Alloc: `mov esi, 0x35A0` → patched to 0x6730 (127 goods)
- Validator: `cmp eax, 0x42; jge` → patched to 0x7F
- **Record index = good type** (type 66 → record 66)

---

## 2. Runtime Data Structures

### 2.1 Global House Type Table
- Base: `[0x5113A0]`
- Stride: 0x624 bytes
- Extended count: 127 (validator 0x37→0x7F)

### 2.2 House Record Layout (0x624 bytes)
| Offset | Size | Description |
|--------|------|-------------|
| +0x60 | 4 | stock entry count |
| +0x64 | 12*66 | stock entries {good, qty, flag} |
| +0x37C | 4*66 | stock reverse map (good → index) |
| +0x484 | 4 | production count (max 20) |
| +0x488 | 4*20 | production list (good IDs) |
| +0x4D8 | 4*66 | production reverse map (good → list index) |
| +0x8 | 4 | **output good ID** (copied to tribe house on build) |

### 2.3 Tribe House Array (per tribe)
- Base: `[0x510BE0]`
- Stride: 0x54C bytes
- **+0x8 = output good ID** (read by potter handler for job 56)

### 2.4 Critical Collisions for Good 66
| Structure | Collision | Workaround |
|-----------|-----------|------------|
| stock reverse map (+0x37C+66*4) | overwrites +0x484 (prod count) | `logicproduction 66` BEFORE `logicstock 66` |
| production revmap (+0x4D8+66*4) | writes to +0x5E0 (near +0x5E4) | tolerated |

---

## 3. Production Pipeline

### 3.1 Loader Phase (houses.ini parsing)
```
logicproduction 66
  → house+0x488[count] = 66
  → house+0x4D8[66] = count
  → house+0x484++
  → PATCH: house+0x8 = 66 (global_house output good)
```

### 3.2 Build Phase (tribe house initialization)
```
Function 0x430D1B (build-time init)
  → Copies global_house fields to tribe_house
  → PATCH: tribe_house+0x8 = global_house+0x8 (output good)
```

### 3.3 Runtime Production Loop (VA 0x4C23D8)
```
for each tribe house:
  count = house+0x484
  for i in 0..count-1:
    good = house+0x488[i]
    produce(good)
```

### 3.4 Job Dispatcher (VA 0x4E21B7)
```
switch(job):
  case 56 (Smolarz): → potter handler (index 192)
  case 24 (Potter): → produce( tribe_house+0x8 )
```

### 3.5 Potter Handler (VA 0x46E1BE)
```
output_good = tribe_house+0x8
if output_good == 0: FAIL  ← was the bug!
produce(output_good)
```

---

## 4. Goods-Table Iteration Loops (all patched)

| VA | RVA | Function | Bound | Status |
|----|-----|----------|-------|--------|
| 0x40B02C | 0xB02C | name search | 0x35A0→0x6730 | ✓ patched |
| 0x415E8E | 0x15E8E | goods init/UI | 0x2CB0 (55) | **CRASH if patched** |
| 0x435CD7 | 0x35CD7 | active goods | 0x35A0→0x6730 | ✓ patched |
| 0x456168 | 0x56168 | production calc | 0x35A0→0x6730 | ✓ patched |
| 0x45FAFA | 0x5FAFA | local arrays | 0x35A0 | **UNSAFE** (stack overflow) |

---

## 5. Loader Guards (all patched)

| VA | RVA | Guard | Patch |
|----|-----|-------|-------|
| 0x415831 | 0x15833 | `cmp eax,0x42` (logicproduction) | 0x42→0x7F |
| 0x4159EF | 0x159F1 | `cmp eax,0x42` (goodtypes) | 0x42→0x7F |
| 0x414292 | 0x14292 | `cmp edi,0x42` (toProduceGoodNeedHouse) | 0x42→0x7F |

---

## 6. Data Files

| File | Purpose |
|------|---------|
| `Data/logic/goodtypes.ini` | 66 goods (1-66), good 66 = coal |
| `Data/logic/jobtypes.ini` | 57 jobs, job 56 = Smolarz |
| `Data/logic/vehicletypes.ini` | vehicle types |
| `Data/text/pol/strings/gameobjects/goods.ini` | good 66 name = "Węgiel" |

### houses.ini - Smolarz (logictype 57)
```ini
[logichousetype]
debugname "work charcoal burner"
logictype 57
logicmaintype 3
logicworker 56 1
logicstock 5 1 1        ; input: wood (good 5)
logicproduction 66      ; output: coal (good 66)
logicstock 66 15 0      ; output stock: coal, cap 15
debugcolor 0 0 100
```

### houses.ini - Storehouse (logictype 1)
```ini
logicstock 66 150 0     ; coal storage in HQ
```

### tribetypes.ini (per tribe, 5 tribes)
```
allowgood 66
allowhouse 57
jobEnablesGood 56 66
jobDefaultGood 56 66
toProduceGoodNeedHouse 66 57
```

---

## 6. Patch Summary (588 total)

### Critical Patches for Good 66 / Job 56
| RVA | Patch | Purpose |
|-----|-------|---------|
| 0x15833 | 0x42→0x7F | logicproduction good guard |
| 0x159F1 | 0x42→0x7F | goodtypes validator |
| 0x14292 | 0x42→0x7F | toProduceGoodNeedHouse guard |
| 0x0B02C | 0x35A0→0x6730 | name search loop |
| 0x35CD7 | 0x35A0→0x6730 | active goods loop |
| 0x56168 | 0x35A0→0x6730 | production calc loop |
| 0x15843 | `mov [esi+8],eax` | logicproduction writes to global_house+8 |
| 0x5C6FC | `mov al,1` | force depot check pass (job 56) |
| 0x6BD36 | dispatcher fix | job 56 → potter handler |
| 0x30D4F | JMP to cave | tribe house init copies output good |
| 0xF2340.. | cave code | copy global_house+8 → tribe_house+8 |

---

## 7. Root Cause Analysis - Why Coal Still Didn't Work

**The critical missing link was tribe house initialization at build time.**

### The Bug
- `global_house+8` was set by logicproduction patch (✓)
- But `tribe_house+8` was **never initialized** from `global_house+8`
- Potter handler reads `tribe_house+8` → got 0 → produced nothing

### The Fix (Added)
- Cave at 0xF2340, hooked at 0x430D4F (build-time init function 0x430D1B)
- Reads global_house[type]+8, writes to tribe_house+8
- Uses global_house stride 0x624, base 0x5113A0

---

## 8. Verification Checklist

If coal still doesn't work, check in order:

1. **Game launches without crash** ✓
2. **Smolarz hut builds** (job 56, logictype 57) ✓
3. **Building info panel shows "Węgiel"** 
   - Requires: goodtypes.ini loaded, production list populated
4. **HQ storage UI shows coal**
   - Requires: storehouse has `logicstock 66 150 0`, goods-table loops patched
5. **Smolarz consumes wood**
   - Requires: `logicstock 5 1 1` (flag 1 = input), recipe `productionInputGoods 5`
6. **Smolarz produces coal**
   - Requires: tribe_house+8 = 66, potter handler reads it
7. **Coal accumulates in Smolarz output stock**
   - Requires: `logicstock 66 15 0` (flag 0 = output)
8. **Coal accumulates in HQ stockpile**
   - Requires: storehouse has `logicstock 66 150 0`, tribe economy distributes

---

## 9. If Still Failing - Next Investigation Targets

### 9.1 Potter Handler Hardcodes Good 24
Check VA 0x46E1BE+ for hardcoded `cmp eax, 24` or similar.

### 9.2 Production Rev-Map Collision
Good 66 writes to +0x5E0 (adjacent to +0x5E4). Check if runtime reads this.

### 9.3 toProduceGoodNeedHouse Map
Only 66 entries (66*8 bytes at 0x1492C). Not relocated. May silently drop good 66.

### 9.4 Goods Loop at 0x415E8E
Crashes if bound extended. May be needed for storage UI.

### 9.5 Tribe Economy Distribution
Check if produced goods actually move from house stock to tribe stockpile.

---

## 10. Conclusion

The goods system **is fully extensible** but requires:
1. Data file overrides (INI > CIF)
2. Loader limit patches (3 guards)
3. Runtime loop patches (3 safe loops, 1 unsafe)
4. Critical initialization patches (global_house+8 → tribe_house+8)
5. Job dispatcher routing

**All structural pieces are now in place.** If coal still doesn't appear, the issue is likely in the potter handler's hardcoded logic or the final distribution step.