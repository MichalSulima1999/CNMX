//! Pseudocode in Rust for key CN.PLMOD.exe engine functions.
//! Based on Ghidra 12.1.4 decompilations (.ai/re_out/decomp_*.md).
//! These are NOT original source — they are a structured representation
//! to help modify the engine. VA addresses are documented in comments.

use crate::engine_structs::*;
use crate::engine_structs::globals::*;
use crate::engine_structs::strides::*;
use crate::engine_structs::limits::*;
use crate::engine_structs::good::*;
use crate::engine_structs::job::*;
use crate::engine_structs::house_type::*;

// ---------------------------------------------------------------------------
// FUN_00473461 — Unit tick / production (VA 0x473461)   [ROOT CAUSE]
//
// Handles ONLY building types 38 (school) and 39 (barracks).
// Type 57 (charcoal burner) -> early return: no timer, no +0x195[66], no production.
// ---------------------------------------------------------------------------
pub unsafe fn fun_00473461(this: *mut Unit, param_1: i32) {
    let bldg_type = *(BUILDINGS_PTR
        .add((*this).building_idx as usize * strides::BUILDING)
        .as_ref()
        .unwrap()
        .house_type as usize); // building_type at building+0x14

    let mut u_var6: u32 = 0;
    let mut local_8: i32 = 0;

    if bldg_type == house_type::SCHOOL as u32 {
        // case 38: read uVar6 and local_8 from building (+8, +0xC)
    } else if bldg_type == house_type::BARRACKS as u32 {
        // case 39: read uVar6 from tribe threshold
        local_8 = 0;
    } else {
        return; // TYPE 57 (charcoal burner) NOT HANDLED
    }

    if u_var6 != 0 {
        // Tribe threshold (NOTE: uses OLD imm 0x6B82, should be 0x8578 — patched at RVA 0x734E0)
        let tribe_offset = (*this).tribe as usize * 0x6B82; // OLD size!
        let u_var5 = *(TRIBE_BASE.add(0x6740 + (tribe_offset + u_var6 as usize) * 4) as *const u32);
        // if local_8 != 0 { u_var5 += *(TRIBE_BASE + 0x6820 + ...) }

        if (*this).production_timer < u_var5 {
            // increment timer
            if 10000i32 - param_1 < (*this).production_timer as i32 {
                (*this).production_timer = 10000;
            } else {
                (*this).production_timer = (*this).production_timer.wrapping_add(param_1 as u32);
            }
        } else {
            // timer reached threshold — perform action
            let _ = fun_0042d9d7(this, u_var6);
            (*this).flag_15c = 1; // +0x15C + good
            fun_0045bbaa(this, u_var6); // sound

            if local_8 != 0 && (*this).can_produce[local_8 as usize] == 0 {
                (*this).can_produce[local_8 as usize] = 1; // SET +0x195[good] = 1
                fun_0045bb51(this, local_8); // sound
            }
            (*this).production_timer = 0; // reset timer

            if (*this).job == u_var6 {
                fun_0044a0d9(this);   // set +0x195 for job goods
                fun_0044b2fa(this);   // set production status +0x21C
            } else {
                fun_00449f2f(this, u_var6); // UI: change selected good
            }
            fun_00449bda(this);

            if local_8 != 0 && fun_0042da65(this, local_8) {
                fun_0043e8a7(this, local_8); // UI: select good to produce
            }
        }
    }
}

// ---------------------------------------------------------------------------
// FUN_0044A0D9 — Set +0x195 for job goods (VA 0x44A0D9)
// Called ONLY from FUN_00473461 when job == u_var6.
// ---------------------------------------------------------------------------
pub unsafe fn fun_0044a0d9(this: *mut Unit) {
    // loop over goods in job block (+0xD8)
    // for each good:
    //   if FUN_0042d9a3 (tribe threshold) || race == 2:
    //     if good == 56: +0x1CD = 1, skip +0x195
    //     else if job == 16 && good == 57: +0x195[57] = 1 (fall through)
    //     else if job != 16: +0x195[good] = 1
    //   GOODS_A2[good] = 1; GOODS_B[good] = 1
}

// ---------------------------------------------------------------------------
// FUN_0042DA65 — Gate: can unit produce good? (VA 0x42DA65)
// ---------------------------------------------------------------------------
pub unsafe fn fun_0042da65(this: *mut Unit, good: u32) -> bool {
    (*this).can_produce[good as usize] != 0
        && fun_0042db20(this, good) // good on job block list
        && (fun_0042d848(this, good) // needforgood: unit has inputs
            || fun_0042d9a3(this, good) // tribe thresholds
            || /* race == 2 */ false)
}

