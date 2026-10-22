//! Engine structures for CN.PLMOD.exe (Knights & Merchants type).
//! ImageBase = 0x400000, 32-bit PE, no ASLR.
//! All VA offsets map to addresses documented in .ai/docs/re/re_engine_comprehensive.md
//! and .ai/docs/re/re_structures.md.

/// Global base addresses (VA).
pub mod globals {
    pub const ELEM_BASE: usize = 0x510_BC4;      // [base] + player * 0x4A80
    pub const TRIBE_BASE: usize = 0x511_200;     // [base] + tribe * 0x1AE08
    pub const HOUSE_TYPES: usize = 0x511_3A0;    // [base] + type * 0x624
    pub const GOOD_TYPES: usize = 0x511_420;     // [base] + good * 0xD0
    pub const BUILDINGS: usize = 0x510_BD0;      // [base] + idx * 0x7E0
    pub const TRIBE_HOUSE: usize = 0x510_BE0;    // [base] + tribe * 0x54C; +0x8 = output good ID
    pub const BUILDING_INSTANCES: usize = 0x568_C0C; // [base] + idx * 0x8BC (player building instances)
    pub const SINGLETON: usize = 0x511_71C;      // obcy menedżer (NIE element aktora)
}

/// Strides (rozszerzone po patchu ID 42 -> 127).
pub mod strides {
    pub const ELEM: usize = 0x4A80;   // was 0x1278 / 0x42
    pub const TRIBE: usize = 0x1AE08; // was 0x3126 / 0x37
    pub const HOUSE_TYPE: usize = 0x624;
    pub const GOOD_TYPE: usize = 0xD0;
    pub const BUILDING: usize = 0x7E0;
    pub const TRIBE_HOUSE: usize = 0x54C;
    pub const BUILDING_INSTANCE: usize = 0x8BC;
}

/// Table sizes after extension (good 66 = coal).
pub mod limits {
    pub const GOODS_COUNT: usize = 127;   // was 66
    pub const HOUSE_TYPES_COUNT: usize = 127; // was 55
    pub const PRODUCTION_LIST_MAX: usize = 20; // 0x14
    pub const STOCK_ENTRIES_MAX: usize = 66;
}

/// Good ids (relevant).
pub mod good {
    pub const WOOD: u32 = 5;   // drewno — input for charcoal
    pub const COAL: u32 = 66;  // węgiel — output of charcoal burner
    pub const BRICK: u32 = 24; // cegła — mirrors coal recipe (atomic 52)
}

/// Job ids.
pub mod job {
    pub const CHARCOAL_BURNER: u32 = 56; // smolarz
}

/// House type ids (logictype).
pub mod house_type {
    pub const SCHOOL: u32 = 38;   // szkoła — obsługiwana przez FUN_00473461 (case 38)
    pub const BARRACKS: u32 = 39; // koszary — obsługiwana przez FUN_00473461 (case 39)
    pub const CHARCOAL_BURNER: u32 = 57; // chałupa węglarska / work charcoal burner — NOT handled
}

/// ---------------------------------------------------------------------------
/// Data structures
/// ---------------------------------------------------------------------------

/// Rekord typu budynku (house_type).
/// VA: DAT_005113A0 + type * 0x624, size = 0x624 bytes.
#[repr(C)]
pub struct HouseType {
    pub category: u32,                 // +0x000
    pub output_good: u32,              // +0x008 — good produced by this building type
    // +0x00C..+0x01A reserved / other fields
    // +0x01B..+0x020 stock entries (3 bytes each)
    pub stock_count: u32,              // +0x060 — number of stock entries
    pub stocks: [StockEntry; 12],      // +0x064 — 12 entries x 12 bytes (good, qty, flag)
    pub stock_revmap: [i32; 66],       // +0x37C — good -> stock index, init -1
    pub production_count: u32,         // +0x484 — number of production recipes (max 20)
    pub production_list: [u32; 20],    // +0x488 — output good IDs
    pub production_revmap: [i32; 66],  // +0x4D8 — good -> production list index
    pub unknown_5e4: u32,              // +0x5E4
    pub zeroed: u32,                   // +0x620
    // padding to 0x624
}

#[repr(C)]
pub struct StockEntry {
    pub good: u32,     // +0x00
    pub qty: u32,      // +0x04
    pub flag: u32,     // +0x08
    // 12 bytes total
}

