#!/usr/bin/env python3
"""
WiFi Audit Kit v4.0 - Production-ready engagement scaffold.

Generates phase-oriented directory tree, actionable checklists (checkbox style),
updated reference manuals, and a professional fillable spreadsheet
(WIFI_AUDIT_TRACKER.xlsx) for WPA2 handshake capture (aircrack-ng) followed by
hashcat cracking with custom rules.

Run:
  python3 wifi_audit_kit.py --name "ClientX-WiFi-Audit-2026-07-17"
  python3 wifi_audit_kit.py --name "Internal-v2" --force
"""

from __future__ import annotations
import argparse
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from textwrap import dedent
import os

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

APP_VERSION = "4.0 (Phase Checklists + Spreadsheet + Hashcat Workflow)"
AUTHOR = "Kalistamp"
LOG_OK = " [+] "
LOG_WARN = " [!] "
LOG_SUB = "   |-- "

@dataclass
class Phase:
    num: int
    name: str
    children: list[str]

DIR_STRUCTURE: list[Phase] = [
    Phase(0, "00_Engagement", ["checklists"]),
    Phase(1, "01_Preparation", ["checklists"]),
    Phase(2, "02_Passive_Recon", ["checklists"]),
    Phase(3, "03_Active_Capture", ["checklists", "sharkcaps/main"]),
    Phase(4, "04_Handshake_Verification", ["checklists"]),
    Phase(5, "05_Cracking_Hashcat", ["checklists", "sessions", "rules"]),
    Phase(6, "06_Wordlist_Management", ["checklists", "combo"]),
    Phase(7, "07_Supplemental_Attacks", ["checklists"]),
    Phase(8, "08_Reporting", ["checklists"]),
]

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="WiFi Audit Kit v4.0")
    p.add_argument("--name", dest="name", default=None,
                   help="Engagement folder name (recommended for automation).")
    p.add_argument("--force", action="store_true",
                   help="Recreate directory if it exists (destructive).")
    p.add_argument("--no-spreadsheet", action="store_true",
                   help="Skip .xlsx generation even if openpyxl is available.")
    return p.parse_args()

def resolve_name(cli_name: str | None) -> Path:
    if cli_name:
        return Path(cli_name.strip())
    default = datetime.now().strftime("%Y-%m-%d_WIFI_AUDIT")
    print(f"{LOG_WARN}No --name supplied. Using default: {default}")
    print(f"{LOG_WARN}For scripted/CI use always pass --name.")
    return Path(default)

def create_structure(base: Path, force: bool) -> None:
    if base.exists():
        if force:
            print(f"{LOG_WARN}--force: removing existing {base}")
            import shutil
            shutil.rmtree(base)
        else:
            print(f"{LOG_WARN}Directory '{base}' already exists. Use --force to overwrite.")
            sys.exit(1)
    base.mkdir(parents=True, exist_ok=False)
    print(f"{LOG_OK}Created engagement root: {base}")
    for phase in DIR_STRUCTURE:
        pdir = base / phase.name
        pdir.mkdir()
        for child in phase.children:
            (pdir / child).mkdir(parents=True, exist_ok=True)
            print(f"{LOG_SUB}Created: {pdir / child}")

def get_disclaimer() -> str:
    return dedent("""\
        DISCLAIMER: This kit is for authorized security testing and educational purposes only.
        Use exclusively on networks you own or have explicit written permission to test.
        Unauthorized access is illegal. The authors assume no liability for misuse.
    """).strip()