// ---------------------------------------------------------------------------
// FUN_004316F3 — Building gate for good (revmap) (VA 0x4316F3)
// ---------------------------------------------------------------------------
pub unsafe fn fun_004316f3(ht: *const HouseType, good: u32, _flag: u8) -> bool {
    // uses stock revmap from house record (+0x37C)
    let idx = (*ht).stock_revmap[good as usize];
    idx >= 0
}

// ---------------------------------------------------------------------------
// FUN_00431F37 — Return revmap[good] from house record (VA 0x431F37)
// ---------------------------------------------------------------------------
pub unsafe fn fun_00431f37(ht: *const HouseType, good: u32) -> i32 {
    (*ht).stock_revmap[good as usize] // +0x37C + good*4
}

// ---------------------------------------------------------------------------
// FUN_0043267F — Search building+0x644 for owner entry (VA 0x43267F)
// Returns (index+100)*0x10 + building if found, 0 if not.
// ---------------------------------------------------------------------------
pub unsafe fn fun_0043267f(bldg: *mut Building, owner: u32) -> usize {
    let base = bldg as *mut u32;
    for i in 0..20usize {
        if *base.add(0x644 / 4 + i) == owner {
            return (i + 100) * 0x10 + bldg as usize;
        }
    }
    0
}

// ---------------------------------------------------------------------------
// FUN_004E21B7 — UI text renderer (VA 0x4E21B7)
// NOT a job dispatcher — previous docs were wrong.
// Renders text with tags: {newline}, tab (0x09), space (0x20), newline (0x0A/0x0D).
// ---------------------------------------------------------------------------
pub unsafe fn fun_004e21b7(
    _param_1: *mut u8,
    x: i32,
    start_pos: *mut u8,
    max_width: i32,
    _building_ctx: *mut u8,
    _font_ctx: *mut u8,
    text: *const u8,
) -> *mut u8 {
    if text.is_null() {
        return start_pos;
    }
    let mut pos = start_pos;
    let mut cursor_x = x;
    let mut p = text;

    loop {
        let b = *p;
        p = p.add(1);
        if b == 0 {
            return pos; // end of string
        }
        if b == 9 {
            // tab
            cursor_x += fun_00439633(_building_ctx, 0x69);
            continue;
        }
        if b == 10 || b == 0x0D {
            // newline
            if *p == 10 { p = p.add(1); }
            pos = pos.add(/* line_height */ 2); // *(building_ctx+8)+2
            cursor_x = x;
            continue;
        }
        if b == 0x20 {
            continue; // space
        }
        if b == 0x7B {
            // '{' tag
            // find '}', check "newline", etc.
        } else if b > 0x1F {
            // collect word, measure with FUN_0043967D, render with FUN_0040ECF9
            // wrap if max_width <= word_w + cursor_x
        }
    }
}

// ---------------------------------------------------------------------------
// FUN_0046D53A — Building interaction / potter handler (VA 0x46D53A)
// ---------------------------------------------------------------------------
pub unsafe fn fun_0046d53a(this: *mut BuildingUiCtx) {
    let list = fun_0041c61e(DAT_00511728, (*this).house_list_idx);
    let pi_begin = fun_0041c7f1(list);
    let pi_end = fun_0041c81f(list);

    if pi_begin == pi_end || pi_begin.is_null() {
        (*this).field_368 = 1;
        fun_0041c84f(list);
        return;
    }

    // validate buildings: exist, built (+0x200 == 0), category == 3 (+0x2C)
    // ...
    // state machine +0xACC (0/2/4) and +0xA68 (5/6)
    // state 6 + good 66: increment counter
    //   DAT_00510BC4 + 0x4A30 + (x*0x12A0 + building+0xC)*4 += 1

    fun_0041c84f(list);
}

// ---------------------------------------------------------------------------
// FUN_0046E1BE — Check building interaction availability (VA 0x46E1BE)
// ---------------------------------------------------------------------------
pub unsafe fn fun_0046e1be(this: *mut BuildingUiCtx, param_1: i32) -> u32 {
    if fun_0042c70a(this as *mut u8) == 0 {
        return 0;
    }
    if fun_0044bcf3(/* tribe_house */ 0 as *mut u8, *(this as *mut u32).add(1)) == 0 {
        return 0;
    }
    // ... range check FUN_0042aa24, FUN_0043b35f
    (*this).field_36c = 0;
    (*this).field_368 = if /* +0xB51 flag == 0 */ false { 0x15 } else { 1 };
    1
}

