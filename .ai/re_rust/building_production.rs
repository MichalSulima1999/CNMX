//! Building production and resource management pseudocode for CN.PLMOD.exe.
//! Based on REA (Ghidra 12.1.4) analysis of CN.PLMOD.exe.
//! Key discovery: production is handled by FUN_00494f01 (building operation)
//! called from map renderer FUN_0049067f, NOT by a separate building tick.

use crate::engine_structs::*;
use crate::engine_structs::globals::*;
use crate::engine_structs::strides::*;
use crate::engine_structs::limits::*;
use crate::engine_structs::good::*;

// ---------------------------------------------------------------------------
// DAT_00568CA8 — Building type data table (stride 0xD0, like good_types)
// ---------------------------------------------------------------------------
// This is a parallel table to house_types (0x5113A0, stride 0x624).
// DAT_00568CA8 + building_type * 0xD0 contains production/resource data.
extern "C" {
    pub static mut DAT_00568CA8: *mut u8;   // building type data table
    pub static mut DAT_00568C0C: *mut u8;   // player building instances (stride 0x8BC)
    pub static mut DAT_00510BD0: *mut u8;   // global building instances (stride 0x7E0)
    pub static mut DAT_00511698: *mut u8;   // sprite table 1
    pub static mut DAT_005116A0: *mut u8;   // sprite table 2
    pub static mut DAT_005116A4: *mut u8;   // sprite table 3
    pub static mut DAT_00568CB0: *mut u8;   // other flags table
    pub static mut DAT_0055529C: *mut u8;   // other flags table (0x0E case)
}

// ---------------------------------------------------------------------------
// FUN_0042BCAE — Table access helper (tab[index])
// Used by sprite functions FUN_0042f710/754/776
// ---------------------------------------------------------------------------
extern "C" {
    pub fn fun_0042bcae(table: *mut u8, index: u32) -> i32 { 0 }
}

// ---------------------------------------------------------------------------
// FUN_0042f710 — Sprite access, table 1 (VA 0x42F710)
// idx * 2 (+1 if flag > 1) into DAT_00511698
// ---------------------------------------------------------------------------
pub unsafe fn fun_0042f710(idx: i32, flag: u32) -> i32 {
    if DAT_00511698.is_null() {
        return 0;
    }
    let mut u_var1 = (idx as u32) * 2;
    if 1 < flag {
        u_var1 = u_var1 + 1;
    }
    fun_0042bcae(DAT_00511698, u_var1)
}

// ---------------------------------------------------------------------------
// FUN_0042f754 — Sprite access, table 2 (VA 0x42F754)
// idx * 2 (+1 if flag > 1) into DAT_005116A0
// ---------------------------------------------------------------------------
pub unsafe fn fun_0042f754(idx: i32, flag: u32) -> i32 {
    if DAT_005116A0.is_null() {
        return 0;
    }
    let mut u_var1 = (idx as u32) * 2;
    if 1 < flag {
        u_var1 = u_var1 + 1;
    }
    fun_0042bcae(DAT_005116A0, u_var1)
}

// ---------------------------------------------------------------------------
// FUN_0042f776 — Sprite access, table 3 (VA 0x42F776)
// idx * 2 (+1 if flag > 1) into DAT_005116A4
// ---------------------------------------------------------------------------
pub unsafe fn fun_0042f776(idx: i32, flag: u32) -> i32 {
    if DAT_005116A4.is_null() {
        return 0;
    }
    let mut u_var1 = (idx as u32) * 2;
    if 1 < flag {
        u_var1 = u_var1 + 1;
    }
    fun_0042bcae(DAT_005116A4, u_var1)
}

// ---------------------------------------------------------------------------
// FUN_0042f798 — Sprite for building/good (VA 0x42F798)
// Calls FUN_0047FFC0 (building instance addr), then FUN_0042f776
// ---------------------------------------------------------------------------
pub unsafe fn fun_0042f798(building_idx: i32, good_idx: u32, flag: u32) -> i32 {
    let bldg_inst = fun_0047ffc0(building_idx);
    if (bldg_inst != 0) && (good_idx < *(bldg_inst.add(0x18) as *const u32)) {
        return fun_0042f776(*(bldg_inst.add(good_idx as usize * 4) as *const i32), flag);
    }
    0
}

// ---------------------------------------------------------------------------
// FUN_0047FFC0 — Building instance address (VA 0x47FFC0)
// building_idx * 0x8BC + 0x3C + DAT_00568C0C
// ---------------------------------------------------------------------------
pub unsafe fn fun_0047ffc0(building_idx: i32) -> i32 {
    building_idx * 0x8BC + 0x3C + DAT_00568C0C as i32
}

