## ok

true

## data.evidence_id

ev_d215350f569c7f83aa4692ff2f1645c451fd65ddd58172ab11fa57c06f52de1c

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
| procedure | 0x46D53A |

## data.raw_result.value


void __fastcall FUN_0046d53a(void *param_1)

{
  int iVar1;
  bool bVar2;
  char cVar3;
  byte bVar4;
  undefined1 uVar5;
  int *piVar6;
  undefined4 uVar7;
  int iVar8;
  uint uVar9;
  char *this;
  undefined4 *puVar10;
  void *pvVar11;
  undefined3 extraout_var;
  short *psVar13;
  int **ppiVar14;
  undefined3 extraout_var_00;
  undefined3 extraout_var_01;
  char *pcVar15;
  int **ppiVar16;
  void *local_18;
  int *local_14;
  int *local_10;
  void *local_c;
  char *local_8;
  int iVar12;
  
  local_c = (void *)FUN_0041c61e(DAT_00511728,*(int *)((int)param_1 + 0xb44));
  piVar6 = (int *)FUN_0041c7f1(local_c);
  local_14 = piVar6;
  local_10 = (int *)FUN_0041c81f(local_c);
  if ((piVar6 == local_10) || (piVar6 == (int *)0x0)) {
    *(undefined4 *)((int)param_1 + 0x368) = 1;
    goto LAB_0046e01f;
  }
  uVar7 = FUN_0041c9dd(piVar6);
  if ((char)uVar7 == '\0') {
    pcVar15 = (char *)0x0;
  }
  else {
    pcVar15 = (char *)(*piVar6 * 0x7e0 + DAT_00510bd0);
  }
  local_8 = pcVar15;
  uVar7 = FUN_0041c9dd(local_10);
  pvVar11 = local_c;
  if ((char)uVar7 == '\0') {
    iVar8 = 0;
  }
  else {
    iVar8 = *local_10 * 0x7e0 + DAT_00510bd0;
  }
  if ((((pcVar15 == (char *)0x0) || (iVar8 == 0)) || (pcVar15[2000] != '\0')) ||
     (((*(char *)(iVar8 + 2000) != '\0' || (*(int *)(pcVar15 + 0x2c) != 3)) ||
      (*(int *)(iVar8 + 0x2c) != 3)))) {
    *(undefined4 *)((int)param_1 + 0x36c) = 3;
    *(undefined4 *)((int)param_1 + 0x374) = 2;
    goto LAB_0046d878;
  }
  if (((char)local_14[2] == '\0') && ((char)local_10[2] == '\0')) {
    uVar7 = FUN_0042c70a((int)param_1);
    if ((((char)uVar7 != '\0') &&
        (uVar9 = FUN_0044bcf3((void *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0),
                              *(int *)((int)param_1 + 4)), (char)uVar9 != '\0')) &&
       (((iVar8 = FUN_0046733f((int)param_1), iVar8 != 0 ||
         (iVar8 = FUN_00467617((int)param_1), iVar8 != 0)) &&
        (uVar7 = FUN_0046e1be(param_1,(int)pcVar15), (char)uVar7 != '\0')))) {
      return;
    }
    iVar8 = *(int *)((int)param_1 + 0xacc);
    if (iVar8 != 0) {
      if (iVar8 == 2) {
        uVar7 = FUN_0046e3a1(param_1,pcVar15);
        if ((char)uVar7 != '\0') {
          return;
        }
      }
      else if (iVar8 == 4) {
        uVar9 = FUN_0042ccc4((int)param_1);
        if ((char)uVar9 == '\0') {
          uVar7 = FUN_0046794b(param_1,*(int *)((int)param_1 + 0xad4));
          if ((char)uVar7 != '\0') {
            *(undefined4 *)((int)param_1 + 0xa68) = 5;
            *(int *)((int)param_1 + 0xa7c) = *local_14;
            *(int *)((int)param_1 + 0xa80) = local_14[1];
            goto LAB_0046de45;
          }
          uVar7 = FUN_00467c0e(param_1,*(int *)((int)param_1 + 0xad4));
          if ((char)uVar7 != '\0') {
            uVar7 = FUN_0042c70a((int)param_1);
            pvVar11 = local_c;
            if (((char)uVar7 == '\0') ||
               (uVar9 = FUN_0044bcf3((void *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0)
                                     ,*(int *)((int)param_1 + 4)), pvVar11 = local_c,
               (char)uVar9 == '\0')) goto LAB_0046d878;
            piVar6 = (int *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0);
            bVar2 = FUN_0044b660((int)piVar6);
            pvVar11 = local_c;
            if ((bVar2) ||
               (bVar2 = FUN_0044b9ab(piVar6,*(int *)((int)param_1 + 0xad4)), pvVar11 = local_c,
               !bVar2)) goto LAB_0046d878;
            local_14 = (int *)0x0;
            FUN_004376cf(piVar6,(short *)&local_14,0);
            ppiVar16 = &local_14;
            puVar10 = (undefined4 *)FUN_004411ca((char *)piVar6);
            uVar7 = FUN_0045c59d(param_1,puVar10,(short *)ppiVar16);
            cVar3 = (char)uVar7;
joined_r0x0046dc82:
            if (cVar3 != '\0') {
              FUN_0044b7b5(piVar6,*(int *)((int)param_1 + 0xad4),1,*(int *)((int)param_1 + 8));
              *(undefined4 *)((int)param_1 + 0xa7c) = *(undefined4 *)((int)param_1 + 0xb48);
              *(undefined4 *)((int)param_1 + 0xa68) = 6;
              *(undefined4 *)((int)param_1 + 0xa80) = *(undefined4 *)((int)param_1 + 0xb4c);
              return;
            }
            goto LAB_0046de54;
          }
        }
        else if (*(int *)((int)param_1 + 0xa68) == 5) {
          this = FUN_0042d7d3((int)param_1);
          if ((this == pcVar15) &&
             (uVar7 = FUN_004316f3(this,*(int *)((int)param_1 + 0xad4),'\0'), (char)uVar7 != '\0'))
          {
LAB_0046d6c7:
            FUN_004422dc(param_1);
LAB_0046d6d0:
            FUN_0045c17b(param_1,0x17,6);
            *(undefined4 *)((int)param_1 + 0x36c) = 1;
            return;
          }
        }
        else if (*(int *)((int)param_1 + 0xa68) == 6) {
          pvVar11 = (void *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0);
          bVar2 = FUN_0044b9ab(pvVar11,*(int *)((int)param_1 + 0xad4));
          if (((!bVar2) || (bVar2 = FUN_0044b660((int)pvVar11), bVar2)) ||
             (uVar7 = FUN_0041ca4b(local_10,*(int *)((int)param_1 + 0xad4)), (char)uVar7 == '\0'))
          goto LAB_0046d735;
LAB_0046da6f:
          *(undefined4 *)((int)param_1 + 0xa7c) = *(undefined4 *)((int)param_1 + 0xb48);
          *(undefined4 *)((int)param_1 + 0xa68) = 6;
          *(undefined4 *)((int)param_1 + 0xa80) = *(undefined4 *)((int)param_1 + 0xb4c);
          *(undefined4 *)((int)param_1 + 0x368) = 0x15;
LAB_0046e01f:
          *(undefined4 *)((int)param_1 + 0x36c) = 0;
          return;
        }
        FUN_00441b83((int)param_1);
      }
    }
    FUN_0042cf27((int)param_1);
    if (*(int *)((int)param_1 + 0xad4) != 0) {
      FUN_00444c6e(param_1);
      return;
    }
    FUN_0042cea6((int)param_1);
    uVar7 = FUN_0042c70a((int)param_1);
    if (((((char)uVar7 == '\0') || (*(char *)((int)param_1 + 0xb51) == '\0')) ||
        (uVar9 = FUN_0044bcf3((void *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0),
                              *(int *)((int)param_1 + 4)), (char)uVar9 == '\0')) ||
       (pvVar11 = (void *)FUN_0046733f((int)param_1), pvVar11 == (void *)0x0)) {
      iVar8 = FUN_00467617((int)param_1);
      if (iVar8 == 0) {
        uVar7 = FUN_0042c70a((int)param_1);
        if ((((char)uVar7 != '\0') &&
            (uVar9 = FUN_0044bcf3((void *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0),
                                  *(int *)((int)param_1 + 4)), (char)uVar9 != '\0')) &&
           (pvVar11 = (void *)FUN_0046733f((int)param_1), pvVar11 != (void *)0x0))
        goto LAB_0046d953;
        goto LAB_0046defa;
      }
      goto LAB_0046d909;
    }
    goto LAB_0046d953;
  }
  uVar9 = FUN_0041c8a6(local_c,*(int *)((int)param_1 + 0x10));
  if ((char)uVar9 == '\0') {
    *(undefined4 *)((int)pvVar11 + 0xc) = 0;
    *(undefined4 *)((int)pvVar11 + 0x10) = 0;
    *(undefined4 *)((int)param_1 + 0x36c) = 3;
    *(undefined4 *)((int)param_1 + 0x374) = 0xf;
    goto LAB_0046d878;
  }
  iVar8 = (int)DAT_00511728 + *(int *)((int)pvVar11 + 4) * 0x18 + 0x38;
  uVar7 = FUN_0042c70a((int)param_1);
  if (((char)uVar7 == '\0') ||
     (uVar9 = FUN_0044bcf3((void *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0),
                           *(int *)((int)param_1 + 4)), pvVar11 = local_c, (char)uVar9 == '\0')) {
    *(undefined4 *)((int)param_1 + 0x36c) = 3;
    *(undefined4 *)((int)param_1 + 0x374) = 0xe;
    *(undefined4 *)((int)local_c + 0xc) = 0;
    *(undefined4 *)((int)local_c + 0x10) = 0;
    pvVar11 = local_c;
    goto LAB_0046d878;
  }
  iVar12 = *(int *)((int)param_1 + 0xacc);
  if ((char)local_10[2] == '\0') {
    if (iVar12 == 0) {
      local_18 = (void *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0);
      local_14 = *(int **)((int)local_c + 0xc);
      if (*(int **)(iVar8 + 0xc) <= local_14) {
        if (*(uint *)(iVar8 + 0x14) <= *(uint *)((int)local_c + 0x10)) {
          *(undefined4 *)((int)local_c + 0xc) = 0;
          *(undefined4 *)((int)local_c + 0x10) = 0;
          uVar5 = FUN_0044b634(local_18,*(int *)(iVar8 + 8));
          if (*(uint *)(iVar8 + 0xc) <= CONCAT31(extraout_var_00,uVar5)) {
            return;
          }
          goto LAB_0046d878;
        }
        uVar7 = FUN_0046e1be(param_1,(int)local_8);
        if ((char)uVar7 != '\0') {
          return;
        }
        bVar2 = FUN_0044b660((int)local_18);
        if (bVar2) {
          *(undefined4 *)((int)local_c + 0xc) = 0;
          *(undefined4 *)((int)local_c + 0x10) = 0;
          return;
        }
        iVar8 = *(int *)(iVar8 + 0x10);
        pcVar15 = local_8;
        goto LAB_0046d909;
      }
      uVar5 = FUN_0044b634(local_18,*(int *)(iVar8 + 8));
      if ((uint)(CONCAT31(extraout_var_01,uVar5) + (int)local_14) < *(uint *)(iVar8 + 0xc)) {
        *(undefined4 *)((int)param_1 + 0xad0) = *(undefined4 *)(iVar8 + 8);
        *(undefined4 *)((int)param_1 + 0x36c) = 3;
        *(undefined4 *)((int)param_1 + 0x374) = 3;
        goto LAB_0046d878;
      }
      uVar7 = FUN_0046e1be(param_1,(int)local_8);
      if ((char)uVar7 != '\0') {
        return;
      }
      pvVar11 = *(void **)(iVar8 + 8);
      goto LAB_0046d953;
    }
    if (iVar12 == 2) {
      uVar7 = FUN_0046e3a1(param_1,local_8);
      if ((char)uVar7 != '\0') {
        return;
      }
      goto LAB_0046defa;
    }
    if (iVar12 != 4) goto LAB_0046defa;
    uVar9 = FUN_0042ccc4((int)param_1);
    if ((char)uVar9 != '\0') {
      if (*(int *)((int)param_1 + 0xa68) == 5) {
        pcVar15 = FUN_0042d7d3((int)param_1);
        if ((pcVar15 == local_8) &&
           (uVar7 = FUN_004316f3(pcVar15,*(int *)((int)param_1 + 0xad4),'\0'), (char)uVar7 != '\0'))
        {
          FUN_004422dc(param_1);
          FUN_0045c17b(param_1,0x17,6);
          *(undefined4 *)((int)param_1 + 0x36c) = 1;
          *(int *)((int)local_c + 0xc) = *(int *)((int)local_c + 0xc) + 1;
          return;
        }
      }
      else if (*(int *)((int)param_1 + 0xa68) == 6) {
        local_18 = (void *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0);
        bVar2 = FUN_0044b9ab(local_18,*(int *)((int)param_1 + 0xad4));
        if (((!bVar2) || (bVar2 = FUN_0044b660((int)local_18), bVar2)) ||
           (*(int *)(iVar8 + 0x10) != *(int *)((int)param_1 + 0xad4))) {
LAB_0046d735:
          *(undefined4 *)((int)param_1 + 0x374) = 0;
          *(undefined4 *)((int)param_1 + 0x36c) = 3;
          return;
        }
        *(undefined4 *)((int)param_1 + 0x36c) = 0;
        *(undefined4 *)((int)param_1 + 0x368) = 0x15;
LAB_0046ddc6:
        *(undefined4 *)((int)param_1 + 0xa7c) = *(undefined4 *)((int)param_1 + 0xb48);
        *(undefined4 *)((int)param_1 + 0xa80) = *(undefined4 *)((int)param_1 + 0xb4c);
        *(undefined4 *)((int)param_1 + 0xa68) = 6;
        *(int *)((int)local_c + 0x10) = *(int *)((int)local_c + 0x10) + 1;
        piVar6 = (int *)(DAT_00510bc4 + 0x4a30 +
                        (*(int *)((int)param_1 + 0x10) * 0x12a0 + *(int *)(local_8 + 0xc)) * 4);
        *piVar6 = *piVar6 + 1;
        return;
      }
      goto LAB_0046defa;
    }
    if (*(int *)((int)param_1 + 0xad4) != *(int *)(iVar8 + 8)) {
      if (*(int *)((int)param_1 + 0xad4) != *(int *)(iVar8 + 0x10)) goto LAB_0046defa;
      pcVar15 = (char *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0);
      bVar2 = FUN_0044b660((int)pcVar15);
      if ((bVar2) || (bVar2 = FUN_0044b9ab(pcVar15,*(int *)((int)param_1 + 0xad4)), !bVar2))
      goto LAB_0046defa;
      local_14 = (int *)0x0;
      FUN_004376cf(pcVar15,(short *)&local_14,0);
      ppiVar16 = &local_14;
      puVar10 = (undefined4 *)FUN_004411ca(pcVar15);
      uVar7 = FUN_0045c59d(param_1,puVar10,(short *)ppiVar16);
      if ((char)uVar7 != '\0') {
        FUN_0044b7b5(pcVar15,*(int *)((int)param_1 + 0xad4),1,*(int *)((int)param_1 + 8));
        goto LAB_0046ddc6;
      }
      goto LAB_0046de54;
    }
LAB_0046de1c:
    *(undefined4 *)((int)param_1 + 0xa68) = 5;
    *(int *)((int)param_1 + 0xa7c) = *local_14;
    *(int *)((int)param_1 + 0xa80) = local_14[1];
    pcVar15 = local_8;
LAB_0046de45:
    uVar7 = FUN_0045c59d(param_1,(undefined4 *)(pcVar15 + 0x1c),(short *)(pcVar15 + 0x24));
    if ((char)uVar7 != '\0') {
      *(undefined4 *)((int)param_1 + 0xacc) = 4;
      return;
    }
LAB_0046de54:
    *(undefined4 *)((int)param_1 + 0x36c) = 3;
    *(undefined4 *)((int)param_1 + 0x374) = 1;
    return;
  }
  if (iVar12 != 0) {
    if (iVar12 == 2) {
      uVar7 = FUN_0046e3a1(param_1,local_8);
      cVar3 = (char)uVar7;
LAB_0046dc10:
      if (cVar3 != '\0') {
        return;
      }
    }
    else if (iVar12 == 4) {
      uVar9 = FUN_0042ccc4((int)param_1);
      if ((char)uVar9 == '\0') {
        iVar12 = *(int *)((int)param_1 + 0xad4);
        iVar1 = *(int *)(iVar8 + 8);
        if (((iVar12 == iVar1) ||
            (((((iVar12 == 0x10 || (iVar12 == 0x12)) || (iVar12 == 0x13)) ||
              (((iVar12 == 0x15 || (iVar12 == 0x38)) || ((iVar12 == 0x16 || (iVar12 == 0x17)))))) &&
             (iVar1 == 0x10)))) || (((iVar12 == 0x11 || (iVar12 == 0x14)) && (iVar1 == 0x11)))) {
          local_14 = (int *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0);
          bVar2 = FUN_0044b660((int)local_14);
          if ((!bVar2) && (bVar2 = FUN_0044b9ab(local_14,*(int *)((int)param_1 + 0xad4)), bVar2)) {
            local_10 = (int *)0x0;
            FUN_004376cf(local_14,(short *)&local_10,0);
            ppiVar16 = &local_10;
            puVar10 = (undefined4 *)FUN_004411ca((char *)local_14);
            uVar7 = FUN_0045c59d(param_1,puVar10,(short *)ppiVar16);
            cVar3 = (char)uVar7;
            piVar6 = local_14;
            goto joined_r0x0046dc82;
          }
        }
        else {
          uVar7 = FUN_004316f3(local_8,iVar12,'\0');
          if ((char)uVar7 != '\0') goto LAB_0046de1c;
          local_10 = (int *)0x0;
          local_14 = (int *)0x0;
          bVar2 = FUN_0045d14f(param_1,&local_10,(short *)&local_14);
          if (bVar2) {
            FUN_0042d008(param_1,&local_10,&local_14);
            ppiVar16 = &local_14;
            ppiVar14 = &local_10;
            goto LAB_0046dc08;
          }
        }
      }
      else {
        iVar12 = *(int *)((int)param_1 + 0xa68);
        if (iVar12 == 1) {
          iVar12 = *(int *)((int)param_1 + 0xad4);
          psVar13 = (short *)FUN_0042cfce((int)param_1);
          bVar2 = FUN_004619f8(iVar12,psVar13);
          if (bVar2) goto LAB_0046d6d0;
          local_14 = (int *)0x0;
          local_10 = (int *)0x0;
          bVar2 = FUN_0045d14f(param_1,&local_14,(short *)&local_10);
          if (bVar2) {
            FUN_0042d008(param_1,&local_14,&local_10);
            ppiVar16 = &local_10;
            ppiVar14 = &local_14;
LAB_0046dc08:
            uVar7 = FUN_0045c23e(param_1,ppiVar14,(short *)ppiVar16);
            cVar3 = (char)uVar7;
            goto LAB_0046dc10;
          }
        }
        else if (iVar12 == 5) {
          pcVar15 = FUN_0042d7d3((int)param_1);
          if ((pcVar15 == local_8) &&
             (uVar7 = FUN_004316f3(pcVar15,*(int *)((int)param_1 + 0xad4),'\0'), (char)uVar7 != '\0'
             )) goto LAB_0046d6c7;
        }
        else if (iVar12 == 6) {
          local_14 = (int *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0);
          bVar2 = FUN_0044b9ab(local_14,*(int *)((int)param_1 + 0xad4));
          if (((!bVar2) || (bVar2 = FUN_0044b660((int)local_14), bVar2)) ||
             (*(int *)(iVar8 + 8) != *(int *)((int)param_1 + 0xad4))) goto LAB_0046d735;
          goto LAB_0046da6f;
        }
      }
    }
  }
  bVar4 = FUN_0046e52e(param_1,local_8,iVar8,(int *)&local_18);
  iVar12 = CONCAT31(extraout_var,bVar4);
  pvVar11 = local_c;
  if (iVar12 == 0) {
    *(undefined4 *)((int)param_1 + 0xad0) = *(undefined4 *)(iVar8 + 8);
    *(undefined4 *)((int)param_1 + 0x36c) = 3;
    *(undefined4 *)((int)param_1 + 0x374) = 3;
    *(undefined4 *)((int)local_c + 0xc) = 0;
    *(undefined4 *)((int)local_c + 0x10) = 0;
  }
  else {
    if (iVar12 == 1) {
      uVar7 = FUN_0046e1be(param_1,(int)local_8);
      if ((char)uVar7 != '\0') {
        return;
      }
      iVar8 = *(int *)(iVar8 + 8);
      pcVar15 = local_8;
LAB_0046d909:
      FUN_0046e02b(param_1,pcVar15,iVar8);
      return;
    }
    if (iVar12 != 2) {
      if (iVar12 != 3) {
LAB_0046defa:
        FUN_0041c84f(local_c);
        *(undefined4 *)((int)param_1 + 0x36c) = 3;
        *(undefined4 *)((int)param_1 + 0x374) = 2;
        return;
      }
      uVar7 = FUN_0046e1be(param_1,(int)local_8);
      pvVar11 = local_18;
      if ((char)uVar7 != '\0') {
        return;
      }
LAB_0046d953:
      FUN_0046e117(param_1,(int)pvVar11);
      return;
    }
  }
LAB_0046d878:
  FUN_0041c84f(pvVar11);
  return;
}