def get_engagement_info() -> str:
    return dedent(f"""\
        =====================================================
        ENGAGEMENT INFO & MASTER CHECKLIST
        WiFi Audit Kit v{APP_VERSION}
        =====================================================

        {get_disclaimer()}

        Engagement Metadata (fill immediately):
        - Client / Scope:
        - Auditor:
        - Date Range:
        - Adapter Model / Driver / Regulatory Domain:
        - Tools Versions (aircrack-ng, hashcat, hcxtools):

        High-Level Workflow (do not skip phases):
        1. Preparation & Safety (01)
        2. Passive Recon & Target Selection (02)
        3. Active Capture / Deauth (03) - goal: WPA2 4-way or PMKID
        4. Handshake / PMKID Verification (04)
        5. Conversion + Hashcat Cracking with custom rules (05)
        6. Wordlist / Rule Hygiene (06)
        7. Supplemental (Evil Twin / Captive Portal) only if in scope (07)
        8. Reporting (08)

        Status Legend: [ ] = todo   [x] = done   [!] = blocked / note

        Master Checklist:
        [ ] All legal authorization documented
        [ ] Adapter verified in monitor mode + power_save off
        [ ] Regulatory domain set correctly (iw reg set XX)
        [ ] airmon-ng check kill executed
        [ ] Target BSSID/Channel/PWR confirmed; PMF status verified via Wireshark
        [ ] Clean pcap with handshake or PMKID captured
        [ ] pcap converted to .hc22000 (preferred) or handled for hashcat
        [ ] hashcat session started with custom rule (oneruletorulethemall.rule or equivalent)
        [ ] Cracked key (or exhaustive attempt) logged with rule/wordlist used
        [ ] Spreadsheet (WIFI_AUDIT_TRACKER.xlsx) updated at each phase
    """).strip()

def get_preparation_checklist() -> str:
    return dedent("""\
        =====================================================
        01_PREPARATION CHECKLIST
        =====================================================

        [ ] sudo apt update && sudo apt install aircrack-ng hashcat hcxtools tshark wireshark
        [ ] Identify wireless interface: iw dev
        [ ] Kill interfering processes: sudo airmon-ng check kill
        [ ] Start monitor mode: sudo airmon-ng start wlan0  (note new interface, usually wlan0mon)
        [ ] Disable power save: sudo iw dev wlan0mon set power_save off
        [ ] Verify: iw dev wlan0mon get power_save   (should show "off")
        [ ] Set regulatory domain (unlock channels/power): sudo iw reg set US   (replace with your country code)
        [ ] Confirm adapter supports injection/monitor: sudo aireplay-ng --test wlan0mon
        [ ] Document adapter chipset/driver/firmware in ENGAGEMENT_INFO.txt
        [ ] Test Wireshark capture on wlan0mon (filter: wlan.fc.type_subtype == 0x08)
    """).strip()

def get_recon_checklist() -> str:
    return dedent("""\
        =====================================================
        02_PASSIVE_RECON CHECKLIST
        =====================================================

        [ ] Broad scan (new terminal): sudo airodump-ng -a wlan0mon
        [ ] Note: "<length: 0>" entries are usually client probe requests, not hidden APs
        [ ] Identify high-value targets (strong PWR, clients present, interesting ESSID)
        [ ] For each target record: BSSID, ESSID, Channel, PWR (dBm), #Clients, Security
        [ ] Check PMF status BEFORE any deauth attempt:
            - Open Wireshark on wlan0mon
            - Filter: wlan.fc.type_subtype == 0x08 && wlan.bssid == AA:BB:CC:DD:EE:FF
            - Inspect Beacon → RSN Information → RSN Capabilities
            - "Management Frame Protection Required = 1" → PMF mandatory (classic deauth usually fails)
        [ ] Update WIFI_AUDIT_TRACKER.xlsx Targets sheet with PMF status
        [ ] Prioritize targets with PMF disabled or optional for highest success probability
    """).strip()