/// Instancja budynku (building instance).
/// VA: DAT_00510BD0 + idx * 0x7E0 (or DAT_00568C0C + idx * 0x8BC for player instances).
#[repr(C)]
pub struct Building {
    pub _pad0: [u8; 0x14],
    pub house_type: u32,               // +0x014 — type id from houses.ini
    pub _pad1: [u8; 0x18 - 0x14 - 4],
    pub _pad2: [u8; 0x200 - 0x20],
    pub built_flag: u32,               // +0x200 — != 0 when building is complete (pcVar15[2000])
    pub _pad3: [u8; 0x60 - 0x200 - 4],
    pub stock_count: u32,              // +0x060
    pub stocks: [u8; 0],               // +0x064 — variable
    // +0x644: owner_entries[20 * 4] — FUN_0043267F searches for owner entry
    pub _pad4: [u8; 0x7E0 - 0x644 - 80],
}

/// Rekord typu towaru (good_type).
/// VA: DAT_00511420 + good * 0xD0, size = 0xD0 bytes.
#[repr(C)]
pub struct GoodType {
    pub name: *const i8,               // +0x000
    // +0x020 landscapetype
    // +0x030 isProducedOnMapFlag
    // +0x031 isProducedInHouseFlag
    // +0x050 productionInputGoods
    pub _pad: [u8; 0xD0 - 8],
}

/// Plemie (tribe record).
/// VA: DAT_00511200 + tribe * 0x1AE08 (extended).
#[repr(C)]
pub struct Tribe {
    pub _pad: [u8; 0x6740],
    pub threshold: [u32; 66],          // +0x6740 — tribe threshold per good
    pub threshold2: [u32; 66],         // +0x6820 — second threshold (added when local_8 != 0)
    pub _pad2: [u8; 0x1AE08 - 0x6820 - 264],
}

/// Jednostka (unit).
#[repr(C)]
pub struct Unit {
    pub _pad0: [u8; 0x14],
    pub tribe: u32,                    // +0x14
    pub job: u32,                      // +0x18 — profession (56 = charcoal burner)
    pub selected_good: u32,            // +0x1C
    pub _pad1: [u8; 0x158 - 0x1C - 4],
    pub production_timer: u32,         // +0x158 — compared with tribe threshold
    pub flag_15c: u8,                  // +0x15C — set by patch 0x4A1C0
    pub _pad2: [u8; 0x195 - 0x15C - 1],
    pub can_produce: [u8; 66],         // +0x195 — "can produce good" flags
    pub _pad3: [u8; 0x21C - 0x195 - 66],
    pub job_good_status: [u8; 66],     // +0x21C — 0, 0xB, 0xC, 0xD, 0xE
    pub _pad4: [u8; 0xA68 - 0x21C - 66],
    pub ui_state: u32,                 // +0xA68 — 5 / 6 in building interaction
    pub interaction_state: u32,        // +0xACC — 0 / 2 / 4
    pub interaction_good: u32,         // +0xAD0
    pub selected_good_interact: u32,   // +0xAD4 — compared with building+8 / +0x10
    pub _pad5: [u8; 0xB34 - 0xAD4 - 4],
    pub building_idx: u32,             // +0xB34 — building this unit is assigned to
    pub _pad6: [u8; 0xB44 - 0xB34 - 4],
    pub house_list_idx: u32,           // +0xB44 — FUN_0041C61E(DAT_00511728, +0xB44)
    pub tribe_idx: u32,                // +0xB48 — * 0x54C + DAT_00510BE0
    pub _pad7: [u8; 0xB4C - 0xB48 - 4],
    pub _pad8: [u8; 0xB51 - 0xB4C - 4],
    pub ui_flag: u8,                   // +0xB51 — affects +0x368 (0x15 vs 1)
}

/// Kontekst UI budynku (używany przez FUN_0046D53A, FUN_0046E1BE).
#[repr(C)]
pub struct BuildingUiCtx {
    pub _pad0: [u8; 0x368],
    pub field_368: u32,                // +0x368 — 0x15 or 1 (depends on +0xB51 flag)
    pub field_36c: u32,                // +0x36C — result state (0/1/3)
    pub field_374: u32,                // +0x374 — sub-state (1/2/3/0xE/0xF)
    // ...
}

/// ---------------------------------------------------------------------------
/// Global mutable state (accessed via raw pointers in pseudocode)
/// ---------------------------------------------------------------------------

extern "C" {
    pub static mut ELEM_BASE: *mut u8;           // 0x510BC4
    pub static mut TRIBE_BASE: *mut u8;          // 0x511200
    pub static mut HOUSE_TYPES_PTR: *mut HouseType; // 0x5113A0
    pub static mut GOOD_TYPES_PTR: *mut GoodType;   // 0x511420
    pub static mut BUILDINGS_PTR: *mut Building;    // 0x510BD0
    pub static mut TRIBE_HOUSE_PTR: *mut u8;        // 0x510BE0
    pub static mut BUILDING_INSTANCES_PTR: *mut u8; // 0x568C0C
    pub static mut SINGLETON: *mut u8;              // 0x51171C
}
