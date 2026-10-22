// Pseudokod funkcji z batch4 (dekompilacje REA Ghidra 12.1.4)
// Te funkcje obsługują walidację typów wpisów w tablicy budynków oraz renderer panelu informacyjnego.
// Źródło: re_out/decomp_UI_B_468A64.md, re_out/decomp_potter_6BDC1.md

use crate::engine_structs::*;
use crate::engine_structs::globals::*;

/// FUN_00434142 — Sprawdza czy budynek ma pracownika
pub unsafe fn fun_00434142(this: *mut Building, worker_idx: i32) -> bool {
    if worker_idx < 5 {
        return (*this).workers[worker_idx] != 0;
    }
    false
}

/// FUN_0046D53A — Potter handler / interakcja z budynkiem
/// Wywoływany przy kliknięciu w budynek
pub unsafe fn fun_0046d53a(this: *mut Building) {
    // Pobierz house list
    let house_list = fun_0041c61e(DAT_00511728, (*this).house_list_idx);
    
    // Pobierz iteratory początku i końca listy
    let pi_begin = fun_0041c7f1(house_list);
    let pi_end = fun_0041c81f(house_list);
    
    if pi_begin == pi_end || pi_begin.is_null() {
        (*this).field_368 = 1;
        return;
    }
    
    // Sprawdź flagi budynku
    let owner1 = fun_0041c9dd(pi_begin);
    let bldg1 = if (owner1 as u8) != 0 { (*pi_begin * 0x7E0 + DAT_00510BD0) as *mut u8 } else { 0 as *mut u8 };
    let owner2 = fun_0041c9dd(pi_end);
    let bldg2 = if (owner2 as u8) != 0 { (*pi_end * 0x7E0 + DAT_00510BD0) as *mut u8 } else { 0 as *mut u8 };
    
    if bldg1.is_null() || bldg2.is_null() || *bldg1.add(2000) != 0 || *bldg2.add(2000) != 0 {
        (*this).field_36c = 3;
        (*this).field_374 = 2;
        return;
    }
    
    if *local_14.offset(2) == 0 && *local_10.offset(2) == 0 {
        let flag = fun_0042c70a(this as i32);
        if (flag as u8) != 0 {
            let field_384 = *(*this).field_384;
            if (field_384 as u8) != 0 {
                // ... dalsza logika
            }
        }
    }
    
    fun_0041c84f(house_list);
}

/// FUN_0042C70A — Sprawdza coś związanego z budykiem
pub unsafe fn fun_0042c70a(this: i32) -> u32 {
    // ... implementacja
    0
}

/// FUN_0041C61E — Pobiera listę domów
pub unsafe fn fun_0041c61e(p1: *mut u8, p2: i32) -> *mut u8 {
    // ... implementacja
    0 as *mut u8
}

/// FUN_0041C7F1 — Pobiera iterator początkowy
pub unsafe fn fun_0041c7f1(p1: *mut u8) -> *mut i32 {
    // ... implementacja
    0 as *mut i32
}

/// FUN_0041C81F — Pobiera iterator końcowy
pub unsafe fn fun_0041c81f(p1: *mut u8) -> *mut i32 {
    // ... implementacja
    0 as *mut i32
}

/// FUN_0041C9DD — Sprawdza właściciela
pub unsafe fn fun_0041c9dd(p1: *mut i32) -> u32 {
    // ... implementacja
    0
}

/// FUN_0041C84F — Zwalnia listę
pub unsafe fn fun_0041c84f(p1: *mut u8) {
    // ... implementacja
}

/// FUN_0046E52E — Sprawdza coś związane z budynkiem
pub unsafe fn fun_0046e52e(p1: *mut u8, p2: *mut u8, p3: i32, p4: *mut u32) -> u8 {
    // ... implementacja
    0
}

/// FUN_00428554 — Sprawdza coś związane z budynkiem
pub unsafe fn fun_00428554(p1: *mut u8, p2: *mut u32) -> u32 {
    // ... implementacja
    0
}

/// FUN_0047FFC0 — Pobiera adres budynku
pub unsafe fn fun_0047ffc0(building_idx: i32) -> i32 {
    building_idx * 0x7E0 + DAT_00510BD0 as i32
}

/// FUN_0045BBAA — Dźwięk
pub unsafe fn fun_0045bbaa(p1: *mut u8, p2: u32) {
    // ... implementacja
}

/// FUN_0045BB51 — Dźwięk
pub unsafe fn fun_0045bb51(p1: *mut u8, p2: i32) {
    // ... implementacja
}

/// FUN_0042C66C — Sprawdza job
pub unsafe fn fun_0042c66c(this: i32) -> bool {
    // ... implementacja
    false
}

/// FUN_0042C6BC — Sprawdza job
pub unsafe fn fun_0042c6bc(this: i32) -> bool {
    // ... implementacja
    false
}

/// FUN_0042C6CF — Sprawdza job
pub unsafe fn fun_0042c6cf(this: i32) -> bool {
    // ... implementacja
    false
}

/// FUN_0042C64F — Sprawdza job
pub unsafe fn fun_0042c64f(this: i32) -> bool {
    // ... implementacja
    false
}

/// FUN_0042C680 — Sprawdza job
pub unsafe fn fun_0042c680(this: *mut Unit) -> bool {
    // ... implementacja
    true
}

/// FUN_0042D88D — Sprawdza dane
pub unsafe fn fun_0042d88d(p1: *mut Unit, p2: i32) -> bool {
    // ... implementacja
    false
}