def get_capture_checklist() -> str:
    return dedent("""\
        =====================================================
        03_ACTIVE_CAPTURE CHECKLIST (aircrack-ng)
        =====================================================

        Goal: Obtain WPA2 4-way handshake or PMKID in clean pcap.

        [ ] Lock dedicated airodump-ng instance to target (new terminal):
            sudo airodump-ng -c <channel> --bssid <BSSID> -w capture_prefix wlan0mon
        [ ] Confirm target has associated clients (look for station MACs)
        [ ] Prefer targeted deauth over broadcast:
            sudo aireplay-ng -0 3 -a <AP_BSSID> -c <CLIENT_MAC> wlan0mon
        [ ] Watch airodump-ng output for "WPA handshake: <BSSID>" or PMKID indicator
        [ ] If no handshake after 10-15s, repeat deauth (max 2-3 bursts of 3 packets)
        [ ] Signal strength guidance: PWR better than -60 dBm strongly preferred
        [ ] If PMF required, do not waste time on deauth; switch to passive or note limitation
        [ ] Stop capture cleanly (Ctrl-C). Verify file size >0 and contains EAPOL frames
        [ ] Quick check: aircrack-ng capture-01.cap   (look for "1 handshake" or IVs/PMKID)
        [ ] Move pcap to 03_Active_Capture/sharkcaps/main/
    """).strip()

def get_handshake_verification_checklist() -> str:
    return dedent("""\
        =====================================================
        04_HANDSHAKE_VERIFICATION CHECKLIST
        =====================================================

        [ ] Open pcap in Wireshark: filter (wlan.fc.type_subtype == 0x08 || eapol)
        [ ] Confirm 4-way handshake (EAPOL Msg 1-4) or PMKID in beacon/association
        [ ] Note handshake type in spreadsheet: "Full 4-way", "PMKID only", or "Both"
        [ ] If only PMKID present, conversion to hc22000 still works for hashcat -m 22000
        [ ] Clean capture if needed (remove unrelated traffic) before conversion
        [ ] Document exact capture file name and size
    """).strip()

def get_cracking_checklist() -> str:
    return dedent("""\
        =====================================================
        05_CRACKING_HASHCAT CHECKLIST
        =====================================================

        Recommended modern path (higher success rate):
        1. Convert with hcxtools (install: sudo apt install hcxtools)
           hcxpcapngtool -o handshake.hc22000 --all --pmkid capture-01.cap

        Alternative (pure aircrack-ng users):
        aircrack-ng -J handshake capture-01.cap
        (then convert .hccap to hc22000 if needed)

        Hashcat invocation examples (custom rule focus):

        # Comprehensive rule attack (oneruletorulethemall.rule or your custom set)
        hashcat -m 22000 -a 0 -w 3 --session audit-001 \\
            handshake.hc22000 wordlist.txt \\
            -r /path/to/oneruletorulethemall.rule \\
            --outfile cracked.txt --outfile-format=2

        # Resume previous session
        hashcat --session audit-001 --restore

        # Mask attack example (fast pattern)
        hashcat -m 22000 -a 3 handshake.hc22000 ?u?l?l?l?d?d?d?d -w 3 --session mask1

        Checklist:
        [ ] Conversion completed and .hc22000 verified (non-zero size)
        [ ] Wordlist + rule file chosen and documented (see 06)
        [ ] hashcat session started with --session for resumability
        [ ] Monitor status: hashcat --status
        [ ] Record in spreadsheet: rule file used, wordlist, start time, speed, status, cracked key (if any)
        [ ] If cracked, verify key works against target (or note for reporting)
        [ ] Exhaustive attempt logged before moving to next rule/mask/hybrid
    """).strip()

def get_wordlist_checklist() -> str:
    return dedent("""\
        =====================================================
        06_WORDLIST_MANAGEMENT CHECKLIST
        =====================================================

        Strategy ranking (2026 reality):
        1. Targeted/custom wordlist (highest ROI when target intel available)
        2. Strong rules + mask + hybrid on smaller high-quality base
        3. Large breach compilation lists (private/paid sources often best)
        4. Public generic lists (rockyou, SecLists) - diminishing returns; use as base only

        Commands (from WORDLIST_UTILS):
        wc -l list.txt
        cat *.txt | sort | uniq > unique.txt
        cat combo.txt | cut -d':' -f2 > passwords_only.txt
        (See full utilities in generated WORDLIST_UTILS.txt)

        [ ] Reviewed target OSINT / naming patterns for custom list (cupp or manual)
        [ ] Selected base wordlist + rule file (document exact paths)
        [ ] Tested small rule subset first before full oneruletorulethemall.rule run
        [ ] Cleaned duplicates and normalized separators before use
        [ ] Updated spreadsheet Cracking sheet with exact rule/wordlist combination
    """).strip()

