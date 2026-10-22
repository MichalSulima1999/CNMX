# Reverse Engineering Findings - CN.PLMOD.exe

**Base Address:** 0x400000 (no ASLR)  
**RVA = VA - 0x400000**

---

## Goods Table

| Field | Value |
|-------|-------|
| Global table base | `[0x511420]` |
| Record stride | 0xD0 bytes |
| Original count | 66 goods (0x35A0 / 0xD0 = 66) |
| Original alloc size | 0x35A0 |
| Extended alloc size | 0x6730 (127 goods) |
| Extended count | 127 |

### Goods Loader (VA 0x41592E)
- Alloc at 0x41595F: `mov esi, 0x35A0` → patched to 0x6730
- Validator at 0x4159EF: `cmp eax, 0x42; jge skip` → imm at 0x4159F1 patched to 0x7F
- Record index = good type (type 66 → record 66)
- Key fields: +0=name, +0x20=landscapetype, +0x30=isProducedOnMapFlag, +0x31=isProducedInHouseFlag, +0x50=productionInputGoods

---

## House Type Table

| Field | Value |
|-------|-------|
| Global table base | `[0x5113A0]` |
| Record stride | 0x624 bytes |
| Original count | 55 types |
| Extended count | 127 types (validator 0x37→0x7F) |
| Alloc size | 0x30BDC (was 0x151BC) |

### House Record Layout (global, 0x624 bytes)
| Offset | Size | Description |
|--------|------|-------------|
| +0x60 | 4 | stock entry count |
| +0x64 | 12*66 | stock entries {good, qty, flag} |
| +0x37C | 4*66 | stock reverse map (good → index), init -1 |
| +0x484 | 4 | production count (max 0x14=20) |
| +0x488 | 4*20 | production list (good IDs) |
| +0x4D8 | 4*66 | production reverse map (good → list index) |
| +0x5E4 | 4 | unknown field |
| +0x620 | 4 | zeroed per-record |

### Tribe House Array (per tribe, stride 0x54C)
| Base | `[0x510BE0]` |
| Stride | 0x54C |
| Key offset | +0x8 = output good ID (copied from global_house+8 on build) |

### logictype Handler (VA 0x415403)
- Validates type < 0x37 (patched to 0x7F)
- Sets `esi = house_table + idx*0x624`
- Fills +0x37C with 66 dwords of -1 (`push 0x42; rep stosd`)

### logicstock Handler (VA 0x41575C)
- Max 66 entries: `cmp [esi+0x60], 0x42; je skip`
- Good ID guard: `cmp edi, 0x42; jg skip` (good 66 ACCEPTED)
- Writes reverse map: `mov [esi + edi*4 + 0x37C], eax` ← **COLLISION for good 66!**
  - +0x37C + 66*4 = +0x484 = production count

### logicproduction Handler (VA 0x41581D)
```
cmp [esi+0x484], 0x14; je skip
parse int → eax
cmp eax, 0x42; jge skip       @0x415831 (imm 0x415833 patched to 0x7F)
mov [esi+ecx*4+0x488], eax    ; production list[count] = good
mov [esi+eax*4+0x4D8], ecx    ; production revmap[good] = count
inc [esi+0x484]               ; count++
```
- Production revmap collision: good 66 → +0x4D8 + 66*4 = +0x5E0 (near +0x5E4)

---

## Jobs Table

| Field | Value |
|-------|-------|
| Global table base | `[0x511520]` (?) |
| Record stride | 0x88 bytes |
| Original count | 0x58 (88) |
| Extended count | 127 (validator 0x58→0x7F) |
| Job 56 | "Smolarz" - name from hook_GetJobString, not data |

---

## Goods-Table Iteration Loops (bound 0x35A0 = 66 goods)

| VA | RVA | Function | Context | Status |
|----|-----|----------|---------|--------|
| 0x40B00C | 0xB00C | name search | linear search via strcmp | **SAFE to patch** (0x35A0 at 0x40B02C) |
| 0x415E8A | 0x15E8A | goods init/UI | bound 0x2CB0 (55) at 0x415EB0 | **CAUSES CRASH if patched** - calls 0x47FEF0 which accesses external array |
| 0x435CD7 | 0x35CD7 | active goods | bound 0x35A0, reads parallel byte array at [esi+eax+0x195] | **PATCHED** (0x35A0→0x6730) |
| 0x456168 | 0x56168 | production calc | bound 0x35A0, calls house-stock lookup, writes [esi+eax*4+0x71C] | **PATCHED** (0x35A0→0x6730) |
| 0x45FAFA | 0x5FAFA | build local arrays | bound 0x35A0, `sub esp,0x2A4`, 66-slot + 102-slot local arrays | **UNSAFE** - would overflow stack |

---

## Production Runtime

### House Production Loop (VA 0x4C23D8)
- Iterates tribe houses
- Reads production count at `house+0x484`
- Reads production list at `house+0x488`
- Calls 0x4E21B7 (job dispatcher)

### Job Dispatcher (VA 0x4E21B7)
- Switch on job type (eax)
- Job 56 (Smolarz) → routes to potter handler (index 192 in lookup table)
- Patch at 0x6BD36: `cmp eax,0x2F; ja 0x46BDC1` → redirects job 56 to potter handler