// ---------------------------------------------------------------------------
// FUN_00495e0c — Building resource management / production (VA 0x495E0c)
// Called WITHIN FUN_00494f01 (not a separate tick).
// Manages counters in DAT_00568CA8 + type*0xD0 (NOT building+0x64 stocks).
// ---------------------------------------------------------------------------
pub unsafe fn fun_00495e0c(building_idx: i32) {
    // Building type data: type * 0xD0 + DAT_00568CA8
    let bldg_type_data = DAT_00568CA8.add(building_idx as usize * 0xD0);

    // Building instance: building_idx * 0x7E0 + DAT_00510BD0
    let bldg = building_idx as i32 * 0x7E0 + DAT_00510BD0 as i32;

    // Player building instance: house_type_idx * 0x8BC + DAT_00568C0C
    let house_type_idx = *(bldg.add(0x20) as *const i32);
    let p_bldg_inst = house_type_idx * 0x8BC + DAT_00568C0C as i32;

    // Value from player building instance: +0x1D8 + house_type_idx * 4
    let u_var5 = *(p_bldg_inst.add(0x1D8 + house_type_idx as usize * 4) as *const u32);

    // Pointer into player building instance: (house_type_idx + 0x26) * 0x34 + p_bldg_inst
    let p_u_var1 = p_bldg_inst.add((house_type_idx as usize + 0x26) * 0x34) as *mut u32;
    let u_var2 = *p_u_var1;

    // Value from building +0x7C8
    let i_var3 = *(bldg.add(0x7C8) as *const i32);
    let mut i_var3_clamped = i_var3;
    if i_var3 < 0 { i_var3_clamped = 0; }

    // Production coefficient: ((u_var5 - building_idx) * u_var2) / u_var5
    let u_var4 = ((u_var5.wrapping_sub(building_idx as u32)).wrapping_mul(u_var2))
        .wrapping_div(u_var5);
    if (i_var3_clamped < (i_var5 as i32)) && (u_var4 == 0) && (u_var2 != 0) {
        // u_var5 here is the original, not clamped — using u_var5
    }

    let u_var5_count = *(bldg_type_data as *const u32);  // production/stock count

    if u_var4 < u_var5_count {
        // CONSUME resource — decrease counter
        let mut u_var5_3: u32 = 0;
        if u_var2 != 0 {
            loop {
                if (u_var5_3 < 200) && (*(bldg_type_data.add(u_var5_3 as usize + 4) as *const i8) != 0) {
                    *(bldg_type_data.add(u_var5_3 as usize + 4) as *mut i8) = 0;  // clear flag
                    *(bldg_type_data as *mut u32) = u_var5_count.wrapping_sub(1);  // decrease count
                    return;
                }
                u_var5_3 = u_var5_3.wrapping_add(1);
                if !(u_var5_3 < u_var2) { break; }
            }
        }
    } else if u_var5_count < u_var4 {
        // CREATE product — increase counter (random)
        let u_var6 = _rand();
        let u_var4_2 = *p_u_var1;
        let mut u_var9: u32 = 0;
        let mut u_var7: u32 = 0;
        if u_var4_2 != 0 {
            loop {
                if (u_var7 < 200) && (*(bldg_type_data.add(u_var7 as usize + 4) as *const i8) == 0) {
                    if u_var6.wrapping_rem(u_var2.wrapping_sub(u_var5_count)) <= u_var9 {
                        *(bldg_type_data.add(u_var7 as usize + 4) as *mut i8) = 1;  // set flag
                        *(bldg_type_data as *mut u32) = u_var5_count.wrapping_add(1);  // increase count
                        return;
                    }
                    u_var9 = u_var9.wrapping_add(1);
                }
                u_var7 = u_var7.wrapping_add(1);
                if !(u_var7 < u_var4_2) { break; }
            }
        }
    }
}

// ---------------------------------------------------------------------------
// FUN_0047E062 — Building type flags (VA 0x47E062)
// param_1 == 0x11: sets flag at DAT_00568CA8 + type*0xD0 + 0xCC
// ---------------------------------------------------------------------------
pub unsafe fn fun_0047e062(param_1: i32, _param_2: u32, param_3: i32, param_4: u32) {
    let b_var2 = param_4 as u8;
    if param_1 == 0x11 {
        if (param_4 >> 1 & 1) != 0 {
            *(DAT_00568CA8.add(param_3 as usize * 0xD0 + 0xCC) as *mut u8) = b_var2 & 1;
        }
    }
    // ... other cases for DAT_00568CB0, DAT_0055529C
}

// ---------------------------------------------------------------------------
// FUN_00494f01 — Building operation (VA 0x494F01)
// Main building operation called from map renderer FUN_0049067f.
// Calls FUN_00495e0c internally (address 0x495738 is within 0x494F01-0x495921).
// ---------------------------------------------------------------------------
pub unsafe fn fun_00494f01(
    building_idx: u32,
    _param_2: *mut u8,
    _param_3: *mut u32,
    _param_4: *mut u32,
    _param_5: i32,
    _param_6: *mut u8,
) {
    let bldg = DAT_00510BD0.add(building_idx as usize * 0x7E0);
    fun_004316d0(bldg as i32);

    let p_bldg_inst = DAT_00568C0C.add(
        (*(bldg.add(0x10) as *const i32) as usize) * strides::BUILDING_INSTANCE
    );

    let bldg_type_data = DAT_00568CA8.add(building_idx as usize * 0xD0);

    // Check built flag (+0x200)
    let built = *(bldg.add(0x200) as *const i8) != 0;

    if built {
        // FUN_0049A65E — production/content of building
        // fun_0049a65e(..., *(bldg.add(0xC)));

        // FUN_0049599B — something with building
        // fun_0049599b(building_idx, ...);

        // FUN_00495E0C is called WITHIN this function (not separately)
    }
}

// ---------------------------------------------------------------------------
// Extern stubs
// ---------------------------------------------------------------------------
extern "C" {
    pub fn fun_004316d0(_: i32) {}
    pub fn fun_0049a65e(_: i32, _: i32) -> i32 { 0 }
    pub fn fun_0049599b(_: u32, _: *mut u32) {}
    pub fn _rand() -> u32 { 0 }
}