def get_supplemental_checklist() -> str:
    return dedent("""\
        =====================================================
        07_SUPPLEMENTAL_ATTACKS CHECKLIST (Evil Twin / Phish)
        =====================================================

        Only execute if explicitly in scope. Success in 2026 is heavily target-dependent
        (device patch level, auto-join settings, captive portal HTTPS, user vigilance on cert warnings).

        Tools referenced: Wifiphisher, WiFi-Pumpkin3 (still functional per community reports but lower reliability vs pre-2018).

        [ ] Confirmed target network type (Open vs PSK) and client device profile
        [ ] Evaluated PMF / 802.11w impact on deauth component
        [ ] Prepared phishing page / captive portal (HTTPS warning risk noted)
        [ ] Executed only after primary handshake capture path exhausted or per scope
        [ ] All captured credentials logged with clear attribution to this phase
        [ ] Restored original AP association for target where possible
    """).strip()

def get_reporting_checklist() -> str:
    return dedent("""\
        =====================================================
        08_REPORTING CHECKLIST
        =====================================================

        [ ] WIFI_AUDIT_TRACKER.xlsx fully populated (all sheets)
        [ ] Executive summary written (impact + evidence)
        [ ] Technical findings with exact commands, files, and rule/wordlist used
        [ ] Screenshots / pcap hashes / cracked key proof attached
        [ ] Recommendations prioritized (patch PMF, passphrase policy, monitoring)
        [ ] All artifacts cleaned or archived per engagement agreement
    """).strip()

def get_wordlist_utils() -> str:
    return dedent("""\
        /////////////////////////////////////////////////////
        WORDLIST & COMBO UTILITIES (v4.0 - reviewed & cleaned)
        /////////////////////////////////////////////////////

        # Count lines
        wc -l example.txt

        # Join multiple files
        cat *.txt > combined.txt

        # Deduplicate + sort
        cat example.txt | sort | uniq > unique.txt

        # Extract passwords from email:pass combos
        cat example.txt | cut -d':' -f2 > passwords_only.txt

        # Normalize separators ( ; → : )
        sed 's/;/:/g' input.txt > normalized.txt

        # Remove trailing spaces after delimiter (corrected)
        sed 's/|.*[[:space:]]*$//' input.txt > output.txt

        Strategy note: Rules + masks on a quality base list outperform raw size for modern WPA passwords.
        Targeted lists (victim-specific intel) remain highest success when authorized.
    """).strip()

def get_tools_resources() -> str:
    return dedent("""\
        =====================================================
        TOOLS & RESOURCES (v4.0 - reviewed)
        =====================================================

        Core: aircrack-ng suite, hashcat, hcxtools (recommended for conversion), Wireshark, tshark
        Evil Twin / Rogue AP: Wifiphisher, WiFi-Pumpkin3 (contextual success rates documented in README)
        Wordlists: SecLists, Kaonashi, targeted generation (cupp), breach compilations (authorized sources only)
        Modern capture: hcxdumptool + hcxpcapngtool (often higher handshake/PMKID yield than pure airodump)
        PMF verification: Wireshark beacon RSN Capabilities inspection (see checklists)
        References: Mathy Vanhoef research, aircrack-ng docs, hcxtools man pages
    """).strip()

