## ok

true

## data.evidence_id

ev_4b3388f68784de5ea53f87c5ddd37aead13f0378959d9fbe5031814ca7aeb601

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
| procedure | 0x4C23D8 |

## data.raw_result.value


/* WARNING: Type propagation algorithm not settling */

void __thiscall FUN_004c227c(void *this,void *param_1,int *param_2)

{
  uint uVar1;
  void *pvVar2;
  void *pvVar3;
  uint *puVar4;
  byte *pbVar5;
  byte *pbVar6;
  uint *puVar7;
  int iVar8;
  uint uVar9;
  int *piVar10;
  int iVar11;
  uint local_1e8 [21];
  int local_194 [2];
  uint local_18c [52];
  uint local_bc [25];
  int aiStack_58 [10];
  uint local_30;
  int *local_2c;
  uint local_28;
  uint *local_24;
  uint *local_20;
  void *local_1c;
  int local_18;
  void *local_14;
  byte *local_10;
  uint *local_c;
  byte *local_8;
  
  FUN_004b7b44(this,param_1,param_2);
  pvVar3 = DAT_00569aa4;
  pvVar2 = DAT_00569aa0;
  local_2c = DAT_00569aa8;
  local_10 = (byte *)(DAT_00569abc + 0x400);
  iVar8 = *(int *)((int)this + 0x70);
  local_14 = DAT_00569aa0;
  local_8 = DAT_00569aa4;
  if (iVar8 == 0) {
    FUN_004e1d9e((int)param_1,(undefined4 *)((int)this + 0x74),2);
  }
  else if (iVar8 == 1) {
    iVar8 = *(int *)((int)this + 0x3ac);
    if (iVar8 != -1) {
      uVar9 = *(uint *)((int)this + iVar8 * 8 + 0x8c);
      puVar4 = *(uint **)((int)this + iVar8 * 8 + 0x88);
      local_30 = uVar9;
      local_c = puVar4;
      puVar7 = (uint *)FUN_0042f798((int)puVar4,uVar9,1);
      iVar11 = (int)puVar4 * 0x8bc + DAT_00568c0c;
      local_1c = *(void **)(iVar11 + 0x3c + uVar9 * 4);
      local_2c = (int *)((int)local_1c * 0x624 + (int)DAT_005113a0);
      local_18 = *local_2c;
      iVar8 = FUN_0048064b(DAT_005113a0,(byte *)s_house_sepia_005076f0);
      FUN_00495ffc((int)local_c,uVar9,(int)param_1,(uint *)0xfa,(byte *)0x12c,iVar8,'\0');
      FUN_004e1e3f((int)param_1,(uint *)0x14,(byte *)0x3c,local_8,(undefined4 *)local_10,puVar7);
      local_8 = (byte *)0x56;
      if ((*(void **)((int)this + 0x3a8) != (void *)0x0) &&
         (pbVar5 = (byte *)FUN_0042bcae(*(void **)((int)this + 0x3a8),(uint)local_1c),
         pbVar5 != (byte *)0x0)) {
        local_8 = FUN_004e21b7(param_1,0x14,(byte *)0x56,500,local_14,local_10,pbVar5);
        local_8 = local_8 + 0x60;
      }
      FUN_004e162e(0x26);
      FUN_004e2172((int)param_1,(uint *)0x14,local_8,local_14,(undefined4 *)local_10,&DAT_00507728);
      local_8 = local_8 + 0x10;
      FUN_00432a48((int)local_c,uVar9,'\0',local_194);
      param_2 = (int *)0x0;
      local_24 = (uint *)0x28;
      if (0 < local_194[0]) {
        local_20 = local_18c;
        do {
          local_1c = (void *)local_20[-1];
          local_28 = *local_20;
          FUN_004e556b((undefined1 *)(aiStack_58 + 2),(byte *)s__setx_10__gfxgood__d__d__00508634);
          FUN_0042f710((int)local_1c,local_28);
          FUN_004e556b((undefined1 *)local_bc,(byte *)s__d__s_005077b4);
          FUN_004b8c93((void *)((int)this + 0x55c),0x271f,(int)param_2,(int)local_24,(int)local_8,
                       0x32,0x18,(uint *)(aiStack_58 + 2),0,local_bc);
          FUN_004b8d4c((void *)((int)this + 0x55c),0x271f,(int)param_2,local_1c,0);
          local_24 = (uint *)((int)local_24 + 0x34);
          param_2 = (int *)((int)param_2 + 1);
          local_20 = local_20 + 5;
        } while ((int)param_2 < local_194[0]);
      }
      local_8 = local_8 + 0x1e;
      uVar9 = local_30 + 1;
      if (uVar9 < *(uint *)(iVar11 + 0x54)) {
        FUN_004e162e(0x27);
        FUN_004e2172((int)param_1,(uint *)0x14,local_8,local_14,(undefined4 *)local_10,&DAT_00507728
                    );
        local_8 = local_8 + 0x10;
        FUN_00432a48((int)local_c,uVar9,'\x01',local_194);
        local_c = (uint *)0x28;
        if (0 < local_194[0]) {
          param_2 = (int *)0x3e8;
          puVar4 = local_18c;
          do {
            local_1c = (void *)*puVar4;
            local_28 = puVar4[-1];
            FUN_004e556b((undefined1 *)(aiStack_58 + 2),(byte *)s__setx_10__gfxgood__d__d__00508634)
            ;
            FUN_0042f710(local_28,(uint)local_1c);
            FUN_004e556b((undefined1 *)local_bc,(byte *)s__d__s_005077b4);
            FUN_004b8c93((void *)((int)this + 0x55c),0x271f,(int)param_2,(int)local_c,(int)local_8,
                         0x32,0x18,(uint *)(aiStack_58 + 2),0,local_bc);
            FUN_004b8d4c((void *)((int)this + 0x55c),0x271f,(int)param_2,local_28,0);
            local_c = local_c + 0xd;
            puVar4 = puVar4 + 5;
            iVar8 = (int)param_2 + -999;
            param_2 = (int *)((int)param_2 + 1);
          } while (iVar8 < local_194[0]);
        }
        local_8 = local_8 + 0x1e;
      }
      if (((local_18 == 1) || (local_18 == 3)) || (piVar10 = local_2c, local_18 == 5)) {
        FUN_004e162e(0x28);
        FUN_004e2172((int)param_1,(uint *)0x14,local_8,local_14,(undefined4 *)local_10,&DAT_00507728
                    );
        piVar10 = local_2c;
        local_8 = local_8 + 0x10;
        local_1e8[0]._0_1_ = 0;
        param_2 = (int *)0x0;
        if (0 < local_2c[3]) {
          local_c = (uint *)(local_2c + 5);
          do {
            local_30 = *local_c;
            FUN_0042f754(local_c[-1],local_30);
            FUN_004e556b((undefined1 *)local_bc,(byte *)s__d__s_005077b4);
            if (param_2 != (int *)0x0) {
              FUN_004e5410(local_1e8,(uint *)&DAT_00508630);
            }
            FUN_004e5410(local_1e8,local_bc);
            param_2 = (int *)((int)param_2 + 1);
            local_c = local_c + 2;
          } while ((int)param_2 < piVar10[3]);
        }
        FUN_004e1e3f((int)param_1,(uint *)0x28,local_8,local_14,(undefined4 *)local_10,local_1e8);
        local_8 = local_8 + 0x16;
      }
      FUN_004e162e(0x29);
      FUN_004e2172((int)param_1,(uint *)0x14,local_8,local_14,(undefined4 *)local_10,&DAT_00507728);
      local_8 = local_8 + 0x10;
      if (local_18 == 1) {
        pbVar5 = (byte *)FUN_004e162e(0x2a);
        FUN_004e2172((int)param_1,(uint *)0x28,local_8,local_14,(undefined4 *)local_10,pbVar5);
      }
      else {
        local_20 = (uint *)0x0;
        local_c = (uint *)0x0;
        if (piVar10[0x18] != 0) {
          local_1c = (void *)((int)this + 0x55c);
          local_18 = 2000;
          piVar10 = piVar10 + 0x1a;
          do {
            local_24 = (uint *)piVar10[-1];
            if (*(int *)(DAT_00510bc4 + 0x5d200) == 1) {
              iVar8 = 2;
            }
            else if (*(int *)(DAT_00510bc4 + 0x5d200) == 2) {
              iVar8 = 5;
            }
            else {
              iVar8 = 1;
            }
            local_30 = iVar8 * *piVar10;
            iVar8 = (int)local_20 * 0xdc;
            FUN_004e2172((int)param_1,(uint *)(iVar8 + 0x28),local_8,local_14,(undefined4 *)local_10
                         ,&DAT_005070cc);
            FUN_004e556b((undefined1 *)(aiStack_58 + 2),(byte *)s__setx_10__gfxgood__d_1__00508618);
            puVar4 = (uint *)FUN_0042f710((int)local_24,1);
            FUN_004b8c93(local_1c,0x271f,local_18,iVar8 + 0x3c,(int)local_8,0x28,0x12,
                         (uint *)(aiStack_58 + 2),0,puVar4);
            FUN_004b8d4c(local_1c,0x271f,local_18,local_24,0);
            FUN_0042f710((int)local_24,local_30);
            FUN_004e2172((int)param_1,(uint *)(iVar8 + 0x68),local_8,local_14,(undefined4 *)local_10
                         ,(byte *)s__s__s_005076b8);
            local_20 = (uint *)((int)local_20 + 1);
            if (local_20 == (uint *)0x2) {
              local_20 = (uint *)0x0;
              local_8 = local_8 + 0x14;
            }
            local_c = (uint *)((int)local_c + 1);
            if (local_c == (uint *)0x14) {
              return;
            }
            piVar10 = piVar10 + 3;
            uVar9 = local_18 - 1999;
            local_18 = local_18 + 1;
          } while (uVar9 < (uint)local_2c[0x18]);
        }
      }
    }
  }
  else if (iVar8 == 2) {
    if (*(int *)((int)this + 0x548) != -1) {
      uVar9 = *(uint *)((int)this + *(int *)((int)this + 0x548) * 4 + 0x3b4);
      local_1c = (void *)FUN_0042f710(uVar9,1);
      FUN_004e2172((int)param_1,(uint *)0x14,(byte *)0x3c,pvVar3,(undefined4 *)local_10,
                   (byte *)s__gfxgood__d_1___s_00508650);
      pbVar5 = (byte *)0x5a;
      if ((*(void **)((int)this + 0x544) != (void *)0x0) &&
         (pbVar6 = (byte *)FUN_0042bcae(*(void **)((int)this + 0x544),uVar9), pbVar6 != (byte *)0x0)
         ) {
        pbVar5 = FUN_004e21b7(param_1,0x14,(byte *)0x5a,500,local_2c,local_10,pbVar6);
        pbVar5 = pbVar5 + 100;
      }
      param_2 = (int *)0x0;
      local_18 = 0;
      if (0 < *(int *)((int)this + 0x84)) {
        piVar10 = (int *)((int)this + 0x8c);
        do {
          local_20 = (uint *)0x0;
          iVar8 = *(int *)(DAT_00568c0c + 0x3c + (piVar10[-1] * 0x22f + *piVar10) * 4);
          uVar1 = *(uint *)((int)DAT_005113a0 + iVar8 * 0x624 + 0x484);
          if (uVar1 != 0) {
            local_24 = (uint *)((int)DAT_005113a0 + iVar8 * 0x624 + 0x488);
            do {
              if (*local_24 == uVar9) {
                aiStack_58[(int)param_2] = local_18;
                param_2 = (int *)((int)param_2 + 1);
                break;
              }
              local_20 = (uint *)((int)local_20 + 1);
              local_24 = local_24 + 1;
            } while (local_20 < uVar1);
          }
          if (param_2 == (int *)0xa) break;
          local_18 = local_18 + 1;
          piVar10 = piVar10 + 2;
        } while (local_18 < *(int *)((int)this + 0x84));
        if (param_2 != (int *)0x0) {
          FUN_004e162e(0x2b);
          FUN_004e556b((undefined1 *)local_1e8,(byte *)s__s__s__005076e8);
          pbVar6 = FUN_004e21b7(param_1,0x14,pbVar5 + 0x1e,500,local_8,local_10,(byte *)local_1e8);
          local_14 = (void *)0x0;
          pbVar6 = pbVar5 + 0x24 + (int)pbVar6;
          if (0 < (int)param_2) {
            do {
              local_28 = *(int *)((int)this + aiStack_58[(int)local_14] * 8 + 0x88);
              local_1c = *(void **)((int)this + aiStack_58[(int)local_14] * 8 + 0x8c);
              pbVar5 = (byte *)FUN_0042f798(local_28,(uint)local_1c,1);
              local_c = (uint *)FUN_004e21b7(param_1,0x14,pbVar6,500,local_2c,local_10,pbVar5);
              FUN_004b8be4((void *)((int)this + 0x55c),20000,(int)local_14,0x1de,(int)pbVar6,0x8f,
                           (uint *)0x0);
              FUN_004b8d4c((void *)((int)this + 0x55c),20000,(int)local_14,local_28,local_1c);
              local_14 = (void *)((int)local_14 + 1);
              pbVar6 = pbVar6 + 2 + (int)local_c;
            } while ((int)local_14 < (int)param_2);
          }
        }
      }
    }
  }
  else if ((iVar8 == 3) && (*(int *)((int)this + 0x554) != -1)) {
    uVar9 = *(int *)((int)this + 0x554) * 2;
    puVar4 = (uint *)FUN_0042bcae(*(void **)((int)this + 0x550),uVar9);
    FUN_004e1e3f((int)param_1,(uint *)0x14,(byte *)0x3c,local_8,(undefined4 *)local_10,puVar4);
    if ((*(int *)((int)this + 0x544) != 0) &&
       (pbVar5 = (byte *)FUN_0042bcae(*(void **)((int)this + 0x550),uVar9 + 1),
       pbVar5 != (byte *)0x0)) {
      FUN_004e21b7(param_1,0x14,(byte *)0x5a,500,pvVar2,local_10,pbVar5);
    }
  }
  return;
}



