## ok

true

## data.evidence_id

ev_abbd7a273d499c00133b48d1eb69b0b26a0e0f1d94b81c53d33c08af709dc077

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
| procedure | 0x4E21B7 |

## data.raw_result.value


byte * __cdecl
FUN_004e21b7(void *param_1,int param_2,byte *param_3,int param_4,void *param_5,byte *param_6,
            byte *param_7)

{
  byte bVar1;
  int iVar2;
  char *pcVar3;
  void *pvVar4;
  byte *_Str;
  int iVar5;
  int iVar6;
  byte *local_8;
  
  if (param_7 == (byte *)0x0) {
    return (byte *)0x0;
  }
  local_8 = param_3;
  iVar6 = *(int *)((int)param_5 + 8) + 2;
  iVar5 = param_2;
  _Str = param_7;
LAB_004e21e3:
  do {
    while( true ) {
      param_7 = _Str;
      bVar1 = *param_7;
      _Str = param_7 + 1;
      if (bVar1 == 0) {
        return local_8 + (iVar6 - (int)param_3);
      }
      if (bVar1 != 9) break;
LAB_004e2301:
      iVar2 = FUN_00439633(param_5,0x69);
      iVar5 = iVar5 + iVar2;
    }
    if ((bVar1 != 10) && (bVar1 != 0xd)) {
      if (bVar1 == 0x20) goto LAB_004e2301;
      if (bVar1 == 0x7b) {
        pcVar3 = _strchr((char *)_Str,0x7d);
        if (pcVar3 != (char *)0x0) {
          pvVar4 = (void *)_strlen("newline");
          iVar2 = FUN_004e6760(_Str,"newline",pvVar4);
          if (iVar2 == 0) {
            local_8 = local_8 + *(int *)((int)param_5 + 8) + 2;
            iVar5 = param_2;
          }
          _Str = (byte *)(pcVar3 + 1);
        }
      }
      else if (0x1f < bVar1) {
        DAT_00569a38 = 0;
        iVar2 = 0;
        do {
          _Str = param_7;
          bVar1 = *_Str;
          if ((((bVar1 == 0) || (bVar1 == 0xd)) || (bVar1 == 0x20)) ||
             ((bVar1 < 0x20 || (bVar1 == 0x7b)))) break;
          (&DAT_00569a38)[iVar2] = bVar1;
          iVar2 = iVar2 + 1;
          param_7 = _Str + 1;
        } while (iVar2 != 100);
        (&DAT_00569a38)[iVar2] = 0;
        iVar2 = FUN_0043967d(param_5,&DAT_00569a38);
        if (param_4 <= iVar2 + iVar5) {
          local_8 = local_8 + iVar6;
          iVar5 = param_2;
        }
        FUN_0040ecf9(param_1,param_5,param_6,iVar5,local_8,&DAT_00569a38);
        iVar5 = iVar5 + iVar2;
      }
      goto LAB_004e21e3;
    }
    if (*_Str == 10) {
      _Str = param_7 + 2;
    }
    param_7 = _Str;
    local_8 = local_8 + iVar6;
    iVar5 = param_2;
    _Str = param_7;
  } while( true );
}



## data.raw_result.limitations



## data.normalized_result


byte * __cdecl
FUN_004e21b7(void *param_1,int param_2,byte *param_3,int param_4,void *param_5,byte *param_6,
            byte *param_7)

{
  byte bVar1;
  int iVar2;
  char *pcVar3;
  void *pvVar4;
  byte *_Str;
  int iVar5;
  int iVar6;
  byte *local_8;
  
  if (param_7 == (byte *)0x0) {
    return (byte *)0x0;
  }
  local_8 = param_3;
  iVar6 = *(int *)((int)param_5 + 8) + 2;
  iVar5 = param_2;
  _Str = param_7;
LAB_004e21e3:
  do {
    while( true ) {
      param_7 = _Str;
      bVar1 = *param_7;
      _Str = param_7 + 1;
      if (bVar1 == 0) {
        return local_8 + (iVar6 - (int)param_3);
      }
      if (bVar1 != 9) break;
LAB_004e2301:
      iVar2 = FUN_00439633(param_5,0x69);
      iVar5 = iVar5 + iVar2;
    }
    if ((bVar1 != 10) && (bVar1 != 0xd)) {
      if (bVar1 == 0x20) goto LAB_004e2301;
      if (bVar1 == 0x7b) {
        pcVar3 = _strchr((char *)_Str,0x7d);
        if (pcVar3 != (char *)0x0) {
          pvVar4 = (void *)_strlen("newline");
          iVar2 = FUN_004e6760(_Str,"newline",pvVar4);
          if (iVar2 == 0) {
            local_8 = local_8 + *(int *)((int)param_5 + 8) + 2;
            iVar5 = param_2;
          }
          _Str = (byte *)(pcVar3 + 1);
        }
      }
      else if (0x1f < bVar1) {
        DAT_00569a38 = 0;
        iVar2 = 0;
        do {
          _Str = param_7;
          bVar1 = *_Str;
          if ((((bVar1 == 0) || (bVar1 == 0xd)) || (bVar1 == 0x20)) ||
             ((bVar1 < 0x20 || (bVar1 == 0x7b)))) break;
          (&DAT_00569a38)[iVar2] = bVar1;
          iVar2 = iVar2 + 1;
          param_7 = _Str + 1;
        } while (iVar2 != 100);
        (&DAT_00569a38)[iVar2] = 0;
        iVar2 = FUN_0043967d(param_5,&DAT_00569a38);
        if (param_4 <= iVar2 + iVar5) {
          local_8 = local_8 + iVar6;
          iVar5 = param_2;
        }
        FUN_0040ecf9(param_1,param_5,param_6,iVar5,local_8,&DAT_00569a38);
        iVar5 = iVar5 + iVar2;
      }
      goto LAB_004e21e3;
    }
    if (*_Str == 10) {
      _Str = param_7 + 2;
    }
    param_7 = _Str;
    local_8 = local_8 + iVar6;
    iVar5 = param_2;
    _Str = param_7;
  } while( true );
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
| duration | 81184ms   |