def create_spreadsheet(base: Path) -> None:
    if not HAS_OPENPYXL:
        print(f"{LOG_WARN}openpyxl not installed. Skipping .xlsx. Install with: pip install openpyxl")
        print(f"{LOG_WARN}Tracker will be maintained manually via the phase checklists and ENGAGEMENT_INFO.txt")
        return
    if base / "WIFI_AUDIT_TRACKER.xlsx" in list((base / "00_Engagement").glob("*.xlsx")):
        return

    wb = Workbook()

    # Styles
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    wrap_align = Alignment(wrap_text=True, vertical="top")

    def style_header(ws, row=1):
        for cell in ws[row]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = thin_border

    def auto_width(ws):
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                try:
                    if cell.value:
                        max_len = max(max_len, len(str(cell.value)))
                except:
                    pass
            ws.column_dimensions[col_letter].width = min(max_len + 2, 45)

    # Sheet 0: Instructions
    ws0 = wb.active
    ws0.title = "Instructions_Workflow"
    ws0['A1'] = "WiFi Audit Tracker v4.0 - Instructions"
    ws0['A1'].font = Font(bold=True, size=14)
    ws0.merge_cells('A1:G1')
    instructions = dedent("""\
        1. Fill Engagement sheet first.
        2. Add each discovered AP to Targets sheet (update PMF status from Wireshark).
        3. Log every capture session in Captures sheet (include exact command and pcap filename).
        4. After verification, record handshake type and move to Cracking sheet.
        5. For every hashcat run, log rule file (e.g. oneruletorulethemall.rule), wordlist, session name, and result.
        6. Use Findings sheet for final risk entries with evidence links.
        7. Update status columns frequently. Use Data Validation dropdowns where present.
        8. All phase checklists in the numbered folders must be completed in parallel.
    """).strip()
    ws0['A3'] = instructions
    ws0['A3'].alignment = wrap_align
    ws0.merge_cells('A3:G12')
    ws0.column_dimensions['A'].width = 100

    # Sheet 1: Engagement
    ws1 = wb.create_sheet("Engagement")
    headers1 = ["Field", "Value", "Notes"]
    for col, h in enumerate(headers1, 1):
        ws1.cell(row=1, column=col, value=h)
    style_header(ws1)
    fields = [
        ("Client / Engagement Name", "", ""),
        ("Auditor", "", ""),
        ("Start Date", datetime.now().strftime("%Y-%m-%d"), ""),
        ("Adapter Model", "", "e.g. Alfa AWUS036ACM"),
        ("Driver / Firmware", "", ""),
        ("Regulatory Domain Set", "", "e.g. US"),
        ("Primary Toolchain", "aircrack-ng + hashcat + hcxtools", ""),
        ("Custom Rule File", "oneruletorulethemall.rule (or path)", ""),
        ("Authorization Documented", "YES / NO", ""),
    ]
    for i, (f, v, n) in enumerate(fields, 2):
        ws1.cell(row=i, column=1, value=f)
        ws1.cell(row=i, column=2, value=v)
        ws1.cell(row=i, column=3, value=n)
    auto_width(ws1)

    # Sheet 2: Targets
    ws2 = wb.create_sheet("Targets")
    headers2 = ["BSSID", "ESSID", "Channel", "PWR (dBm)", "Clients", "PMF Status", "Security", "Capture Status", "Handshake Type", "Notes"]
    for col, h in enumerate(headers2, 1):
        ws2.cell(row=1, column=col, value=h)
    style_header(ws2)
    dv_pmf = DataValidation(type="list", formula1='"Required,Optional,Disabled,Unknown"', allow_blank=True)
    ws2.add_data_validation(dv_pmf)
    dv_pmf.add('F2:F1000')
    dv_cap = DataValidation(type="list", formula1='"Not Started,In Progress,Handshake Captured,PMKID Only,Failed,Passive Only"', allow_blank=True)
    ws2.add_data_validation(dv_cap)
    dv_cap.add('H2:H1000')
    auto_width(ws2)

    # Sheet 3: Captures
    ws3 = wb.create_sheet("Captures")
    headers3 = ["Timestamp", "Target BSSID", "Channel", "Command Used", "Duration (min)", "Pcap Filename", "Handshake Acquired", "PMKID Present", "Notes"]
    for col, h in enumerate(headers3, 1):
        ws3.cell(row=1, column=col, value=h)
    style_header(ws3)
    auto_width(ws3)

    # Sheet 4: Cracking
    ws4 = wb.create_sheet("Cracking")
    headers4 = ["Session Name", "Start Time", "Target BSSID", "Hash Type (22000/16800)", "Rule File", "Wordlist / Mask", "Status", "Key Found", "Speed (H/s)", "Notes"]
    for col, h in enumerate(headers4, 1):
        ws4.cell(row=1, column=col, value=h)
    style_header(ws4)
    dv_status = DataValidation(type="list", formula1='"Running,Paused,Exhausted,Cracked,Abandoned"', allow_blank=True)
    ws4.add_data_validation(dv_status)
    dv_status.add('G2:G1000')
    auto_width(ws4)

    # Sheet 5: Findings
    ws5 = wb.create_sheet("Findings")
    headers5 = ["Finding ID", "Severity", "Target", "Description", "Evidence (file/command)", "Recommendation", "Status"]
    for col, h in enumerate(headers5, 1):
        ws5.cell(row=1, column=col, value=h)
    style_header(ws5)
    auto_width(ws5)

    wb.save(base / "00_Engagement" / "WIFI_AUDIT_TRACKER.xlsx")
    print(f"{LOG_OK}Generated WIFI_AUDIT_TRACKER.xlsx with 6 sheets + data validation")

