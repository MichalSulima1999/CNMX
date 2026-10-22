## ok

true

## data.evidence_id

ev_3aa838cc5a50bb5081e6f9d37ff1cfd3abb5f2d3aa769b182eb37131364fc7ce

## data.subject.name

G:\Games\CnMod 1.2\CN.PLMOD.exe.orig.before_scriptfix

## data.subject.digest

| Key    | Value                                                            |
|--------|------------------------------------------------------------------|
| sha256 | 367419b7a797c3db6c64c162f5bb74ad1668252ee32e60dfe8d685e0a4d63f00 |

## data.subject.format

pe

## data.subject.architecture

x86

## data.subject.local_path

G:\Games\CnMod 1.2\CN.PLMOD.exe.orig.before_scriptfix

## data.provider

| Key     | Value  |
|---------|--------|
| id      | ghidra |
| name    | Ghidra |
| version | 12.1.4 |

## data.analysis_profile.provider

| Key     | Value  |
|---------|--------|
| id      | ghidra |
| name    | Ghidra |
| version | 12.1.4 |

## data.analysis_profile.parameters.target_kind

executable

## data.analysis_profile.parameters.target_format

pe

## data.analysis_profile.parameters.executable_role

application

## data.analysis_profile.parameters.managed

false

## data.analysis_profile.parameters.native_aot_metadata

| Key                  | Value                       |
|----------------------|-----------------------------|
| contract_revision    | rtr-9.1-x64-pe-read-only-v3 |
| source_bytes         | 134217728                   |
| work_units           | 67108864                    |
| working_memory_bytes | 67108864                    |
| report_bytes         | 4194304                     |

## data.analysis_profile.parameters.architecture

x86

## data.analysis_profile.parameters.available_architectures

x86

## data.analysis_profile.parameters.import_mode

ephemeral-source-immutable

## data.analysis_profile.parameters.annotation_policy

atomic-function-entry-metadata-v1

## data.analysis_profile.parameters.load_image_observations

source-mappings-entry-context-v2

## data.analysis_profile.parameters.function_body_evidence

complete-inclusive-ranges-v1

## data.analysis_profile.parameters.function_references

complete-body-and-entry-reference-manager-v2

## data.analysis_profile.parameters.string_inventory_evidence

defined-data-coverage-v1

## data.analysis_profile.parameters.location_resolution

explicit-address-exact-entry-symbol-first-v3

## data.analysis_profile.parameters.instruction_flow_evidence

decoded-return-pcode-v1

## data.analysis_profile.parameters.function_boundary_observations

ghidra-terminal-call-limitations-v1

## data.analysis_profile.parameters.no_return_repair

disabled-windows-p0

## data.analysis_profile.parameters.process_launch

official-headless-script-v1

## data.analysis_profile.parameters.jump_table_evidence

typed-case-default-blocks-v1

## data.analysis_profile.parameters.decompiler_jump_loads

true

## data.analysis_profile.parameters.loader

auto-from-header

## data.analysis_profile.parameters.language_id

auto-from-header

## data.analysis_profile.parameters.compiler_spec_id

auto-default

## data.analysis_profile.parameters.analyzer_preset

ghidra-default

## data.analysis_profile.digest

b9d116ea480a02cc8773b19372074a3caf77785cbc080b1ac7133b5110e40b17

## data.predicate_type

rea.analysis

## data.operation

procedure_pseudo_code

## data.parameters

| Key       | Value    |
|-----------|----------|
| procedure | 0x46BDC1 |

## data.raw_result.value


void __fastcall FUN_0046bad7(void *param_1)

