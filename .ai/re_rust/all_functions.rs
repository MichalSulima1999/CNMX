// ============================================================================
// Wszystkie zidentyfikowane funkcje CN.PLMOD.exe jako pseudokod Rust.
// Źródło: REA (Ghidra 12.1.4) procedure_pseudo_code.
// ============================================================================

use crate::engine_structs::*;
use crate::engine_structs::globals::*;
use crate::engine_structs::strides::*;
use crate::engine_structs::limits::*;
use crate::engine_structs::good::*;
use crate::engine_structs::job::*;
use crate::engine_structs::house_type::*;

// ============================================================================
// Extern declarations
// ============================================================================

extern "C" {
    pub fn fun_00473461(this: *mut Unit, param_1: i32);
    pub fn fun_0042d9d7(this: *mut Unit, good: u32) -> u32;
    pub fn fun_0045bbaa(this: *mut Unit, good: u32);
    pub fn fun_0045bb51(this: *mut Unit, good: i32);
    pub fn fun_0044b226(this: *mut Unit);
    pub fn fun_00449bda(this: *mut Unit);
    pub fn fun_0042da65(this: *mut Unit, good: u32) -> bool;
    pub fn fun_0042db20(this: *mut Unit, good: u32) -> u32;
    pub fn fun_0042d848(this: *mut Unit, good: u32) -> bool;
    pub fn fun_0042d9a3(this: *mut Unit, good: u32) -> bool;
    pub fn fun_004316f3(this: *mut Building, good: u32, flag: u8) -> bool;
    pub fn fun_004319d7(this: *mut Building, good: u32, flag: u8) -> i32;
    pub fn fun_0041531d();
    pub fn fun_00413e7b();
    pub fn fun_0041592e();
    pub fn fun_00415403();
    pub fn fun_0041575c();
    pub fn fun_0041581d();
    pub fn fun_00449f2f(this: *mut Unit, new_good: i32);
    pub fn fun_0042f710(idx: i32, flag: u32) -> i32;
    pub fn fun_0042f754(idx: i32, flag: u32) -> i32;
    pub fn fun_0042f776(idx: i32, flag: u32) -> i32;
    pub fn fun_0042f798(building_idx: i32, good_idx: u32, flag: u32) -> i32;
    pub fn fun_0047ffc0(building_idx: i32) -> i32;
    pub fn fun_00494f01(building_idx: u32, p2: *mut u8, p3: *mut u32, p4: *mut u32, p5: i32, p6: *mut u8);
    pub fn fun_00495e0c(building_idx: i32);
    pub fn fun_0049599b(building_idx: i32, p2: *mut u8);
    pub fn fun_0042878e(p1: u32, p2: i32);
    pub fn fun_004238dc(p1: *mut u16) -> *mut u8;
    pub fn fun_004325db(this: *mut u8, param_1: i32) -> u32;
    pub fn fun_0045c709(p1: *mut u32) -> u32;
    pub fn fun_0041c61e(p1: *mut u8, p2: i32) -> *mut u8;
    pub fn fun_0041c7f1(p1: *mut u8) -> *mut i32;
    pub fn fun_0041c81f(p1: *mut u8) -> *mut i32;
    pub fn fun_0041c9dd(p1: *mut i32) -> u32;
    pub fn fun_0041c84f(p1: *mut u8);
    pub fn fun_00439633(_: *mut u8, _: u32) -> i32 { 0 }
    pub fn fun_0043967d(_: *mut u8, _: *const u8) -> i32 { 0 }
    pub fn fun_0040ecf9(_: *mut u8, _: *mut u8, _: *mut u8, _: i32, _: *mut u8, _: *const u8) {}
    pub fn fun_004e6760(_: *const u8, _: *const u8, _: usize) -> i32 { 0 }
    pub fn fun_0042c70a(_: i32) -> u32 { 1 }
    pub fn fun_0044bcf3(_: *mut u8, _: i32) -> u32 { 1 }
    pub fn fun_004411ca(_: *mut u8) -> *mut u16 { 0 as *mut u16 }
    pub fn fun_0043f8f3(_: i32) -> u32 { 0 }
    pub fn fun_0042aa24(_: u16, _: u16, _: i16, _: u16) -> u32 { 0 }
    pub fn fun_0043b35f(_: i32, _: *mut u16, _: *mut u16, _: *mut u16, _: i32) -> u32 { 0 }
    pub fn fun_0044124e(_: *mut u8, _: *mut u32) {}
    pub fn fun_0043f725(_: *mut u8, _: *mut u8) {}
    pub fn fun_0042aed3(_: *mut u16) -> u32 { 0 }
    pub fn fun_0043d54f(_: i32) -> i32 { 0 }
    pub fn fun_0043d037(_: i32) {}
    pub fn fun_0042d88d(_: *mut Unit, _: i32) -> bool { false }
    pub fn fun_0042d71b(_: i32) -> u32 { 0 }
    pub fn fun_0042d73a(_: i32) -> u32 { 0 }
    pub fn fun_0042c66c(_: i32) -> bool { false }
    pub fn fun_0042c6bc(_: i32) -> bool { false }
    pub fn fun_0045bcac(_: i32) {}
    pub fn fun_0040b58c(_: *mut u16) -> u32 { 0 }
    pub fn fun_0040ba80(_: u32, _: i32, _: *mut u16, _: u32) {}
    pub fn fun_00438ccc(_: *mut u8, _: *mut u32) {}
    pub fn fun_0040bae1(_: u32, _: i32) {}
    pub fn fun_00453067(_: i32) {}
    pub fn fun_004417c7(_: u32) -> *mut u8 { 0 as *mut u8 }
    pub fn fun_00441800(_: u32) -> u32 { 0 }
    pub fn fun_0043bfbc(_: *mut u8, _: *mut u8) -> bool { false }
    pub fn fun_00439ab3(_: *mut u8, _: i32) -> u32 { 1 }
    pub fn fun_0042c597(_: i32) -> u32 { 0 }
    pub fn fun_00461c14(_: i32, _: i32) -> i32 { 0 }
    pub fn fun_00435504(_: i32) -> u32 { 0 }
    pub fn fun_0043289b(_: *mut u8, _: u32) -> u32 { 0 }
    pub fn fun_00433056(_: i32) -> u32 { 0 }
    pub fn fun_00433386(_: i32) -> bool { false }
    pub fn fun_004325db(_: *mut u8, _: i32) -> u32 { 0 }
    pub fn fun_0043267f(_: *mut u8, _: i32) -> *mut u8 { 0 as *mut u8 }
    pub fn fun_004326ec(_: *mut u8, _: i32) -> u32 { 0 }
    pub fn fun_0043270f(_: i32) -> i32 { 0 }
    pub fn fn_0042c680(_: *mut Unit) -> bool { true }
    pub fn fn_0042c68a(_: *mut Unit) -> bool { false }
    pub fn fn_0042c64f(_: i32) -> bool { false }
    pub fn fn_0042d803(_: *mut Unit, _: i32) -> bool { true }
    pub fn fn_0043e09a(_: *mut Unit, _: i32) -> u32 { 2 }
    pub fn fn_0043bf90(_: *mut u8) {}
    pub fn fn_0044b7b5(_: *mut u8, _: i32, _: i32, _: i32) {}
    pub fn fn_0044b9ab(_: *mut u8, _: i32) -> bool { false }
    pub fn fn_0042c66c(_: i32) -> bool { false }
    pub fn fn_0042c6bc(_: i32) -> bool { false }
    pub unsafe fn fn_004127ef(_: u32, _: i32, _: u8, _: u32, _: i32, _: i32) {}
    pub unsafe fn fn_0042878e(_: u32, _: i32) {}
    pub unsafe fn fn_0045c709(_: *mut u32) -> u32 { 0 }
    pub unsafe fn fn_0041ee3(_: i32) {}
    pub unsafe fn fn_0043d037(_: i32) {}
    pub unsafe fn fn_0045bcac(_: i32) {}
    pub unsafe fn fn_004530d6(_: i32) {}
    pub unsafe fn fn_004325db(_: *mut u8, _: i32) -> u32 { 0 }
    pub unsafe fn fn_0043267f(_: *mut u8, _: i32) -> *mut u8 { 0 as *mut u8 }
    pub unsafe fn fn_004326ec(_: *mut u8, _: i32) -> u32 { 0 }
    pub unsafe fn fn_0043270f(_: i32) -> i32 { 0 }
    pub unsafe fn fn_0042c680(_: *mut Unit) -> bool { true }
    pub unsafe fn fn_0042c68a(_: *mut Unit) -> bool { false }
    pub unsafe fn fn_0042c64f(_: i32) -> bool { false }
    pub unsafe fn fn_0042d803(_: *mut Unit, _: i32) -> bool { true }
    pub unsafe fn fn_0043e09a(_: *mut Unit, _: i32) -> u32 { 2 }
    pub unsafe fn fn_0043bf90(_: *mut u8) {}
    pub unsafe fn fn_0044b7b5(_: *mut u8, _: i32, _: i32, _: i32) {}
    pub unsafe fn fn_0044b9ab(_: *mut u8, _: i32) -> bool { false }
    pub unsafe fn fn_0042c66c(_: i32) -> bool { false }
    pub unsafe fn fn_0042c6bc(_: i32) -> bool { false }
    pub unsafe fn fn_0042c6cf(_: i32) -> bool { false }
    pub unsafe fn fn_0044b7b5(_: *mut u8, _: i32, _: i32, _: i32) {}
    pub unsafe fn fn_0044b9ab(_: *mut u8, _: i32) -> bool { false }
    pub unsafe fn fn_0042c6e3(_: i32) -> bool { false }
    pub unsafe fn fn_0045c709(_: *mut u32) -> u32 { 0 }
    pub unsafe fn fn_0041ee3(_: i32) {}
    pub unsafe fn fn_0043d037(_: i32) {}
    pub unsafe fn fn_0045bcac(_: i32) {}
    pub unsafe fn fn_004530d6(_: i32) {}
    pub unsafe fn fn_004417c7(_: u32) -> *mut u8 { 0 as *mut u8 }
    pub unsafe fn fn_00441800(_: u32) -> u32 { 0 }
    pub unsafe fn fn_0043bfbc(_: *mut u8, _: *mut u8) -> bool { false }
    pub unsafe fn fn_00439ab3(_: *mut u8, _: i32) -> u32 { 1 }
    pub unsafe fn fn_0040b58c(_: *mut u16) -> u32 { 0 }
    pub unsafe fn fn_00428554(_: *mut u8, _: *mut u32, _: *mut u16) -> u32 { 0 }
    pub unsafe fn fn_0048000a() -> i32 { 0 }
    pub unsafe fn fn_0047fe3a(_: i32) -> i32 { 0 }
    pub unsafe fn fn_00480010(_: i32, _: i32) -> i32 { 0 }
    pub unsafe fn fn_004238dc(_: *mut u16) -> *mut u8 { 0 as *mut u8 }
    pub unsafe fn fn_004127ef(_: u32, _: i32, _: u8, _: u32, _: i32, _: i32) {}
    pub unsafe fn fn_0043bf90(_: *mut u8) {}
    pub unsafe fn fn_004530d6(_: i32) {}
    pub unsafe fn fn_004325db(_: *mut u8, _: i32) -> u32 { 0 }
    pub unsafe fn fn_0043267f(_: *mut u8, _: i32) -> *mut u8 { 0 as *mut u8 }
    pub unsafe fn fn_00435504(_: i32) -> u32 { 0 }
    pub unsafe fn fn_00432753(_: *mut u8, _: *mut u32) -> u32 { 0 }
    pub unsafe fn fn_0043289b(_: *mut u8, _: u32) -> u32 { 0 }
    pub unsafe fn fn_004326ec(_: *mut u8, _: i32) -> u32 { 0 }
    pub unsafe fn fn_00433056(_: i32) -> u32 { 0 }
    pub unsafe fn fn_00433386(_: i32) -> bool { false }
    pub unsafe fn fn_0042d7d3(_: i32) -> *mut u8 { 0 as *mut u8 }
    pub unsafe fn fn_00431d2a(_: *mut u8, _: i32, _: i32, _: u8) {}
    pub unsafe fn fn_0042c6e3(_: i32) -> bool { false }
    pub unsafe fn fn_0045c709(_: *mut u32) -> u32 { 0 }
    pub unsafe fn fn_0041ee3(_: i32) {}
    pub unsafe fn fn_0043d037(_: i32) {}
    pub unsafe fn fn_0045bcac(_: i32) {}
    pub unsafe fn fn_004530d6(_: i32) {}
    pub unsafe fn fn_004316e0(_: i32) -> i32 { 0 }
    pub unsafe fn fn_004322da(_: *mut Building, _: i32) -> u32 { 0 }
    pub unsafe fn fn_0043e09a(_: *mut Unit, _: i32) -> u32 { 0 }
    pub unsafe fn fn_004319d7(_: *const HouseType, _: u32, _: u8) -> i32 { 0 }
    pub unsafe fn fn_00434142(_: *mut Building, _: i32) -> bool { false }
    pub unsafe fn fn_0042c6f0(_: *mut Unit) -> bool { true }
    pub unsafe fn fn_0042c597(_: *mut Unit) -> u32 { 0 }
    pub unsafe fn fn_0042c5b3(_: *mut Unit) -> u32 { 0 }
    pub unsafe fn fn_0042c676(_: *mut Unit) -> bool { false }
    pub unsafe fn fn_0042c6bc(_: *mut Unit) -> bool { false }
    pub unsafe fn fn_0042c6cf(_: *mut Unit) -> bool { false }
    pub unsafe fn fn_0042c8a8(_: *mut Unit) -> bool { false }
    pub unsafe fn fn_004316e0(_: i32) -> i32 { 0 }
    pub unsafe fn fn_004322da(_: *mut Building, _: i32) -> u32 { 0 }
    pub unsafe fn fn_0043e09a(_: *mut Unit, _: i32) -> u32 { 0 }
    pub unsafe fn fn_004319d7(_: *const HouseType, _: u32, _: u8) -> i32 { 0 }
    pub unsafe fn fn_00434142(_: *mut Building, _: i32) -> bool { false }
    pub unsafe fn fn_0042c6f0(_: *mut Unit) -> bool { true }
    pub unsafe fn fn_0042c597(_: *mut Unit) -> u32 { 0 }
    pub unsafe fn fn_0042c5b3(_: *mut Unit) -> u32 { 0 }
    pub unsafe fn fn_0042c676(_: *mut Unit) -> bool { false }
    pub unsafe fn fn_0042c6bc(_: *mut Unit) -> bool { false }
    pub unsafe fn fn_0042c6cf(_: *mut Unit) -> bool { false }
    pub unsafe fn fn_0042c8a8(_: *mut Unit) -> bool { false }
    pub unsafe fn fn_0042c63b(_: i32) -> bool { false }
    pub unsafe fn fn_0042c680(_: *mut Unit) -> bool { true }
    pub unsafe fn fn_0042c68a(_: *mut Unit) -> bool { false }
    pub unsafe fn fn_0042c64f(_: i32) -> bool { false }
    pub unsafe fn fn_0042d803(_: *mut Unit, _: i32) -> bool { true }
    pub unsafe fn fn_0043234d(_: *mut Unit, _: i32) -> bool { false }
    pub unsafe fn fn_0043242c(_: *mut Unit, _: i32) -> u32 { 0 }
    pub unsafe fn fn_00432516(_: *mut Unit, _: i32) -> bool { false }
    pub unsafe fn fn_0043256b(_: *mut Unit, _: i32) -> bool { false }
    pub unsafe fn fn_0043267f(_: *mut Unit, _: i32) -> *mut u8 { 0 as *mut u8 }
    pub unsafe fn fn_004326ec(_: *mut Unit, _: i32) -> u32 { 0 }
    pub unsafe fn fn_0043270f(_: i32) -> i32 { 0 }
    pub unsafe fn fn_00432753(_: *mut Unit, _: *mut u32) -> u32 { 0 }
    pub unsafe fn fn_0043289b(_: *mut Unit, _: u32) -> u32 { 0 }
    pub unsafe fn fn_00432753(_: *mut Unit, _: *mut u32) -> u32 { 0 }
    pub unsafe fn fn_00433056(_: i32) -> u32 { 0 }
    pub unsafe fn fn_00433386(_: i32) -> bool { false }
    pub unsafe fn fn_00435504(_: i32) -> u32 { 0 }
    pub unsafe fn fn_004316f3(_: *mut Building, _: u32, _: u8) -> bool { false }
    pub unsafe fn fn_00431f37(_: *const HouseType, _: u32) -> i32 { -1 }
    pub unsafe fn fn_00431d2a(_: *mut Building, _: i32, _: i32, _: u8) {}
    pub unsafe fn fn_004376cf(_: *mut Building, _: *mut u32, _: i32) {}
    pub unsafe fn fn_004376cf(_: *mut Building, _: *mut u32, _: i32) {}
    pub unsafe fn fn_004411ca(_: *mut Building) -> *mut u16 { 0 as *mut u16 }
    pub unsafe fn fn_0044124e(_: *mut Building, _: *mut u32) {}
    pub unsafe fn fn_00441800(_: u32) -> u32 { 0 }
    pub unsafe fn fn_004417c7(_: u32) -> *mut u8 { 0 as *mut u8 }
    pub unsafe fn fn_00441987(_: i32) -> u32 { 0 }
    pub unsafe fn fn_00441b83(_: *mut Building) {}
    pub unsafe fn fn_00441ee3(_: i32) {}
    pub unsafe fn fn_004422dc(_: *mut Unit) {}
    pub unsafe fn fn_00444c6e(_: *mut Unit) {}
    pub unsafe fn fn_00449bda(_: *mut Unit) {}
    pub unsafe fn fn_00449f2f(_: *mut Unit, _: i32) {}
    pub unsafe fn fn_0044a0d9(_: *mut Unit) {}
    pub unsafe fn fn_0044b226(_: *mut Unit) {}
    pub unsafe fn fn_0044b2fa(_: *mut Unit) {}
    pub unsafe fn fn_0044b5d9(_: *mut Unit, _: i32) -> u32 { 0 }
    pub unsafe fn fn_0044b5e7(_: *mut Unit, _: i32, _: i32) {}
    pub unsafe fn fn_0044b634(_: *mut Building, _: i32) -> u8 { 0 }
    pub unsafe fn fn_0044b660(_: *mut Building) -> bool { false }
    pub unsafe fn fn_0044b7b5(_: *mut Building, _: i32, _: i32, _: i32) {}
    pub unsafe fn fn_0044b9ab(_: *mut Building, _: i32) -> bool { false }
    pub unsafe fn fn_0044bcf3(_: *mut Building, _: i32) -> u32 { 0 }
    pub unsafe fn fn_0045bb51(_: *mut Unit, _: i32) {}
    pub unsafe fn fn_0045bbaa(_: *mut Unit, _: u32) {}
    pub unsafe fn fn_0045bcac(_: i32) {}
    pub unsafe fn fn_0045c17b(_: *mut Unit, _: i32, _: i32) {}
    pub unsafe fn fn_0045c59d(_: *mut Unit, _: *mut u32, _: *mut i16) -> bool { false }
    pub unsafe fn fn_0045c66e(_: i32) -> u32 { 0 }
    pub unsafe fn fn_0045c709(_: *mut u32) -> u32 { 0 }
    pub unsafe fn fn_0045d14f(_: *mut Unit, _: *mut u32, _: *mut i16) -> bool { false }
    pub unsafe fn fn_00461c14(_: i32, _: i32) -> i32 { 0 }
    pub unsafe fn fn_004619f8(_: i32, _: *mut u16) -> bool { false }
    pub unsafe fn fn_0046733f(_: *mut Unit) -> *mut u8 { 0 as *mut u8 }
    pub unsafe fn fn_00467617(_: *mut Unit) -> i32 { 0 }
    pub unsafe fn fn_0046794b(_: *mut Unit, _: i32) -> bool { false }
    pub unsafe fn fn_00467c0e(_: *mut Unit, _: i32) -> bool { false }
    pub unsafe fn fn_004680ea(_: *mut Unit) {}
    pub unsafe fn fn_004681ab(_: *mut Unit) {}
    pub unsafe fn fn_0046897c(_: *mut Unit) {}
    pub unsafe fn fn_0046d53a(_: *mut Unit) {}
    pub unsafe fn fn_0046e1be(_: *mut Unit, _: i32) -> u32 { 0 }
    pub unsafe fn fn_0046e117(_: *mut Unit, _: *mut u8) {}
    pub unsafe fn fn_0046e3a1(_: *mut Unit, _: *mut u8) -> bool { false }
    pub unsafe fn fn_0046e52e(_: *mut Unit, _: *mut u8, _: i32, _: *mut u32) -> u8 { 0 }
    pub unsafe fn fn_00473461(_: *mut Unit, _: i32) {}
    pub unsafe fn fn_0047c825(_: *mut u8, _: u32) -> i32 { 0 }
    pub unsafe fn fn_0047ffc0(_: i32) -> i32 { 0 }
    pub unsafe fn fn_0048064b(_: i32, _: *mut u8) -> i32 { 0 }
    pub unsafe fn fn_00490d10(_: i32, _: i32) {}
    pub unsafe fn fn_00494f01(_: i32, _: *mut u8, _: *mut u32, _: *mut u32, _: i32, _: *mut u8) {}
    pub unsafe fn fn_0049599b(_: i32, _: *mut u8) {}
    pub unsafe fn fn_00495e0c(_: i32) {}
    pub unsafe fn fn_004a2222(_: *mut u32) {}
    pub unsafe fn fn_004a693b(_: *mut u8, _: *mut u8, _: *mut u8) {}
    pub unsafe fn fn_004b7b44(_: *mut u8, _: *mut u8, _: *mut u32) {}
    pub unsafe fn fn_004b8b00(_: *mut u32) {}
    pub unsafe fn fn_004b8b04(_: *mut u32, _: *mut i32, _: *mut u8) {}
    pub unsafe fn fn_004b8b4f(_: *mut u32, _: *mut i32, _: *mut u8) {}
    pub unsafe fn fn_004b8be4(_: *mut u8, _: i32, _: i32, _: *mut u8, _: i32, _: *mut u32) {}
    pub unsafe fn fn_004b8c93(_: *mut u8, _: i32, _: i32, _: i32, _: *mut u8, _: i32, _: i32, _: *mut u32, _: *mut u8) {}
    pub unsafe fn fn_004b8d4c(_: *mut u8, _: i32, _: i32, _: *mut u8, _: i32) {}
    pub unsafe fn fn_004b8d89(_: *mut u8, _: i32, _: i32) {}
    pub unsafe fn fn_004c198b(_: i32) {}
    pub unsafe fn fn_004c1d1e(_: i32) {}
    pub unsafe fn fn_004c227c(_: *mut u8, _: *mut u8, _: *mut i32) {}
    pub unsafe fn fn_004c560b(_: i32) {}
    pub unsafe fn fn_004caaa5(_: i32, _: *mut i32, _: i32) {}
    pub unsafe fn fn_004caaea(_: i32, _: *mut i32, _: u8, _: *mut u8) {}
    pub unsafe fn fn_004cb028(_: i32) {}
    pub unsafe fn fn_004cb133(_: i32) {}
    pub unsafe fn fn_004cca49(_: i32) {}
    pub unsafe fn fn_004cce2f(_: i32) {}
    pub unsafe fn fn_004cd406(_: i32) {}
    pub unsafe fn fn_004d037(_: i32) {}
    pub unsafe fn fn_004e1d9e(_: i32, _: *mut u32, _: i32) {}
    pub unsafe fn fn_004e1e3f(_: i32, _: *mut u32, _: i32, _: *mut u8, _: *mut u32, _: *mut u8) {}
    pub unsafe fn fn_004e2172(_: i32, _: *mut u32, _: *mut u8, _: *mut u8, _: *mut u32, _: *mut u8) {}
    pub unsafe fn fn_004e21b7(_: *mut u8, _: i32, _: *mut u8, _: i32, _: *mut u8, _: *mut u8, _: *mut u8) -> *mut u8 { 0 as *mut u8 }
    pub unsafe fn fn_004e5410(_: *mut u32, _: *mut u32) {}
    pub unsafe fn fn_004e556b(_: *mut u8, _: *mut u8) {}
    pub unsafe fn fn_004e5628(_: *mut u8) {}
    pub unsafe fn fn_004e5820(_: *mut u8) {}
    pub unsafe fn fn_004e6760(_: *const u8, _: *const u8, _: usize) -> i32 { 0 }
    pub unsafe fn _memset(_: *mut u8, _: i32, _: usize) -> *mut u8 { 0 as *mut u8 }
    pub unsafe fn _rand() -> u32 { 0 }

    pub static mut DAT_00510BD8: *mut u8 = 0x510_BD8 as *mut u8;
    pub static mut DAT_00510BE0: *mut u8 = 0x510_BE0 as *mut u8;
    pub static mut DAT_00510BE8: *mut u8 = 0x510_BE8 as *mut u8;
    pub static mut DAT_00510BF0: *mut u8 = 0x510_BF0 as *mut u8;
    pub static mut DAT_00510BC4: *mut u8 = 0x510_BC4 as *mut u8;
    pub static mut DAT_005113A0: *mut u8 = 0x511_3A0 as *mut u8;
    pub static mut DAT_005112FC: *mut u8 = 0x511_2FC as *mut u8;
    pub static mut DAT_00511200: *mut u8 = 0x511_200 as *mut u8;
    pub static mut DAT_00511208: *mut u8 = 0x511_208 as *mut u8;
    pub static mut DAT_00511214: *mut u8 = 0x511_214 as *mut u8;
    pub static mut DAT_00511180: *mut u8 = 0x511_180 as *mut u8;
    pub static mut DAT_00510BD0: *mut u8 = 0x510_BD0 as *mut u8;
    pub static mut DAT_00510BC8: *mut u8 = 0x510_BC8 as *mut u8;
    pub static mut DAT_00510BD4: *mut u8 = 0x510_BD4 as *mut u8;
    pub static mut DAT_005113A4: *mut u8 = 0x511_3A4 as *mut u8;
    pub static mut DAT_00511224: *mut u8 = 0x511_224 as *mut u8;
    pub static mut DAT_0051120C: *mut u8 = 0x511_20C as *mut u8;
    pub static mut DAT_00511210: *mut u8 = 0x511_210 as *mut u8;
    pub static mut DAT_00511170: *mut u8 = 0x511_170 as *mut u8;
    pub static mut DAT_00511174: *mut u8 = 0x511_174 as *mut u8;
    pub static mut DAT_00511178: *mut u8 = 0x511_178 as *mut u8;
    pub static mut DAT_00511240: *mut u8 = 0x511_240 as *mut u8;
    pub static mut DAT_00511160: *mut u8 = 0x511_160 as *mut u8;
    pub static mut DAT_0051117C: *mut u8 = 0x511_17C as *mut u8;
    pub static mut DAT_00510A10: *mut u8 = 0x510_A10 as *mut u8;
    pub static mut DAT_00510A14: *mut u8 = 0x510_A14 as *mut u8;
    pub static mut DAT_00510A20: *mut u8 = 0x510_A20 as *mut u8;
    pub static mut DAT_00510BEC: *mut u8 = 0x510_BEC as *mut u8;
    pub static mut DAT_00510C0C: *mut u8 = 0x510_C0C as *mut u8;
    pub static mut DAT_00510C10: *mut u8 = 0x510_C10 as *mut u8;
    pub static mut DAT_00510C14: *mut u8 = 0x510_C14 as *mut u8;
    pub static mut DAT_005113AC: *mut u8 = 0x511_3AC as *mut u8;
    pub static mut DAT_00510BF4: *mut u8 = 0x510_BF4 as *mut u8;
    pub static mut DAT_005113A8: *mut u8 = 0x511_3A8 as *mut u8;
    pub static mut DAT_005113B0: *mut u8 = 0x511_3B0 as *mut u8;
    pub static mut DAT_005113B4: *mut u8 = 0x511_3B4 as *mut u8;
    pub static mut DAT_005113B8: *mut u8 = 0x511_3B8 as *mut u8;
    pub static mut DAT_005113BC: *mut u8 = 0x511_3BC as *mut u8;
    pub static mut DAT_005113C0: *mut u8 = 0x511_3C0 as *mut u8;
    pub static mut DAT_005113C4: *mut u8 = 0x511_3C4 as *mut u8;
    pub static mut DAT_005113C8: *mut u8 = 0x511_3C8 as *mut u8;
    pub static mut DAT_005113CC: *mut u8 = 0x511_3CC as *mut u8;
    pub static mut DAT_005113D0: *mut u8 = 0x511_3D0 as *mut u8;
    pub static mut DAT_005113D4: *mut u8 = 0x511_3D4 as *mut u8;
    pub static mut DAT_005113D8: *mut u8 = 0x511_3D8 as *mut u8;
    pub static mut DAT_005113DC: *mut u8 = 0x511_3DC as *mut u8;
    pub static mut DAT_005113E0: *mut u8 = 0x511_3E0 as *mut u8;
    pub static mut DAT_005113E4: *mut u8 = 0x511_3E4 as *mut u8;
    pub static mut DAT_005113E8: *mut u8 = 0x511_3E8 as *mut u8;
    pub static mut DAT_005113EC: *mut u8 = 0x511_3EC as *mut u8;
    pub static mut DAT_005113F0: *mut u8 = 0x511_3F0 as *mut u8;
    pub static mut DAT_005113F4: *mut u8 = 0x511_3F4 as *mut u8;
    pub static mut DAT_005113F8: *mut u8 = 0x511_3F8 as *mut u8;
    pub static mut DAT_005113FC: *mut u8 = 0x511_3FC as *mut u8;
    pub static mut DAT_00511400: *mut u8 = 0x511_400 as *mut u8;
    pub static mut DAT_00511404: *mut u8 = 0x511_404 as *mut u8;
    pub static mut DAT_00511408: *mut u8 = 0x511_408 as *mut u8;
    pub static mut DAT_0051140C: *mut u8 = 0x511_40C as *mut u8;
    pub static mut DAT_00511410: *mut u8 = 0x511_410 as *mut u8;
    pub static mut DAT_00511414: *mut u8 = 0x511_414 as *mut u8;
    pub static mut DAT_00511418: *mut u8 = 0x511_418 as *mut u8;
    pub static mut DAT_0051141C: *mut u8 = 0x511_41C as *mut u8;
    pub static mut DAT_00511420: *mut u8 = 0x511_420 as *mut u8;
    pub static mut DAT_00511424: *mut u8 = 0x511_424 as *mut u8;
    pub static mut DAT_00511428: *mut u8 = 0x511_428 as *mut u8;
    pub static mut DAT_0051142C: *mut u8 = 0x511_42C as *mut u8;
    pub static mut DAT_00511430: *mut u8 = 0x511_430 as *mut u8;
    pub static mut DAT_00511434: *mut u8 = 0x511_434 as *mut u8;
    pub static mut DAT_00511438: *mut u8 = 0x511_438 as *mut u8;
    pub static mut DAT_0051143C: *mut u8 = 0x511_43C as *mut u8;
    pub static mut DAT_00511440: *mut u8 = 0x511_440 as *mut u8;
    pub static mut DAT_00511444: *mut u8 = 0x511_444 as *mut u8;
    pub static mut DAT_00511448: *mut u8 = 0x511_448 as *mut u8;
    pub static mut DAT_0051144C: *mut u8 = 0x511_44C as *mut u8;
    pub static mut DAT_00511450: *mut u8 = 0x511_450 as *mut u8;
    pub static mut DAT_00511454: *mut u8 = 0x511_454 as *mut u8;
    pub static mut DAT_00511458: *mut u8 = 0x511_458 as *mut u8;
    pub static mut DAT_0051145C: *mut u8 = 0x511_45C as *mut u8;
    pub static mut DAT_00511460: *mut u8 = 0x511_460 as *mut u8;
    pub static mut DAT_00511464: *mut u8 = 0x511_464 as *mut u8;
    pub static mut DAT_00511468: *mut u8 = 0x511_468 as *mut u8;
    pub static mut DAT_0051146C: *mut u8 = 0x511_46C as *mut u8;
    pub static mut DAT_00511470: *mut u8 = 0x511_470 as *mut u8;
    pub static mut DAT_00511474: *mut u8 = 0x511_474 as *mut u8;
    pub static mut DAT_00511478: *mut u8 = 0x511_478 as *mut u8;
    pub static mut DAT_0051147C: *mut u8 = 0x511_47C as *mut u8;
    pub static mut DAT_00511480: *mut u8 = 0x511_480 as *mut u8;
    pub static mut DAT_00511484: *mut u8 = 0x511_484 as *mut u8;
    pub static mut DAT_00511488: *mut u8 = 0x511_488 as *mut u8;
    pub static mut DAT_0051148C: *mut u8 = 0x511_48C as *mut u8;
    pub static mut DAT_00511490: *mut u8 = 0x511_490 as *mut u8;
    pub static mut DAT_00511494: *mut u8 = 0x511_494 as *mut u8;
    pub static mut DAT_00511498: *mut u8 = 0x511_498 as *mut u8;
    pub static mut DAT_0051149C: *mut u8 = 0x511_49C as *mut u8;
    pub static mut DAT_005114A0: *mut u8 = 0x511_4A0 as *mut u8;
    pub static mut DAT_005114A4: *mut u8 = 0x511_4A4 as *mut u8;
    pub static mut DAT_005114A8: *mut u8 = 0x511_4A8 as *mut u8;
    pub static mut DAT_005114AC: *mut u8 = 0x511_4AC as *mut u8;
    pub static mut DAT_005114B0: *mut u8 = 0x511_4B0 as *mut u8;
    pub static mut DAT_005114B4: *mut u8 = 0x511_4B4 as *mut u8;
    pub static mut DAT_005114B8: *mut u8 = 0x511_4B8 as *mut u8;
    pub static mut DAT_005114BC: *mut u8 = 0x511_4BC as *mut u8;
    pub static mut DAT_005114C0: *mut u8 = 0x511_4C0 as *mut u8;
    pub static mut DAT_005114C4: *mut u8 = 0x511_4C4 as *mut u8;
    pub static mut DAT_005114C8: *mut u8 = 0x511_4C8 as *mut u8;
    pub static mut DAT_005114CC: *mut u8 = 0x511_4CC as *mut u8;
    pub static mut DAT_005114D0: *mut u8 = 0x511_4D0 as *mut u8;
    pub static mut DAT_005114D4: *mut u8 = 0x511_4D4 as *mut u8;
    pub static mut DAT_005114D8: *mut u8 = 0x511_4D8 as *mut u8;
    pub static mut DAT_005114DC: *mut u8 = 0x511_4DC as *mut u8;
    pub static mut DAT_005114E0: *mut u8 = 0x511_4E0 as *mut u8;
    pub static mut DAT_005114E4: *mut u8 = 0x511_4E4 as *mut u8;
    pub static mut DAT_005114E8: *mut u8 = 0x511_4E8 as *mut u8;
    pub static mut DAT_005114EC: *mut u8 = 0x511_4EC as *mut u8;
    pub static mut DAT_005114F0: *mut u8 = 0x511_4F0 as *mut u8;
    pub static mut DAT_005114F4: *mut u8 = 0x511_4F4 as *mut u8;
    pub static mut DAT_005114F8: *mut u8 = 0x511_4F8 as *mut u8;
    pub static mut DAT_005114FC: *mut u8 = 0x511_4FC as *mut u8;
    pub static mut DAT_00511500: *mut u8 = 0x511_500 as *mut u8;
    pub static mut DAT_00511504: *mut u8 = 0x511_504 as *mut u8;
    pub static mut DAT_00511508: *mut u8 = 0x511_508 as *mut u8;
    pub static mut DAT_0051150C: *mut u8 = 0x511_50C as *mut u8;
    pub static mut DAT_00511510: *mut u8 = 0x511_510 as *mut u8;
    pub static mut DAT_00511514: *mut u8 = 0x511_514 as *mut u8;
    pub static mut DAT_00511518: *mut u8 = 0x511_518 as *mut u8;
    pub static mut DAT_0051151C: *mut u8 = 0x511_51C as *mut u8;
    pub static mut DAT_00511520: *mut u8 = 0x511_520 as *mut u8;
    pub static mut DAT_00511524: *mut u8 = 0x511_524 as *mut u8;
    pub static mut DAT_00511528: *mut u8 = 0x511_528 as *mut u8;
    pub static mut DAT_0051152C: *mut u8 = 0x511_52C as *mut u8;
    pub static mut DAT_00511530: *mut u8 = 0x511_530 as *mut u8;
    pub static mut DAT_00511534: *mut u8 = 0x511_534 as *mut u8;
    pub static mut DAT_00511538: *mut u8 = 0x511_538 as *mut u8;
    pub static mut DAT_0051153C: *mut u8 = 0x511_53C as *mut u8;
    pub static mut DAT_00511540: *mut u8 = 0x511_540 as *mut u8;
    pub static mut DAT_00511544: *mut u8 = 0x511_544 as *mut u8;
    pub static mut DAT_00511548: *mut u8 = 0x511_548 as *mut u8;
    pub static mut DAT_0051154C: *mut u8 = 0x511_54C as *mut u8;
    pub static mut DAT_00511550: *mut u8 = 0x511_550 as *mut u8;
    pub static mut DAT_00511554: *mut u8 = 0x511_554 as *mut u8;
    pub static mut DAT_00511558: *mut u8 = 0x511_558 as *mut u8;
    pub static mut DAT_0051155C: *mut u8 = 0x511_55C as *mut u8;
    pub static mut DAT_00511560: *mut u8 = 0x511_560 as *mut u8;
    pub static mut DAT_00511564: *mut u8 = 0x511_564 as *mut u8;
    pub static mut DAT_00511568: *mut u8 = 0x511_568 as *mut u8;
    pub static mut DAT_0051156C: *mut u8 = 0x511_56C as *mut u8;
    pub static mut DAT_00511570: *mut u8 = 0x511_570 as *mut u8;
    pub static mut DAT_00511574: *mut u8 = 0x511_574 as *mut u8;
    pub static mut DAT_00511578: *mut u8 = 0x511_578 as *mut u8;
    pub static mut DAT_0051157C: *mut u8 = 0x511_57C as *mut u8;
    pub static mut DAT_00511580: *mut u8 = 0x511_580 as *mut u8;
    pub static mut DAT_00511584: *mut u8 = 0x511_584 as *mut u8;
    pub static mut DAT_00511588: *mut u8 = 0x511_588 as *mut u8;
    pub static mut DAT_0051158C: *mut u8 = 0x511_58C as *mut u8;
    pub static mut DAT_00511590: *mut u8 = 0x511_590 as *mut u8;
    pub static mut DAT_00511594: *mut u8 = 0x511_594 as *mut u8;
    pub static mut DAT_00511598: *mut u8 = 0x511_598 as *mut u8;
    pub static mut DAT_0051159C: *mut u8 = 0x511_59C as *mut u8;
    pub static mut DAT_005115A0: *mut u8 = 0x511_5A0 as *mut u8;
    pub static mut DAT_005115A4: *mut u8 = 0x511_5A4 as *mut u8;
    pub static mut DAT_005115A8: *mut u8 = 0x511_5A8 as *mut u8;
    pub static mut DAT_005115AC: *mut u8 = 0x511_5AC as *mut u8;
    pub static mut DAT_005115B0: *mut u8 = 0x511_5B0 as *mut u8;
    pub static mut DAT_005115B4: *mut u8 = 0x511_5B4 as *mut u8;
    pub static mut DAT_005115B8: *mut u8 = 0x511_5B8 as *mut u8;
    pub static mut DAT_005115BC: *mut u8 = 0x511_5BC as *mut u8;
    pub static mut DAT_005115C0: *mut u8 = 0x511_5C0 as *mut u8;
    pub static mut DAT_005115C4: *mut u8 = 0x511_5C4 as *mut u8;
    pub static mut DAT_005115C8: *mut u8 = 0x511_5C8 as *mut u8;
    pub static mut DAT_005115CC: *mut u8 = 0x511_5CC as *mut u8;
    pub static mut DAT_005115D0: *mut u8 = 0x511_5D0 as *mut u8;
    pub static mut DAT_005115D4: *mut u8 = 0x511_5D4 as *mut u8;
    pub static mut DAT_005115D8: *mut u8 = 0x511_5D8 as *mut u8;
    pub static mut DAT_005115DC: *mut u8 = 0x511_5DC as *mut u8;
    pub static mut DAT_005115E0: *mut u8 = 0x511_5E0 as *mut u8;
    pub static mut DAT_005115E4: *mut u8 = 0x511_5E4 as *mut u8;
    pub static mut DAT_005115E8: *mut u8 = 0x511_5E8 as *mut u8;
    pub static mut DAT_005115EC: *mut u8 = 0x511_5EC as *mut u8;
    pub static mut DAT_005115F0: *mut u8 = 0x511_5F0 as *mut u8;
    pub static mut DAT_005115F4: *mut u8 = 0x511_5F4 as *mut u8;
    pub static mut DAT_005115F8: *mut u8 = 0x511_5F8 as *mut u8;
    pub static mut DAT_005115FC: *mut u8 = 0x511_5FC as *mut u8;
    pub static mut DAT_00511600: *mut u8 = 0x511_600 as *mut u8;
    pub static mut DAT_00511604: *mut u8 = 0x511_604 as *mut u8;
    pub static mut DAT_00511608: *mut u8 = 0x511_608 as *mut u8;
    pub static mut DAT_0051160C: *mut u8 = 0x511_60C as *mut u8;
    pub static mut DAT_00511610: *mut u8 = 0x511_610 as *mut u8;
    pub static mut DAT_00511614: *mut u8 = 0x511_614 as *mut u8;
    pub static mut DAT_00511618: *mut u8 = 0x511_618 as *mut u8;
    pub static mut DAT_0051161C: *mut u8 = 0x511_61C as *mut u8;
    pub static mut DAT_00511620: *mut u8 = 0x511_620 as *mut u8;
    pub static mut DAT_00511624: *mut u8 = 0x511_624 as *mut u8;
    pub static mut DAT_00511628: *mut u8 = 0x511_628 as *mut u8;
    pub static mut DAT_0051162C: *mut u8 = 0x511_62C as *mut u8;
    pub static mut DAT_00511630: *mut u8 = 0x511_630 as *mut u8;
    pub static mut DAT_00511634: *mut u8 = 0x511_634 as *mut u8;
    pub static mut DAT_00511638: *mut u8 = 0x511_638 as *mut u8;
    pub static mut DAT_0051163C: *mut u8 = 0x511_63C as *mut u8;
    pub static mut DAT_00511640: *mut u8 = 0x511_640 as *mut u8;
    pub static mut DAT_00511644: *mut u8 = 0x511_644 as *mut u8;
    pub static mut DAT_00511648: *mut u8 = 0x511_648 as *mut u8;
    pub static mut DAT_0051164C: *mut u8 = 0x511_64C as *mut u8;
    pub static mut DAT_00511650: *mut u8 = 0x511_650 as *mut u8;
    pub static mut DAT_00511654: *mut u8 = 0x511_654 as *mut u8;
    pub static mut DAT_00511658: *mut u8 = 0x511_658 as *mut u8;
    pub static mut DAT_0051165C: *mut u8 = 0x511_65C as *mut u8;
    pub static mut DAT_00511660: *mut u8 = 0x511_660 as *mut u8;
    pub static mut DAT_00511664: *mut u8 = 0x511_664 as *mut u8;
    pub static mut DAT_00511668: *mut u8 = 0x511_668 as *mut u8;
    pub static mut DAT_0051166C: *mut u8 = 0x511_66C as *mut u8;
    pub static mut DAT_00511670: *mut u8 = 0x511_670 as *mut u8;
    pub static mut DAT_00511674: *mut u8 = 0x511_674 as *mut u8;
    pub static mut DAT_00511678: *mut u8 = 0x511_678 as *mut u8;
    pub static mut DAT_0051167C: *mut u8 = 0x511_67C as *mut u8;
    pub static mut DAT_00511680: *mut u8 = 0x511_680 as *mut u8;
    pub static mut DAT_00511684: *mut u8 = 0x511_684 as *mut u8;
    pub static mut DAT_00511688: *mut u8 = 0x511_688 as *mut u8;
    pub static mut DAT_0051168C: *mut u8 = 0x511_68C as *mut u8;
    pub static mut DAT_00511690: *mut u8 = 0x511_690 as *mut u8;
    pub static mut DAT_00511694: *mut u8 = 0x511_694 as *mut u8;
    pub static mut DAT_00511698: *mut u8 = 0x511_698 as *mut u8;
    pub static mut DAT_0051169C: *mut u8 = 0x511_69C as *mut u8;
    pub static mut DAT_005116A0: *mut u8 = 0x511_6A0 as *mut u8;
    pub static mut DAT_005116A4: *mut u8 = 0x511_6A4 as *mut u8;
    pub static mut DAT_005116A8: *mut u8 = 0x511_6A8 as *mut u8;
    pub static mut DAT_005116AC: *mut u8 = 0x511_6AC as *mut u8;
    pub static mut DAT_005116B0: *mut u8 = 0x511_6B0 as *mut u8;
    pub static mut DAT_005116B4: *mut u8 = 0x511_6B4 as *mut u8;
    pub static mut DAT_005116B8: *mut u8 = 0x511_6B8 as *mut u8;
    pub static mut DAT_005116BC: *mut u8 = 0x511_6BC as *mut u8;
    pub static mut DAT_005116C0: *mut u8 = 0x511_6C0 as *mut u8;
    pub static mut DAT_00568CA8: *mut u8 = 0x568_CA8 as *mut u8;
    pub static mut DAT_00568CB0: *mut u8 = 0x568_CB0 as *mut u8;
    pub static mut DAT_00568CB8: *mut u8 = 0x568_CB8 as *mut u8;
    pub static mut DAT_00568C0C: *mut u8 = 0x568_C0C as *mut u8;
    pub static mut DAT_005552A8: *mut u8 = 0x555_2A8 as *mut u8;
    pub static mut DAT_0055529C: *mut u8 = 0x555_29C as *mut u8;
    pub static mut DAT_00568C28: *mut u8 = 0x568_C28 as *mut u8;
    pub static mut DAT_00568C50: *mut u8 = 0x568_C50 as *mut u8;
    pub static mut DAT_00568548: *mut u8 = 0x568_548 as *mut u8;
    pub static mut DAT_0056858C: *mut u8 = 0x568_58C as *mut u8;
    pub static mut DAT_00569254: *mut u8 = 0x569_254 as *mut u8;
    pub static mut DAT_00569258: *mut u8 = 0x569_258 as *mut u8;
    pub static mut DAT_00569AA0: *mut u8 = 0x569_AA0 as *mut u8;
    pub static mut DAT_00569AA4: *mut u8 = 0x569_AA4 as *mut u8;
    pub static mut DAT_00569AA8: *mut u8 = 0x569_AA8 as *mut u8;
    pub static mut DAT_00569ABC: *mut u8 = 0x569_ABC as *mut u8;
    pub static mut DAT_00569AD0: *mut u8 = 0x569_AD0 as *mut u8;
    pub static mut DAT_00511728: *mut u8 = 0x511_728 as *mut u8;
    pub static mut DAT_00512764: *mut u8 = 0x512_764 as *mut u8;
    pub static mut DAT_00512760: *mut u8 = 0x512_760 as *mut u8;
    pub static mut DAT_005076F0: *mut u8 = 0x507_6F0 as *mut u8;
    pub static mut DAT_005077B0: *mut u8 = 0x507_7B0 as *mut u8;
    pub static mut DAT_00507728: *mut u8 = 0x507_728 as *mut u8;
    pub static mut DAT_005071F0: *mut u8 = 0x507_1F0 as *mut u8;
    pub static mut DAT_00510A10: *mut u8 = 0x510_A10 as *mut u8;
    pub static mut DAT_00510BF0: *mut u8 = 0x510_BF0 as *mut u8;
    pub static mut DAT_00568CE4: *mut u8 = 0x568_C54 as *mut u8;
    pub static mut DAT_00568CE8: *mut u8 = 0x568_C58 as *mut u8;
}

