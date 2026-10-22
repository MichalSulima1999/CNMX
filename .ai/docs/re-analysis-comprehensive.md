# Comprehensive Reverse Engineering Analysis - CN.PLMOD.exe

**Game:** The Nations / Die Völker / Kultury (Polish version)  
**Mod:** CN.PLMOD (CnMod 1.2)  
**Executable:** CN.PLMOD.exe (base 0x400000, no ASLR, x86)  
**Engine Patch:** EtapC.dll + launcher.exe (runtime patching via MinHook)  
**Analysis Date:** 2024-10-12  
**Analyst:** AI-assisted RE session

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [EXE Structure & Memory Layout](#exe-structure--memory-layout)
3. [Data Loading Pipeline](#data-loading-pipeline)
4. [Goods System](#goods-system)
5. [House/Building System](#housebuilding-system)
6. [Job/Worker System](#jobworker-system)
7. [Tribe/Economy System](#tribeeconomy-system)
8. [Production Pipeline](#production-pipeline)
9. [Script/Bytecode System](#scriptbytecode-system)
10. [UI Data Sources](#ui-data-sources)
11. [Current Patches Summary](#current-patches-summary)
12. [Critical Gaps & Root Causes](#critical-gaps--root-causes)
13. [Action Plan](#action-plan)

---

## Executive Summary

**Goal:** Add fully working job 56 "Smolarz" (charcoal burner) + Smolarz hut (logictype 57) producing coal (good 66 "Węgiel") with full UI integration (building panel, worker assignment, storage).

**Current State:** 596 runtime patches applied via EtapC.dll, but coal **not visible in any UI** and **not produced**.

**Root Cause Identified:** Multiple independent systems must align:
1. ✅ Data loading (INI overrides working)
2. ✅ Engine limits (596 patches applied)
3. ✅ Building panel logicproduction reading
4. ❌ **Worker UI job validation** (hardcoded job whitelists excluding job 56)
5. ❌ **Production execution** (potter handler bytecode hardcodes good 24)
6. ❌ **Missing houses.ini** in Data\logic\ (was only in CN.PLMOD\types\)

**Critical Insight:** The building panel reads `logicproduction` directly from house data, but worker UI and production execution use **separate code paths** with their own validation and hardcoded values.

---

## EXE Structure & Memory Layout

### PE Header
- **Base Address:** 0x400000 (no ASLR)
- **Entry Point:** 0x401000
- **Image Size:** ~0x170000
- **Sections:**
  - `.text` (0x1000-0xF21CB) - Code
  - `.rdata` (0xF3000-0xFD534) - Read-only data
  - `.data` (0xFE000-0x16B8B8) - Read-write data
  - `.rsrc` (0x16C000-0x173AE8) - Resources

### Key Global Addresses
| Address | Symbol | Description |
|---------|--------|-------------|
| 0x5113A0 | `g_houseTable` | Global house type table base |
| 0x511420 | `g_goodsTable` | Global goods table base |
| 0x511520 | `g_jobTable` | Global job table base |
| 0x510BE0 | `g_tribeHouseArray` | Per-tribe house array (stride 0x54C) |
| 0x510BF0 | `g_tribeData` | Per-tribe data (stride 0x54C) |
| 0x510BD0 | `g_goodExtra` | Good extra data (stride 0x7E0) |
| 0x510C0C | `g_gameState` | Global game state |
| 0x5114C4 | `g_tribeHouseCount` | Tribe house count |
| 0x5006E3 | `szGoodTypesIni` | "data\logic\goodtypes.ini" |
| 0x500117 | `szJobTypesIni` | "data\logic\jobtypes.ini" |
| 0x50045F | `szVehicleTypesIni` | "data\logic\vehicletypes.ini" |
| 0x5006C8 | `szHousesIni` | "data\logic\houses.ini" |

---

## Data Loading Pipeline

### INI Override Mechanism
The engine loads `.cif` files first, then **overrides with `.ini` files** if present:
```
.cif (original) → parsed → RAM tables
    ↓
.ini (mod) → parsed → OVERRIDES RAM tables (same format)
```

**INI Format:**
```ini
<CULTURES_CIF_BEGIN><03FD><NNNNNNNN> Don't modify this line!
[section]
key value
...
<CULTURES_CIF_END> Don't modify this line!
```
- Header: `<CULTURES_CIF_BEGIN><03FD><NNNNNNNN>` where N = body line count (hex, 8 digits)
- `%01%section` → `[section]`
- `%02%` stripped
- Encoding: CP1250, CRLF

**Verified Working INI Overrides:**
- `Data\logic\jobtypes.ini` ✅ (job 56 "Smolarz" works)
- `Data\logic\vehicletypes.ini` ✅
- `Data\logic\goodtypes.ini` ✅ (66 goods, good 66 = coal)
- `Data\logic\houses.ini` ✅ **NOW COPIED** (was missing from Data\logic\)

### Critical Missing File
**`Data\logic\houses.ini` was MISSING** - only existed in `CN.PLMOD\types\houses.ini`.  
Engine loads from `Data\logic\houses.ini` (string at 0x5006C8).  
**Fixed:** Copied to `Data\logic\houses.ini` with `logicproduction 66` for Smolarz.

---

## Goods System

### Goods Table (0x511420, stride 0xD0, max 127 goods)
| Offset | Field | Type | Description |
|--------|-------|------|-------------|
| +0x00 | name | char[32] | Internal name (e.g., "coal") |
| +0x20 | landscapeType | dword | Terrain type for map gen |
| +0x24 | weaponType | dword | Default -1 |
| +0x30 | isProducedOnMapFlag | byte | Generated on map |
| +0x31 | isProducedInHouseFlag | byte | Produced in building |
| +0x32 | isBioLandscapeFlag | byte | Bio terrain |
| +0x50 | productionInputGoods | dword[] | Input goods (space-separated) |
| +0x54 | atomicForProduction | dword | Production atomic type |

### Loader Limits (All Patched)
| Check | VA | Original | Patched | Purpose |
|-------|-----|----------|---------|---------|
| Alloc size | 0x41595F | 0x35A0 | 0x6730 | 66 → 127 goods |
| Validator | 0x4159EF | 0x42 | 0x7F | Accept good IDs up to 127 |
| Loop 1 (active goods) | 0x435CD7 | 0x35A0 | 0x6730 | Per-player goods iteration |
| Loop 2 (production calc) | 0x456168 | 0x35A0 | 0x6730 | Production calculation |
| Loop 3 (name search) | 0x00B02C | 0x35A0 | 0x6730 | Name lookup |
| Loop 4 (stack arrays) | 0x45FAFA | 0x35A0 | **NOT PATCHED** | Stack overflow risk! |

### Good 66 (Coal) Definition
```ini
[goodtype]
name "coal"
type 66
landscapeType 50
isInputGoodFlag 0
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 5
atomicForProduction 52
```
- Mirrors brick (type 24) recipe: input wood (5), atomic 52
- Name "Węgiel" in `Data\text\pol\strings\gameobjects\goods.ini` (string 66)

---

## House/Building System

### House Table (0x5113A0, stride 0x624, max 127 types)
| Offset | Size | Field |
|--------|------|-------|
| +0x60 | 4 | Stock entry count |
| +0x64 | 12×66 | Stock entries {good, qty, flag} |
| +0x37C | 4×66 | Stock reverse map (good → index) |
| +0x484 | 4 | Production count (max 20) |
| +0x488 | 4×20 | Production list (good IDs) |
| +0x4D8 | 4×66 | Production reverse map (good → list index) |
| +0x5E4 | 4 | Unknown |
| +0x620 | 4 | Zeroed per-record |

### Loader Logic (0x415403-0x41585B)
- `logictype` handler: validates type < 0x37 (patched to 0x7F), sets `esi = houseTable + idx*0x624`
- `logicstock`: max 66 entries, writes reverse map at `[esi + good*4 + 0x37C]`
  - **COLLISION:** good 66 writes to `[esi+0x37C+66*4] = [esi+0x484]` = production count!
  - **Workaround:** `logicproduction 66` BEFORE `logicstock 66` → final count = 1 = stock index
- `logicproduction`: validates good < 0x42 (patched to 0x7F), adds to production list
- **PATCH:** `logicproduction` writes good ID to `global_house+8` (copied to tribe_house+8 on build)

### Smolarz Hut Definition
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

### Tribe House Array (0x510BE0, stride 0x54C)
| Offset | Field |
|--------|-------|
| +0x04 | House type index |
| +0x08 | **Output good ID** (copied from global_house+8 on build) |
| +0x1C | House type limit |
| +0x1E8 | House type ID |
| +0x1DC | Script/atomic index |

---

## Job/Worker System

### Job Table (0x511520, stride 0x88, max 127 jobs)
| Offset | Field |
|--------|-------|
| +0x00 | Name string pointer |
| +0x04 | Unknown |
| +0x08 | Job flags |
| ... | ... |

### Job 56 "Smolarz"
- **Name:** From `hook_GetJobString` (not data) - "Smolarz"
- **Dispatcher Patch:** 0x6BD36 redirects job 56 → potter handler (index 192)
- **Potter Handler:** 0x46D53A → calls deposit function 0x46E1BE
- **Deposit Function (0x46E1BE):** Reads `tribe_house+8` (output good), produces that good

### Worker Assignment UI - THE MISSING LINK
**Worker UI reads `jobEnablesGood`/`jobDefaultGood` from tribetypes** but has **hardcoded job whitelists** in validation functions:

| VA | Function | Original Check | Patched |
|-----|----------|----------------|---------|
| 0x44181C | UI list 1 | `cmp eax, 0x3A` (58) | `cmp eax, 0x38` (56) |
| 0x44181F | UI list 2 | `cmp eax, 0x39` (57) | `cmp eax, 0x38` (56) |
| 0x441821 | UI list 3 | `cmp eax, 0x41` (65) | `cmp eax, 0x38` (56) |
| 0x468A64 | UI list 4 | `cmp eax, 0x39` (57) | `cmp eax, 0x38` (56) |
| 0x468A69 | UI list 4 cont. | `cmp eax, 0x3A` (58) | `cmp eax, 0x38` (56) |

**These were PATCHED** (5 patches) to allow job 56 in worker production UI.

---

## Tribe/Economy System

### Tribetypes Configuration (per tribe, 5 tribes in `tribetypes.ini`)
```ini
allowgood 66
allowhouse 57
jobEnablesGood 56 66
jobDefaultGood 56 66
toProduceGoodNeedHouse 66 57
```
- All 5 tribes have these entries (25 lines total)
- `toProduceGoodNeedHouse 66 57` added (was missing)

### toProduceGoodNeedHouse Map (0x1492C, stride 8, 66 entries)
- Maps good ID → house type that produces it
- **Not relocated** (still 66 entries) - but good 66 entry added
- Only writer found in .text (no readers in .text)

---

## Production Pipeline

### Runtime Production Loop (0x4C23D8)
```assembly
; Iterate tribe houses
mov edx, [eax + 0x484]  ; production count
test edx, edx
jbe skip
add eax, 0x488          ; production list
loop:
    mov eax, [eax]      ; good ID
    call 0x4E21B7       ; job dispatcher
```

### Job Dispatcher (0x4E21B7)
- Parses bytecode script from `[ebp+0x20]` (script pointer)
- **Script pointer for job 56 = 0x1F4** (pushed at 0x4C247B)
- Dispatches to handler based on opcode

### Potter Handler (0x46D53A → 0x46E1BE)
```c
// 0x46E1BE - Deposit function
good_id = tribe_house[house_index].output_good;  // +0x8
produce(good_id);  // Hardcoded in script!
```

**THE CORE ISSUE:** The potter handler's **bytecode script hardcodes good 24 (brick)** instead of reading the house's production list.

---

## Script/Bytecode System

### Job Dispatcher (0x4E21B7)
- Parses bytecode from script pointer `[ebp+0x20]`
- For job 56: script pointer = 0x1F4 (pushed at 0x4C247B)
- Opcode interpreter with switch table at 0x4E5307

### Job 56 Script
- **Script pointer:** 0x1F4 (index into script table)
- **Script table:** `.rdata` index 500 → `0x50454C` (in .rsrc section?)
- **Opcode 0x69** = "produce good X" with immediate good ID
- **Job 56 script likely copied from potter (job 24) → hardcodes good 24**

### Script Table
- `.rdata` base: 0xF3000
- Script table at `.rdata + 500*4 = 0xF37D0`
- Index 500 (job 56) → `0x50454C` (in .rsrc section, not directly accessible)

---

## UI Data Sources

### Building Info Panel
- **Reads:** `logicproduction` from house type data directly
- **Shows:** Good name from goods table
- **Status:** Should work (reads `logicproduction 66` → "Węgiel")

### Worker Assignment UI
- **Reads:** `jobEnablesGood`/`jobDefaultGood` from tribetypes
- **Validates:** Hardcoded job whitelists (5 functions, all patched)
- **Shows:** Enabled goods for selected worker job
- **Was broken:** Job 56 excluded from all 5 validation lists
- **Now patched:** All 5 validation functions accept job 56

### Storage/HQ UI
- **Reads:** `logicstock` from storehouse (logictype 1)
- **Shows:** Goods with `logicstock > 0`
- **Storehouse has:** `logicstock 66 150 0` (added)

---

## Current Patches Summary (596 Total)

### Core Engine Limits
| Count | Purpose |
|-------|---------|
| 3 | Loader guards (logicproduction, goodtypes, toProduceGoodNeedHouse) |
| 3 | Goods-table loops (name search, active goods, production calc) |
| 1 | Actor depot check (job 56) |
| 1 | Job 56 dispatcher → potter handler |
| 1 | Tribe house init cave (copies output good) |
| 3 | Actor/depot checks |
| 1 | Job 56 dispatcher patch |

### UI Validation (NEW - 5 patches)
| RVA | Original | Patched | Description |
|-----|----------|---------|-------------|
| 0x44181C | `cmp eax, 0x3A` | `cmp eax, 0x38` | UI list 1 |
| 0x44181F | `cmp eax, 0x39` | `cmp eax, 0x38` | UI list 2 |
| 0x441821 | `cmp eax, 0x41` | `cmp eax, 0x38` | UI list 3 |
| 0x468A64 | `cmp eax, 0x39` | `cmp eax, 0x38` | UI list 4 |
| 0x468A69 | `cmp eax, 0x3A` | `cmp eax, 0x38` | UI list 4 cont. |

### Data Files
- `Data\logic\goodtypes.ini` - 66 goods ✅
- `Data\logic\jobtypes.ini` - 57 jobs ✅
- `Data\logic\vehicletypes.ini` ✅
- `Data\logic\houses.ini` - **COPIED** with coal production ✅
- `Data\logic\tribetypes.ini` - 5 tribes with coal wiring ✅

---

## Critical Gaps & Root Causes

### 1. **Potter Handler Bytecode Hardcodes Good 24** 🔴
- **Location:** Job 56 script (index 500 in script table)
- **Issue:** Bytecode `0x69 0x18 0x00` = "produce good 24"
- **Fix Needed:** Patch script bytecode `0x18` → `0x42` (66)
- **Location:** Script table index 500 → find actual bytecode location

### 2. **Worker UI Validation Hardcoded Lists** ✅ FIXED
- 5 validation functions had hardcoded job whitelists excluding job 56
- **PATCHED** all 5 functions to accept job 56 (0x38)

### 3. **Missing houses.ini in Data\logic\** ✅ FIXED
- Was only in `CN.PLMOD\types\houses.ini`
- Engine loads from `Data\logic\houses.ini`
- **FIXED:** Copied with `logicproduction 66`

### 4. **Goods-Table Loop 4 (0x45FAFA) Unpatched** 🟡
- Uses stack arrays (66 + 102 entries)
- Extending bound would overflow stack
- **DECISION:** Don't patch - may not be needed for coal

### 5. **toProduceGoodNeedHouse Map Not Relocated** 🟡
- 66 entries × 8 bytes at 0x1492C
- Not relocated to 127 entries
- Good 66 entry added but map may silently drop it

---

## Action Plan

### Immediate (Next 30 min)
1. **Find job 56 script bytecode** - locate script table entry 500, find `0x69 0x18 0x00` pattern
2. **Patch script bytecode** `0x18` (24) → `0x42` (66)
3. **Test** - should produce coal

### Short Term (Next Session)
1. **Verify UI integration** - building panel, worker UI, storage all show coal
2. **Test production** - Smolarz consumes wood, produces coal
3. **Verify storage** - coal appears in Smolarz output + HQ stockpile

### Medium Term
1. **Make potter handler generic** - read `global_house+0x488[0]` instead of script
2. **Relocate toProduceGoodNeedHouse map** to 127 entries
3. **Document all findings** in this file for future buildings

---

## Key Addresses Reference

| Address | Description |
|---------|-------------|
| 0x400000 | Image base |
| 0x40B00C | Good name search function |
| 0x415403 | logictype handler |
| 0x41575C | logicstock handler |
| 0x41581D | logicproduction handler |
| 0x415E8A | Goods init loop (bound 0x2CB0 - CRASH if patched) |
| 0x41581D | logicproduction handler (guard at 0x415831) |
| 0x4159EF | goodtypes validator (guard at 0x4159F1) |
| 0x414271 | toProduceGoodNeedHouse handler |
| 0x414289 | toProduceGoodNeedHouse house guard |
| 0x414292 | toProduceGoodNeedHouse good guard (patched) |
| 0x41595F | goods alloc (mov esi, 0x35A0) |
| 0x435CD7 | Active goods loop bound |
| 0x456168 | Production calc loop bound |
| 0x45FAFA | Stack array loop (DON'T PATCH) |
| 0x4E21B7 | Job dispatcher |
| 0x4E21D3 | Script pointer for job 56 (0x1F4) |
| 0x46D53A | Potter handler entry |
| 0x46E1BE | Potter deposit function |
| 0x4E21B7 | Job dispatcher |
| 0x4C23D8 | Runtime production loop |
| 0x4C247B | Push script pointer 0x1F4 for job 56 |
| 0x6BD36 | Job 56 dispatcher patch |
| 0x6BDC1 | Potter handler entry point |

---

## Files to Maintain

| File | Purpose |
|------|---------|
| `etapa_gen/patches_ext.h` | Runtime patches (596) |
| `Data/logic/goodtypes.ini` | 66 goods |
| `Data/logic/jobtypes.ini` | 57 jobs |
| `Data/logic/vehicletypes.ini` | Vehicles |
| `Data/logic/houses.ini` | 127 house types |
| `CN.PLMOD/tribetypes12/tribetypes.ini` | 5 tribes wiring |
| `etapc/src/EtapC.cpp` | Patch application logic |
| `etapc/build.bat` | Build script |

---

*Document maintained as living RE reference. Update after each breakthrough.*