{
  bool bVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  byte bVar5;
  undefined1 uVar6;
  undefined4 uVar7;
  
  if (*(int *)((int)param_1 + 0x370) != 0) {
    *(int *)((int)param_1 + 0x370) = 0;
  }
  if ((*(int *)((int)param_1 + 0xacc) == 0) && (*(int *)((int)param_1 + 0xad4) != 0)) {
LAB_0046bb5a:
    FUN_00444c6e(param_1);
    return;
  }
  if ((*(uint *)((int)param_1 + 0xb84) >> 1 & 1) != 0) {
    if (*(int *)((int)param_1 + 0xacc) != 0) {
      FUN_00441b83((int)param_1);
    }
LAB_0046bb1c:
    *(undefined4 *)((int)param_1 + 0x36c) = 0;
    *(undefined4 *)((int)param_1 + 0x368) = 1;
    FUN_0044434a(param_1);
    return;
  }
  bVar1 = FUN_0042ce57(param_1,0xffffffff);
  if (bVar1) {
    if (*(int *)((int)param_1 + 0xacc) != 0) {
      FUN_00441b83((int)param_1);
    }
    if (*(int *)((int)param_1 + 0xad4) != 0) goto LAB_0046bb5a;
    goto LAB_0046bb1c;
  }
  uVar2 = FUN_0042c8a8((int)param_1);
  if ((char)uVar2 != '\0') {
    FUN_004732cf(param_1);
    return;
  }
  uVar2 = FUN_0042c960((int)param_1);
  if ((char)uVar2 == '\0') {
    bVar1 = FUN_0042c6f0((int)param_1);
    if (bVar1) goto LAB_0046bb98;
  }
  else {
    bVar1 = FUN_0042c6f0((int)param_1);
    if (!bVar1) goto LAB_0046bbbb;
LAB_0046bb98:
    uVar2 = FUN_0042c977((int)param_1);
    if (((char)uVar2 != '\0') &&
       (*(int *)(*(int *)((int)param_1 + 0xb34) * 0x7e0 + 0x2c + DAT_00510bd0) != 3)) {
LAB_0046bbbb:
      *(undefined4 *)((int)param_1 + 0x36c) = 3;
      *(undefined4 *)((int)param_1 + 0x374) = 2;
      return;
    }
  }
  uVar2 = FUN_0045c66e((int)param_1);
  if ((char)uVar2 == '\0') {
    return;
  }
  if ((*(int *)((int)param_1 + 0xacc) == 0) && (*(char *)((int)param_1 + 0xa60) == '\0')) {
    iVar3 = FUN_0042d4ba((int)param_1);
    if ((iVar3 == 0) || (*(int *)((int)param_1 + 0xae0) != 0)) {
      iVar3 = FUN_0042d4b3((int)param_1);
      if ((iVar3 != 0) && (*(int *)((int)param_1 + 0xadc) == 0)) {
        uVar6 = (undefined1)*(undefined4 *)((int)param_1 + 0x10);
        uVar7 = 0xffffffff;
        uVar2 = FUN_0042d4b3((int)param_1);
        bVar5 = 0x4f;
        goto LAB_0046bc3b;
      }
    }
    else {
      uVar6 = (undefined1)*(undefined4 *)((int)param_1 + 0x10);
      uVar7 = 0xffffffff;
      uVar2 = FUN_0042d4ba((int)param_1);
      bVar5 = 0x50;
LAB_0046bc3b:
      FUN_0043be61(param_1,bVar5,uVar6,0,0,uVar2,uVar7);
      FUN_0043c101(param_1);
      *(undefined1 *)((int)param_1 + 0xa60) = 1;
    }
    if (*(int *)((int)param_1 + 0x368) != 8) {
      return;
    }
  }
  bVar1 = FUN_0042cf4b((int)param_1);
  if (bVar1) {
    uVar2 = FUN_0042cf57((int)param_1);
    if ((char)uVar2 == '\0') {
      FUN_00441b83((int)param_1);
    }
    else {
      uVar4 = FUN_0042ccc4((int)param_1);
      if ((char)uVar4 != '\0') goto LAB_0046bce7;
      iVar3 = *(int *)((int)param_1 + 0xa68);
      if (iVar3 == 2) {
        *(undefined4 *)((int)param_1 + 0xad0) = *(undefined4 *)((int)param_1 + 0xa78);
        uVar2 = FUN_0045c4ac(param_1,(undefined4 *)((int)param_1 + 0xa6c),
                             (short *)((int)param_1 + 0xa70),'\0');
        if ((char)uVar2 != '\0') {
          FUN_0042c69e((int)param_1);
          return;
        }
      }
      else {
        uVar2 = FUN_0045c23e(param_1,(undefined4 *)((int)param_1 + 0xa6c),
                             (short *)((int)param_1 + 0xa70));
        if ((char)uVar2 != '\0') {
          *(int *)((int)param_1 + 0xa68) = iVar3;
          return;
        }
      }
    }
    FUN_0042cf27((int)param_1);
  }
LAB_0046bce7:
  uVar2 = FUN_0042c70a((int)param_1);
  if ((char)uVar2 != '\0') {
    iVar3 = *(int *)(*(int *)((int)param_1 + 0xb48) * 0x54c + 0x1ec + DAT_00510be0);
    uVar2 = FUN_0042c68a((int)param_1);
    if ((((char)uVar2 == '\0') || ((iVar3 != 0x33 && (iVar3 != 0x32)))) &&
       (bVar1 = FUN_0042c69e((int)param_1), !bVar1)) goto LAB_0046be4e;
  }
  switch(*(undefined4 *)((int)param_1 + 0x18)) {
  case 1:
  case 2:
  case 3:
  case 4:
    *(undefined4 *)((int)param_1 + 0x368) = 1;
    *(undefined4 *)((int)param_1 + 0x36c) = 0;
    *(undefined4 *)((int)param_1 + 0x37c) = 10;
    break;
  case 5:
    FUN_0046beed(param_1);
    break;
  case 6:
  case 0x17:
  case 0x1a:
  case 0x1b:
    *(undefined4 *)((int)param_1 + 0x368) = 1;
    *(undefined4 *)((int)param_1 + 0x36c) = 0;
    break;
  case 7:
    FUN_0046bf4b(param_1);
    break;
  case 8:
    FUN_0046bf9c(param_1);
    break;
  case 9:
    FUN_0046bfe4(param_1);
    break;
  case 10:
    FUN_0046bfe4(param_1);
    break;
  case 0xb:
  case 0xc:
  case 0xd:
  case 0xe:
  case 0x11:
  case 0x13:
  case 0x14:
  case 0x15:
    FUN_00473695(param_1);
    break;
  case 0xf:
    FUN_0046bffd(param_1);
    break;
  case 0x10:
    FUN_0046c248(param_1);
    break;
  case 0x12:
    FUN_0046c822(param_1);
    break;
  case 0x16:
    FUN_0046c8e7(param_1);
    break;
  case 0x18:
    FUN_0046caad(param_1);
    break;
  case 0x19:
    FUN_0046d53a(param_1);
    break;
  case 0x1c:
    FUN_0046e721(param_1);
    break;
  case 0x1d:
    FUN_0046e883(param_1);
    break;
  case 0x1e:
    FUN_0046e952(param_1);
    break;
  case 0x1f:
  case 0x20:
  case 0x21:
  case 0x22:
  case 0x23:
  case 0x24:
  case 0x25:
  case 0x26:
  case 0x27:
  case 0x28:
  case 0x29:
  case 0x2a:
  case 0x2b:
  case 0x2c:
  case 0x2d:
  case 0x2e:
  case 0x2f:
    FUN_0046eaf8(param_1);
    break;
  default:
    FUN_00440176((uint *)s_human_creature_is_trying_to_star_00504ec8);
  }
  uVar2 = FUN_0042c70a((int)param_1);
  if ((char)uVar2 == '\0') {
    return;
  }
  bVar1 = FUN_0042c69e((int)param_1);
  if (!bVar1) {
    return;
  }
  if (*(int *)((int)param_1 + 0x36c) != 3) {
    return;
  }
  if (*(int *)((int)param_1 + 0x374) != 2) {
    return;
  }
LAB_0046be4e:
  *(undefined4 *)((int)param_1 + 0x36c) = 0;
  if (*(char *)((int)param_1 + 0xb51) == '\0') {
    *(undefined4 *)((int)param_1 + 0x368) = 0x15;
  }
  else {
    *(undefined4 *)((int)param_1 + 0x368) = 1;
  }
  return;
}



