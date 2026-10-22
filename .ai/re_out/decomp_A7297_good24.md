## ok

true

## data.evidence_id

ev_5c8231d06dcce762cbb95ba7979371a82f870054785918c80a0aa89a15da54fe

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
| procedure | 0x4A7297 |

## data.raw_result.value


void __thiscall FUN_004a693b(void *this,void *param_1,byte *param_2)

{
  void *pvVar1;
  char cVar2;
  byte *pbVar3;
  char *this_00;
  int iVar4;
  uint uVar5;
  int *piVar6;
  int iVar7;
  uint *puVar8;
  undefined4 *puVar9;
  uint *puVar10;
  int iVar11;
  byte *pbVar12;
  char *pcVar13;
  char *pcVar14;
  undefined4 local_1d4 [20];
  byte local_184 [100];
  undefined4 local_120 [21];
  CRect local_cc [16];
  CRect local_bc [16];
  CRect local_ac [16];
  undefined4 local_9c [21];
  int local_48;
  int local_44;
  int local_40;
  int local_3c;
  undefined4 local_38;
  int local_34;
  int local_30;
  uint local_2c;
  int local_28;
  uint local_24;
  byte *local_20;
  int local_1c;
  uint *local_18;
  byte *local_14;
  void *local_10;
  byte *local_c;
  uint *local_8;
  
  FUN_004b8b00((undefined4 *)((int)this + 0x308));
  local_24 = 0;
  local_14 = (byte *)((int)this + 0x8c);
  local_8 = &DAT_004f6208;
  do {
    if (*(char *)((int)this + local_24 + 0x70) != '\0') {
      FUN_0041026e(&local_44,(undefined4 *)local_14);
      local_40 = local_40 + *(int *)(param_2 + 4);
      local_44 = local_44 + *(int *)param_2;
      if (*(char *)(local_24 + 0x7b + (int)this) != '\0') {
        local_44 = local_44 + -200 + local_3c;
        local_3c = 200;
      }
      local_38 = 0x10;
      FUN_004caaa5((int)param_1,&local_44,5);
      if (*local_8 == 0xffffffff) {
        pbVar3 = (byte *)local_8[1];
      }
      else {
        pbVar3 = (byte *)FUN_004e1658(*local_8);
      }
      FUN_004caaea(param_1,&local_44,'\x01',pbVar3);
      if (*(char *)(local_24 + 0x7b + (int)this) == '\0') {
        FUN_0041026e(&local_34,(undefined4 *)local_14);
        local_34 = local_34 + *(int *)param_2;
        local_28 = local_28 + -0x10;
        local_30 = local_30 + 0x10 + *(int *)(param_2 + 4);
        FUN_004caaa5((int)param_1,&local_34,1);
      }
    }
    local_24 = local_24 + 1;
    local_8 = local_8 + 4;
    local_14 = (byte *)((int)local_14 + 0x10);
  } while (local_24 < 0xb);
  this_00 = FUN_004a765f();
  if (this_00 != (char *)0x0) {
    local_24 = FUN_004316d0((int)this_00);
    local_48 = FUN_0047ffc0(*(int *)(this_00 + 0x10));
    local_10 = DAT_00569aa0;
    local_14 = (byte *)(DAT_00569ab0 + 0x400);
    local_1c = 0;
    do {
      if ((*(char *)((int)this + local_1c + 0x70) != '\0') &&
         (*(char *)(local_1c + 0x7b + (int)this) == '\0')) {
        if (local_1c == 0) {
          iVar7 = *(int *)((int)this + 0x90);
          local_c = (byte *)(*(int *)((int)this + 0x8c) + 0xc0);
          local_8 = (uint *)((*(int *)((int)this + 0x94) - (int)local_c) + -4 +
                            *(int *)((int)this + 0x8c));
          pbVar12 = (byte *)(iVar7 + 0x16);
          pbVar3 = (byte *)FUN_0042f776(*(int *)(this_00 + 0x14),1);
          iVar4 = FUN_0043967d(local_10,pbVar3);
          FUN_0040ecf9(param_1,local_10,local_14,(int)(local_c + ((int)local_8 - iVar4) / 2),pbVar12
                       ,pbVar3);
          iVar4 = *(int *)(this_00 + 0x7c8);
          local_18 = *(uint **)(local_48 + 0x19c + *(int *)(this_00 + 0x20) * 4);
          CRect::CRect((CRect *)&local_34,(int)local_c,iVar7 + 0x28,(int)local_8,8);
          FUN_004e1d9e((int)param_1,&local_34,2);
          FUN_004102f6(&local_34,-2,-2);
          local_2c = (local_2c * iVar4) / (uint)local_18;
          uVar5 = (uint)(iVar4 * 0xff) / (uint)local_18;
          if (0xff < uVar5) {
            uVar5 = 0xff;
          }
          FUN_0040dbbf(param_1,&local_34,(byte *)(DAT_00569ad0 + 4 + uVar5 * 4));
          FUN_004e1658(0x14);
          pcVar14 = s__s___d___0050778c;
          piVar6 = (int *)CRect::CRect((CRect *)&local_44,(int)local_c,iVar7 + 0x26,(int)local_8,0xc
                                      );
          FUN_004b8b4f((void *)((int)this + 0x308),piVar6,(byte *)pcVar14);
          pbVar3 = (byte *)(iVar7 + 0x31);
          pcVar14 = FUN_004a765f();
          if ((pcVar14 == (char *)0x0) || (iVar7 = FUN_004316e0((int)pcVar14), iVar7 != 1))
          goto LAB_004a75d0;
          FUN_004e1658(0x15);
          FUN_004e556b(local_184,(byte *)s__s___d_005071f0);
          pbVar12 = local_184;
          iVar7 = FUN_0043967d(local_10,local_184);
          FUN_0040ecf9(param_1,local_10,local_14,(int)(local_c + ((int)local_8 - iVar7) / 2),pbVar3,
                       pbVar12);
        }
        if (local_1c == 1) {
          iVar7 = *(int *)((int)this + 0x9c);
          param_2 = (byte *)(iVar7 + 8);
          local_c = (byte *)(*(int *)((int)this + 0xa0) + 0x16);
          local_20 = param_2;
          cVar2 = FUN_0040b067(*(int *)(this_00 + 4),*DAT_00569274,local_120);
          pbVar3 = local_c;
          if (cVar2 != '\0') {
            iVar4 = FUN_004407dd(local_120,0xe);
            if ((char)iVar4 == '\0') {
              FUN_004b8d89((void *)((int)this + 0x31ec),0x2729,0);
            }
            else {
              puVar8 = (uint *)FUN_004e1658(0x8c);
              FUN_004b8be4((void *)((int)this + 0x31ec),0x2729,0,(int)param_2,(int)(local_c + 2),
                           0x1e,puVar8);
              param_2 = (byte *)(iVar7 + 0x26);
            }
            iVar7 = FUN_004407dd(local_120,0xf);
            if ((char)iVar7 == '\0') {
              FUN_004b8d89((void *)((int)this + 0x31ec),0x272a,0);
              pbVar3 = local_c;
            }
            else {
              puVar8 = (uint *)FUN_004e1658(0x8d);
              pbVar3 = local_c;
              FUN_004b8be4((void *)((int)this + 0x31ec),0x272a,0,(int)param_2,(int)(local_c + 2),
                           0x1d,puVar8);
              param_2 = param_2 + 0x1e;
            }
            if (this_00[0x7d8] == '\0') {
              uVar5 = 0x8f;
            }
            else {
              uVar5 = 0x8e;
            }
            pbVar12 = (byte *)FUN_004e1658(uVar5);
            FUN_0040ecf9(param_1,local_10,local_14,(int)param_2,pbVar3,pbVar12);
            if (*(int *)(this_00 + 0x14) == 1) {
              FUN_004b8d89((void *)((int)this + 0x31ec),0x272b,0);
              pbVar3 = pbVar3 + 0x14;
            }
            else {
              puVar8 = (uint *)FUN_004e1658(0x90);
              FUN_004b8be4((void *)((int)this + 0x31ec),0x272b,0,(int)local_20,(int)(pbVar3 + 0x16),
                           0x1d,puVar8);
              pbVar3 = pbVar3 + 0x26;
            }
          }
          FUN_004a8596(this,1,(int)(pbVar3 + (-8 - *(int *)((int)this + 0xa0))));
        }
        if (local_1c == 2) {
          iVar7 = *(int *)((int)this + 0xb0);
          local_18 = (uint *)(*(int *)((int)this + 0xac) + 8);
          param_2 = (byte *)(iVar7 + 0x12);
          if (*(int *)(this_00 + 0x2c) == 1) {
            FUN_00433041((int)this_00);
            uVar5 = 0x16;
LAB_004a6e2a:
            FUN_004e1658(uVar5);
            FUN_0040edc8(param_1,local_10,local_14,(int)local_18,param_2,
                         (byte *)s__s___d____00507214);
            param_2 = (byte *)(iVar7 + 0x22);
          }
          else if (*(int *)(this_00 + 0x2c) == 2) {
            FUN_00433041((int)this_00);
            uVar5 = 0x17;
            goto LAB_004a6e2a;
          }
          local_c = (byte *)0x0;
          if (0 < *(int *)(this_00 + 0x38)) {
            pcVar14 = this_00 + 0x44;
            do {
              FUN_0042f710(*(int *)(pcVar14 + -8),1);
              pcVar13 = s__gfxgood__d_1___s__d____d____d_00507768;
              puVar9 = (undefined4 *)FUN_004e1e29();
              FUN_004e2172((int)param_1,local_18,param_2,local_10,puVar9,(byte *)pcVar13);
              param_2 = param_2 + 0xc;
              local_c = local_c + 1;
              pcVar14 = pcVar14 + 0x14;
            } while ((int)local_c < *(int *)(this_00 + 0x38));
          }
          FUN_004a8596(this,2,(int)(param_2 + (-8 - *(int *)((int)this + 0xb0))));
        }
        if (local_1c == 3) {
          iVar7 = *(int *)((int)this + 0xc0);
          iVar4 = *(int *)((int)this + 0xbc);
          local_8 = (uint *)(iVar4 + 8);
          FUN_00433519(this_00,*DAT_00569274,local_9c);
          pbVar3 = (byte *)(iVar7 + 0x16);
          if (this_00[0x780] == '\0') {
            uVar5 = 0x33;
          }
          else {
            uVar5 = 0x32;
          }
          FUN_004e1658(uVar5);
          FUN_004e1658(0x29);
          FUN_004e1658(0x28);
          FUN_004e2172((int)param_1,(uint *)(iVar4 + 0x1c),pbVar3,local_10,(undefined4 *)local_14,
                       (byte *)s__s__s___s__setx__d__d_00507750);
          iVar4 = FUN_004407dd(local_9c,4);
          if ((char)iVar4 == '\0') {
            FUN_004b8d89((void *)((int)this + 0x31ec),0x2722,0);
          }
          else {
            puVar8 = (uint *)FUN_004e1658(0x2a);
            FUN_004b8be4((void *)((int)this + 0x31ec),0x2722,0,(int)local_8,(int)pbVar3,0x1e,puVar8)
            ;
          }
          iVar4 = FUN_004407dd(local_9c,5);
          if ((char)iVar4 == '\0') {
            FUN_004b8d89((void *)((int)this + 0x31ec),0x2721,0);
            puVar8 = local_8;
          }
          else {
            puVar10 = (uint *)FUN_004e1658(0x2b);
            puVar8 = local_8;
            FUN_004b8be4((void *)((int)this + 0x31ec),0x2721,0,(int)local_8,(int)pbVar3,0x1d,puVar10
                        );
          }
          pbVar3 = (byte *)(iVar7 + 0x26);
          if (this_00[0x788] == '\0') {
            uVar5 = 0x33;
          }
          else {
            uVar5 = 0x32;
          }
          FUN_004e1658(uVar5);
          FUN_004e1658(0x2c);
          FUN_004e1658(0x28);
          FUN_004e2172((int)param_1,puVar8 + 5,pbVar3,local_10,(undefined4 *)local_14,
                       (byte *)s__s__s___s__setx__d__d_00507750);
          iVar4 = FUN_004407dd(local_9c,6);
          if ((char)iVar4 == '\0') {
            FUN_004b8d89((void *)((int)this + 0x31ec),0x2724,0);
          }
          else {
            puVar8 = (uint *)FUN_004e1658(0x2d);
            FUN_004b8be4((void *)((int)this + 0x31ec),0x2724,0,(int)local_8,(int)pbVar3,0x1e,puVar8)
            ;
          }
          iVar4 = FUN_004407dd(local_9c,7);
          if ((char)iVar4 == '\0') {
            FUN_004b8d89((void *)((int)this + 0x31ec),0x2723,0);
            puVar8 = local_8;
          }
          else {
            puVar10 = (uint *)FUN_004e1658(0x2e);
            puVar8 = local_8;
            FUN_004b8be4((void *)((int)this + 0x31ec),0x2723,0,(int)local_8,(int)pbVar3,0x1d,puVar10
                        );
          }
          pbVar3 = (byte *)(iVar7 + 0x36);
          if (this_00[0x790] == '\0') {
            uVar5 = 0x33;
          }
          else {
            uVar5 = 0x32;
          }
          FUN_004e1658(uVar5);
          FUN_004e1658(0x2f);
          FUN_004e1658(0x28);
          FUN_004e2172((int)param_1,puVar8 + 5,pbVar3,local_10,(undefined4 *)local_14,
                       (byte *)s__s__s___s__setx__d__d_00507750);
          iVar4 = FUN_004407dd(local_9c,8);
          if ((char)iVar4 == '\0') {
            FUN_004b8d89((void *)((int)this + 0x31ec),0x2726,0);
          }
          else {
            puVar8 = (uint *)FUN_004e1658(0x30);
            FUN_004b8be4((void *)((int)this + 0x31ec),0x2726,0,(int)local_8,(int)pbVar3,0x1e,puVar8)
            ;
          }
          iVar4 = FUN_004407dd(local_9c,9);
          if ((char)iVar4 == '\0') {
            FUN_004b8d89((void *)((int)this + 0x31ec),0x2725,0);
          }
          else {
            puVar8 = (uint *)FUN_004e1658(0x31);
            FUN_004b8be4((void *)((int)this + 0x31ec),0x2725,0,(int)local_8,(int)pbVar3,0x1d,puVar8)
            ;
          }
          FUN_00432753(this_00,local_1d4);
          FUN_004e1658(0x34);
          FUN_0040edc8(param_1,local_10,local_14,(int)local_8,(byte *)(iVar7 + 0x4a),
                       (byte *)s__s___d__d_00507744);
          FUN_004a8596(this,3,(int)((byte *)(iVar7 + 0x4a) + (4 - *(int *)((int)this + 0xc0))));
        }
        if ((((local_1c == 4) || (local_1c == 5)) || (local_1c == 6)) &&
           (iVar7 = *(int *)((int)this + 0x178), iVar7 != 0)) {
          local_18 = (uint *)FUN_0042f710(iVar7,1);
          piVar6 = (int *)(local_1c * 0x10 + 0x8c + (int)this);
          iVar4 = *piVar6;
          local_20 = (byte *)(piVar6[3] + -0x15 + piVar6[1]);
          FUN_00431fa7(this_00,iVar7);
          FUN_004e1658(0x3d);
          FUN_004e2172((int)param_1,(uint *)(iVar4 + 8),local_20,local_10,(undefined4 *)local_14,
                       (byte *)s__gfxgood__d_1___s___d_0050772c);
          puVar8 = local_18;
          piVar6 = (int *)CRect::CRect(local_bc,iVar4 + 8,(int)local_20,0x28,0x10);
          FUN_004b8b04((void *)((int)this + 0x308),piVar6,(char *)puVar8);
        }
        if (local_1c == 5) {
          iVar7 = *(int *)((int)this + 0xdc);
          iVar4 = *(int *)((int)this + 0xe0);
          local_18 = (uint *)(iVar7 + 10);
          FUN_004e1658(0x3e);
          FUN_0040edc8(param_1,local_10,local_14,(int)local_18,(byte *)(iVar4 + 0x12),&DAT_00507728)
          ;
          FUN_004e1658(0x3f);
          FUN_0040edc8(param_1,local_10,local_14,iVar7 + 0x7c,(byte *)(iVar4 + 0x12),&DAT_00507728);
          local_8 = (uint *)0x0;
          param_2 = (byte *)(iVar4 + 0x24);
          local_20 = (byte *)(iVar4 + 0x1e);
          if (*(int *)(local_24 + 0x60) != 0) {
            local_c = (byte *)(local_24 + 0x6c);
            do {
              iVar7 = *(int *)(local_c + -8);
              if (iVar7 < 0x38) {
                iVar4 = *(int *)(this_00 + 0x14);
                if (((iVar4 == 7) || (iVar4 == 8)) || ((iVar4 == 9 || (iVar4 == 1)))) {
                  cVar2 = '\x01';
                }
                else {
                  cVar2 = '\0';
                }
                FUN_00431a83(this_00,iVar7,cVar2);
                if (*local_c == 0) {
                  local_20 = local_20 + 0x12;
                }
                else {
                  pcVar14 = s__gfxgood__d_1____1f_00507710;
                  puVar9 = (undefined4 *)FUN_004e1e29();
                  FUN_004e2172((int)param_1,local_18,param_2,local_10,puVar9,(byte *)pcVar14);
                  pcVar14 = (char *)FUN_0042f710(iVar7,1);
                  piVar6 = (int *)CRect::CRect(local_cc,(int)local_18,(int)param_2,100,0xc);
                  FUN_004b8b04((void *)((int)this + 0x308),piVar6,pcVar14);
                  param_2 = param_2 + 0xe;
                }
              }
              local_8 = (uint *)((int)local_8 + 1);
              local_c = local_c + 0xc;
            } while (local_8 < *(uint **)(local_24 + 0x60));
          }
          pbVar3 = local_20;
          if ((int)local_20 < (int)param_2) {
            pbVar3 = param_2;
          }
          FUN_004a8596(this,5,(int)(pbVar3 + (0xc - *(int *)((int)this + 0xe0))));
        }
        if (local_1c == 6) {
          local_20 = (byte *)0x0;
          local_18 = (uint *)(*(int *)((int)this + 0xec) + 4);
          pbVar3 = (byte *)(*(int *)((int)this + 0xf0) + 0x14);
          if (*(int *)(local_24 + 0x60) == 0) goto LAB_004a75d0;
          local_c = (byte *)(local_24 + 0x6c);
          do {
            iVar7 = *(int *)(local_c + -8);
            if (iVar7 < 0x38) {
              iVar4 = *(int *)(this_00 + 0x14);
              if (((iVar4 == 7) || (iVar4 == 8)) || ((iVar4 == 9 || (iVar4 == 1)))) {
                cVar2 = '\x01';
              }
              else {
                cVar2 = '\0';
              }
              FUN_00431a83(this_00,iVar7,cVar2);
              if (*local_c != 0) {
                pcVar14 = s__gfxgood__d_1____1f_00507710;
                puVar9 = (undefined4 *)FUN_004e1e29();
                FUN_004e2172((int)param_1,local_18 + 1,pbVar3,local_10,puVar9,(byte *)pcVar14);
                pcVar14 = (char *)FUN_0042f710(iVar7,1);
                piVar6 = (int *)CRect::CRect(local_ac,(int)(local_18 + 1),(int)pbVar3,100,0xc);
                FUN_004b8b04((void *)((int)this + 0x308),piVar6,pcVar14);
                pbVar3 = pbVar3 + 0xe;
              }
            }
            local_20 = local_20 + 1;
            local_c = local_c + 0xc;
          } while (local_20 < *(byte **)(local_24 + 0x60));
        }
        if (local_1c == 9) {
          iVar7 = *(int *)((int)this + 0x120);
          iVar4 = *(int *)((int)this + 0x11c);
          iVar11 = FUN_004316e0((int)this_00);
          if (iVar11 != 1) goto LAB_004a75d0;
          pbVar3 = (byte *)FUN_0042f776(*(int *)(this_00 + 0x14),1);
          FUN_0040ecf9(param_1,local_10,local_14,iVar4 + 0xc4,(byte *)(iVar7 + 0x18),pbVar3);
        }
        if (local_1c == 10) {
          local_18 = (uint *)(*(int *)((int)this + 300) + 4);
          param_2 = (byte *)(*(int *)((int)this + 0x130) + 0x12);
          pbVar3 = (byte *)0xffffffff;
          while (local_20 = (byte *)FUN_0041cb32(DAT_00511728,(int)this_00,(int)pbVar3),
                pvVar1 = DAT_00511728, local_20 != (byte *)0xffffffff) {
            iVar7 = (int)local_20 * 0x18;
            FUN_0042f710(*(int *)((int)DAT_00511728 + iVar7 + 0x40),
                         *(uint *)((int)DAT_00511728 + iVar7 + 0x44));
            FUN_004e1658(0x5b);
            FUN_0042f710(*(int *)((int)pvVar1 + iVar7 + 0x48),*(uint *)((int)pvVar1 + iVar7 + 0x4c))
            ;
            FUN_004e1658(0x5a);
            FUN_0040edc8(param_1,local_10,local_14,(int)local_18,param_2,
                         (byte *)s__s__d__s____s__d__s_005076fc);
            param_2 = param_2 + 0xc;
            pbVar3 = local_20;
          }
        }
      }
LAB_004a75d0:
      local_1c = local_1c + 1;
    } while (local_1c < 0xb);
  }
  return;
}