### Potter Handler (VA 0x46D53A)
- Reads `tribe_house+8` (output good ID)
- **BUG:** `tribe_house+8` never set for Smolarz (remains 0)
- **FIX:** Patched logicproduction handler to write good ID to `global_house+8` (copied to tribe_house+8 on build)

### Depot Check (VA 0x45C6FC)
- `test al, 1` / `jnz` - checks actor flag at +0xB84 bit 8
- Patched to `mov al, 1` to force pass for job 56

---

## toProduceGoodNeedHouse (VA 0x414271)
- Writes `map[good] = house` at `[esi + edi*8 + 0x1492C]`
- Guards: house < 0x37 (patched), good < 0x42 (patched to 0x7F)
- Map size: 66*8 bytes = 0x210 - NOT relocated
- Only writer found in .text (no readers)

---

## Critical Collisions for Good 66

1. **Stock reverse map** at +0x37C + 66*4 = +0x484 (production count)
   - Workaround: `logicproduction 66` BEFORE `logicstock 66 15 0`
   - Final: production count = 1 = coal stock index

2. **Production reverse map** at +0x4D8 + 66*4 = +0x5E0
   - Writes 0 (list index) at +0x5E0 (adjacent to live field +0x5E4)
   - Likely harmless

---

## Data Files (override .cif)

| File | Purpose |
|------|---------|
| `Data/logic/jobtypes.ini` | 649 lines, job 56 = Smolarz |
| `Data/logic/vehicletypes.ini` | Vehicle types |
| `Data/logic/goodtypes.ini` | 66 goods, good 66 = coal (mirrors brick) |
| `Data/text/pol/strings/gameobjects/goods.ini` | Good 66 name = "Węgiel" |

### goodtypes.ini Format
- Header: `<CULTURES_CIF_BEGIN><03FD><NNNNNNNN>` where N = body line count (hex, 8 digits)
- Body: `[goodtype]` blocks, `%01%`→`[`, `%02%` stripped
- Footer: `<CULTURES_CIF_END>`
- Encoding: CP1250, CRLF

---

## Patch Table (patches_ext.h)

Format: `{ RVA, offset, size, { new_bytes[8] }, "description" }`
- Applier writes at `base + RVA + offset`
- 580 total patches, 0 overlaps

### Key Patches for Good 66 / Job 56 / House 57
| RVA | Offset | Size | New Bytes | Description |
|-----|--------|------|-----------|-------------|
| 0x15833 | 0 | 1 | 7F | logicproduction good guard 0x42→0x7F |
| 0x159F1 | 0 | 1 | 7F | goodtypes validator 0x42→0x7F |
| 0x14292 | 2 | 1 | 7F | toProduceGoodNeedHouse good guard 0x42→0x7F |
| 0x56168 | 0 | 4 | 30 67 00 00 | production calc loop 0x35A0→0x6730 |
| 0x35CD7 | 0 | 4 | 30 67 00 00 | active goods loop 0x35A0→0x6730 |
| 0xB02C | 0 | 4 | 30 67 00 00 | name search loop 0x35A0→0x6730 |
| 0x15843 | 0 | 6 | 89 86 08 00 00 00 | logicproduction: write good to global_house+8 |
| 0x5C6FC | 0 | 1 | B0 01 | force depot check pass (actor flag) |
| 0x6BD36 | 2 | 4 | 85 00 00 00 | job 56 dispatcher → potter handler |

---

## Tribetypes Wiring (CN.PLMOD/tribetypes12/tribetypes.ini)
Per tribe (5 tribes):
- `allowgood 66`
- `allowhouse 57`
- `jobEnablesGood 56 66`
- `jobDefaultGood 56 66`
- `toProduceGoodNeedHouse 66 57` (added)

---

## Smolarz Hut Definition (CN.PLMOD/types/houses.ini)
```ini
[logichousetype]
debugname "work charcoal burner"
logictype 57
logicmaintype 3
logicworker 56 1
logicstock 5 1 1        ; input: wood (good 5), qty 1, flag 1
logicproduction 66      ; output: coal (good 66) - MUST BE BEFORE logicstock 66
logicstock 66 15 0      ; output stock: coal, cap 15, flag 0
debugcolor 0 0 100
```

---

## Good 66 Definition (Data/logic/goodtypes.ini)
```
[goodtype]
name "coal"
type 66
landscapetype 50
isInputGoodFlag 0
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 5
atomicForProduction 52
```
- Mirrors brick (type 24) recipe: input wood (5), atomic 52

---

## Outstanding Issues

1. **Storage UI doesn't show coal** - goods-loop at 0x415E8E crashes if bound extended. Need to find safe iteration path.

2. **Production rev-map collision** - good 66 writes to +0x5E0, need to verify no runtime reads.

3. **toProduceGoodNeedHouse map** - 66-entry only, not relocated. May silently ignore good 66.

---

## Next Investigation Targets

- [ ] Find storage UI goods iteration (likely 0x435CD7 or 0x456168 - already patched)
- [ ] Check if 0x415E8E is called at startup only (crash) or also at runtime
- [ ] Verify 0x4E21B7 actually produces goods (not just dispatches)
- [ ] Search for hardcoded good 24 in potter handler
- [ ] Find tribe_house+8 copy-on-build code