## data.raw_result.limitations

Ghidra Listing reports a terminal call at 0x46bb2e to 0x44434a FUN_0044434a (external=false, thunk=false, hasNoReturn=false); fallthrough is excluded by Ghidra's flow model. The reason for the terminal flow is not established by this observation.,Ghidra Listing reports a terminal call at 0x46bb5c to 0x444c6e FUN_00444c6e (external=false, thunk=false, hasNoReturn=false); fallthrough is excluded by Ghidra's flow model. The reason for the terminal flow is not established by this observation.,Ghidra Listing reports a terminal call at 0x46bb71 to 0x4732cf FUN_004732cf (external=false, thunk=false, hasNoReturn=false); fallthrough is excluded by Ghidra's flow model. The reason for the terminal flow is not established by this observation.,Ghidra Listing reports a terminal call at 0x46bcd6 to 0x42c69e FUN_0042c69e (external=false, thunk=false, hasNoReturn=false); fallthrough is excluded by Ghidra's flow model. The reason for the terminal flow is not established by this observation.

## data.normalized_result


void __fastcall FUN_0046bad7(void *param_1)

{
  bool bVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  byte bVar5;
  undefined1 uVar6;
  undefined4 uVar7;
  
  if (*(int *)((int)param_1 + 0x370) != 0) {
    *(int *)((int)param_1 + 0x370) = 0;
  }
  if ((*(int *)((int)param_1 + 0xacc) == 0) && (*(int *)((int)param_1 + 0xad4) != 0)) {
LAB_0046bb5a:
    FUN_00444c6e(param_1);
    return;
  }
  if ((*(uint *)((int)param_1 + 0xb84) >> 1 & 1) != 0) {
    if (*(int *)((int)param_1 + 0xacc) != 0) {
      FUN_00441b83((int)param_1);
    }
LAB_0046bb1c:
    *(undefined4 *)((int)param_1 + 0x36c) = 0;
    *(undefined4 *)((int)param_1 + 0x368) = 1;
    FUN_0044434a(param_1);
    return;
  }
  bVar1 = FUN_0042ce57(param_1,0xffffffff);
  if (bVar1) {
    if (*(int *)((int)param_1 + 0xacc) != 0) {
      FUN_00441b83((int)param_1);
    }
    if (*(int *)((int)param_1 + 0xad4) != 0) goto LAB_0046bb5a;
    goto LAB_0046bb1c;
  }
  uVar2 = FUN_0042c8a8((int)param_1);
  if ((char)uVar2 != '\0') {
    FUN_004732cf(param_1);
    return;
  }
  uVar2 = FUN_0042c960((int)param_1);
  if ((char)uVar2 == '\0') {
    bVar1 = FUN_0042c6f0((int)param_1);
    if (bVar1) goto LAB_0046bb98;
  }
  else {
    bVar1 = FUN_0042c6f0((int)param_1);
    if (!bVar1) goto LAB_0046bbbb;
LAB_0046bb98:
    uVar2 = FUN_0042c977((int)param_1);
    if (((char)uVar2 != '\0') &&
       (*(int *)(*(int *)((int)param_1 + 0xb34) * 0x7e0 + 0x2c + DAT_00510bd0) != 3)) {
LAB_0046bbbb:
      *(undefined4 *)((int)param_1 + 0x36c) = 3;
      *(undefined4 *)((int)param_1 + 0x374) = 2;
      return;
    }
  }
  uVar2 = FUN_0045c66e((int)param_1);
  if ((char)uVar2 == '\0') {
    return;
  }
  if ((*(int *)((int)param_1 + 0xacc) == 0) && (*(char *)((int)param_1 + 0xa60) == '\0')) {
    iVar3 = FUN_0042d4ba((int)param_1);
    if ((iVar3 == 0) || (*(int *)((int)param_1 + 0xae0) != 0)) {
      iVar3 = FUN_0042d4b3((int)param_1);
      if ((iVar3 != 0) && (*(int *)((int)param_1 + 0xadc) == 0)) {
        uVar6 = (undefined1)*(undefined4 *)((int)param_1 + 0x10);
        uVar7 = 0xffffffff;
        uVar2 = FUN_0042d4b3((int)param_1);
        bVar5 = 0x4f;
        goto LAB_0046bc3b;
      }
    }
    else {
      uVar6 = (undefined1)*(undefined4 *)((int)param_1 + 0x10);
      uVar7 = 0xffffffff;
      uVar2 = FUN_0042d4ba((int)param_1);
      bVar5 = 0x50;
LAB_0046bc3b:
      FUN_0043be61(param_1,bVar5,uVar6,0,0,uVar2,uVar7);
      FUN_0043c101(param_1);
      *(undefined1 *)((int)param_1 + 0xa60) = 1;
    }
    if (*(int *)((int)param_1 + 0x368) != 8) {
      return;
    }
  }
  bVar1 = FUN_0042cf4b((int)param_1);
  if (bVar1) {
    uVar2 = FUN_0042cf57((int)param_1);
    if ((char)uVar2 == '\0') {
      FUN_00441b83((int)param_1);
    }
    else {
      uVar4 = FUN_0042ccc4((int)param_1);
      if ((char)uVar4 != '\0') goto LAB_0046bce7;
      iVar3 = *(int *)((int)param_1 + 0xa68);
      if (iVar3 == 2) {
        *(undefined4 *)((int)param_1 + 0xad0) = *(undefined4 *)((int)param_1 + 0xa78);
        uVar2 = FUN_0045c4ac(param_1,(undefined4 *)((int)param_1 + 0xa6c),
                             (short *)((int)param_1 + 0xa70),'\0');
        if ((char)uVar2 != '\0') {
          FUN_0042c69e((int)param_1);
          return;
        }
      }
      else {
        uVar2 = FUN_0045c23e(param_1,(undefined4 *)((int)param_1 + 0xa6c),
                             (short *)((int)param_1 + 0xa70));
        if ((char)uVar2 != '\0') {
          *(int *)((int)param_1 + 0xa68) = iVar3;
          return;
        }
      }
    }
    FUN_0042cf27((int)param_1);
  }
LAB_0046bce7:
  uVar2 = FUN_0042c70a((int)param_1);
  if ((char)uVar2 != '\0') {
    iVar3 = *(int *)(*(int *)((int)param_1 + 0xb48) * 0x54c + 0x1ec + DAT_00510be0);
    uVar2 = FUN_0042c68a((int)param_1);
    if ((((char)uVar2 == '\0') || ((iVar3 != 0x33 && (iVar3 != 0x32)))) &&
       (bVar1 = FUN_0042c69e((int)param_1), !bVar1)) goto LAB_0046be4e;
  }
  switch(*(undefined4 *)((int)param_1 + 0x18)) {
  case 1:
  case 2:
  case 3:
  case 4:
    *(undefined4 *)((int)param_1 + 0x368) = 1;
    *(undefined4 *)((int)param_1 + 0x36c) = 0;
    *(undefined4 *)((int)param_1 + 0x37c) = 10;
    break;
  case 5:
    FUN_0046beed(param_1);
    break;
  case 6:
  case 0x17:
  case 0x1a:
  case 0x1b:
    *(undefined4 *)((int)param_1 + 0x368) = 1;
    *(undefined4 *)((int)param_1 + 0x36c) = 0;
    break;
  case 7:
    FUN_0046bf4b(param_1);
    break;
  case 8:
    FUN_0046bf9c(param_1);
    break;
  case 9:
    FUN_0046bfe4(param_1);
    break;
  case 10:
    FUN_0046bfe4(param_1);
    break;
  case 0xb:
  case 0xc:
  case 0xd:
  case 0xe:
  case 0x11:
  case 0x13:
  case 0x14:
  case 0x15:
    FUN_00473695(param_1);
    break;
  case 0xf:
    FUN_0046bffd(param_1);
    break;
  case 0x10:
    FUN_0046c248(param_1);
    break;
  case 0x12:
    FUN_0046c822(param_1);
    break;
  case 0x16:
    FUN_0046c8e7(param_1);
    break;
  case 0x18:
    FUN_0046caad(param_1);
    break;
  case 0x19:
    FUN_0046d53a(param_1);
    break;
  case 0x1c:
    FUN_0046e721(param_1);
    break;
  case 0x1d:
    FUN_0046e883(param_1);
    break;
  case 0x1e:
    FUN_0046e952(param_1);
    break;
  case 0x1f:
  case 0x20:
  case 0x21:
  case 0x22:
  case 0x23:
  case 0x24:
  case 0x25:
  case 0x26:
  case 0x27:
  case 0x28:
  case 0x29:
  case 0x2a:
  case 0x2b:
  case 0x2c:
  case 0x2d:
  case 0x2e:
  case 0x2f:
    FUN_0046eaf8(param_1);
    break;
  default:
    FUN_00440176((uint *)s_human_creature_is_trying_to_star_00504ec8);
  }
  uVar2 = FUN_0042c70a((int)param_1);
  if ((char)uVar2 == '\0') {
    return;
  }
  bVar1 = FUN_0042c69e((int)param_1);
  if (!bVar1) {
    return;
  }
  if (*(int *)((int)param_1 + 0x36c) != 3) {
    return;
  }
  if (*(int *)((int)param_1 + 0x374) != 2) {
    return;
  }
LAB_0046be4e:
  *(undefined4 *)((int)param_1 + 0x36c) = 0;
  if (*(char *)((int)param_1 + 0xb51) == '\0') {
    *(undefined4 *)((int)param_1 + 0x368) = 0x15;
  }
  else {
    *(undefined4 *)((int)param_1 + 0x368) = 1;
  }
  return;
}