## data.raw_result.limitations



## data.normalized_result


void __fastcall FUN_0046d53a(void *param_1)

{
  int iVar1;
  bool bVar2;
  char cVar3;
  byte bVar4;
  undefined1 uVar5;
  int *piVar6;
  undefined4 uVar7;
  int iVar8;
  uint uVar9;
  char *this;
  undefined4 *puVar10;
  void *pvVar11;
  undefined3 extraout_var;
  short *psVar13;
  int **ppiVar14;
  undefined3 extraout_var_00;
  undefined3 extraout_var_01;
  char *pcVar15;
  int **ppiVar16;
  void *local_18;
  int *local_14;
  int *local_10;
  void *local_c;
  char *local_8;
  int iVar12;
  
  local_c = (void *)FUN_0041c61e(DAT_00511728,*(int *)((int)param_1 + 0xb44));
  piVar6 = (int *)FUN_0041c7f1(local_c);
  local_14 = piVar6;
  local_10 = (int *)FUN_0041c81f(local_c);
  if ((piVar6 == local_10) || (piVar6 == (int *)0x0)) {
    *(undefined4 *)((int)param_1 + 0x368) = 1;
    goto LAB_0046e01f;
  }
  uVar7 = FUN_0041c9dd(piVar6);
  if ((char)uVar7 == '\0') {
    pcVar15 = (char *)0x0;
  }
  else {
    pcVar15 = (char *)(*piVar6 * 0x7e0 + DAT_00510bd0);
  }
  local_8 = pcVar15;
  uVar7 = FUN_0041c9dd(local_10);
  pvVar11 = local_c;
  if ((char)uVar7 == '\0') {
    iVar8 = 0;
  }
  else {
    iVar8 = *local_10 * 0x7e0 + DAT_00510bd0;
  }
  if ((((pcVar15 == (char *)0x0) || (iVar8 == 0)) || (pcVar15[2000] != '\0')) ||
     (((*(char *)(iVar8 + 2000) != '\0' || (*(int *)(pcVar15 + 0x2c) != 3)) ||
      (*(int *)(iVar8 + 0x2c) != 3)))) {
    *(undefined4 *)((int)param_1 + 0x36c) = 3;
    *(undefined4 *)((int)param_1 + 0x374) = 2;
    goto LAB_0046d878;
  }
  if (((char)local_14[2] == '\0') && ((char)local_10[2] == '\0')) {
    uVar7 = FUN_0042c70a((int)param_1);
    if ((((char)uVar7 != '\0') &&
        (uVar9 = FUN_0044bcf3((void *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0),
                              *(int *)((int)param_1 + 4)), (char)uVar9 != '\0')) &&
       (((iVar8 = FUN_0046733f((int)param_1), iVar8 != 0 ||
         (iVar8 = FUN_00467617((int)param_1), iVar8 != 0)) &&
        (uVar7 = FUN_0046e1be(param_1,(int)pcVar15), (char)uVar7 != '\0')))) {
      return;
    }
    iVar8 = *(int *)((int)param_1 + 0xacc);
    if (iVar8 != 0) {
      if (iVar8 == 2) {
        uVar7 = FUN_0046e3a1(param_1,pcVar15);
        if ((char)uVar7 != '\0') {
          return;
        }
      }
      else if (iVar8 == 4) {
        uVar9 = FUN_0042ccc4((int)param_1);
        if ((char)uVar9 == '\0') {
          uVar7 = FUN_0046794b(param_1,*(int *)((int)param_1 + 0xad4));
          if ((char)uVar7 != '\0') {
            *(undefined4 *)((int)param_1 + 0xa68) = 5;
            *(int *)((int)param_1 + 0xa7c) = *local_14;
            *(int *)((int)param_1 + 0xa80) = local_14[1];
            goto LAB_0046de45;
          }
          uVar7 = FUN_00467c0e(param_1,*(int *)((int)param_1 + 0xad4));
          if ((char)uVar7 != '\0') {
            uVar7 = FUN_0042c70a((int)param_1);
            pvVar11 = local_c;
            if (((char)uVar7 == '\0') ||
               (uVar9 = FUN_0044bcf3((void *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0)
                                     ,*(int *)((int)param_1 + 4)), pvVar11 = local_c,
               (char)uVar9 == '\0')) goto LAB_0046d878;
            piVar6 = (int *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0);
            bVar2 = FUN_0044b660((int)piVar6);
            pvVar11 = local_c;
            if ((bVar2) ||
               (bVar2 = FUN_0044b9ab(piVar6,*(int *)((int)param_1 + 0xad4)), pvVar11 = local_c,
               !bVar2)) goto LAB_0046d878;
            local_14 = (int *)0x0;
            FUN_004376cf(piVar6,(short *)&local_14,0);
            ppiVar16 = &local_14;
            puVar10 = (undefined4 *)FUN_004411ca((char *)piVar6);
            uVar7 = FUN_0045c59d(param_1,puVar10,(short *)ppiVar16);
            cVar3 = (char)uVar7;
joined_r0x0046dc82:
            if (cVar3 != '\0') {
              FUN_0044b7b5(piVar6,*(int *)((int)param_1 + 0xad4),1,*(int *)((int)param_1 + 8));
              *(undefined4 *)((int)param_1 + 0xa7c) = *(undefined4 *)((int)param_1 + 0xb48);
              *(undefined4 *)((int)param_1 + 0xa68) = 6;
              *(undefined4 *)((int)param_1 + 0xa80) = *(undefined4 *)((int)param_1 + 0xb4c);
              return;
            }
            goto LAB_0046de54;
          }
        }
        else if (*(int *)((int)param_1 + 0xa68) == 5) {
          this = FUN_0042d7d3((int)param_1);
          if ((this == pcVar15) &&
             (uVar7 = FUN_004316f3(this,*(int *)((int)param_1 + 0xad4),'\0'), (char)uVar7 != '\0'))
          {
LAB_0046d6c7:
            FUN_004422dc(param_1);
LAB_0046d6d0:
            FUN_0045c17b(param_1,0x17,6);
            *(undefined4 *)((int)param_1 + 0x36c) = 1;
            return;
          }
        }
        else if (*(int *)((int)param_1 + 0xa68) == 6) {
          pvVar11 = (void *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0);
          bVar2 = FUN_0044b9ab(pvVar11,*(int *)((int)param_1 + 0xad4));
          if (((!bVar2) || (bVar2 = FUN_0044b660((int)pvVar11), bVar2)) ||
             (uVar7 = FUN_0041ca4b(local_10,*(int *)((int)param_1 + 0xad4)), (char)uVar7 == '\0'))
          goto LAB_0046d735;
LAB_0046da6f:
          *(undefined4 *)((int)param_1 + 0xa7c) = *(undefined4 *)((int)param_1 + 0xb48);
          *(undefined4 *)((int)param_1 + 0xa68) = 6;
          *(undefined4 *)((int)param_1 + 0xa80) = *(undefined4 *)((int)param_1 + 0xb4c);
          *(undefined4 *)((int)param_1 + 0x368) = 0x15;
LAB_0046e01f:
          *(undefined4 *)((int)param_1 + 0x36c) = 0;
          return;
        }
        FUN_00441b83((int)param_1);
      }
    }
    FUN_0042cf27((int)param_1);
    if (*(int *)((int)param_1 + 0xad4) != 0) {
      FUN_00444c6e(param_1);
      return;
    }
    FUN_0042cea6((int)param_1);
    uVar7 = FUN_0042c70a((int)param_1);
    if (((((char)uVar7 == '\0') || (*(char *)((int)param_1 + 0xb51) == '\0')) ||
        (uVar9 = FUN_0044bcf3((void *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0),
                              *(int *)((int)param_1 + 4)), (char)uVar9 == '\0')) ||
       (pvVar11 = (void *)FUN_0046733f((int)param_1), pvVar11 == (void *)0x0)) {
      iVar8 = FUN_00467617((int)param_1);
      if (iVar8 == 0) {
        uVar7 = FUN_0042c70a((int)param_1);
        if ((((char)uVar7 != '\0') &&
            (uVar9 = FUN_0044bcf3((void *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0),
                                  *(int *)((int)param_1 + 4)), (char)uVar9 != '\0')) &&
           (pvVar11 = (void *)FUN_0046733f((int)param_1), pvVar11 != (void *)0x0))
        goto LAB_0046d953;
        goto LAB_0046defa;
      }
      goto LAB_0046d909;
    }
    goto LAB_0046d953;
  }
  uVar9 = FUN_0041c8a6(local_c,*(int *)((int)param_1 + 0x10));
  if ((char)uVar9 == '\0') {
    *(undefined4 *)((int)pvVar11 + 0xc) = 0;
    *(undefined4 *)((int)pvVar11 + 0x10) = 0;
    *(undefined4 *)((int)param_1 + 0x36c) = 3;
    *(undefined4 *)((int)param_1 + 0x374) = 0xf;
    goto LAB_0046d878;
  }
  iVar8 = (int)DAT_00511728 + *(int *)((int)pvVar11 + 4) * 0x18 + 0x38;
  uVar7 = FUN_0042c70a((int)param_1);
  if (((char)uVar7 == '\0') ||
     (uVar9 = FUN_0044bcf3((void *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0),
                           *(int *)((int)param_1 + 4)), pvVar11 = local_c, (char)uVar9 == '\0')) {
    *(undefined4 *)((int)param_1 + 0x36c) = 3;
    *(undefined4 *)((int)param_1 + 0x374) = 0xe;
    *(undefined4 *)((int)local_c + 0xc) = 0;
    *(undefined4 *)((int)local_c + 0x10) = 0;
    pvVar11 = local_c;
    goto LAB_0046d878;
  }
  iVar12 = *(int *)((int)param_1 + 0xacc);
  if ((char)local_10[2] == '\0') {
    if (iVar12 == 0) {
      local_18 = (void *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0);
      local_14 = *(int **)((int)local_c + 0xc);
      if (*(int **)(iVar8 + 0xc) <= local_14) {
        if (*(uint *)(iVar8 + 0x14) <= *(uint *)((int)local_c + 0x10)) {
          *(undefined4 *)((int)local_c + 0xc) = 0;
          *(undefined4 *)((int)local_c + 0x10) = 0;
          uVar5 = FUN_0044b634(local_18,*(int *)(iVar8 + 8));
          if (*(uint *)(iVar8 + 0xc) <= CONCAT31(extraout_var_00,uVar5)) {
            return;
          }
          goto LAB_0046d878;
        }
        uVar7 = FUN_0046e1be(param_1,(int)local_8);
        if ((char)uVar7 != '\0') {
          return;
        }
        bVar2 = FUN_0044b660((int)local_18);
        if (bVar2) {
          *(undefined4 *)((int)local_c + 0xc) = 0;
          *(undefined4 *)((int)local_c + 0x10) = 0;
          return;
        }
        iVar8 = *(int *)(iVar8 + 0x10);
        pcVar15 = local_8;
        goto LAB_0046d909;
      }
      uVar5 = FUN_0044b634(local_18,*(int *)(iVar8 + 8));
      if ((uint)(CONCAT31(extraout_var_01,uVar5) + (int)local_14) < *(uint *)(iVar8 + 0xc)) {
        *(undefined4 *)((int)param_1 + 0xad0) = *(undefined4 *)(iVar8 + 8);
        *(undefined4 *)((int)param_1 + 0x36c) = 3;
        *(undefined4 *)((int)param_1 + 0x374) = 3;
        goto LAB_0046d878;
      }
      uVar7 = FUN_0046e1be(param_1,(int)local_8);
      if ((char)uVar7 != '\0') {
        return;
      }
      pvVar11 = *(void **)(iVar8 + 8);
      goto LAB_0046d953;
    }
    if (iVar12 == 2) {
      uVar7 = FUN_0046e3a1(param_1,local_8);
      if ((char)uVar7 != '\0') {
        return;
      }
      goto LAB_0046defa;
    }
    if (iVar12 != 4) goto LAB_0046defa;
    uVar9 = FUN_0042ccc4((int)param_1);
    if ((char)uVar9 != '\0') {
      if (*(int *)((int)param_1 + 0xa68) == 5) {
        pcVar15 = FUN_0042d7d3((int)param_1);
        if ((pcVar15 == local_8) &&
           (uVar7 = FUN_004316f3(pcVar15,*(int *)((int)param_1 + 0xad4),'\0'), (char)uVar7 != '\0'))
        {
          FUN_004422dc(param_1);
          FUN_0045c17b(param_1,0x17,6);
          *(undefined4 *)((int)param_1 + 0x36c) = 1;
          *(int *)((int)local_c + 0xc) = *(int *)((int)local_c + 0xc) + 1;
          return;
        }
      }
      else if (*(int *)((int)param_1 + 0xa68) == 6) {
        local_18 = (void *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0);
        bVar2 = FUN_0044b9ab(local_18,*(int *)((int)param_1 + 0xad4));
        if (((!bVar2) || (bVar2 = FUN_0044b660((int)local_18), bVar2)) ||
           (*(int *)(iVar8 + 0x10) != *(int *)((int)param_1 + 0xad4))) {
LAB_0046d735:
          *(undefined4 *)((int)param_1 + 0x374) = 0;
          *(undefined4 *)((int)param_1 + 0x36c) = 3;
          return;
        }
        *(undefined4 *)((int)param_1 + 0x36c) = 0;
        *(undefined4 *)((int)param_1 + 0x368) = 0x15;
LAB_0046ddc6:
        *(undefined4 *)((int)param_1 + 0xa7c) = *(undefined4 *)((int)param_1 + 0xb48);
        *(undefined4 *)((int)param_1 + 0xa80) = *(undefined4 *)((int)param_1 + 0xb4c);
        *(undefined4 *)((int)param_1 + 0xa68) = 6;
        *(int *)((int)local_c + 0x10) = *(int *)((int)local_c + 0x10) + 1;
        piVar6 = (int *)(DAT_00510bc4 + 0x4a30 +
                        (*(int *)((int)param_1 + 0x10) * 0x12a0 + *(int *)(local_8 + 0xc)) * 4);
        *piVar6 = *piVar6 + 1;
        return;
      }
      goto LAB_0046defa;
    }
    if (*(int *)((int)param_1 + 0xad4) != *(int *)(iVar8 + 8)) {
      if (*(int *)((int)param_1 + 0xad4) != *(int *)(iVar8 + 0x10)) goto LAB_0046defa;
      pcVar15 = (char *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0);
      bVar2 = FUN_0044b660((int)pcVar15);
      if ((bVar2) || (bVar2 = FUN_0044b9ab(pcVar15,*(int *)((int)param_1 + 0xad4)), !bVar2))
      goto LAB_0046defa;
      local_14 = (int *)0x0;
      FUN_004376cf(pcVar15,(short *)&local_14,0);
      ppiVar16 = &local_14;
      puVar10 = (undefined4 *)FUN_004411ca(pcVar15);
      uVar7 = FUN_0045c59d(param_1,puVar10,(short *)ppiVar16);
      if ((char)uVar7 != '\0') {
        FUN_0044b7b5(pcVar15,*(int *)((int)param_1 + 0xad4),1,*(int *)((int)param_1 + 8));
        goto LAB_0046ddc6;
      }
      goto LAB_0046de54;
    }
LAB_0046de1c:
    *(undefined4 *)((int)param_1 + 0xa68) = 5;
    *(int *)((int)param_1 + 0xa7c) = *local_14;
    *(int *)((int)param_1 + 0xa80) = local_14[1];
    pcVar15 = local_8;
LAB_0046de45:
    uVar7 = FUN_0045c59d(param_1,(undefined4 *)(pcVar15 + 0x1c),(short *)(pcVar15 + 0x24));
    if ((char)uVar7 != '\0') {
      *(undefined4 *)((int)param_1 + 0xacc) = 4;
      return;
    }
LAB_0046de54:
    *(undefined4 *)((int)param_1 + 0x36c) = 3;
    *(undefined4 *)((int)param_1 + 0x374) = 1;
    return;
  }
  if (iVar12 != 0) {
    if (iVar12 == 2) {
      uVar7 = FUN_0046e3a1(param_1,local_8);
      cVar3 = (char)uVar7;
LAB_0046dc10:
      if (cVar3 != '\0') {
        return;
      }
    }
    else if (iVar12 == 4) {
      uVar9 = FUN_0042ccc4((int)param_1);
      if ((char)uVar9 == '\0') {
        iVar12 = *(int *)((int)param_1 + 0xad4);
        iVar1 = *(int *)(iVar8 + 8);
        if (((iVar12 == iVar1) ||
            (((((iVar12 == 0x10 || (iVar12 == 0x12)) || (iVar12 == 0x13)) ||
              (((iVar12 == 0x15 || (iVar12 == 0x38)) || ((iVar12 == 0x16 || (iVar12 == 0x17)))))) &&
             (iVar1 == 0x10)))) || (((iVar12 == 0x11 || (iVar12 == 0x14)) && (iVar1 == 0x11)))) {
          local_14 = (int *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0);
          bVar2 = FUN_0044b660((int)local_14);
          if ((!bVar2) && (bVar2 = FUN_0044b9ab(local_14,*(int *)((int)param_1 + 0xad4)), bVar2)) {
            local_10 = (int *)0x0;
            FUN_004376cf(local_14,(short *)&local_10,0);
            ppiVar16 = &local_10;
            puVar10 = (undefined4 *)FUN_004411ca((char *)local_14);
            uVar7 = FUN_0045c59d(param_1,puVar10,(short *)ppiVar16);
            cVar3 = (char)uVar7;
            piVar6 = local_14;
            goto joined_r0x0046dc82;
          }
        }
        else {
          uVar7 = FUN_004316f3(local_8,iVar12,'\0');
          if ((char)uVar7 != '\0') goto LAB_0046de1c;
          local_10 = (int *)0x0;
          local_14 = (int *)0x0;
          bVar2 = FUN_0045d14f(param_1,&local_10,(short *)&local_14);
          if (bVar2) {
            FUN_0042d008(param_1,&local_10,&local_14);
            ppiVar16 = &local_14;
            ppiVar14 = &local_10;
            goto LAB_0046dc08;
          }
        }
      }
      else {
        iVar12 = *(int *)((int)param_1 + 0xa68);
        if (iVar12 == 1) {
          iVar12 = *(int *)((int)param_1 + 0xad4);
          psVar13 = (short *)FUN_0042cfce((int)param_1);
          bVar2 = FUN_004619f8(iVar12,psVar13);
          if (bVar2) goto LAB_0046d6d0;
          local_14 = (int *)0x0;
          local_10 = (int *)0x0;
          bVar2 = FUN_0045d14f(param_1,&local_14,(short *)&local_10);
          if (bVar2) {
            FUN_0042d008(param_1,&local_14,&local_10);
            ppiVar16 = &local_10;
            ppiVar14 = &local_14;
LAB_0046dc08:
            uVar7 = FUN_0045c23e(param_1,ppiVar14,(short *)ppiVar16);
            cVar3 = (char)uVar7;
            goto LAB_0046dc10;
          }
        }
        else if (iVar12 == 5) {
          pcVar15 = FUN_0042d7d3((int)param_1);
          if ((pcVar15 == local_8) &&
             (uVar7 = FUN_004316f3(pcVar15,*(int *)((int)param_1 + 0xad4),'\0'), (char)uVar7 != '\0'
             )) goto LAB_0046d6c7;
        }
        else if (iVar12 == 6) {
          local_14 = (int *)(*(int *)((int)param_1 + 0xb48) * 0x54c + DAT_00510be0);
          bVar2 = FUN_0044b9ab(local_14,*(int *)((int)param_1 + 0xad4));
          if (((!bVar2) || (bVar2 = FUN_0044b660((int)local_14), bVar2)) ||
             (*(int *)(iVar8 + 8) != *(int *)((int)param_1 + 0xad4))) goto LAB_0046d735;
          goto LAB_0046da6f;
        }
      }
    }
  }
  bVar4 = FUN_0046e52e(param_1,local_8,iVar8,(int *)&local_18);
  iVar12 = CONCAT31(extraout_var,bVar4);
  pvVar11 = local_c;
  if (iVar12 == 0) {
    *(undefined4 *)((int)param_1 + 0xad0) = *(undefined4 *)(iVar8 + 8);
    *(undefined4 *)((int)param_1 + 0x36c) = 3;
    *(undefined4 *)((int)param_1 + 0x374) = 3;
    *(undefined4 *)((int)local_c + 0xc) = 0;
    *(undefined4 *)((int)local_c + 0x10) = 0;
  }
  else {
    if (iVar12 == 1) {
      uVar7 = FUN_0046e1be(param_1,(int)local_8);
      if ((char)uVar7 != '\0') {
        return;
      }
      iVar8 = *(int *)(iVar8 + 8);
      pcVar15 = local_8;
LAB_0046d909:
      FUN_0046e02b(param_1,pcVar15,iVar8);
      return;
    }
    if (iVar12 != 2) {
      if (iVar12 != 3) {
LAB_0046defa:
        FUN_0041c84f(local_c);
        *(undefined4 *)((int)param_1 + 0x36c) = 3;
        *(undefined4 *)((int)param_1 + 0x374) = 2;
        return;
      }
      uVar7 = FUN_0046e1be(param_1,(int)local_8);
      pvVar11 = local_18;
      if ((char)uVar7 != '\0') {
        return;
      }
LAB_0046d953:
      FUN_0046e117(param_1,(int)pvVar11);
      return;
    }
  }
LAB_0046d878:
  FUN_0041c84f(pvVar11);
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
| duration | 78891ms   |
