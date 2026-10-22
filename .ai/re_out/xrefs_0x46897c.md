## ok

true

## data.evidence_id

ev_6b6848e56fba8e53c8149b2592f4518ae2512c7ca02623d988439957d19ee829

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

xrefs

## data.parameters

| Key     | Value    |
|---------|----------|
| address | 0x46897c |

## data.raw_result

0x467edf

## data.normalized_result

0x467edf

## data.confidence

observed

## data.authority

shipped-artifact

## data.environment

null

## data.limitations

The session serves operations only after Ghidra reports default auto-analysis complete; incomplete analysis does not expose partial results.,The imported Program and temporary project are ephemeral and deleted on close. Annotation operations edit session database metadata; original executable bytes are never written.,Cancelling an active Ghidra request terminates its ephemeral database and discards session annotations. The selected target remains open; the next provider query imports the original artifact again.,Default-space addresses use lowercase 0x-prefixed hexadecimal; other address spaces use <percent-encoded-space>:0x<hex>.,The direct address list projects exact Ghidra references to one address but does not expose their kinds; procedure_references and analyze_function preserve available kind metadata.,Synthetic Ghidra entry-point references without actionable memory sources are omitted.,Windows Ghidra P0 accepts approved native x86 and x86-64 PE applications and DLLs; managed, hostile, sensitive, and mutable-path targets are unsupported.,The Windows bridge uses authenticated IPv4 loopback because Node path-based IPC does not expose Java AF_UNIX sockets; the endpoint file contains no bearer token.,Windows sessions require the matching packaged Windows x64 native addon, local NTFS targets and runtimes, and Windows 10 or later. Native handles enforce path admission, private DACLs, and Job Object ownership automatically.

## data.locations



## data.evidence_links



## meta

| Key      | Value   |
|----------|---------|
| command  | xrefs   |
| duration | 80044ms |