/// FUN_0042D803 — Sprawdza dane
pub unsafe fn fun_0042d803(p1: *mut Unit, p2: u32) -> bool {
    // ... implementacja
    true
}

/// FUN_0042D848 — Sprawdza dane
pub unsafe fn fun_0042d848(p1: *mut Unit, p2: u32) -> bool {
    // ... implementacja
    false
}

/// FUN_0042D97D — Sprawdza dane
pub unsafe fn fun_0042d97d(p1: *mut Unit, p2: u32) -> bool {
    // ... implementacja
    false
}

/// FUN_0042D9A3 — Sprawdza dane
pub unsafe fn fun_0042d9a3(p1: *mut Unit, p2: u32) -> bool {
    // ... implementacja
    false
}

/// FUN_0042DA65 — Sprawdza dane
pub unsafe fn fun_0042da65(p1: *mut Unit, p2: u32) -> bool {
    // ... implementacja
    false
}

/// FUN_0042DB20 — Sprawdza dane
pub unsafe fn fun_0042db20(p1: *mut Unit, p2: u32) -> u32 {
    // ... implementacja
    0
}

/// FUN_004316E0 — Pobiera house type
pub unsafe fn fun_004316e0(building_instance: i32) -> i32 {
    // ... implementacja
    0
}

/// FUN_004316F3 — Bramka budynku
pub unsafe fn fun_004316f3(p1: *mut Building, p2: u32, p3: u8) -> bool {
    // ... implementacja
    false
}

/// FUN_004319D7 — Pobiera ilość towaru
pub unsafe fn fun_004319d7(p1: *const HouseType, p2: u32) -> i32 {
    // ... implementacja
    0
}

/// FUN_00434142 — Sprawdza pracownika
pub unsafe fn fun_00434142(p1: *mut Building, p2: i32) -> bool {
    // ... implementacja
    false
}

/// FUN_00435504 — Pobiera dane
pub unsafe fn fun_00435504(p1: i32) -> u32 {
    // ... implementacja
    0
}

/// FUN_00439633 — Pobiera dane
pub unsafe fn fun_00439633(p1: *mut u8, p2: u32) -> i32 {
    // ... implementacja
    0
}

/// FUN_0043967D — Pobiera dane
pub unsafe fn fun_0043967d(p1: *mut u8, p2: *const u8) -> i32 {
    // ... implementacja
    0
}

/// FUN_0043B35F — Sprawdza dane
pub unsafe fn fun_0043b35f(p1: i32, p2: *mut u16, p3: *mut u16, p4: *mut u16, p5: i32) -> u32 {
    // ... implementacja
    0
}

/// FUN_0043BFBC — Sprawdza dane
pub unsafe fn fun_0043bfbc(p1: *mut u8, p2: *mut u8) -> bool {
    // ... implementacja
    false
}

/// FUN_0043D037 — Operacja na danych
pub unsafe fn fun_0043d037(p1: i32) {
    // ... implementacja
}

/// FUN_0043D54F — Pobiera dane
pub unsafe fn fun_0043d54f(p1: i32) -> i32 {
    // ... implementacja
    0
}

/// FUN_0043E09A — Wybiera good do produkcji
pub unsafe fn fun_0043e09a(p1: *mut Unit, p2: i32) -> u32 {
    // ... implementacja
    2
}

/// FUN_0043E8A7 — Wybiera good do produkcji
pub unsafe fn fun_0043e8a7(p1: *mut Unit, p2: i32) {
    // ... implementacja
}

/// FUN_004411CA — Pobiera wskaźnik
pub unsafe fn fun_004411ca(p1: *mut u8) -> *mut u16 {
    // ... implementacja
    0 as *mut u16
}

/// FUN_0044124E — Operacja na danych
pub unsafe fn fun_0044124e(p1: *mut u8, p2: *mut u32) {
    // ... implementacja
}

/// FUN_004417C7 — Pobiera wskaźnik
pub unsafe fn fun_004417c7(p1: u32) -> *mut u8 {
    // ... implementacja
    0 as *mut u8
}

/// FUN_00441800 — UI
pub unsafe fn fun_00441800(p1: *mut u8) {
    // ... implementacja
}

/// FUN_00441B83 — Czyszczenie stanu
pub unsafe fn fun_00441b83(p1: i32) {
    // ... implementacja
}

/// FUN_00441EE3 — Operacja na danych
pub unsafe fn fun_00441ee3(p1: i32) {
    // ... implementacja
}

pub unsafe fn fun_0044b226(this: *mut Unit) {
    let mut i_var5: i32 = 1;
    let mut pi_var4 = (this as *mut i32).add(0x220 / 4);
    loop {
        if *this.offset(0x195 + i_var5) == 0 {
            *pi_var4 = 0x0c;
        } else {
            let u_var2 = fun_0042db20(this, i_var5 as u32);
            if u_var2 == 0 {
                *pi_var4 = 0xd;
            } else {
                let b_var1 = fun_0042da65(this, i_var5 as u32);
                *pi_var4 = (-(b_var1 as u32) & 0xfffffff2) + 0xe;
            }
        }
        i_var5 += 1;
        pi_var4 = pi_var4.add(1);
        if !(i_var5 < 0x42) { break; }
    }
}

pub unsafe fn fn_004417c7(param_1: u32) -> *mut u8 {
    // FUN_004417C7 - Pobiera wskaźnik
    0 as *mut u8
}
