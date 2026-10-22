## ok

true

## data.evidence_id

ev_eaea89974d95cfdc3b0574f642961df312371cbd2dc0e3509d77a98c1a127d8d

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
| procedure | 0x46E1BE |

## data.raw_result.value


uint __thiscall FUN_0046e1be(void *this,int param_1)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  char *this_00;
  char local_20;
  undefined1 local_1f;
  undefined4 local_1c;
  undefined4 local_18;
  uint local_14;
  undefined4 local_c;
  short local_8;
  short local_6;
  
  uVar1 = FUN_0042c70a((int)this);
  if ((char)uVar1 != '\0') {
    uVar1 = FUN_0044bcf3((void *)(*(int *)((int)this + 0xb48) * 0x54c + DAT_00510be0),
                         *(int *)((int)this + 4));
    if ((char)uVar1 != '\0') {
      this_00 = (char *)(*(int *)((int)this + 0xb48) * 0x54c + DAT_00510be0);
      local_c = (short *)FUN_004411ca(this_00);
      uVar1 = FUN_0043f8f3((int)this_00);
      if ((((char)uVar1 != '\0') || (*(int *)(this_00 + 0x4fc) == 1)) ||
         (uVar1 = FUN_0042aa24(*local_c,local_c[1],*(short *)(param_1 + 0x24),
                               *(ushort *)(param_1 + 0x26)), 5 < uVar1)) {
        uVar1 = FUN_0043f8f3((int)this_00);
        if (((char)uVar1 != '\0') || (*(int *)(this_00 + 0x4fc) == 1)) {
          *(undefined4 *)((int)this + 0x36c) = 0;
          if (*(char *)((int)this + 0xb51) == '\0') {
            *(undefined4 *)((int)this + 0x368) = 0x15;
          }
          else {
            *(undefined4 *)((int)this + 0x368) = 1;
          }
          return 1;
        }
        local_8 = *local_c;
        local_6 = local_c[1];
        local_c = (short *)0x0;
        uVar2 = FUN_0043b35f(*(int *)(this_00 + 0x1e8),(short *)(param_1 + 0x24),&local_8,
                             (short *)0x14,2);
        if ((char)uVar2 != '\0') {
          FUN_0044124e(this_00,&local_c);
          _memset(&local_20,0,0x14);
          local_1f = *(undefined1 *)((int)this + 0x10);
          local_1c = *(undefined4 *)(this_00 + 4);
          local_18 = *(undefined4 *)(this_00 + 8);
          local_20 = 'e';
          if (((local_8 != (short)local_c) || (local_6 != local_c._2_2_)) ||
             (uVar2 = FUN_0043b35f(*(int *)(this_00 + 0x1e8),&local_8,(short *)&local_c,
                                   (short *)0x14,1), (char)uVar2 != '\0')) {
            local_14 = FUN_0042aed3(&local_8);
            FUN_0043f725(this_00,&local_20);
            *(undefined4 *)((int)this + 0x36c) = 0;
            *(undefined4 *)((int)this + 0x368) = 1;
            return 1;
          }
        }
        *(undefined4 *)((int)this + 0x36c) = 3;
        *(undefined4 *)((int)this + 0x374) = 1;
        iVar3 = FUN_0043d54f((int)this);
        if (iVar3 == 0) {
          *(undefined4 *)((int)this + 0x374) = 0;
          *(undefined4 *)((int)this + 0x36c) = 3;
        }
        return CONCAT31((int3)((uint)iVar3 >> 8),1);
      }
    }
  }
  return uVar1 & 0xffffff00;
}



## data.raw_result.limitations



## data.normalized_result


