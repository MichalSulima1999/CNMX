//! Production logic pseudocode for CN.PLMOD.exe.
//! Models the charcoal-burner production chain (wood -> coal) and the
//! building-tick gap that prevents type-57 buildings from producing.

use crate::engine_structs::*;
use crate::engine_structs::globals::*;
use crate::engine_structs::strides::*;
use crate::engine_structs::limits::*;
use crate::engine_structs::good::*;
use crate::engine_structs::job::*;
use crate::engine_structs::house_type::*;

/// Result of a production attempt.
pub enum ProductionResult {
    NoBuilding,      // no building assigned
    NotHandled,      // building type not handled by unit tick (e.g. 57)
    TimerRunning,    // production timer not yet at threshold
    Produced { good: u32 }, // produced output good
    NoInputs,        // unit cannot produce (gate failed)
}

/// Simulate one unit tick for a charcoal burner (job 56) in a charcoal burner building (type 57).
///
/// In the real engine, `FUN_00473461` returns early for type 57, so this always
/// returns `NotHandled` unless the logictype is changed to 38 (see re_production_pipeline.md).
pub fn tick_charcoal_burner(
    unit: &Unit,
    building: &Building,
    house_type: &HouseType,
    tribe_threshold: u32,
) -> ProductionResult {
    // 1. Building type gate (FUN_00473461: SUB EDX,0x26 / DEC EDX / JNZ return)
    if building.house_type != house_type::SCHOOL as u32
        && building.house_type != house_type::BARRACKS as u32
    {
        // Type 57 (charcoal burner) falls here -> NOT HANDLED
        return ProductionResult::NotHandled;
    }

    // 2. Output good comes from logicproduction, NOT logictype.
    //    house_type.production_list[0] == COAL (66), production_count == 1.
    if house_type.production_count == 0 {
        return ProductionResult::NoBuilding;
    }
    let output_good = house_type.production_list[0];

    // 3. Timer vs tribe threshold (FUN_00473461 timer logic)
    if unit.production_timer < tribe_threshold {
        return ProductionResult::TimerRunning;
    }

    // 4. Gate: can unit produce this good? (FUN_0042DA65)
    if !unit.can_produce[output_good as usize] != 0 {
        // Actually: can_produce[good] != 0
        return ProductionResult::NoInputs;
    }

    // 5. Consume input (wood, good 5), produce output (coal, good 66).
    //    NO CODE IN ENGINE DOES THIS for type 57 — must be added via patch/code cave.
    ProductionResult::Produced { good: output_good }
}

/// Hypothesis fix: change charcoal burner logictype 57 -> 38 in houses.ini.
/// Then `tick_charcoal_burner` proceeds past the building-type gate and the
/// unit-tick production chain runs (sets +0x195[66], calls FUN_0044A0D9/FUN_0044B2FA).
///
/// Required data wiring (tribetypes.ini per tribe):
///   allowgood 66
///   allowhouse 57
///   jobDefaultGood 56 66
///   jobEnablesGood 56 66
///   jobEnablesJob 56 56
///   toProduceGoodNeedHouse 66 57
///
/// Required data (houses.ini, type 57):
///   logicworker 56 1
///   logicstock 5 1 1        ; input: wood
///   logicproduction 66     ; output: coal  (MUST be before logicstock 66 — revmap collision)
///   logicstock 66 15 0     ; output stock: coal cap 15
///
/// Patches (patches_ext.h) needed for ID 66:
///   RVA 0x15833: logicproduction good guard 0x42 -> 0x7F
///   RVA 0x159F1: goodtypes validator 0x42 -> 0x7F
///   RVA 0x15843: logicproduction write good to global_house+8
///   RVA 0x6BD36: job 56 dispatcher -> potter handler
///   RVA 0x5C6FC: force depot check pass
///   RVA 0xB02C / 0x35CD7 / 0x56168: loops 0x35A0 -> 0x6730 (66 -> 127 goods)

/// Missing piece the engine does NOT have: a "building production tick"
/// that iterates all player buildings, checks logicproduction, consumes
/// input goods, and creates output goods. Production is currently driven
/// solely by the unit tick (FUN_00473461). Candidates for building tick:
///   FUN_0047FFC0, FUN_0048EA9F, FUN_00494F01, FUN_00495E0C
///   (all reference DAT_00568C0C, stride 0x8BC).