## data.confidence

observed

## data.authority

shipped-artifact

## data.environment

null

## data.limitations

The session serves operations only after Ghidra reports default auto-analysis complete; incomplete analysis does not expose partial results.,The imported Program and temporary project are ephemeral and deleted on close. Annotation operations edit session database metadata; original executable bytes are never written.,Cancelling an active Ghidra request terminates its ephemeral database and discards session annotations. The selected target remains open; the next provider query imports the original artifact again.,Default-space addresses use lowercase 0x-prefixed hexadecimal; other address spaces use <percent-encoded-space>:0x<hex>.,Pseudocode is Ghidra decompiler output, not original source and not text-equivalent to Hopper output.,External functions and functions without an analyzable body return null; other decompiler failures remain explicit.,Ghidra Listing reports a terminal call at 0x46bb2e to 0x44434a FUN_0044434a (external=false, thunk=false, hasNoReturn=false); fallthrough is excluded by Ghidra's flow model. The reason for the terminal flow is not established by this observation.,Ghidra Listing reports a terminal call at 0x46bb5c to 0x444c6e FUN_00444c6e (external=false, thunk=false, hasNoReturn=false); fallthrough is excluded by Ghidra's flow model. The reason for the terminal flow is not established by this observation.,Ghidra Listing reports a terminal call at 0x46bb71 to 0x4732cf FUN_004732cf (external=false, thunk=false, hasNoReturn=false); fallthrough is excluded by Ghidra's flow model. The reason for the terminal flow is not established by this observation.,Ghidra Listing reports a terminal call at 0x46bcd6 to 0x42c69e FUN_0042c69e (external=false, thunk=false, hasNoReturn=false); fallthrough is excluded by Ghidra's flow model. The reason for the terminal flow is not established by this observation.,Windows Ghidra P0 accepts approved native x86 and x86-64 PE applications and DLLs; managed, hostile, sensitive, and mutable-path targets are unsupported.,The Windows bridge uses authenticated IPv4 loopback because Node path-based IPC does not expose Java AF_UNIX sockets; the endpoint file contains no bearer token.,Windows sessions require the matching packaged Windows x64 native addon, local NTFS targets and runtimes, and Windows 10 or later. Native handles enforce path admission, private DACLs, and Job Object ownership automatically.

## data.locations



## data.evidence_links



## meta

| Key      | Value     |
|----------|-----------|
| command  | decompile |
| duration | 80278ms   |