// ============================================================================
// Batch 4 - implementacje pomniejszych funkcji
// ============================================================================

pub unsafe fn fun_0042c63b(param_1: i32) -> bool {
    // FUN_0042C63B - sprawdza czy job == 5
    *(param_1 as *mut i32).add(0x18 / 4) == 5
}

pub unsafe fn fun_0042c64f(param_1: i32) -> bool {
    // FUN_0042C64F - sprawdza czy job == 7
    *(param_1 as *mut i32).add(0x18 / 4) == 7
}

pub unsafe fn fun_0042c68a(param_1: i32) -> bool {
    // FUN_0042C68A - sprawdza czy job == 0x19 lub 0x1a
    let job = *(param_1 as *mut i32).add(0x18 / 4);
    job != 0x19 && job != 0x1a
}

pub unsafe fn fun_004325db(_: *mut u8, _: i32) -> bool {
    // FUN_004325DB - walidacja podstawowa
    false
}

pub unsafe fn fun_0043267f(this: *mut u8, param_1: i32) -> *mut u8 {
    // FUN_0043267F - szuka w tablicy building+0x644 wpisu równego param_1
    let mut u_var2: u32 = 0;
    let mut pi_var1 = (this.add(0x644) as *mut i32);
    loop {
        if *pi_var1.add(-1) as u8 != 0 && *pi_var1 == param_1 {
            return this.add(((u_var2 + 100) * 0x10) as usize);
        }
        u_var2 = u_var2.wrapping_add(1);
        pi_var1 = pi_var1.add(4);
        if u_var2 > 0x13 {
            return 0 as *mut u8;
        }
    }
}