## data.raw_result.limitations



## data.normalized_result


/* WARNING: Type propagation algorithm not settling */

void __thiscall FUN_004c227c(void *this,void *param_1,int *param_2)

{
  uint uVar1;
  void *pvVar2;
  void *pvVar3;
  uint *puVar4;
  byte *pbVar5;
  byte *pbVar6;
  uint *puVar7;
  int iVar8;
  uint uVar9;
  int *piVar10;
  int iVar11;
  uint local_1e8 [21];
  int local_194 [2];
  uint local_18c [52];
  uint local_bc [25];
  int aiStack_58 [10];
  uint local_30;
  int *local_2c;
  uint local_28;
  uint *local_24;
  uint *local_20;
  void *local_1c;
  int local_18;
  void *local_14;
  byte *local_10;
  uint *local_c;
  byte *local_8;
  
  FUN_004b7b44(this,param_1,param_2);
  pvVar3 = DAT_00569aa4;
  pvVar2 = DAT_00569aa0;
  local_2c = DAT_00569aa8;
  local_10 = (byte *)(DAT_00569abc + 0x400);
  iVar8 = *(int *)((int)this + 0x70);
  local_14 = DAT_00569aa0;
  local_8 = DAT_00569aa4;
  if (iVar8 == 0) {
    FUN_004e1d9e((int)param_1,(undefined4 *)((int)this + 0x74),2);
  }
  else if (iVar8 == 1) {
    iVar8 = *(int *)((int)this + 0x3ac);
    if (iVar8 != -1) {
      uVar9 = *(uint *)((int)this + iVar8 * 8 + 0x8c);
      puVar4 = *(uint **)((int)this + iVar8 * 8 + 0x88);
      local_30 = uVar9;
      local_c = puVar4;
      puVar7 = (uint *)FUN_0042f798((int)puVar4,uVar9,1);
      iVar11 = (int)puVar4 * 0x8bc + DAT_00568c0c;
      local_1c = *(void **)(iVar11 + 0x3c + uVar9 * 4);
      local_2c = (int *)((int)local_1c * 0x624 + (int)DAT_005113a0);
      local_18 = *local_2c;
      iVar8 = FUN_0048064b(DAT_005113a0,(byte *)s_house_sepia_005076f0);
      FUN_00495ffc((int)local_c,uVar9,(int)param_1,(uint *)0xfa,(byte *)0x12c,iVar8,'\0');
      FUN_004e1e3f((int)param_1,(uint *)0x14,(byte *)0x3c,local_8,(undefined4 *)local_10,puVar7);
      local_8 = (byte *)0x56;
      if ((*(void **)((int)this + 0x3a8) != (void *)0x0) &&
         (pbVar5 = (byte *)FUN_0042bcae(*(void **)((int)this + 0x3a8),(uint)local_1c),
         pbVar5 != (byte *)0x0)) {
        local_8 = FUN_004e21b7(param_1,0x14,(byte *)0x56,500,local_14,local_10,pbVar5);
        local_8 = local_8 + 0x60;
      }
      FUN_004e162e(0x26);
      FUN_004e2172((int)param_1,(uint *)0x14,local_8,local_14,(undefined4 *)local_10,&DAT_00507728);
      local_8 = local_8 + 0x10;
      FUN_00432a48((int)local_c,uVar9,'\0',local_194);
      param_2 = (int *)0x0;
      local_24 = (uint *)0x28;
      if (0 < local_194[0]) {
        local_20 = local_18c;
        do {
          local_1c = (void *)local_20[-1];
          local_28 = *local_20;
          FUN_004e556b((undefined1 *)(aiStack_58 + 2),(byte *)s__setx_10__gfxgood__d__d__00508634);
          FUN_0042f710((int)local_1c,local_28);
          FUN_004e556b((undefined1 *)local_bc,(byte *)s__d__s_005077b4);
          FUN_004b8c93((void *)((int)this + 0x55c),0x271f,(int)param_2,(int)local_24,(int)local_8,
                       0x32,0x18,(uint *)(aiStack_58 + 2),0,local_bc);
          FUN_004b8d4c((void *)((int)this + 0x55c),0x271f,(int)param_2,local_1c,0);
          local_24 = (uint *)((int)local_24 + 0x34);
          param_2 = (int *)((int)param_2 + 1);
          local_20 = local_20 + 5;
        } while ((int)param_2 < local_194[0]);
      }
      local_8 = local_8 + 0x1e;
      uVar9 = local_30 + 1;
      if (uVar9 < *(uint *)(iVar11 + 0x54)) {
        FUN_004e162e(0x27);
        FUN_004e2172((int)param_1,(uint *)0x14,local_8,local_14,(undefined4 *)local_10,&DAT_00507728
                    );
        local_8 = local_8 + 0x10;
        FUN_00432a48((int)local_c,uVar9,'\x01',local_194);
        local_c = (uint *)0x28;
        if (0 < local_194[0]) {
          param_2 = (int *)0x3e8;
          puVar4 = local_18c;
          do {
            local_1c = (void *)*puVar4;
            local_28 = puVar4[-1];
            FUN_004e556b((undefined1 *)(aiStack_58 + 2),(byte *)s__setx_10__gfxgood__d__d__00508634)
            ;
            FUN_0042f710(local_28,(uint)local_1c);
            FUN_004e556b((undefined1 *)local_bc,(byte *)s__d__s_005077b4);
            FUN_004b8c93((void *)((int)this + 0x55c),0x271f,(int)param_2,(int)local_c,(int)local_8,
                         0x32,0x18,(uint *)(aiStack_58 + 2),0,local_bc);
            FUN_004b8d4c((void *)((int)this + 0x55c),0x271f,(int)param_2,local_28,0);
            local_c = local_c + 0xd;
            puVar4 = puVar4 + 5;
            iVar8 = (int)param_2 + -999;
            param_2 = (int *)((int)param_2 + 1);
          } while (iVar8 < local_194[0]);
        }
        local_8 = local_8 + 0x1e;
      }
      if (((local_18 == 1) || (local_18 == 3)) || (piVar10 = local_2c, local_18 == 5)) {
        FUN_004e162e(0x28);
        FUN_004e2172((int)param_1,(uint *)0x14,local_8,local_14,(undefined4 *)local_10,&DAT_00507728
                    );
        piVar10 = local_2c;
        local_8 = local_8 + 0x10;
        local_1e8[0]._0_1_ = 0;
        param_2 = (int *)0x0;
        if (0 < local_2c[3]) {
          local_c = (uint *)(local_2c + 5);
          do {
            local_30 = *local_c;
            FUN_0042f754(local_c[-1],local_30);
            FUN_004e556b((undefined1 *)local_bc,(byte *)s__d__s_005077b4);
            if (param_2 != (int *)0x0) {
              FUN_004e5410(local_1e8,(uint *)&DAT_00508630);
            }
            FUN_004e5410(local_1e8,local_bc);
            param_2 = (int *)((int)param_2 + 1);
            local_c = local_c + 2;
          } while ((int)param_2 < piVar10[3]);
        }
        FUN_004e1e3f((int)param_1,(uint *)0x28,local_8,local_14,(undefined4 *)local_10,local_1e8);
        local_8 = local_8 + 0x16;
      }
      FUN_004e162e(0x29);
      FUN_004e2172((int)param_1,(uint *)0x14,local_8,local_14,(undefined4 *)local_10,&DAT_00507728);
      local_8 = local_8 + 0x10;
      if (local_18 == 1) {
        pbVar5 = (byte *)FUN_004e162e(0x2a);
        FUN_004e2172((int)param_1,(uint *)0x28,local_8,local_14,(undefined4 *)local_10,pbVar5);
      }
      else {
        local_20 = (uint *)0x0;
        local_c = (uint *)0x0;
        if (piVar10[0x18] != 0) {
          local_1c = (void *)((int)this + 0x55c);
          local_18 = 2000;
          piVar10 = piVar10 + 0x1a;
          do {
            local_24 = (uint *)piVar10[-1];
            if (*(int *)(DAT_00510bc4 + 0x5d200) == 1) {
              iVar8 = 2;
            }
            else if (*(int *)(DAT_00510bc4 + 0x5d200) == 2) {
              iVar8 = 5;
            }
            else {
              iVar8 = 1;
            }
            local_30 = iVar8 * *piVar10;
            iVar8 = (int)local_20 * 0xdc;
            FUN_004e2172((int)param_1,(uint *)(iVar8 + 0x28),local_8,local_14,(undefined4 *)local_10
                         ,&DAT_005070cc);
            FUN_004e556b((undefined1 *)(aiStack_58 + 2),(byte *)s__setx_10__gfxgood__d_1__00508618);
            puVar4 = (uint *)FUN_0042f710((int)local_24,1);
            FUN_004b8c93(local_1c,0x271f,local_18,iVar8 + 0x3c,(int)local_8,0x28,0x12,
                         (uint *)(aiStack_58 + 2),0,puVar4);
            FUN_004b8d4c(local_1c,0x271f,local_18,local_24,0);
            FUN_0042f710((int)local_24,local_30);
            FUN_004e2172((int)param_1,(uint *)(iVar8 + 0x68),local_8,local_14,(undefined4 *)local_10
                         ,(byte *)s__s__s_005076b8);
            local_20 = (uint *)((int)local_20 + 1);
            if (local_20 == (uint *)0x2) {
              local_20 = (uint *)0x0;
              local_8 = local_8 + 0x14;
            }
            local_c = (uint *)((int)local_c + 1);
            if (local_c == (uint *)0x14) {
              return;
            }
            piVar10 = piVar10 + 3;
            uVar9 = local_18 - 1999;
            local_18 = local_18 + 1;
          } while (uVar9 < (uint)local_2c[0x18]);
        }
      }
    }
  }
  else if (iVar8 == 2) {
    if (*(int *)((int)this + 0x548) != -1) {
      uVar9 = *(uint *)((int)this + *(int *)((int)this + 0x548) * 4 + 0x3b4);
      local_1c = (void *)FUN_0042f710(uVar9,1);
      FUN_004e2172((int)param_1,(uint *)0x14,(byte *)0x3c,pvVar3,(undefined4 *)local_10,
                   (byte *)s__gfxgood__d_1___s_00508650);
      pbVar5 = (byte *)0x5a;
      if ((*(void **)((int)this + 0x544) != (void *)0x0) &&
         (pbVar6 = (byte *)FUN_0042bcae(*(void **)((int)this + 0x544),uVar9), pbVar6 != (byte *)0x0)
         ) {
        pbVar5 = FUN_004e21b7(param_1,0x14,(byte *)0x5a,500,local_2c,local_10,pbVar6);
        pbVar5 = pbVar5 + 100;
      }
      param_2 = (int *)0x0;
      local_18 = 0;
      if (0 < *(int *)((int)this + 0x84)) {
        piVar10 = (int *)((int)this + 0x8c);
        do {
          local_20 = (uint *)0x0;
          iVar8 = *(int *)(DAT_00568c0c + 0x3c + (piVar10[-1] * 0x22f + *piVar10) * 4);
          uVar1 = *(uint *)((int)DAT_005113a0 + iVar8 * 0x624 + 0x484);
          if (uVar1 != 0) {
            local_24 = (uint *)((int)DAT_005113a0 + iVar8 * 0x624 + 0x488);
            do {
              if (*local_24 == uVar9) {
                aiStack_58[(int)param_2] = local_18;
                param_2 = (int *)((int)param_2 + 1);
                break;
              }
              local_20 = (uint *)((int)local_20 + 1);
              local_24 = local_24 + 1;
            } while (local_20 < uVar1);
          }
          if (param_2 == (int *)0xa) break;
          local_18 = local_18 + 1;
          piVar10 = piVar10 + 2;
        } while (local_18 < *(int *)((int)this + 0x84));
        if (param_2 != (int *)0x0) {
          FUN_004e162e(0x2b);
          FUN_004e556b((undefined1 *)local_1e8,(byte *)s__s__s__005076e8);
          pbVar6 = FUN_004e21b7(param_1,0x14,pbVar5 + 0x1e,500,local_8,local_10,(byte *)local_1e8);
          local_14 = (void *)0x0;
          pbVar6 = pbVar5 + 0x24 + (int)pbVar6;
          if (0 < (int)param_2) {
            do {
              local_28 = *(int *)((int)this + aiStack_58[(int)local_14] * 8 + 0x88);
              local_1c = *(void **)((int)this + aiStack_58[(int)local_14] * 8 + 0x8c);
              pbVar5 = (byte *)FUN_0042f798(local_28,(uint)local_1c,1);
              local_c = (uint *)FUN_004e21b7(param_1,0x14,pbVar6,500,local_2c,local_10,pbVar5);
              FUN_004b8be4((void *)((int)this + 0x55c),20000,(int)local_14,0x1de,(int)pbVar6,0x8f,
                           (uint *)0x0);
              FUN_004b8d4c((void *)((int)this + 0x55c),20000,(int)local_14,local_28,local_1c);
              local_14 = (void *)((int)local_14 + 1);
              pbVar6 = pbVar6 + 2 + (int)local_c;
            } while ((int)local_14 < (int)param_2);
          }
        }
      }
    }
  }
  else if ((iVar8 == 3) && (*(int *)((int)this + 0x554) != -1)) {
    uVar9 = *(int *)((int)this + 0x554) * 2;
    puVar4 = (uint *)FUN_0042bcae(*(void **)((int)this + 0x550),uVar9);
    FUN_004e1e3f((int)param_1,(uint *)0x14,(byte *)0x3c,local_8,(undefined4 *)local_10,puVar4);
    if ((*(int *)((int)this + 0x544) != 0) &&
       (pbVar5 = (byte *)FUN_0042bcae(*(void **)((int)this + 0x550),uVar9 + 1),
       pbVar5 != (byte *)0x0)) {
      FUN_004e21b7(param_1,0x14,(byte *)0x5a,500,pvVar2,local_10,pbVar5);
    }
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

The session serves operations only after Ghidra reports default auto-analysis complete; incomplete analysis does not expose partial results.,The imported Program and temporary project are ephemeral and deleted on close. Annotation operations edit session database metadata; original executable bytes are never written.,Cancelling an active Ghidra request terminates its ephemeral database and discards session annotations. The selected target remains open; the next provider query imports the original artifact again.,Default-space addresses use lowercase 0x-prefixed hexadecimal; other address spaces use <percent-encoded-space>:0x<hex>.,Pseudocode is Ghidra decompiler output, not original source and not text-equivalent to Hopper output.,External functions and functions without an analyzable body return null; other decompiler failures remain explicit.,Windows Ghidra P0 accepts approved native x86 and x86-64 PE applications and DLLs; managed, hostile, sensitive, and mutable-path targets are unsupported.,The Windows bridge uses authenticated IPv4 loopback because Node path-based IPC does not expose Java AF_UNIX sockets; the endpoint file contains no bearer token.,Windows sessions require the matching packaged Windows x64 native addon, local NTFS targets and runtimes, and Windows 10 or later. Native handles enforce path admission, private DACLs, and Job Object ownership automatically.

## data.locations



## data.evidence_links



## meta

| Key      | Value     |
|----------|-----------|
| command  | decompile |
| duration | 81940ms   |