def write_files(base: Path) -> None:
    manifest = [
        (base / "README.md", get_disclaimer() + "\n\n" + "# WiFi Audit Kit v4.0\n\nFull phase-oriented workflow with checklists and tracker spreadsheet. See 00_Engagement/ENGAGEMENT_INFO.txt and WIFI_AUDIT_TRACKER.xlsx."),
        (base / "00_Engagement" / "ENGAGEMENT_INFO.txt", get_engagement_info()),
        (base / "01_Preparation" / "checklists" / "PREPARATION_CHECKLIST.txt", get_preparation_checklist()),
        (base / "02_Passive_Recon" / "checklists" / "RECON_CHECKLIST.txt", get_recon_checklist()),
        (base / "03_Active_Capture" / "checklists" / "CAPTURE_CHECKLIST.txt", get_capture_checklist()),
        (base / "04_Handshake_Verification" / "checklists" / "HANDSHAKE_VERIFICATION_CHECKLIST.txt", get_handshake_verification_checklist()),
        (base / "05_Cracking_Hashcat" / "checklists" / "CRACKING_CHECKLIST.txt", get_cracking_checklist()),
        (base / "06_Wordlist_Management" / "checklists" / "WORDLIST_CHECKLIST.txt", get_wordlist_checklist()),
        (base / "07_Supplemental_Attacks" / "checklists" / "SUPPLEMENTAL_CHECKLIST.txt", get_supplemental_checklist()),
        (base / "08_Reporting" / "checklists" / "REPORTING_CHECKLIST.txt", get_reporting_checklist()),
        (base / "06_Wordlist_Management" / "WORDLIST_UTILS.txt", get_wordlist_utils()),
        (base / "TOOLS_RESOURCES.txt", get_tools_resources()),
    ]
    for path, content in manifest:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content + "\n")
        print(f"{LOG_SUB}Wrote: {path}")

def main() -> None:
    args = parse_args()
    print(f"\n[ WiFi Audit Kit | {APP_VERSION} ]\n")
    base = resolve_name(args.name)
    create_structure(base, args.force)
    write_files(base)
    if not args.no_spreadsheet:
        create_spreadsheet(base)
    print(f"\n{LOG_OK}Kit created successfully at: {base.resolve()}")
    print(f"{LOG_OK}Next: cd {base} && cat 00_Engagement/ENGAGEMENT_INFO.txt")
    print(f"{LOG_OK}Open WIFI_AUDIT_TRACKER.xlsx and begin filling Targets + Captures sheets.")

if __name__ == "__main__":
    main()