pub unsafe fn fun_00432753(_: *mut u8, _: *mut u32) -> u32 {
    // FUN_00432753 - pobiera dane
    0
}

pub unsafe fn fun_0043289b(_: *mut u8, _: u32) -> u32 {
    // FUN_0043289B - pobiera dane
    0
}

pub unsafe fn fun_00433056(param_1: i32) -> u32 {
    // FUN_00433056 - zwraca dane z rejestru
    let b_var1 = *(param_1 as *mut u8);
    if b_var1 < 0x19 {
        if b_var1 != 0x18 {
            return 1;
        }
    } else {
        if b_var1 >= 0x24 {
            if b_var1 >= 0x30 {
                return 1;
            }
        } else {
            let job = *(param_1 as *mut i32).add(0x18 / 4);
            if job != 0x19 && job != 0x1a {
                return 0;
            }
        }
    }
    let job = *(param_1 as *mut i32).add(0x18 / 4);
    if job != 0x19 && job != 0x1a {
        return 0;
    }
    1
}

pub unsafe fn fun_00435504(param_1: i32) -> u32 {
    // FUN_00435504 - szuka w tablicy po ID
    let mut b_var1 = *(param_1 as *mut u8);
    let mut i_var2: i32 = 0;
    let mut pi_var1 = param_1;
    loop {
        if *pi_var1 as u8 == 0x15 {
            return *(param_1 as *mut u32).add(1);
        }
        i_var2 += 1;
        pi_var1 += 0xc58 / 4 + 1;
        if i_var2 >= 0x57 {
            break;
        }
    }
    0
}