// ---------------------------------------------------------------------------
// FUN_004A693B — Building info panel renderer (VA 0x4A7297)
// ---------------------------------------------------------------------------
pub unsafe fn fun_004a693b(this: *mut u8, _param_1: *mut u8, _param_2: *mut u8) {
    // iterates 0xB sections of building info panel
    // section 0: name + progress bar
    // section 1: build cost
    // section 2: production (gfxgood icons)
    // section 5: stock list (iterates +0x60 count, +0x64 stocks)
    // section 10: employed units (iterates via FUN_0041cb32)
}

// ---------------------------------------------------------------------------
// FUN_004C227C — Building types list UI renderer (VA 0x4C23D8)
// ---------------------------------------------------------------------------
pub unsafe fn fun_004c227c(this: *mut u8, _param_1: *mut u8, _param_2: *mut i32) {
    // iterates player building instances (DAT_00568C0C, stride 0x8BC)
    // for each: get production_count (+0x484) and production_list (+0x488)
    // via FUN_00432A48, render list rows
}

// ---------------------------------------------------------------------------
// Parser stubs (file data)
// ---------------------------------------------------------------------------
pub unsafe fn fun_0041531d() { /* houses.ini parser */ }
pub unsafe fn fun_00413e7b() { /* tribetypes.ini parser */ }
pub unsafe fn fun_0041592e() { /* goodtypes.ini loader (alloc 0x35A0 -> 0x6730) */ }
pub unsafe fn fun_00415403() { /* logictype handler */ }
pub unsafe fn fun_0041575c() { /* logicstock handler */ }
pub unsafe fn fun_0041581d() { /* logicproduction handler */ }

// External function stubs referenced above
extern "C" {
    pub fn fun_0042d9d7(_: *mut Unit, _: u32) -> u32 { 0 }
    pub fn fun_0045bbaa(_: *mut Unit, _: u32) {}
    pub fn fun_0045bb51(_: *mut Unit, _: i32) {}
    pub fn fun_0044b2fa(_: *mut Unit) {}
    pub fn fun_00449f2f(_: *mut Unit, _: u32) {}
    pub fn fun_00449bda(_: *mut Unit) {}
    pub fn fun_0043e8a7(_: *mut Unit, _: i32) {}
    pub fn fun_0042db20(_: *mut Unit, _: u32) -> bool { false }
    pub fn fun_0042d848(_: *mut Unit, _: u32) -> bool { false }
    pub fn fun_0042d9a3(_: *mut Unit, _: u32) -> bool { false }
    pub fn fun_00439633(_: *mut u8, _: u32) -> i32 { 0 }
    pub fn fun_0043967d(_: *mut u8, _: *const u8) -> i32 { 0 }
    pub fn fun_0040ecf9(_: *mut u8, _: *mut u8, _: *mut u8, _: i32, _: *mut u8, _: *const u8) {}
    pub fn fun_004e6760(_: *const u8, _: *const u8, _: usize) -> i32 { 0 }
    pub fn fun_0042c70a(_: *mut u8) -> u32 { 1 }
    pub fn fun_0044bcf3(_: *mut u8, _: i32) -> u32 { 1 }
    pub fn fun_004411ca(_: *mut u8) -> *mut u16 { 0 as *mut u16 }
    pub fn fun_0043f8f3(_: i32) -> u32 { 0 }
    pub fn fun_0042aa24(_: u16, _: u16, _: i16, _: u16) -> u32 { 0 }
    pub fn fun_0043b35f(_: i32, _: *mut u16, _: *mut u16, _: *mut u16, _: i32) -> u32 { 0 }
    pub fn fun_0044124e(_: *mut u8, _: *mut u32) {}
    pub fn fun_0043f725(_: *mut u8, _: *mut u8) {}
    pub fn fun_0042aed3(_: *mut u16) -> u32 { 0 }
    pub fn fun_0043d54f(_: i32) -> i32 { 0 }
    pub fn fun_0041c61e(_: *mut u8, _: i32) -> *mut u8 { 0 as *mut u8 }
    pub fn fun_0041c7f1(_: *mut u8) -> *mut i32 { 0 as *mut i32 }
    pub fn fun_0041c81f(_: *mut u8) -> *mut i32 { 0 as *mut i32 }
    pub fn fun_0041c9dd(_: *mut i32) -> u32 { 0 }
    pub fn fun_0041c84f(_: *mut u8) {}
    pub fn fun_0042f710(_: i32, _: u32) {}
    pub fn fun_00432a48(_: i32, _: u32, _: u8, _: *mut i32) {}
    pub const DAT_00511728: *mut u8 = 0x511_728 as *mut u8;
}