uint __thiscall FUN_0046e1be(void *this,int param_1)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  char *this_00;
  char local_20;
  undefined1 local_1f;
  undefined4 local_1c;
  undefined4 local_18;
  uint local_14;
  undefined4 local_c;
  short local_8;
  short local_6;
  
  uVar1 = FUN_0042c70a((int)this);
  if ((char)uVar1 != '\0') {
    uVar1 = FUN_0044bcf3((void *)(*(int *)((int)this + 0xb48) * 0x54c + DAT_00510be0),
                         *(int *)((int)this + 4));
    if ((char)uVar1 != '\0') {
      this_00 = (char *)(*(int *)((int)this + 0xb48) * 0x54c + DAT_00510be0);
      local_c = (short *)FUN_004411ca(this_00);
      uVar1 = FUN_0043f8f3((int)this_00);
      if ((((char)uVar1 != '\0') || (*(int *)(this_00 + 0x4fc) == 1)) ||
         (uVar1 = FUN_0042aa24(*local_c,local_c[1],*(short *)(param_1 + 0x24),
                               *(ushort *)(param_1 + 0x26)), 5 < uVar1)) {
        uVar1 = FUN_0043f8f3((int)this_00);
        if (((char)uVar1 != '\0') || (*(int *)(this_00 + 0x4fc) == 1)) {
          *(undefined4 *)((int)this + 0x36c) = 0;
          if (*(char *)((int)this + 0xb51) == '\0') {
            *(undefined4 *)((int)this + 0x368) = 0x15;
          }
          else {
            *(undefined4 *)((int)this + 0x368) = 1;
          }
          return 1;
        }
        local_8 = *local_c;
        local_6 = local_c[1];
        local_c = (short *)0x0;
        uVar2 = FUN_0043b35f(*(int *)(this_00 + 0x1e8),(short *)(param_1 + 0x24),&local_8,
                             (short *)0x14,2);
        if ((char)uVar2 != '\0') {
          FUN_0044124e(this_00,&local_c);
          _memset(&local_20,0,0x14);
          local_1f = *(undefined1 *)((int)this + 0x10);
          local_1c = *(undefined4 *)(this_00 + 4);
          local_18 = *(undefined4 *)(this_00 + 8);
          local_20 = 'e';
          if (((local_8 != (short)local_c) || (local_6 != local_c._2_2_)) ||
             (uVar2 = FUN_0043b35f(*(int *)(this_00 + 0x1e8),&local_8,(short *)&local_c,
                                   (short *)0x14,1), (char)uVar2 != '\0')) {
            local_14 = FUN_0042aed3(&local_8);
            FUN_0043f725(this_00,&local_20);
            *(undefined4 *)((int)this + 0x36c) = 0;
            *(undefined4 *)((int)this + 0x368) = 1;
            return 1;
          }
        }
        *(undefined4 *)((int)this + 0x36c) = 3;
        *(undefined4 *)((int)this + 0x374) = 1;
        iVar3 = FUN_0043d54f((int)this);
        if (iVar3 == 0) {
          *(undefined4 *)((int)this + 0x374) = 0;
          *(undefined4 *)((int)this + 0x36c) = 3;
        }
        return CONCAT31((int3)((uint)iVar3 >> 8),1);
      }
    }
  }
  return uVar1 & 0xffffff00;
}



## data.confidence

observed

## data.authority

shipped-artifact

## data.environment

null

## data.limitations

The session serves operations only after Ghidra reports default auto-analysis complete; incomplete analysis does not expose partial results.,The imported Program and temporary project are ephemeral and deleted on close. Annotation operations edit session database metadata; original executable bytes are never written.,Cancelling an active Ghidra request terminates its ephemeral database and discards session annotations. The selected target remains open; the next provider query imports the original artifact again.,Default-space addresses use lowercase 0x-prefixed hexadecimal; other address spaces use <percent-encoded-space>:0x<hex>.,Pseudocode is Ghidra decompiler output, not original source and not text-equivalent to Hopper output.,External functions and functions without an analyzable body return null; other decompiler failures remain explicit.,Windows Ghidra P0 accepts approved native x86 and x86-64 PE applications and DLLs; managed, hostile, sensitive, and mutable-path targets are unsupported.,The Windows bridge uses authenticated IPv4 loopback because Node path-based IPC does not expose Java AF_UNIX sockets; the endpoint file contains no bearer token.,Windows sessions require the matching packaged Windows x64 native addon, local NTFS targets and runtimes, and Windows 10 or later. Native handles enforce path admission, private DACLs, and Job Object ownership automatically.

## data.locations



## data.evidence_links



## meta

| Key      | Value     |
|----------|-----------|
| command  | decompile |
| duration | 79537ms   |