pub unsafe fn fun_0042d7d3(param_1: i32) -> *mut u8 {
    // FUN_0042D7D3 - pobiera wskaźnik
    let pi_var1 = *(param_1 as *mut *mut u8);
    if pi_var1.is_null() {
        return 0 as *mut u8;
    }
    pi_var1
}

pub unsafe fn fun_00431d2a(_: *mut u8, _: i32, _: i32, _: u8) {
    // FUN_00431D2A - operacja na danych
}

pub unsafe fn fun_0045c709(_: *mut u32) -> u32 {
    // FUN_0045C709 - pobiera dane
    0
}

pub unsafe fn fun_0042c680(_: *mut Unit) -> bool {
    // FUN_0042C680 - sprawdza job
    false
}

pub unsafe fn fun_004619f8(_: i32, _: *mut u16) -> bool {
    // FUN_004619F8 - sprawdza dane
    false
}

pub unsafe fn fun_004127ef(_: u32, _: i32, _: u8, _: u32, _: i32, _: i32) {
    // FUN_004127EF - operacja na danych
}

pub unsafe fn fun_0045bcac(_: i32) {
    // FUN_0045BCAC - operacja na danych
}

pub unsafe fn fun_0042c6e3(_: i32) -> bool {
    // FUN_0042C6E3 - sprawdza dane
    false
}

pub unsafe fn fun_004417c7(_: u32) -> *mut u8 {
    // FUN_004417C7 - pobiera wskaźnik
    0 as *mut u8
}

pub unsafe fn fn_0042c680(_: *mut Unit) -> bool {
    // FN_0042C680 - sprawdza job
    false
}

pub unsafe fn fn_0043e09a(_: *mut Unit, _: i32) -> u32 {
    // FN_0043E09A - operacja na danych
    2
}

pub unsafe fn fn_0043bf90(_: *mut u8) {
    // FN_0043BF90 - operacja na danych
}

pub unsafe fn fn_0044b7b5(_: *mut u8, _: i32, _: i32, _: i32) {
    // FN_0044B7B5 - operacja na danych
}

pub unsafe fn fn_0044b9ab(_: *mut u8, _: i32) -> bool {
    // FN_0044B9AB - sprawdza dane
    false
}

pub unsafe fn fn_0042c66c(_: i32) -> bool {
    // FN_0042C66C - sprawdza dane
    false
}

pub unsafe fn fn_0042c6bc(_: i32) -> bool {
    // FN_0042C6BC - sprawdza dane
    false
}

pub unsafe fn fn_0042c6cf(_: i32) -> bool {
    // FN_0042C6CF - sprawdza dane
    false
}

pub unsafe fn fn_0042d803(_: *mut Unit, _: i32) -> bool {
    // FN_0042D803 - sprawdza dane
    true
}

pub unsafe fn fn_0043234d(_: *mut Unit, _: i32) -> bool {
    // FN_0043234D - sprawdza dane
    false
}

pub unsafe fn fn_0043242c(_: *mut Unit, _: i32) -> u32 {
    // FN_0043242C - operacja na danych
    0
}

pub unsafe fn fn_00432516(_: *mut Unit, _: i32) -> bool {
    // FN_00432516 - sprawdza dane
    false
}

pub unsafe fn fn_0043256b(_: *mut Unit, _: i32) -> bool {
    // FN_0043256B - sprawdza dane
    false
}

pub unsafe fn fn_0043267f(_: *mut u8, _: i32) -> *mut u8 {
    // FN_0043267F - szuka w tablicy
    0 as *mut u8
}

pub unsafe fn fn_004326ec(_: *mut u8, _: i32) -> u32 {
    // FN_004326EC - pobiera dane
    0
}

pub unsafe fn fn_0043270f(_: i32) -> i32 {
    // FN_0043270F - pobiera dane
    0
}

pub unsafe fn fn_00432753(_: *mut u8, _: *mut u32) -> u32 {
    // FN_00432753 - pobiera dane
    0
}

pub unsafe fn fn_0043289b(_: *mut u8, _: u32) -> u32 {
    // FN_0043289B - pobiera dane
    0
}

pub unsafe fn fn_00433056(_: i32) -> u32 {
    // FN_00433056 - pobiera dane
    0
}

pub unsafe fn fn_00433386(_: i32) -> bool {
    // FN_00433386 - sprawdza dane
    false
}

pub unsafe fn fn_00435504(_: i32) -> u32 {
    // FN_00435504 - pobiera dane
    0
}

pub unsafe fn fn_004316f3(_: *mut Building, _: u32, _: u8) -> bool {
    // FN_004316F3 - bramka budynku dla gooda
    false
}

pub unsafe fn fn_00431f37(_: *const HouseType, _: u32) -> i32 {
    // FN_00431F37 - zwraca revmap[good] z rekordu domu
    -1
}

pub unsafe fn fn_004319d7(_: *const HouseType, _: u32, _: u8) -> i32 {
    // FN_004319D7 - pobiera ilość towaru w budynku
    0
}

pub unsafe fn fn_00434142(_: *mut Building, _: i32) -> bool {
    // FN_00434142 - sprawdza pracownika
    false
}

pub unsafe fn fn_0043bfbc(_: *mut u8, _: *mut u8) -> bool {
    // FN_0043BFBC - operacja na danych
    false
}

pub unsafe fn fn_0043e09a(_: *mut Unit, _: i32) -> u32 {
    // FN_0043E09A - wybiera good do produkcji
    2
}

pub unsafe fn fn_0043bf90(_: *mut u8) {
    // FN_0043BF90 - operacja na danych
}

pub unsafe fn fn_00453067(_: i32) -> i32 {
    // FN_00453067 - pobiera dane
    -1
}

pub unsafe fn fn_00452fe6(_: i32) -> bool {
    // FN_00452FE6 - sprawdza dane
    false
}

pub unsafe fn fn_0045bb51(_: *mut Unit, _: i32) {
    // FN_0045BB51 - dźwięk
}

pub unsafe fn fn_0045bbaa(_: *mut Unit, _: u32) {
    // FN_0045BBAA - dźwięk
}

pub unsafe fn fn_004417c7(_: u32) -> *mut u8 {
    // FN_004417C7 - pobiera wskaźnik
    0 as *mut u8
}

pub unsafe fn fn_00441800(_: u32) -> u32 {
    // FN_00441800 - UI
    0
}

pub unsafe fn fn_0044b7b5(_: *mut u8, _: i32, _: i32, _: i32) {
    // FN_0044B7B5 - operacja na danych
}

pub unsafe fn fn_0044b9ab(_: *mut u8, _: i32) -> bool {
    // FN_0044B9AB - sprawdza dane
    false
}

pub unsafe fn fn_0044bcf3(_: *mut u8, _: i32) -> u32 {
    // FN_0044BCF3 - sprawdza dane
    0
}

pub unsafe fn fn_0044b634(_: *mut Building, _: i32) -> u8 {
    // FN_0044B634 - operacja na danych
    0
}

pub unsafe fn fn_0044b660(_: *mut Building) -> bool {
    // FN_0044B660 - sprawdza dane
    false
}

pub unsafe fn fn_00441ee3(_: i32) {
    // FN_00441EE3 - operacja na danych
}

pub unsafe fn fn_0042d88d(_: *mut Unit, _: i32) -> bool {
    // FN_0042D88D - sprawdza dane
    false
}

pub unsafe fn fn_0042d7d3(_: i32) -> *mut u8 {
    // FN_0042D7D3 - pobiera wskaźnik
    0 as *mut u8
}

pub unsafe fn fn_0042d71b(_: i32) -> u32 {
    // FN_0042D71B - pobiera dane
    0
}

pub unsafe fn fn_0042d73a(_: i32) -> u32 {
    // FN_0042D73A - pobiera dane
    0
}

pub unsafe fn fn_0042c6e3(_: i32) -> bool {
    // FN_0042C6E3 - sprawdza dane
    false
}

pub unsafe fn fn_0042c66c(_: i32) -> bool {
    // FN_0042C66C - sprawdza dane
    false
}

pub unsafe fn fn_0042c6bc(_: i32) -> bool {
    // FN_0042C6BC - sprawdza dane
    false
}

pub unsafe fn fn_0042c6cf(_: i32) -> bool {
    // FN_0042C6CF - sprawdza dane
    false
}

pub unsafe fn fn_0042c680(_: *mut Unit) -> bool {
    // FN_0042C680 - sprawdza job
    true
}

pub unsafe fn fn_0042c64f(_: i32) -> bool {
    // FN_0042C64F - sprawdza dane
    false
}

pub unsafe fn fn_0042c70a(_: i32) -> u32 {
    // FN_0042C70A - pobiera dane
    1
}

pub unsafe fn fn_0042c597(_: i32) -> u32 {
    // FN_0042C597 - pobiera dane
    0
}

pub unsafe fn fn_0042aa24(_: u16, _: u16, _: i16, _: u16) -> u32 {
    // FN_0042AA24 - sprawdza dane
    0
}

pub unsafe fn fn_0042aed3(_: *mut u16) -> u32 {
    // FN_0042AED3 - pobiera dane
    0
}

pub unsafe fn fn_0043f725(_: *mut u8, _: *mut u8) {
    // FN_0043F725 - operacja na danych
}

pub unsafe fn fn_0043d54f(_: i32) -> i32 {
    // FN_0043D54F - pobiera dane
    0
}