## data.raw_result.limitations



## data.normalized_result


void __thiscall FUN_004a693b(void *this,void *param_1,byte *param_2)

{
  void *pvVar1;
  char cVar2;
  byte *pbVar3;
  char *this_00;
  int iVar4;
  uint uVar5;
  int *piVar6;
  int iVar7;
  uint *puVar8;
  undefined4 *puVar9;
  uint *puVar10;
  int iVar11;
  byte *pbVar12;
  char *pcVar13;
  char *pcVar14;
  undefined4 local_1d4 [20];
  byte local_184 [100];
  undefined4 local_120 [21];
  CRect local_cc [16];
  CRect local_bc [16];
  CRect local_ac [16];
  undefined4 local_9c [21];
  int local_48;
  int local_44;
  int local_40;
  int local_3c;
  undefined4 local_38;
  int local_34;
  int local_30;
  uint local_2c;
  int local_28;
  uint local_24;
  byte *local_20;
  int local_1c;
  uint *local_18;
  byte *local_14;
  void *local_10;
  byte *local_c;
  uint *local_8;
  
  FUN_004b8b00((undefined4 *)((int)this + 0x308));
  local_24 = 0;
  local_14 = (byte *)((int)this + 0x8c);
  local_8 = &DAT_004f6208;
  do {
    if (*(char *)((int)this + local_24 + 0x70) != '\0') {
      FUN_0041026e(&local_44,(undefined4 *)local_14);
      local_40 = local_40 + *(int *)(param_2 + 4);
      local_44 = local_44 + *(int *)param_2;
      if (*(char *)(local_24 + 0x7b + (int)this) != '\0') {
        local_44 = local_44 + -200 + local_3c;
        local_3c = 200;
      }
      local_38 = 0x10;
      FUN_004caaa5((int)param_1,&local_44,5);
      if (*local_8 == 0xffffffff) {
        pbVar3 = (byte *)local_8[1];
      }
      else {
        pbVar3 = (byte *)FUN_004e1658(*local_8);
      }
      FUN_004caaea(param_1,&local_44,'\x01',pbVar3);
      if (*(char *)(local_24 + 0x7b + (int)this) == '\0') {
        FUN_0041026e(&local_34,(undefined4 *)local_14);
        local_34 = local_34 + *(int *)param_2;
        local_28 = local_28 + -0x10;
        local_30 = local_30 + 0x10 + *(int *)(param_2 + 4);
        FUN_004caaa5((int)param_1,&local_34,1);
      }
    }
    local_24 = local_24 + 1;
    local_8 = local_8 + 4;
    local_14 = (byte *)((int)local_14 + 0x10);
  } while (local_24 < 0xb);
  this_00 = FUN_004a765f();
  if (this_00 != (char *)0x0) {
    local_24 = FUN_004316d0((int)this_00);
    local_48 = FUN_0047ffc0(*(int *)(this_00 + 0x10));
    local_10 = DAT_00569aa0;
    local_14 = (byte *)(DAT_00569ab0 + 0x400);
    local_1c = 0;
    do {
      if ((*(char *)((int)this + local_1c + 0x70) != '\0') &&
         (*(char *)(local_1c + 0x7b + (int)this) == '\0')) {
        if (local_1c == 0) {
          iVar7 = *(int *)((int)this + 0x90);
          local_c = (byte *)(*(int *)((int)this + 0x8c) + 0xc0);
          local_8 = (uint *)((*(int *)((int)this + 0x94) - (int)local_c) + -4 +
                            *(int *)((int)this + 0x8c));
          pbVar12 = (byte *)(iVar7 + 0x16);
          pbVar3 = (byte *)FUN_0042f776(*(int *)(this_00 + 0x14),1);
          iVar4 = FUN_0043967d(local_10,pbVar3);
          FUN_0040ecf9(param_1,local_10,local_14,(int)(local_c + ((int)local_8 - iVar4) / 2),pbVar12
                       ,pbVar3);
          iVar4 = *(int *)(this_00 + 0x7c8);
          local_18 = *(uint **)(local_48 + 0x19c + *(int *)(this_00 + 0x20) * 4);
          CRect::CRect((CRect *)&local_34,(int)local_c,iVar7 + 0x28,(int)local_8,8);
          FUN_004e1d9e((int)param_1,&local_34,2);
          FUN_004102f6(&local_34,-2,-2);
          local_2c = (local_2c * iVar4) / (uint)local_18;
          uVar5 = (uint)(iVar4 * 0xff) / (uint)local_18;
          if (0xff < uVar5) {
            uVar5 = 0xff;
          }
          FUN_0040dbbf(param_1,&local_34,(byte *)(DAT_00569ad0 + 4 + uVar5 * 4));
          FUN_004e1658(0x14);
          pcVar14 = s__s___d___0050778c;
          piVar6 = (int *)CRect::CRect((CRect *)&local_44,(int)local_c,iVar7 + 0x26,(int)local_8,0xc
                                      );
          FUN_004b8b4f((void *)((int)this + 0x308),piVar6,(byte *)pcVar14);
          pbVar3 = (byte *)(iVar7 + 0x31);
          pcVar14 = FUN_004a765f();
          if ((pcVar14 == (char *)0x0) || (iVar7 = FUN_004316e0((int)pcVar14), iVar7 != 1))
          goto LAB_004a75d0;
          FUN_004e1658(0x15);
          FUN_004e556b(local_184,(byte *)s__s___d_005071f0);
          pbVar12 = local_184;
          iVar7 = FUN_0043967d(local_10,local_184);
          FUN_0040ecf9(param_1,local_10,local_14,(int)(local_c + ((int)local_8 - iVar7) / 2),pbVar3,
                       pbVar12);
        }
        if (local_1c == 1) {
          iVar7 = *(int *)((int)this + 0x9c);
          param_2 = (byte *)(iVar7 + 8);
          local_c = (byte *)(*(int *)((int)this + 0xa0) + 0x16);
          local_20 = param_2;
          cVar2 = FUN_0040b067(*(int *)(this_00 + 4),*DAT_00569274,local_120);
          pbVar3 = local_c;
          if (cVar2 != '\0') {
            iVar4 = FUN_004407dd(local_120,0xe);
            if ((char)iVar4 == '\0') {
              FUN_004b8d89((void *)((int)this + 0x31ec),0x2729,0);
            }
            else {
              puVar8 = (uint *)FUN_004e1658(0x8c);
              FUN_004b8be4((void *)((int)this + 0x31ec),0x2729,0,(int)param_2,(int)(local_c + 2),
                           0x1e,puVar8);
              param_2 = (byte *)(iVar7 + 0x26);
            }
            iVar7 = FUN_004407dd(local_120,0xf);
            if ((char)iVar7 == '\0') {
              FUN_004b8d89((void *)((int)this + 0x31ec),0x272a,0);
              pbVar3 = local_c;
            }
            else {
              puVar8 = (uint *)FUN_004e1658(0x8d);
              pbVar3 = local_c;
              FUN_004b8be4((void *)((int)this + 0x31ec),0x272a,0,(int)param_2,(int)(local_c + 2),
                           0x1d,puVar8);
              param_2 = param_2 + 0x1e;
            }
            if (this_00[0x7d8] == '\0') {
              uVar5 = 0x8f;
            }
            else {
              uVar5 = 0x8e;
            }
            pbVar12 = (byte *)FUN_004e1658(uVar5);
            FUN_0040ecf9(param_1,local_10,local_14,(int)param_2,pbVar3,pbVar12);
            if (*(int *)(this_00 + 0x14) == 1) {
              FUN_004b8d89((void *)((int)this + 0x31ec),0x272b,0);
              pbVar3 = pbVar3 + 0x14;
            }
            else {
              puVar8 = (uint *)FUN_004e1658(0x90);
              FUN_004b8be4((void *)((int)this + 0x31ec),0x272b,0,(int)local_20,(int)(pbVar3 + 0x16),
                           0x1d,puVar8);
              pbVar3 = pbVar3 + 0x26;
            }
          }
          FUN_004a8596(this,1,(int)(pbVar3 + (-8 - *(int *)((int)this + 0xa0))));
        }
        if (local_1c == 2) {
          iVar7 = *(int *)((int)this + 0xb0);
          local_18 = (uint *)(*(int *)((int)this + 0xac) + 8);
          param_2 = (byte *)(iVar7 + 0x12);
          if (*(int *)(this_00 + 0x2c) == 1) {
            FUN_00433041((int)this_00);
            uVar5 = 0x16;
LAB_004a6e2a:
            FUN_004e1658(uVar5);
            FUN_0040edc8(param_1,local_10,local_14,(int)local_18,param_2,
                         (byte *)s__s___d____00507214);
            param_2 = (byte *)(iVar7 + 0x22);
          }
          else if (*(int *)(this_00 + 0x2c) == 2) {
            FUN_00433041((int)this_00);
            uVar5 = 0x17;
            goto LAB_004a6e2a;
          }
          local_c = (byte *)0x0;
          if (0 < *(int *)(this_00 + 0x38)) {
            pcVar14 = this_00 + 0x44;
            do {
              FUN_0042f710(*(int *)(pcVar14 + -8),1);
              pcVar13 = s__gfxgood__d_1___s__d____d____d_00507768;
              puVar9 = (undefined4 *)FUN_004e1e29();
              FUN_004e2172((int)param_1,local_18,param_2,local_10,puVar9,(byte *)pcVar13);
              param_2 = param_2 + 0xc;
              local_c = local_c + 1;
              pcVar14 = pcVar14 + 0x14;
            } while ((int)local_c < *(int *)(this_00 + 0x38));
          }
          FUN_004a8596(this,2,(int)(param_2 + (-8 - *(int *)((int)this + 0xb0))));
        }
        if (local_1c == 3) {
          iVar7 = *(int *)((int)this + 0xc0);
          iVar4 = *(int *)((int)this + 0xbc);
          local_8 = (uint *)(iVar4 + 8);
          FUN_00433519(this_00,*DAT_00569274,local_9c);
          pbVar3 = (byte *)(iVar7 + 0x16);
          if (this_00[0x780] == '\0') {
            uVar5 = 0x33;
          }
          else {
            uVar5 = 0x32;
          }
          FUN_004e1658(uVar5);
          FUN_004e1658(0x29);
          FUN_004e1658(0x28);
          FUN_004e2172((int)param_1,(uint *)(iVar4 + 0x1c),pbVar3,local_10,(undefined4 *)local_14,
                       (byte *)s__s__s___s__setx__d__d_00507750);
          iVar4 = FUN_004407dd(local_9c,4);
          if ((char)iVar4 == '\0') {
            FUN_004b8d89((void *)((int)this + 0x31ec),0x2722,0);
          }
          else {
            puVar8 = (uint *)FUN_004e1658(0x2a);
            FUN_004b8be4((void *)((int)this + 0x31ec),0x2722,0,(int)local_8,(int)pbVar3,0x1e,puVar8)
            ;
          }
          iVar4 = FUN_004407dd(local_9c,5);
          if ((char)iVar4 == '\0') {
            FUN_004b8d89((void *)((int)this + 0x31ec),0x2721,0);
            puVar8 = local_8;
          }
          else {
            puVar10 = (uint *)FUN_004e1658(0x2b);
            puVar8 = local_8;
            FUN_004b8be4((void *)((int)this + 0x31ec),0x2721,0,(int)local_8,(int)pbVar3,0x1d,puVar10
                        );
          }
          pbVar3 = (byte *)(iVar7 + 0x26);
          if (this_00[0x788] == '\0') {
            uVar5 = 0x33;
          }
          else {
            uVar5 = 0x32;
          }
          FUN_004e1658(uVar5);
          FUN_004e1658(0x2c);
          FUN_004e1658(0x28);
          FUN_004e2172((int)param_1,puVar8 + 5,pbVar3,local_10,(undefined4 *)local_14,
                       (byte *)s__s__s___s__setx__d__d_00507750);
          iVar4 = FUN_004407dd(local_9c,6);
          if ((char)iVar4 == '\0') {
            FUN_004b8d89((void *)((int)this + 0x31ec),0x2724,0);
          }
          else {
            puVar8 = (uint *)FUN_004e1658(0x2d);
            FUN_004b8be4((void *)((int)this + 0x31ec),0x2724,0,(int)local_8,(int)pbVar3,0x1e,puVar8)
            ;
          }
          iVar4 = FUN_004407dd(local_9c,7);
          if ((char)iVar4 == '\0') {
            FUN_004b8d89((void *)((int)this + 0x31ec),0x2723,0);
            puVar8 = local_8;
          }
          else {
            puVar10 = (uint *)FUN_004e1658(0x2e);
            puVar8 = local_8;
            FUN_004b8be4((void *)((int)this + 0x31ec),0x2723,0,(int)local_8,(int)pbVar3,0x1d,puVar10
                        );
          }
          pbVar3 = (byte *)(iVar7 + 0x36);
          if (this_00[0x790] == '\0') {
            uVar5 = 0x33;
          }
          else {
            uVar5 = 0x32;
          }
          FUN_004e1658(uVar5);
          FUN_004e1658(0x2f);
          FUN_004e1658(0x28);
          FUN_004e2172((int)param_1,puVar8 + 5,pbVar3,local_10,(undefined4 *)local_14,
                       (byte *)s__s__s___s__setx__d__d_00507750);
          iVar4 = FUN_004407dd(local_9c,8);
          if ((char)iVar4 == '\0') {
            FUN_004b8d89((void *)((int)this + 0x31ec),0x2726,0);
          }
          else {
            puVar8 = (uint *)FUN_004e1658(0x30);
            FUN_004b8be4((void *)((int)this + 0x31ec),0x2726,0,(int)local_8,(int)pbVar3,0x1e,puVar8)
            ;
          }
          iVar4 = FUN_004407dd(local_9c,9);
          if ((char)iVar4 == '\0') {
            FUN_004b8d89((void *)((int)this + 0x31ec),0x2725,0);
          }
          else {
            puVar8 = (uint *)FUN_004e1658(0x31);
            FUN_004b8be4((void *)((int)this + 0x31ec),0x2725,0,(int)local_8,(int)pbVar3,0x1d,puVar8)
            ;
          }
          FUN_00432753(this_00,local_1d4);
          FUN_004e1658(0x34);
          FUN_0040edc8(param_1,local_10,local_14,(int)local_8,(byte *)(iVar7 + 0x4a),
                       (byte *)s__s___d__d_00507744);
          FUN_004a8596(this,3,(int)((byte *)(iVar7 + 0x4a) + (4 - *(int *)((int)this + 0xc0))));
        }
        if ((((local_1c == 4) || (local_1c == 5)) || (local_1c == 6)) &&
           (iVar7 = *(int *)((int)this + 0x178), iVar7 != 0)) {
          local_18 = (uint *)FUN_0042f710(iVar7,1);
          piVar6 = (int *)(local_1c * 0x10 + 0x8c + (int)this);
          iVar4 = *piVar6;
          local_20 = (byte *)(piVar6[3] + -0x15 + piVar6[1]);
          FUN_00431fa7(this_00,iVar7);
          FUN_004e1658(0x3d);
          FUN_004e2172((int)param_1,(uint *)(iVar4 + 8),local_20,local_10,(undefined4 *)local_14,
                       (byte *)s__gfxgood__d_1___s___d_0050772c);
          puVar8 = local_18;
          piVar6 = (int *)CRect::CRect(local_bc,iVar4 + 8,(int)local_20,0x28,0x10);
          FUN_004b8b04((void *)((int)this + 0x308),piVar6,(char *)puVar8);
        }
        if (local_1c == 5) {
          iVar7 = *(int *)((int)this + 0xdc);
          iVar4 = *(int *)((int)this + 0xe0);
          local_18 = (uint *)(iVar7 + 10);
          FUN_004e1658(0x3e);
          FUN_0040edc8(param_1,local_10,local_14,(int)local_18,(byte *)(iVar4 + 0x12),&DAT_00507728)
          ;
          FUN_004e1658(0x3f);
          FUN_0040edc8(param_1,local_10,local_14,iVar7 + 0x7c,(byte *)(iVar4 + 0x12),&DAT_00507728);
          local_8 = (uint *)0x0;
          param_2 = (byte *)(iVar4 + 0x24);
          local_20 = (byte *)(iVar4 + 0x1e);
          if (*(int *)(local_24 + 0x60) != 0) {
            local_c = (byte *)(local_24 + 0x6c);
            do {
              iVar7 = *(int *)(local_c + -8);
              if (iVar7 < 0x38) {
                iVar4 = *(int *)(this_00 + 0x14);
                if (((iVar4 == 7) || (iVar4 == 8)) || ((iVar4 == 9 || (iVar4 == 1)))) {
                  cVar2 = '\x01';
                }
                else {
                  cVar2 = '\0';
                }
                FUN_00431a83(this_00,iVar7,cVar2);
                if (*local_c == 0) {
                  local_20 = local_20 + 0x12;
                }
                else {
                  pcVar14 = s__gfxgood__d_1____1f_00507710;
                  puVar9 = (undefined4 *)FUN_004e1e29();
                  FUN_004e2172((int)param_1,local_18,param_2,local_10,puVar9,(byte *)pcVar14);
                  pcVar14 = (char *)FUN_0042f710(iVar7,1);
                  piVar6 = (int *)CRect::CRect(local_cc,(int)local_18,(int)param_2,100,0xc);
                  FUN_004b8b04((void *)((int)this + 0x308),piVar6,pcVar14);
                  param_2 = param_2 + 0xe;
                }
              }
              local_8 = (uint *)((int)local_8 + 1);
              local_c = local_c + 0xc;
            } while (local_8 < *(uint **)(local_24 + 0x60));
          }
          pbVar3 = local_20;
          if ((int)local_20 < (int)param_2) {
            pbVar3 = param_2;
          }
          FUN_004a8596(this,5,(int)(pbVar3 + (0xc - *(int *)((int)this + 0xe0))));
        }
        if (local_1c == 6) {
          local_20 = (byte *)0x0;
          local_18 = (uint *)(*(int *)((int)this + 0xec) + 4);
          pbVar3 = (byte *)(*(int *)((int)this + 0xf0) + 0x14);
          if (*(int *)(local_24 + 0x60) == 0) goto LAB_004a75d0;
          local_c = (byte *)(local_24 + 0x6c);
          do {
            iVar7 = *(int *)(local_c + -8);
            if (iVar7 < 0x38) {
              iVar4 = *(int *)(this_00 + 0x14);
              if (((iVar4 == 7) || (iVar4 == 8)) || ((iVar4 == 9 || (iVar4 == 1)))) {
                cVar2 = '\x01';
              }
              else {
                cVar2 = '\0';
              }
              FUN_00431a83(this_00,iVar7,cVar2);
              if (*local_c != 0) {
                pcVar14 = s__gfxgood__d_1____1f_00507710;
                puVar9 = (undefined4 *)FUN_004e1e29();
                FUN_004e2172((int)param_1,local_18 + 1,pbVar3,local_10,puVar9,(byte *)pcVar14);
                pcVar14 = (char *)FUN_0042f710(iVar7,1);
                piVar6 = (int *)CRect::CRect(local_ac,(int)(local_18 + 1),(int)pbVar3,100,0xc);
                FUN_004b8b04((void *)((int)this + 0x308),piVar6,pcVar14);
                pbVar3 = pbVar3 + 0xe;
              }
            }
            local_20 = local_20 + 1;
            local_c = local_c + 0xc;
          } while (local_20 < *(byte **)(local_24 + 0x60));
        }
        if (local_1c == 9) {
          iVar7 = *(int *)((int)this + 0x120);
          iVar4 = *(int *)((int)this + 0x11c);
          iVar11 = FUN_004316e0((int)this_00);
          if (iVar11 != 1) goto LAB_004a75d0;
          pbVar3 = (byte *)FUN_0042f776(*(int *)(this_00 + 0x14),1);
          FUN_0040ecf9(param_1,local_10,local_14,iVar4 + 0xc4,(byte *)(iVar7 + 0x18),pbVar3);
        }
        if (local_1c == 10) {
          local_18 = (uint *)(*(int *)((int)this + 300) + 4);
          param_2 = (byte *)(*(int *)((int)this + 0x130) + 0x12);
          pbVar3 = (byte *)0xffffffff;
          while (local_20 = (byte *)FUN_0041cb32(DAT_00511728,(int)this_00,(int)pbVar3),
                pvVar1 = DAT_00511728, local_20 != (byte *)0xffffffff) {
            iVar7 = (int)local_20 * 0x18;
            FUN_0042f710(*(int *)((int)DAT_00511728 + iVar7 + 0x40),
                         *(uint *)((int)DAT_00511728 + iVar7 + 0x44));
            FUN_004e1658(0x5b);
            FUN_0042f710(*(int *)((int)pvVar1 + iVar7 + 0x48),*(uint *)((int)pvVar1 + iVar7 + 0x4c))
            ;
            FUN_004e1658(0x5a);
            FUN_0040edc8(param_1,local_10,local_14,(int)local_18,param_2,
                         (byte *)s__s__d__s____s__d__s_005076fc);
            param_2 = param_2 + 0xc;
            pbVar3 = local_20;
          }
        }
      }
LAB_004a75d0:
      local_1c = local_1c + 1;
    } while (local_1c < 0xb);
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
| duration | 84396ms   |
