# Final Status - Coal Production Issue

## What's Working ✓
- Game launches without crash
- Smolarz hut (job 56, logictype 57) builds
- All loader guards patched (3 guards)
- All safe goods-table loops patched (3 loops)
- logicproduction writes to global_house+8 ✓
- Tribe house init cave copies global_house+8 → tribe_house+8 ✓
- Actor+0x544 set from tribe_house+8 on worker assignment ✓
- Storehouse has coal storage (logicstock 66 150 0) ✓
- Good 66 "Węgiel" defined in goodtypes.ini and strings ✓
- Job 56 "Smolarz" assignable with correct name ✓

## Most Likely Remaining Issue: Job Script Hardcodes Good 24

**The job dispatcher (0x4E21B7) interprets bytecode scripts for each job.** The production loop calls the dispatcher with a script pointer. The script for job 56 (Smolarz) was likely copied from potter (job 24) and **hardcodes good 24 (brick)** in the bytecode instead of using the house's production list.

### Evidence:
- Job 56 dispatcher patch (0x6BD36) redirects to potter handler (0x6BDC1)
- Potter handler validates but actual production is in job script bytecode
- Job scripts are bytecode interpreted by dispatcher (0x4E21B7)
- Job 56 script likely copied from job 24 (potter) which produces good 24

## Next Step: Find and Patch Job 56 Script

### Where Job Scripts Are Stored
The dispatcher (0x4E21B7) receives a script pointer at `[ebp+0x20]`. The production loop calls it with a fixed pointer `0x1F4` (pushed at 0x4C247B). This is likely an **index into a script table** or offset in a script data section.

### Search Locations:
1. **Script table** - array of script pointers indexed by job type
   - Search for: `mov eax, [job_script_table + eax*4]` near dispatcher
   
2. **Job script data** - bytecode blobs in .data/.rdata
   - Look for opcode patterns: job 24 script likely contains good 24 (0x18)

3. **Jobtypes data** - jobtypes.ini/.cif may have script references
   - Check jobtypes.cif for script field

### Quick Search Commands:
```bash
# Find script table (array of pointers)
python -c "import pefile,re; pe=pefile.PE('CN.PLMOD.exe'); data=open('CN.PLMOD.exe','rb').read(); [print(hex(0x400000+s.VirtualAddress+h)) for s in pe.sections if b'.text' in s.Name for h in [m.start() for m in re.finditer(re.escape(b'\x8B\x04\x85'), open('CN.PLMOD.exe','rb').read()[s.PointerToRawData:s.PointerToRawData+s.SizeOfRawData])][:5]]"

# Find good 24 (0x18) in job script context
python -c "import pefile,re; pe=pefile.PE('CN.PLMOD.exe'); data=open('CN.PLMOD.exe','rb').read(); [print(hex(h)) for h in [m.start() for m in re.finditer(re.escape(b'\x18'), data)] if 0x100000 < h < 0x200000][:20]"
```

## Alternative: Patch Potter Handler to Use House Production List

If job scripts are too complex, patch the potter handler (0x46E1BE) to:
1. Read the house's production list from global_house+0x488
2. Use the first good in the list instead of hardcoded value

This would make Smolarz use whatever `logicproduction` defines in houses.ini.

## Immediate Test
Before deep script analysis, verify: **does the Smolarz hut show "Węgiel" in its building info panel?**
- If YES: panel reads production list correctly, issue is in production execution
- If NO: panel doesn't read production list, issue is in panel code

The user said "W UI jest pokazane, że budynek pobiera surowce (drewno), ale nic nie produkuje" - UI shows input consumption but no output. This suggests the panel reads the production list (knows it needs wood) but production execution fails.

**This confirms the job script / production execution is the issue, not the data loading.**