pub unsafe fn fn_0043f8f3(_: i32) -> u32 {
    // FN_0043F8F3 - pobiera dane
    0
}

pub unsafe fn fn_0043e09a(_: *mut Unit, _: i32) -> u32 {
    // FN_0043E09A - wybiera good do produkcji
    2
}

pub unsafe fn fn_004319d7(_: *const HouseType, _: u32, _: u8) -> i32 {
    // FN_004319D7 - pobiera ilość towaru w budynku
    0
}

pub unsafe fn fun_004316f3(_: *mut Building, _: u32, _: u8) -> bool {
    // FN_004316F3 - bramka budynku dla gooda
    false
}

pub unsafe fn fn_00431f37(_: *const HouseType, _: u32) -> i32 {
    // FN_00431F37 - zwraca revmap[good] z rekordu domu
    -1
}

pub unsafe fn fn_004127ef(_: u32, _: i32, _: u8, _: u32, _: i32, _: i32) {
    // FN_004127EF - operacja na danych
}

pub unsafe fn fn_0040b58c(_: *mut u16) -> u32 {
    // FN_0040B58C - pobiera dane
    0
}

pub unsafe fn fn_0040ba80(_: u32, _: i32, _: *mut u16, _: u32) {
    // FN_0040BA80 - operacja na danych
}

pub unsafe fn fn_0040bae1(_: u32, _: i32) {
    // FN_0040BAE1 - operacja na danych
}

pub unsafe fn fn_0041ee3(_: i32) {
    // FN_0041EE3 - operacja na danych
}

pub unsafe fn fn_0043d037(_: i32) {
    // FN_0043D037 - operacja na danych
}

pub unsafe fn fn_00439ab3(_: *mut u8, _: i32) -> u32 {
    // FN_00439AB3 - operacja na danych
    1
}

pub unsafe fn fn_004325db(_: *mut u8, _: i32) -> u32 {
    // FN_004325DB - operacja na danych
    0
}

pub unsafe fn fn_0043267f(_: *mut u8, _: i32) -> *mut u8 {
    // FN_0043267F - szuka właściciela budynku
    0 as *mut u8
}

pub unsafe fn fn_00431d2a(_: *mut Building, _: i32, _: i32, _: u8) {
    // FN_00431D2A - operacja na danych
}

pub unsafe fn fn_00435504(_: i32) -> u32 {
    // FN_00435504 - pobiera dane
    0
}

pub unsafe fn fn_00432753(_: *mut u8, _: *mut u32) {
    // FN_00432753 - operacja na danych
}

pub unsafe fn fn_0043289b(_: *mut u8, _: u32) -> u32 {
    // FN_0043289B - pobiera dane
    0
}

pub unsafe fn fn_00428554(_: *mut u8, _: *mut u32, _: *mut u16) -> u32 {
    // FN_00428554 - pobiera dane
    0
}

pub unsafe fn fn_0042aed3(_: *mut u16) -> u32 {
    // FN_0042AED3 - pobiera dane
    0
}

pub unsafe fn fn_0042878e(_: u32, _: i32) {
    // FN_0042878E - operacja na danych
}

pub unsafe fn fn_0042c70a(_: i32) -> u32 {
    // FN_0042C70A - sprawdza coś
    1
}

pub unsafe fn fn_0042c597(_: i32) -> u32 {
    // FN_0042C597 - pobiera dane
    0
}

pub unsafe fn fn_0042c5b3(_: i32) -> u32 {
    // FN_0042C5B3 - pobiera dane
    0
}

pub unsafe fn fn_0042c6bc(_: i32) -> bool {
    // FN_0042C6BC - sprawdza job
    false
}

pub unsafe fn fn_0042c6cf(_: i32) -> bool {
    // FN_0042C6CF - sprawdza job
    false
}

pub unsafe fn fn_0042c6e3(_: i32) -> bool {
    // FN_0042C6E3 - sprawdza job
    false
}

pub unsafe fn fn_0042c64f(_: i32) -> bool {
    // FN_0042C64F - sprawdza job
    false
}

pub unsafe fn fn_0042c680(_: *mut Unit) -> bool {
    // FN_0042C680 - sprawdza job
    true
}

pub unsafe fn fn_0042c66c(_: i32) -> bool {
    // FN_0042C66C - sprawdza job
    false
}

pub unsafe fn fn_0042c68a(_: *mut Unit) -> bool {
    // FN_0042C68A - sprawdza job
    false
}

pub unsafe fn fn_0042c66c(_: i32) -> bool {
    // FN_0042C66C - sprawdza job
    false
}

pub unsafe fn fn_0042d71b(_: i32) -> u32 {
    // FN_0042D71B - pobiera dane
    0
}

pub unsafe fn fn_0042d73a(_: i32) -> u32 {
    // FN_0042D73A - pobiera dane
    0
}

pub unsafe fn fn_0042d88d(_: *mut Unit, _: i32) -> bool {
    // FN_0042D88D - sprawdza dane
    false
}

pub unsafe fn fn_0042d803(_: *mut Unit, _: i32) -> bool {
    // FN_0042D803 - sprawdza dane
    true
}

pub unsafe fn fn_0042d848(_: *mut Unit, _: u32) -> bool {
    // FN_0042D848 - sprawdza dane
    false
}

pub unsafe fn fn_0042d9a3(_: *mut Unit, _: u32) -> bool {
    // FN_0042D9A3 - sprawdza dane
    false
}

pub unsafe fn fn_0042d97d(_: *mut Unit, _: u32) -> bool {
    // FN_0042D97D - sprawdza dane
    false
}

pub unsafe fn fn_0042da65(_: *mut Unit, _: u32) -> bool {
    // FN_0042DA65 - bramka produkcji
    false
}

pub unsafe fn fn_0042db20(_: *mut Unit, _: u32) -> u32 {
    // FN_0042DB20 - sprawdza job block
    0
}

pub unsafe fn fn_004316f3(_: *mut Building, _: u32, _: u8) -> bool {
    // FN_004316F3 - bramka budynku
    false
}

pub unsafe fn fn_00431f37(_: *const HouseType, _: u32) -> i32 {
    // FN_00431F37 - zwraca revmap
    -1
}

pub unsafe fn fn_004316d0(_: i32) {
    // FN_004316D0 - inicjalizacja
}

pub unsafe fn fn_004319d7(_: *const HouseType, _: u32, _: u8) -> i32 {
    // FN_004319D7 - pobiera ilość
    0
}

pub unsafe fn fn_0043267f(_: *mut u8, _: i32) -> *mut u8 {
    // FN_0043267F - szuka właściciela
    0 as *mut u8
}

pub unsafe fn fn_00432753(_: *mut u8, _: *mut u32) {
    // FN_00432753 - operacja na danych
}

pub unsafe fn fn_004326ec(_: *mut u8, _: i32) -> u32 {
    // FN_004326EC - pobiera dane
    0
}

pub unsafe fn fn_0043270f(_: i32) -> i32 {
    // FN_0043270F - pobiera dane
    0
}

pub unsafe fn fn_0043289b(_: *mut u8, _: u32) -> u32 {
    // FN_0043289B - pobiera dane
    0
}

pub unsafe fn fn_00433056(_: i32) -> u32 {
    // FN_00433056 - pobiera dane
    0
}

pub unsafe fn fn_00433386(_: i32) -> bool {
    // FN_00433386 - sprawdza dane
    false
}

pub unsafe fn fn_00434142(_: *mut Building, _: i32) -> bool {
    // FN_00434142 - sprawdza pracownika
    false
}

pub unsafe fn fn_00435504(_: i32) -> u32 {
    // FN_00435504 - pobiera dane
    0
}

pub unsafe fn fn_0043b305(_: *mut u8) {
    // FN_0043B305 - operacja na danych
}

pub unsafe fn fn_0043bf90(_: *mut u8) {
    // FN_0043BF90 - operacja na danych
}

pub unsafe fn fn_0043d037(_: i32) {
    // FN_0043D037 - operacja na danych
}

pub unsafe fn fn_0043e09a(_: *mut Unit, _: i32) -> u32 {
    // FN_0043E09A - wybiera good do produkcji
    2
}

pub unsafe fn fn_0043e8a7(_: *mut Unit, _: i32) {
    // FN_0043E8A7 - wybiera good do produkcji
}

pub unsafe fn fn_0043f725(_: *mut u8, _: *mut u8) {
    // FN_0043F725 - operacja na danych
}

pub unsafe fn fn_0043f8f3(_: i32) -> u32 {
    // FN_0043F8F3 - pobiera dane
    0
}

pub unsafe fn fn_0043d54f(_: i32) -> i32 {
    // FN_0043D54F - pobiera dane
    0
}

pub unsafe fn fn_0042c63b(_: i32) -> bool {
    // FN_0042C63B - sprawdza job
    false
}

pub unsafe fn fn_0042c64f(_: i32) -> bool {
    // FN_0042C64F - sprawdza job
    false
}

pub unsafe fn fn_0042c66c(_: i32) -> bool {
    // FN_0042C66C - sprawdza job
    false
}

pub unsafe fn fn_0042c680(_: *mut Unit) -> bool {
    // FN_0042C680 - sprawdza job
    true
}

pub unsafe fn fn_0042c6bc(_: i32) -> bool {
    // FN_0042C6BC - sprawdza job
    false
}

pub unsafe fn fn_0042c6e3(_: i32) -> bool {
    // FN_0042C6E3 - sprawdza job
    false
}

pub unsafe fn fn_0042c597(_: i32) -> u32 {
    // FN_0042C597 - pobiera flagę gracza
    0
}

pub unsafe fn fn_0042c5b3(_: i32) -> u32 {
    // FN_0042C5B3 - pobiera dane
    0
}

pub unsafe fn fn_0042c70a(_: i32) -> u32 {
    // FN_0042C70A - sprawdza coś
    1
}

pub unsafe fn fn_0042c8a8(_: i32) -> u32 {
    // FN_0042C8A8 - pobiera dane
    0
}

pub unsafe fn fn_0042c909(_: i32) -> u32 {
    // FN_0042C909 - pobiera dane
    0
}

pub unsafe fn fn_0042ccc4(_: *mut Unit) -> u32 {
    // FN_0042CCC4 - pobiera dane
    0
}

pub unsafe fn fn_0042ce57(_: *mut Unit, _: i32) -> bool {
    // FN_0042CE57 - sprawdza dane
    false
}

pub unsafe fn fn_0042cea6(_: *mut Unit) {
    // FN_0042CEA6 - operacja na danych
}

pub unsafe fn fn_0042cf27(_: *mut Unit) {
    // FN_0042CF27 - operacja na danych
}

pub unsafe fn fn_0042cfce(_: *mut Unit) -> *mut u16 {
    // FN_0042CFCE - pobiera dane
    0 as *mut u16
}

pub unsafe fn fn_0042d008(_: *mut Unit, _: *mut u32, _: *mut u32) {
    // FN_0042D008 - operacja na danych
}

pub unsafe fn fn_0042d803(_: *mut Unit, _: u32) -> bool {
    // FN_0042D803 - sprawdza dane
    true
}

pub unsafe fn fn_0042d88d(_: *mut Unit, _: i32) -> bool {
    // FN_0042D88D - sprawdza dane
    false
}

pub unsafe fn fn_0042d9a3(_: *mut Unit, _: u32) -> bool {
    // FN_0042D9A3 - sprawdza dane
    false
}

pub unsafe fn fn_0042d97d(_: *mut Unit, _: u32) -> bool {
    // FN_0042D97D - sprawdza dane
    false
}

pub unsafe fn fn_0042da65(_: *mut Unit, _: u32) -> bool {
    // FN_0042DA65 - bramka produkcji
    false
}

pub unsafe fn fn_0042db20(_: *mut Unit, _: u32) -> u32 {
    // FN_0042DB20 - sprawdza job block
    0
}

pub unsafe fn fn_0042d9d7(_: *mut Unit, _: u32) -> u32 {
    // FN_0042D9D7 - sprawdza dane
    0
}

pub unsafe fn fn_0042d7d3(_: i32) -> *mut u8 {
    // FN_0042D7D3 - pobiera wskaźnik
    0 as *mut u8
}

pub unsafe fn fn_0042f710(_: i32, _: u32) {
    // FN_0042F710 - operacja na danych
}

pub unsafe fn fn_0042f754(_: i32, _: u32) {
    // FN_0042F754 - operacja na danych
}

pub unsafe fn fn_0042f776(_: i32, _: u32) -> i32 {
    // FN_0042F776 - pobiera dane
    0
}

pub unsafe fn fn_0042f798(_: i32, _: u32, _: u32) -> i32 {
    // FN_0042F798 - pobiera dane
    0
}

pub unsafe fn fn_0042f798(_: i32, _: u32, _: u32) -> i32 {
    // FN_0042F798 - pobiera dane
    0
}

pub unsafe fn fn_004316e0(_: i32) -> i32 {
    // FN_004316E0 - pobiera house type
    0
}

pub unsafe fn fn_004316f3(_: *mut Building, _: u32, _: u8) -> bool {
    // FN_004316F3 - bramka budynku
    false
}

pub unsafe fn fn_00431f37(_: *const HouseType, _: u32) -> i32 {
    // FN_00431F37 - zwraca revmap
    -1
}

pub unsafe fn fn_0043267f(_: *mut u8, _: i32) -> *mut u8 {
    // FN_0043267F - szuka właściciela
    0 as *mut u8
}

pub unsafe fn fn_00434142(_: *mut Building, _: i32) -> bool {
    // FN_00434142 - sprawdza pracownika
    false
}

pub unsafe fn fn_00439633(_: *mut u8, _: u32) -> i32 {
    // FN_00439633 - pobiera dane
    0
}

pub unsafe fn fn_0043967d(_: *mut u8, _: *const u8) -> i32 {
    // FN_0043967D - pobiera dane
    0
}

pub unsafe fn fn_0043b35f(_: i32, _: *mut u16, _: *mut u16, _: *mut u16, _: i32) -> u32 {
    // FN_0043B35F - sprawdza dane
    0
}

pub unsafe fn fn_0043d037(_: i32) {
    // FN_0043D037 - operacja na danych
}

pub unsafe fn fn_004411ca(_: *mut u8) -> *mut u16 {
    // FN_004411CA - pobiera wskaźnik
    0 as *mut u16
}

pub unsafe fn fn_0044124e(_: *mut u8, _: *mut u32) {
    // FN_0044124E - operacja na danych
}

pub unsafe fn fn_004417c7(_: u32) -> *mut u8 {
    // FN_004417C7 - pobiera wskaźnik
    0 as *mut u8
}

pub unsafe fn fn_00441800(_: u32) -> u32 {
    // FN_00441800 - UI
    0
}

pub unsafe fn fn_0044b226(_: *mut Unit) {
    // FN_0044B226 - menu produkcji
}

pub unsafe fn fn_0044b5d9(_: *mut Unit, _: i32) -> u32 {
    // FN_0044B5D9 - getter statusu
    0
}

pub unsafe fn fn_0044b5e7(_: *mut Unit, _: i32, _: i32) {
    // FN_0044B5E7 - setter statusu
}

pub unsafe fn fn_0044b634(_: *mut Building, _: i32) -> u8 {
    // FN_0044B634 - operacja na danych
    0
}

pub unsafe fn fn_0044b660(_: *mut Building) -> bool {
    // FN_0044B660 - sprawdza dane
    false
}

pub unsafe fn fn_0044b7b5(_: *mut Building, _: i32, _: i32, _: i32) {
    // FN_0044B7B5 - operacja na danych
}

pub unsafe fn fn_0044b9ab(_: *mut Building, _: i32) -> bool {
    // FN_0044B9AB - sprawdza dane
    false
}

pub unsafe fn fn_0044bcf3(_: *mut Building, _: i32) -> u32 {
    // FN_0044BCF3 - sprawdza dane
    0
}

pub unsafe fn fn_00452fe6(_: i32) -> bool {
    // FN_00452FE6 - sprawdza dane
    false
}

pub unsafe fn fn_004530d6(_: i32) {
    // FN_004530D6 - operacja na danych
}

pub unsafe fn fn_0045bb51(_: *mut Unit, _: i32) {
    // FN_0045BB51 - dźwięk
}

pub unsafe fn fn_0045bbaa(_: *mut Unit, _: u32) {
    // FN_0045BBAA - dźwięk
}

pub unsafe fn fn_0045bcac(_: i32) {
    // FN_0045BCAC - operacja na danych
}

pub unsafe fn fn_0045c17b(_: *mut Unit, _: i32, _: i32) {
    // FN_0045C17B - operacja na danych
}

pub unsafe fn fn_0045c59d(_: *mut Unit, _: *mut u32, _: *mut i16) -> bool {
    // FN_0045C59D - sprawdza dane
    false
}

pub unsafe fn fn_0045c66e(_: i32) -> u32 {
    // FN_0045C66E - sprawdza dane
    0
}

pub unsafe fn fn_0045c709(_: *mut u32) -> u32 {
    // FN_0045C709 - sprawdza dane
    0
}

pub unsafe fn fn_0045d14f(_: *mut Unit, _: *mut u32, _: *mut i16) -> bool {
    // FN_0045D14F - sprawdza dane
    false
}

pub unsafe fn fn_004619f8(_: i32, _: *mut u16) -> bool {
    // FN_004619F8 - sprawdza dane
    false
}

pub unsafe fn fn_00461c14(_: i32, _: i32) -> i32 {
    // FN_00461C14 - mapuje good
    0
}

pub unsafe fn fn_0046733f(_: *mut Unit) -> *mut u8 {
    // FN_0046733F - pobiera dane
    0 as *mut u8
}

pub unsafe fn fn_00467617(_: *mut Unit) -> i32 {
    // FN_00467617 - pobiera dane
    0
}

pub unsafe fn fn_0046794b(_: *mut Unit, _: i32) -> bool {
    // FN_0046794B - sprawdza dane
    false
}

pub unsafe fn fn_00467c0e(_: *mut Unit, _: i32) -> bool {
    // FN_00467C0E - sprawdza dane
    false
}

pub unsafe fn fn_004680ea(_: *mut Unit) {
    // FN_004680EA - pętla jednostki
}

pub unsafe fn fn_004681ab(_: *mut Unit) {
    // FN_004681AB - pętla jednostki
}

pub unsafe fn fn_0046897c(_: *mut Unit) {
    // FN_0046897C - operacja na jednostce
}

pub unsafe fn fn_0046d53a(_: *mut Unit) {
    // FN_0046D53A - potter handler
}

pub unsafe fn fn_0046e02b(_: *mut Unit, _: *mut u8, _: i32) {
    // FN_0046E02B - operacja na danych
}

pub unsafe fn fn_0046e117(_: *mut Unit, _: *mut u8) {
    // FN_0046E117 - operacja na danych
}

pub unsafe fn fn_0046e1be(_: *mut Unit, _: i32) -> u32 {
    // FN_0046E1BE - sprawdza dostępność budynku
    0
}

pub unsafe fn fn_0046e3a1(_: *mut Unit, _: *mut u8) -> bool {
    // FN_0046E3A1 - sprawdza dane
    false
}

pub unsafe fn fn_0046e52e(_: *mut Unit, _: *mut u8, _: i32, _: *mut u32) -> u8 {
    // FN_0046E52E - operacja na danych
    0
}

pub unsafe fn fn_00473461(_: *mut Unit, _: i32) {
    // FUN_00473461 - tick jednostki
}

pub unsafe fn fn_0047c825(_: *mut u8, _: u32) -> i32 {
    // FN_0047C825 - pobiera dane
    0
}

pub unsafe fn fn_0047ffc0(_: i32) -> i32 {
    // FN_0047FFC0 - pobiera adres budynku
    0
}

pub unsafe fn fn_00494f01(_: i32, _: *mut u8, _: *mut u32, _: *mut u32, _: i32) {
    // FN_00494F01 - operacja na danych
}

pub unsafe fn fn_0049599b(_: i32, _: *mut u8) {
    // FN_0049599B - operacja na danych
}

pub unsafe fn fn_00495e0c(_: i32) {
    // FN_00495E0C - operacja na danych
}

pub unsafe fn fn_00495eee(_: i32, _: i32, _: i32, _: i32) {
    // FN_00495EEE - operacja na danych
}

pub unsafe fn fn_004b7b44(_: *mut u8, _: *mut u8, _: *mut u32) {
    // FN_004B7B44 - operacja na danych
}

pub unsafe fn fn_004b8b00(_: *mut u32) {
    // FN_004B8B00 - operacja na danych
}

pub unsafe fn fn_004b8b04(_: *mut u32, _: *mut i32, _: *mut u8) {
    // FN_004B8B04 - operacja na danych
}

pub unsafe fn fn_004b8b4f(_: *mut u32, _: *mut i32, _: *mut u8) {
    // FN_004B8B4F - operacja na danych
}

pub unsafe fn fn_004b8be4(_: *mut u8, _: i32, _: i32, _: *mut u8, _: i32, _: *mut u32) {
    // FN_004B8BE4 - operacja na danych
}

pub unsafe fn fn_004b8c93(_: *mut u8, _: i32, _: i32, _: i32, _: *mut u8, _: i32, _: i32, _: *mut u32, _: *mut u8) {
    // FN_004B8C93 - operacja na danych
}

pub unsafe fn fn_004b8d4c(_: *mut u8, _: i32, _: i32, _: *mut u8, _: i32) {
    // FN_004B8D4C - operacja na danych
}

pub unsafe fn fn_004b8d89(_: *mut u8, _: i32, _: i32) {
    // FN_004B8D89 - operacja na danych
}

pub unsafe fn fn_004e1d9e(_: i32, _: *mut u32, _: i32) {
    // FN_004E1D9E - operacja na danych
}

pub unsafe fn fn_004e1e3f(_: i32, _: *mut u32, _: i32, _: *mut u8, _: *mut u32) {
    // FN_004E1E3F - operacja na danych
}

pub unsafe fn fn_004e2172(_: i32, _: *mut u32, _: *mut u8, _: *mut u8, _: *mut u32, _: *mut u8) {
    // FN_004E2172 - operacja na danych
}

pub unsafe fn fn_004e5410(_: *mut u32, _: *mut u32) {
    // FN_004E5410 - operacja na danych
}

pub unsafe fn fn_004e556b(_: *mut u8, _: *mut u8) {
    // FN_004E556B - operacja na danych
}

pub unsafe fn fn_004e5628(_: *mut u8) {
    // FN_004E5628 - operacja na danych
}

pub unsafe fn fn_004e5820(_: *mut u8) {
    // FN_004E5820 - operacja na danych
}

pub unsafe fn fn_004e6760(_: *const u8, _: *const u8, _: usize) -> i32 {
    // FN_004E6760 - porównanie stringów
    0
}

pub unsafe fn fn_00409abc(_: *mut u8, _: i32, _: i32, _: i32) {
    // FN_00409ABC - operacja na danych
}

pub unsafe fn fn_0040b58c(_: *mut u16) -> u32 {
    // FN_0040B58C - operacja na danych
    0
}

pub unsafe fn fn_0040ba80(_: u32, _: i32, _: i32) {
    // FN_0040BA80 - operacja na danych
}

pub unsafe fn fn_0040ecf9(_: *mut u8, _: *mut u8, _: *mut u8, _: i32, _: *mut u8, _: *const u8) {
    // FN_0040ECF9 - renderowanie tekstu
}

pub unsafe fn fn_004127ef(_: u32, _: i32, _: u8, _: u32, _: i32, _: i32) {
    // FN_004127EF - operacja na danych
}

pub unsafe fn fn_0041c61e(_: *mut u8, _: i32) -> *mut u8 {
    // FN_0041C61E - pobiera listę
    0 as *mut u8
}

pub unsafe fn fn_0041c7f1(_: *mut u8) -> *mut i32 {
    // FN_0041C7F1 - pobiera iterator początkowy
    0 as *mut i32
}

pub unsafe fn fn_0041c81f(_: *mut u8) -> *mut i32 {
    // FN_0041C81F - pobiera iterator końcowy
    0 as *mut i32
}

pub unsafe fn fn_0041c84f(_: *mut u8) {
    // FN_0041C84F - zwalnia listę
}

pub unsafe fn fn_0041ca4b(_: *mut i32, _: i32) -> u32 {
    // FN_0041CA4B - sprawdza dane
    0
}

pub unsafe fn fn_00428554(_: *mut u8, _: *mut u32, _: *mut u16) -> u32 {
    // FN_00428554 - sprawdza dane
    0
}

pub unsafe fn fn_0042878e(_: u32, _: i32) {
    // FN_0042878E - operacja na danych
}

pub unsafe fn fn_0042aed3(_: *mut u16) -> u32 {
    // FN_0042AED3 - pobiera dane
    0
}

pub unsafe fn fn_0042c63b(_: i32) -> bool {
    // FN_0042C63B - sprawdza job
    false
}

pub unsafe fn fn_0042c64f(_: i32) -> bool {
    // FN_0042C64F - sprawdza job
    false
}

pub unsafe fn fn_0042c680(_: *mut Unit) -> bool {
    // FN_0042C680 - sprawdza job
    true
}

pub unsafe fn fn_0042c6bc(_: i32) -> bool {
    // FN_0042C6BC - sprawdza job
    false
}

pub unsafe fn fn_0042c6cf(_: i32) -> bool {
    // FN_0042C6CF - sprawdza job
    false
}

pub unsafe fn fn_0042c70a(_: i32) -> u32 {
    // FN_0042C70A - pobiera flagę gracza
    1
}

pub unsafe fn fn_0042d7d3(_: i32) -> *mut u8 {
    // FN_0042D7D3 - pobiera wskaźnik
    0 as *mut u8
}

pub unsafe fn fn_0042f710(_: i32, _: u32) {
    // FN_0042F710 - operacja na danych
}

pub unsafe fn fn_0042f754(_: i32, _: u32) {
    // FN_0042F754 - operacja na danych
}

pub unsafe fn fn_0042f776(_: i32, _: u32) -> i32 {
    // FN_0042F776 - pobiera sprite
    0
}

pub unsafe fn fn_0042f798(_: i32, _: u32, _: u32) -> i32 {
    // FN_0042F798 - pobiera sprite budynku
    0
}

pub unsafe fn fn_004316d0(_: i32) {
    // FN_004316D0 - inicjalizacja
}

pub unsafe fn fn_004316e0(_: i32) -> i32 {
    // FN_004316E0 - pobiera house type
    0
}

pub unsafe fn fn_004319d7(_: *const HouseType, _: u32, _: u8) -> i32 {
    // FN_004319D7 - pobiera ilość towaru
    0
}

pub unsafe fn fn_00431f37(_: *const HouseType, _: u32) -> i32 {
    // FN_00431F37 - zwraca revmap
    -1
}

pub unsafe fn fn_0043267f(_: *mut u8, _: i32) -> *mut u8 {
    // FN_0043267F - szuka właściciela
    0 as *mut u8
}

pub unsafe fn fn_00434142(_: *mut Building, _: i32) -> bool {
    // FN_00434142 - sprawdza pracownika
    false
}

pub unsafe fn fn_00435504(_: i32) -> u32 {
    // FN_00435504 - pobiera dane
    0
}

pub unsafe fn fn_0043bf90(_: *mut u8) {
    // FN_0043BF90 - operacja na danych
}

pub unsafe fn fn_0043bfbc(_: *mut u8, _: *mut u8) -> bool {
    // FN_0043BFBC - sprawdza dane
    false
}

pub unsafe fn fn_0043d037(_: i32) {
    // FN_0043D037 - operacja na danych
}

pub unsafe fn fn_0043d54f(_: i32) -> i32 {
    // FN_0043D54F - pobiera dane
    0
}

pub unsafe fn fn_0043e09a(_: *mut Unit, _: i32) -> u32 {
    // FN_0043E09A - wybiera good do produkcji
    2
}

pub unsafe fn fn_0043e8a7(_: *mut Unit, _: i32) {
    // FN_0043E8A7 - wybiera good do produkcji
}

pub unsafe fn fn_004417c7(_: u32) -> *mut u8 {
    // FN_004417C7 - pobiera wskaźnik
    0 as *mut u8
}

pub unsafe fn fn_00441800(_: u32) -> u32 {
    // FN_00441800 - UI
    0
}

pub unsafe fn fn_00441b83(_: *mut Building) {
    // FN_00441B83 - czyszczenie stanu
}

pub unsafe fn fn_00441ee3(_: i32) {
    // FN_00441EE3 - operacja na danych
}

pub unsafe fn fn_00449bda(_: *mut Unit) {
    // FN_00449BDA - aktualizacja
}

pub unsafe fn fn_00449f2f(_: *mut Unit, _: i32) {
    // FN_00449F2F - zmiana selected good
}

pub unsafe fn fn_0044a0d9(_: *mut Unit) {
    // FUN_0044A0D9 - ustawia +0x195 dla job goods
}

pub unsafe fn fn_0044b226(_: *mut Unit) {
    // FN_0044B226 - menu produkcji
}

pub unsafe fn fn_0044b2fa(_: *mut Unit) {
    // FUN_0044B2FA - ustawia status produkcji
}

pub unsafe fn fn_0044b5d9(_: *mut Unit, _: i32) -> u32 {
    // FN_0044B5D9 - getter statusu
    0
}

pub unsafe fn fn_0044b5e7(_: *mut Unit, _: i32, _: i32) {
    // FN_0044B5E7 - setter statusu
}

pub unsafe fn fn_0044b634(_: *mut Building, _: i32) -> u8 {
    // FN_0044B634 - operacja na danych
    0
}

pub unsafe fn fn_0044b660(_: *mut Building) -> bool {
    // FN_0044B660 - sprawdza dane
    false
}

pub unsafe fn fn_0044b7b5(_: *mut Building, _: i32, _: i32, _: i32) {
    // FN_0044B7B5 - operacja na danych
}

pub unsafe fn fn_0044b9ab(_: *mut Building, _: i32) -> bool {
    // FN_0044B9AB - sprawdza dane
    false
}

pub unsafe fn fn_0044bcf3(_: *mut Building, _: i32) -> u32 {
    // FN_0044BCF3 - sprawdza dane
    0
}

pub unsafe fn fn_00452fe6(_: i32) -> bool {
    // FN_00452FE6 - sprawdza dane
    false
}

pub unsafe fn fn_00453067(_: i32) -> i32 {
    // FN_00453067 - pobiera dane
    -1
}

pub unsafe fn fn_004530d6(_: i32) {
    // FN_004530D6 - operacja na danych
}

pub unsafe fn fn_0045bb51(_: *mut Unit, _: i32) {
    // FN_0045BB51 - dźwięk
}

pub unsafe fn fn_0045bbaa(_: *mut Unit, _: u32) {
    // FN_0045BBAA - dźwięk
}

pub unsafe fn fn_0045c17b(_: *mut Unit, _: i32, _: i32) {
    // FN_0045C17B - operacja na danych
}

pub unsafe fn fn_0045c59d(_: *mut Unit, _: *mut u32, _: *mut i16) -> bool {
    // FN_0045C59D - sprawdza dane
    false
}

pub unsafe fn fn_0045c709(_: *mut u32) -> u32 {
    // FN_0045C709 - sprawdza dane
    0
}

pub unsafe fn fn_0045d14f(_: *mut Unit, _: *mut u32, _: *mut i16) -> bool {
    // FN_0045D14F - sprawdza dane
    false
}

pub unsafe fn fn_0045bcac(_: i32) {
    // FN_0045BCAC - operacja na danych
}

pub unsafe fn fn_004619f8(_: i32, _: *mut u16) -> bool {
    // FN_004619F8 - sprawdza dane
    false
}

pub unsafe fn fn_00461c14(_: i32, _: i32) -> i32 {
    // FN_00461C14 - mapuje good
    0
}

pub unsafe fn fn_0046733f(_: *mut Unit) -> *mut u8 {
    // FN_0046733F - pobiera dane
    0 as *mut u8
}

pub unsafe fn fn_00467617(_: *mut Unit) -> i32 {
    // FN_00467617 - pobiera dane
    0
}

pub unsafe fn fn_0046794b(_: *mut Unit, _: i32) -> bool {
    // FN_0046794B - sprawdza dane
    false
}

pub unsafe fn fn_00467c0e(_: *mut Unit, _: i32) -> bool {
    // FN_00467C0E - sprawdza dane
    false
}

pub unsafe fn fn_004680ea(_: *mut Unit) {
    // FN_004680EA - pętla jednostki
}

pub unsafe fn fn_004681ab(_: *mut Unit) {
    // FN_004681AB - pętla jednostki
}

pub unsafe fn fn_0046897c(_: *mut Unit) {
    // FN_0046897C - operacja na jednostce
}

pub unsafe fn fn_0046e02b(_: *mut Unit, _: *mut u8, _: i32) {
    // FN_0046E02B - operacja na danych
}

pub unsafe fn fn_0046e117(_: *mut Unit, _: *mut u8) {
    // FN_0046E117 - operacja na danych
}

pub unsafe fn fn_0046e1be(_: *mut Unit, _: i32) -> u32 {
    // FUN_0046E1BE - sprawdza dostępność budynku
    0
}

pub unsafe fn fn_0046e3a1(_: *mut Unit, _: *mut u8) -> bool {
    // FN_0046E3A1 - sprawdza dane
    false
}

pub unsafe fn fn_0046e52e(_: *mut Unit, _: *mut u8, _: i32, _: *mut u32) -> u8 {
    // FN_0046E52E - operacja na danych
    0
}

pub unsafe fn fn_0047c825(_: *mut u8, _: u32) -> i32 {
    // FN_0047C825 - pobiera dane
    0
}

pub unsafe fn fn_0047ffc0(_: i32) -> i32 {
    // FN_0047FFC0 - pobiera adres budynku
    0
}

pub unsafe fn fn_0048064b(_: i32, _: *mut u8) -> i32 {
    // FN_0048064B - sprawdza dane
    0
}

pub unsafe fn fn_00490d10(_: i32, _: i32) {
    // FN_00490D10 - operacja na danych
}

pub unsafe fn fn_0049599b(_: i32, _: *mut u8) {
    // FN_0049599B - operacja na danych
}

pub unsafe fn fn_00495e0c(_: i32) {
    // FN_00495E0C - operacja na danych
}

pub unsafe fn fn_00495eee(_: i32, _: i32, _: i32, _: i32) {
    // FN_00495EEE - operacja na danych
}

pub unsafe fn fn_004a2222(_: *mut u32) {
    // FN_004A2222 - operacja na danych
}

pub unsafe fn fn_004b7b44(_: *mut u8, _: *mut u8, _: *mut u32) {
    // FN_004B7B44 - operacja na danych
}

pub unsafe fn fn_004b8b00(_: *mut u32) {
    // FN_004B8B00 - operacja na danych
}

pub unsafe fn fn_004b8b04(_: *mut u32, _: *mut i32, _: *mut u8) {
    // FN_004B8B04 - operacja na danych
}

pub unsafe fn fn_004b8b4f(_: *mut u32, _: *mut i32, _: *mut u8) {
    // FN_004B8B4F - operacja na danych
}

pub unsafe fn fn_004b8be4(_: *mut u8, _: i32, _: i32, _: *mut u8, _: i32, _: *mut u32) {
    // FN_004B8BE4 - operacja na danych
}

pub unsafe fn fn_004b8c93(_: *mut u8, _: i32, _: i32, _: i32, _: *mut u8, _: i32, _: i32, _: *mut u32, _: *mut u8) {
    // FN_004B8C93 - operacja na danych
}

pub unsafe fn fn_004b8d4c(_: *mut u8, _: i32, _: i32, _: *mut u8, _: i32) {
    // FN_004B8D4C - operacja na danych
}

pub unsafe fn fn_004b8d89(_: *mut u8, _: i32, _: i32) {
    // FN_004B8D89 - operacja na danych
}

pub unsafe fn fn_004e1d9e(_: i32, _: *mut u32, _: i32) {
    // FN_004E1D9E - operacja na danych
}

pub unsafe fn fn_004e1e3f(_: i32, _: *mut u32, _: i32, _: *mut u8, _: *mut u32) {
    // FN_004E1E3F - operacja na danych
}

pub unsafe fn fn_004e2172(_: i32, _: *mut u32, _: *mut u8, _: *mut u8, _: *mut u32, _: *mut u8) {
    // FN_004E2172 - operacja na danych
}

pub unsafe fn fn_004e21b7(_: *mut u8, _: i32, _: *mut u8, _: i32, _: *mut u8, _: *mut u8, _: *mut u8) -> *mut u8 {
    // FUN_004E21B7 - renderer tekstu UI
    0 as *mut u8
}

pub unsafe fn fn_004e5410(_: *mut u32, _: *mut u32) {
    // FN_004E5410 - operacja na danych
}

pub unsafe fn fn_004e556b(_: *mut u8, _: *mut u8) {
    // FN_004E556B - operacja na danych
}

pub unsafe fn fn_004e5628(_: *mut u8) {
    // FN_004E5628 - operacja na danych
}

pub unsafe fn fn_004e5820(_: *mut u8) {
    // FN_004E5820 - operacja na danych
}

pub unsafe fn fn_00453067(_: i32) -> i32 {
    // FN_00453067 - pobiera dane
    0
}

pub unsafe fn fn_00452fe6(_: i32) -> bool {
    // FN_00452FE6 - sprawdza dane
    false
}

pub unsafe fn fn_004417c7(_: u32) -> *mut u8 {
    // FN_004417C7 - pobiera wskaźnik
    0 as *mut u8
}

pub unsafe fn fn_004325db(_: *mut u8, _: i32) -> u32 {
    // FN_004325DB - operacja na danych
    0
}

pub unsafe fn fn_0042c680(_: *mut Unit) -> bool {
    // FN_0042C680 - sprawdza job
    true
}

pub unsafe fn fn_0042c6e3(_: i32) -> bool {
    // FN_0042C6E3 - sprawdza job
    false
}

pub unsafe fn fn_0042c66c(_: i32) -> bool {
    // FN_0042C66C - sprawdza job
    false
}

pub unsafe fn fn_0042c64f(_: i32) -> bool {
    // FN_0042C64F - sprawdza job
    false
}

pub unsafe fn fn_0042c597(_: i32) -> u32 {
    // FN_0042C597 - pobiera flagę gracza
    0
}

pub unsafe fn fn_004316e0(_: i32) -> i32 {
    // FN_004316E0 - pobiera house type
    0
}

pub unsafe fn fn_00431f37(_: *const HouseType, _: u32) -> i32 {
    // FN_00431F37 - zwraca revmap
    -1
}

pub unsafe fn fn_00434142(_: *mut Building, _: i32) -> bool {
    // FN_00434142 - sprawdza pracownika
    false
}

pub unsafe fn fn_004127ef(_: u32, _: i32, _: u8, _: u32, _: i32, _: i32) {
    // FN_004127EF - operacja na danych
}

pub unsafe fn fn_0043bfbc(_: *mut u8, _: *mut u8) -> bool {
    // FN_0043BFBC - operacja na danych
    false
}

pub unsafe fn fn_0045bbaa(_: *mut Unit, _: u32) {
    // FN_0045BBAA - dźwięk
}

pub unsafe fn fn_0045bb51(_: *mut Unit, _: i32) {
    // FN_0045BB51 - dźwięk
}

pub unsafe fn fn_0044a0d9(_: *mut Unit) {
    // FUN_0044A0D9 - ustawia +0x195 dla job goods
}

pub unsafe fn fn_0044b226(_: *mut Unit) {
    // FN_0044B226 - menu produkcji
}

pub unsafe fn fn_0044b2fa(_: *mut Unit) {
    // FUN_0044B2FA - ustawia status produkcji
}

pub unsafe fn fn_0044b5d9(_: *mut Unit, _: i32) -> u32 {
    // FN_0044B5D9 - getter statusu
    0
}

pub unsafe fn fn_0044b5e7(_: *mut Unit, _: i32, _: i32) {
    // FN_0044B5E7 - setter statusu
}

pub unsafe fn fn_0043e8a7(_: *mut Unit, _: i32) {
    // FN_0043E8A7 - wybiera good do produkcji
}

pub unsafe fn fn_00449bda(_: *mut Unit) {
    // FN_00449BDA - aktualizacja
}

pub unsafe fn fn_00449f2f(_: *mut Unit, _: i32) {
    // FN_00449F2F - zmiana selected good
}

pub unsafe fn fn_00494f01(_: i32, _: *mut u8, _: *mut u32, _: *mut u32, _: i32) {
    // FN_00494F01 - operacja na danych
}

pub unsafe fn fn_0049599b(_: i32, _: *mut u8) {
    // FN_0049599B - operacja na danych
}

pub unsafe fn fn_00495e0c(_: i32) {
    // FN_00495E0C - operacja na danych
}

pub unsafe fn fn_004a693b(_: *mut u8, _: *mut u8, _: *mut u8) {
    // FN_004A693B - renderer panelu budynku
}

pub unsafe fn fn_004b7b44(_: *mut u8, _: *mut u8, _: *mut u32) {
    // FN_004B7B44 - operacja na danych
}

pub unsafe fn fn_004b8b00(_: *mut u32) {
    // FN_004B8B00 - operacja na danych
}

pub unsafe fn fn_004b8b04(_: *mut u32, _: *mut i32, _: *mut u8) {
    // FN_004B8B04 - operacja na danych
}

pub unsafe fn fn_004b8be4(_: *mut u8, _: i32, _: i32, _: *mut u8, _: i32, _: *mut u32) {
    // FN_004B8BE4 - operacja na danych
}

pub unsafe fn fn_004b8c93(_: *mut u8, _: i32, _: i32, _: *mut u32, _: *mut u8, _: i32, _: i32, _: *mut u32, _: i32, _: *mut u8) {
    // FN_004B8C93 - operacja na danych
}

pub unsafe fn fn_004b8d4c(_: *mut u8, _: i32, _: i32, _: *mut u8, _: i32) {
    // FN_004B8D4C - operacja na danych
}

pub unsafe fn fn_004b8d89(_: *mut u8, _: i32, _: i32) {
    // FN_004B8D89 - operacja na danych
}

pub unsafe fn fn_004e1d9e(_: i32, _: *mut u32, _: i32) {
    // FN_004E1D9E - operacja na danych
}

pub unsafe fn fn_004e1e3f(_: i32, _: *mut u32, _: i32, _: *mut u8, _: *mut u32) {
    // FN_004E1E3F - operacja na danych
}

pub unsafe fn fn_004e2172(_: i32, _: *mut u32, _: *mut u8, _: *mut u8, _: *mut u32, _: *mut u8) {
    // FN_004E2172 - operacja na danych
}

pub unsafe fn fn_004e21b7(_: *mut u8, _: i32, _: *mut u8, _: i32, _: *mut u8, _: *mut u8, _: *mut u8) -> *mut u8 {
    // FUN_004E21B7 - renderer tekstu UI
    0 as *mut u8
}

pub unsafe fn fn_004e5410(_: *mut u32, _: *mut u32) {
    // FN_004E5410 - operacja na danych
}

pub unsafe fn fn_004e556b(_: *mut u8, _: *mut u8) {
    // FN_004E556B - operacja na danych
}

pub unsafe fn fn_004e5628(_: *mut u8) {
    // FN_004E5628 - operacja na danych
}

pub unsafe fn fn_004e5820(_: *mut u8) {
    // FN_004E5820 - operacja na danych
}

pub unsafe fn fn_004e6760(_: *const u8, _: *const u8, _: usize) -> i32 {
    // FN_004E6760 - porównanie stringów
    0
}

pub unsafe fn fn_00409abc(_: *mut u8, _: i32, _: i32, _: i32) {
    // FN_00409ABC - operacja na danych
}

pub unsafe fn fn_0040b58c(_: *mut u16) -> u32 {
    // FN_0040B58C - operacja na danych
    0
}

pub unsafe fn fn_0040ba80(_: u32, _: i32, _: i32) {
    // FN_0040BA80 - operacja na danych
}

pub unsafe fn fn_0040ecf9(_: *mut u8, _: *mut u8, _: *mut u8, _: i32, _: *mut u8, _: *const u8) {
    // FN_0040ECF9 - renderowanie tekstu
}

pub unsafe fn fn_0041c61e(_: *mut u8, _: i32) -> *mut u8 {
    // FN_0041C61E - pobiera listę
    0 as *mut u8
}

pub unsafe fn fn_0041c7f1(_: *mut u8) -> *mut i32 {
    // FN_0041C7F1 - pobiera iterator początkowy
    0 as *mut i32
}

pub unsafe fn fn_0041c81f(_: *mut u8) -> *mut i32 {
    // FN_0041C81F - pobiera iterator końcowy
    0 as *mut i32
}

pub unsafe fn fn_0041c84f(_: *mut u8) {
    // FN_0041C84F - zwalnia listę
}

pub unsafe fn fn_0041ca4b(_: *mut i32, _: i32) -> u32 {
    // FN_0041CA4B - sprawdza dane
    0
}

pub unsafe fn fn_0042c6bc(_: i32) -> bool {
    // FN_0042C6BC - sprawdza job
    false
}

pub unsafe fn fn_0042c6cf(_: i32) -> bool {
    // FN_0042C6CF - sprawdza job
    false
}

pub unsafe fn fn_0042c6e3(_: i32) -> bool {
    // FN_0042C6E3 - sprawdza job
    false
}

pub unsafe fn fn_0042d803(_: *mut Unit, _: u32) -> bool {
    // FN_0042D803 - sprawdza dane
    true
}

pub unsafe fn fn_0042d848(_: *mut Unit, _: u32) -> bool {
    // FN_0042D848 - sprawdza dane
    false
}

pub unsafe fn fn_0042d88d(_: *mut Unit, _: i32) -> bool {
    // FN_0042D88D - sprawdza dane
    false
}

pub unsafe fn fn_0042d97d(_: *mut Unit, _: u32) -> bool {
    // FN_0042D97D - sprawdza dane
    false
}

pub unsafe fn fn_0042d9a3(_: *mut Unit, _: u32) -> bool {
    // FN_0042D9A3 - sprawdza dane
    false
}

pub unsafe fn fn_0042da65(_: *mut Unit, _: u32) -> bool {
    // FUN_0042DA65 - bramka produkcji
    false
}

pub unsafe fn fn_0042db20(_: *mut Unit, _: u32) -> u32 {
    // FUN_0042DB20 - sprawdza job block
    0
}

pub unsafe fn fn_004316d0(_: i32) {
    // FN_004316D0 - inicjalizacja
}

pub unsafe fn fn_004316e0(_: i32) -> i32 {
    // FN_004316E0 - pobiera house type
    0
}

pub unsafe fn fn_004319d7(_: *const HouseType, _: u32, _: u8) -> i32 {
    // FN_004319D7 - pobiera ilość towaru
    0
}

pub unsafe fn fn_00431f37(_: *const HouseType, _: u32) -> i32 {
    // FN_00431F37 - zwraca revmap
    -1
}

pub unsafe fn fn_0043267f(_: *mut u8, _: i32) -> *mut u8 {
    // FN_0043267F - szuka właściciela
    0 as *mut u8
}

pub unsafe fn fn_00434142(_: *mut Building, _: i32) -> bool {
    // FN_00434142 - sprawdza pracownika
    false
}

pub unsafe fn fn_00435504(_: i32) -> u32 {
    // FN_00435504 - pobiera dane
    0
}

pub unsafe fn fn_0043b305(_: *mut u8) {
    // FN_0043B305 - operacja na danych
}

pub unsafe fn fn_0043bf90(_: *mut u8) {
    // FN_0043BF90 - operacja na danych
}

pub unsafe fn fn_0043bfbc(_: *mut u8, _: *mut u8) -> bool {
    // FN_0043BFBC - operacja na danych
    false
}

pub unsafe fn fn_0043d037(_: i32) {
    // FN_0043D037 - operacja na danych
}

pub unsafe fn fn_0043d54f(_: i32) -> i32 {
    // FN_0043D54F - pobiera dane
    0
}

pub unsafe fn fn_0043e09a(_: *mut Unit, _: i32) -> u32 {
    // FN_0043E09A - wybiera good do produkcji
    2
}

pub unsafe fn fn_0043e8a7(_: *mut Unit, _: i32) {
    // FN_0043E8A7 - wybiera good do produkcji
}

pub unsafe fn fn_004411ca(_: *mut u8) -> *mut u16 {
    // FN_004411CA - pobiera wskaźnik
    0 as *mut u16
}

pub unsafe fn fn_0044124e(_: *mut u8, _: *mut u32) {
    // FN_0044124E - operacja na danych
}

pub unsafe fn fn_004417c7(_: u32) -> *mut u8 {
    // FN_004417C7 - pobiera wskaźnik
    0 as *mut u8
}

pub unsafe fn fn_00441800(_: u32) -> u32 {
    // FN_00441800 - UI
    0
}

pub unsafe fn fn_00441b83(_: *mut Building) {
    // FN_00441B83 - czyszczenie stanu
}

pub unsafe fn fn_00441ee3(_: i32) {
    // FN_00441EE3 - operacja na danych
}

pub unsafe fn fn_00449bda(_: *mut Unit) {
    // FN_00449BDA - aktualizacja
}

pub unsafe fn fn_00449f2f(_: *mut Unit, _: i32) {
    // FN_00449F2F - zmiana selected good
}

pub unsafe fn fn_0044a0d9(_: *mut Unit) {
    // FUN_0044A0D9 - ustawia +0x195 dla job goods
}

pub unsafe fn fn_0044b226(_: *mut Unit) {
    // FN_0044B226 - menu produkcji
}

pub unsafe fn fn_0044b2fa(_: *mut Unit) {
    // FUN_0044B2FA - ustawia status produkcji
}

pub unsafe fn fn_0044b5d9(_: *mut Unit, _: i32) -> u32 {
    // FN_0044B5D9 - getter statusu
    0
}

pub unsafe fn fn_0044b5e7(_: *mut Unit, _: i32, _: i32) {
    // FN_0044B5E7 - setter statusu
}

pub unsafe fn fn_0044b634(_: *mut Building, _: i32) -> u8 {
    // FN_0044B634 - operacja na danych
    0
}

pub unsafe fn fn_0044b660(_: *mut Building) -> bool {
    // FN_0044B660 - sprawdza dane
    false
}

pub unsafe fn fn_0044b7b5(_: *mut Building, _: i32, _: i32, _: i32) {
    // FN_0044B7B5 - operacja na danych
}

pub unsafe fn fn_0044b9ab(_: *mut Building, _: i32) -> bool {
    // FN_0044B9AB - sprawdza dane
    false
}

pub unsafe fn fn_0044bcf3(_: *mut Building, _: i32) -> u32 {
    // FN_0044BCF3 - sprawdza dane
    0
}

pub unsafe fn fn_00452fe6(_: i32) -> bool {
    // FN_00452FE6 - sprawdza dane
    false
}

pub unsafe fn fn_00453067(_: i32) -> i32 {
    // FN_00453067 - pobiera dane
    -1
}

pub unsafe fn fn_004530d6(_: i32) {
    // FN_004530D6 - operacja na danych
}

pub unsafe fn fn_0045bb51(_: *mut Unit, _: i32) {
    // FN_0045BB51 - dźwięk
}

pub unsafe fn fn_0045bbaa(_: *mut Unit, _: u32) {
    // FN_0045BBAA - dźwięk
}

pub unsafe fn fn_0045bcac(_: i32) {
    // FN_0045BCAC - operacja na danych
}

pub unsafe fn fn_0045c17b(_: *mut Unit, _: i32, _: i32) {
    // FN_0045C17B - operacja na danych
}

pub unsafe fn fn_0045c59d(_: *mut Unit, _: *mut u32, _: *mut i16) -> bool {
    // FN_0045C59D - sprawdza dane
    false
}

pub unsafe fn fn_0045c66e(_: i32) -> u32 {
    // FN_0045C66E - sprawdza dane
    0
}

pub unsafe fn fn_0045c709(_: *mut u32) -> u32 {
    // FN_0045C709 - sprawdza dane
    0
}

pub unsafe fn fn_0045d14f(_: *mut Unit, _: *mut u32, _: *mut i16) -> bool {
    // FN_0045D14F - sprawdza dane
    false
}

pub unsafe fn fn_004619f8(_: i32, _: *mut u16) -> bool {
    // FN_004619F8 - sprawdza dane
    false
}

pub unsafe fn fn_00461c14(_: i32, _: i32) -> i32 {
    // FN_00461C14 - mapuje good
    0
}

pub unsafe fn fn_0046733f(_: *mut Unit) -> *mut u8 {
    // FN_0046733F - pobiera dane
    0 as *mut u8
}

pub unsafe fn fn_00467617(_: *mut Unit) -> i32 {
    // FN_00467617 - pobiera dane
    0
}

pub unsafe fn fn_0046794b(_: *mut Unit, _: i32) -> bool {
    // FN_0046794B - sprawdza dane
    false
}

pub unsafe fn fn_00467c0e(_: *mut Unit, _: i32) -> bool {
    // FN_00467C0E - sprawdza dane
    false
}

pub unsafe fn fn_004680ea(_: *mut Unit) {
    // FN_004680EA - pętla jednostki
}

pub unsafe fn fn_004681ab(_: *mut Unit) {
    // FN_004681AB - pętla jednostki
}

pub unsafe fn fn_0046897c(_: *mut Unit) {
    // FN_0046897C - operacja na jednostce
}

pub unsafe fn fn_0046d53a(_: *mut Unit) {
    // FUN_0046D53A - potter handler
}

pub unsafe fn fn_0046e02b(_: *mut Unit, _: *mut u8, _: i32) {
    // FN_0046E02B - operacja na danych
}

pub unsafe fn fn_0046e117(_: *mut Unit, _: *mut u8) {
    // FN_0046E117 - operacja na danych
}

pub unsafe fn fn_0046e1be(_: *mut Unit, _: i32) -> u32 {
    // FUN_0046E1BE - sprawdza dostępność budynku
    0
}

pub unsafe fn fn_0046e3a1(_: *mut Unit, _: *mut u8) -> bool {
    // FN_0046E3A1 - sprawdza dane
    false
}

pub unsafe fn fn_0046e52e(_: *mut Unit, _: *mut u8, _: i32, _: *mut u32) -> u8 {
    // FN_0046E52E - operacja na danych
    0
}

pub unsafe fn fn_00473461(_: *mut Unit, _: i32) {
    // FUN_00473461 - tick jednostki
}

pub unsafe fn fn_0047c825(_: *mut u8, _: u32) -> i32 {
    // FN_0047C825 - pobiera dane
    0
}

pub unsafe fn fn_0047ffc0(_: i32) -> i32 {
    // FN_0047FFC0 - pobiera adres budynku
    0
}

pub unsafe fn fn_00490d10(_: i32, _: i32) {
    // FN_00490D10 - operacja na danych
}

pub unsafe fn fn_00494f01(_: i32, _: *mut u8, _: *mut u32, _: *mut u32, _: i32) {
    // FN_00494F01 - operacja na danych
}

pub unsafe fn fn_0049599b(_: i32, _: *mut u8) {
    // FN_0049599B - operacja na danych
}

pub unsafe fn fn_00495e0c(_: i32) {
    // FN_00495E0C - operacja na danych
}

pub unsafe fn fn_00495eee(_: i32, _: i32, _: i32, _: i32) {
    // FN_00495EEE - operacja na danych
}

pub unsafe fn fn_004a2222(_: *mut u32) {
    // FN_004A2222 - operacja na danych
}

pub unsafe fn fn_004b7b44(_: *mut u8, _: *mut u8, _: *mut u32) {
    // FN_004B7B44 - operacja na danych
}

pub unsafe fn fn_004b8b00(_: *mut u32) {
    // FN_004B8B00 - operacja na danych
}

pub unsafe fn fn_004b8b04(_: *mut u32, _: *mut i32, _: *mut u8) {
    // FN_004B8B04 - operacja na danych
}

pub unsafe fn fn_004b8be4(_: *mut u8, _: i32, _: i32, _: *mut u8, _: i32, _: *mut u32) {
    // FN_004B8BE4 - operacja na danych
}

pub unsafe fn fn_004b8c93(_: *mut u8, _: i32, _: i32, _: i32, _: *mut u8, _: i32, _: i32, _: *mut u32, _: i32, _: *mut u8) {
    // FN_004B8C93 - operacja na danych
}

pub unsafe fn fn_004b8d4c(_: *mut u8, _: i32, _: i32, _: *mut u8, _: i32) {
    // FN_004B8D4C - operacja na danych
}

pub unsafe fn fn_004b8d89(_: *mut u8, _: i32, _: i32) {
    // FN_004B8D89 - operacja na danych
}

pub unsafe fn fn_004e1d9e(_: i32, _: *mut u32, _: i32) {
    // FN_004E1D9E - operacja na danych
}

pub unsafe fn fn_004e1e3f(_: i32, _: *mut u32, _: i32, _: *mut u8, _: *mut u32) {
    // FN_004E1E3F - operacja na danych
}

pub unsafe fn fn_004e2172(_: i32, _: *mut u32, _: *mut u8, _: *mut u8, _: *mut u32, _: *mut u8) {
    // FN_004E2172 - operacja na danych
}

pub unsafe fn fn_004e21b7(_: *mut u8, _: i32, _: *mut u8, _: i32, _: *mut u8, _: *mut u8, _: *mut u8) -> *mut u8 {
    // FUN_004E21B7 - renderer tekstu UI
    0 as *mut u8
}

pub unsafe fn fn_004e5410(_: *mut u32, _: *mut u32) {
    // FN_004E5410 - operacja na danych
}

pub unsafe fn fn_004e556b(_: *mut u8, _: *mut u8) {
    // FN_004E556B - operacja na danych
}

pub unsafe fn fn_004e5628(_: *mut u8) {
    // FN_004E5628 - operacja na danych
}

pub unsafe fn fn_004e5820(_: *mut u8) {
    // FN_004E5820 - operacja na danych
}

pub unsafe fn fn_004e6760(_: *const u8, _: *const u8, _: usize) -> i32 {
    // FN_004E6760 - porównanie stringów
    0
}

pub unsafe fn _memset(_: *mut u8, _: i32, _: usize) -> *mut u8 {
    0 as *mut u8
}

pub unsafe fn _rand() -> u32 {
    0
}

pub static mut DAT_00510BD8: *mut u8 = 0x510_BD8 as *mut u8;
pub static mut DAT_00510BE0: *mut u8 = 0x510_BE0 as *mut u8;
pub static mut DAT_00510BE8: *mut u8 = 0x510_BE8 as *mut u8;
pub static mut DAT_00510BF0: *mut u8 = 0x510_BF0 as *mut u8;
pub static mut DAT_00510BC4: *mut u8 = 0x510_BC4 as *mut u8;
pub static mut DAT_00511200: *mut u8 = 0x511_200 as *mut u8;
pub static mut DAT_00511208: *mut u8 = 0x511_208 as *mut u8;
pub static mut DAT_00511214: *mut u8 = 0x511_214 as *mut u8;
pub static mut DAT_00511180: *mut u8 = 0x511_180 as *mut u8;
pub static mut DAT_00510BD0: *mut u8 = 0x510_BD0 as *mut u8;
pub static mut DAT_00510BC8: *mut u8 = 0x510_BC8 as *mut u8;
pub static mut DAT_00510BD4: *mut u8 = 0x510_BD4 as *mut u8;
pub static mut DAT_005113A0: *mut u8 = 0x511_3A0 as *mut u8;
pub static mut DAT_005113A4: *mut u8 = 0x511_3A4 as *mut u8;
pub static mut DAT_005113AC: *mut u8 = 0x511_3AC as *mut u8;
pub static mut DAT_00512764: *mut u8 = 0x512_764 as *mut u8;
pub static mut DAT_00512760: *mut u8 = 0x512_760 as *mut u8;
pub static mut DAT_00568CA8: *mut u8 = 0x568_CA8 as *mut u8;
pub static mut DAT_00568CB0: *mut u8 = 0x568_CB0 as *mut u8;
pub static mut DAT_00568CB8: *mut u8 = 0x568_CB8 as *mut u8;
pub static mut DAT_00568C0C: *mut u8 = 0x568_C0C as *mut u8;
pub static mut DAT_005552A8: *mut u8 = 0x555_2A8 as *mut u8;
pub static mut DAT_0055529C: *mut u8 = 0x555_29C as *mut u8;
