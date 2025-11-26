#!/usr/bin/env python3

# Disclaimer: This script is for educational purposes only.
# Use only on networks you own or have explicit authorization to test.

import os
import sys
from datetime import datetime
from pathlib import Path

# --- Configuration ---
DIR_STRUCTURE = {
    "sharkcaps": ["main"],  # For raw packet captures (.cap files)
    "word_li": ["combo"],   # For custom/cleaned wordlists
    "hashcat": [],          # For output files and .hc22000 (hashcat format) files
    "xtras": []             # For miscellaneous notes, screenshots, etc.
}

def sub_banner():
    """Prints the application banner."""
    version = "3.3 (WEP Attack Added)"
    ascii_banner = f"""
____ _  _ ___  ____ ____ _    ___  ____ ____  ___  _  _
[__  |  | |__] |___ |  | |    |  \ |___ |__/  |__]  \_/
___] |__| |__] |    |__| |___ |__/ |___ |  \ .|    |

        [ WiFi Recon Assessment Setup | Version {version} ]
        [ Defensive Blue Team Tooling ]

"""
    print(ascii_banner)

def create_directory_structure(base_dir: Path):
    """Creates the main directory and its subdirectories."""
    try:
        # 0o755 is the standard permission for directories (rwxr-xr-x)
        os.makedirs(base_dir, mode=0o755, exist_ok=False)
        print(f" [+] Created main assessment directory: {base_dir}")

        for parent, children in DIR_STRUCTURE.items():
            parent_path = base_dir / parent
            os.makedirs(parent_path, mode=0o755, exist_ok=True)
            print(f"   |-- Created folder: {parent_path}")
            for child in children:
                child_path = parent_path / child
                os.makedirs(child_path, mode=0o755, exist_ok=True)
                print(f"   |-- Created folder: {child_path}")

    except FileExistsError:
        print(f" [!] Error: Directory '{base_dir}' already exists. Please choose a new name.")
        sys.exit(1)
    except Exception as e:
        print(f" [!] An error occurred during directory creation: {e}")
        sys.exit(1)

# --- Documentation Content: MEAT_CONTENT (WIFI MANUAL) ---
MEAT_CONTENT = """
=====================================================
WIFI ASSESSMENT MANUAL: AIRCRACK-NG SUITE GUIDE
=====================================================

This manual outlines the steps for capturing and cracking WPA/WPA2 Handshakes, 
plus older WEP cracking techniques, using the aircrack-ng suite. Refer to the 
official Newbie Guide for full context: https://www.aircrack-ng.org/doku.php?id=newbie_guide

-----------------------------------------------------
STEP 1: PREPARATION AND INTERFACE SETUP (airmon-ng)
-----------------------------------------------------

# 1.1 Kill interfering processes (Crucial!)
# Stops processes like NetworkManager that can interfere with monitor mode.
# Command:
sudo airmon-ng check kill 

# 1.2 Start Monitor Mode
# Replaces 'wlan0' with your actual wireless interface name.
# Command:
sudo airmon-ng start wlan0 
# Output will show the new monitor interface name (e.g., wlan0mon).

# 1.3 List available interfaces to confirm new monitor mode interface
# Command:
iwconfig

-----------------------------------------------------
STEP 2: PASSIVE RECONNAISSANCE (airodump-ng)
-----------------------------------------------------

# 2.1 Discover Networks in the Area
# Lists all Access Points (APs), channels, and BSSIDs within range.
# Command:
sudo airodump-ng wlan0mon 

# 2.2 Target a Specific Network and Capture
# Run this command in a NEW terminal window and let it run.
# -c [channel]: Specifies the channel of the target AP.
# --bssid [MAC]: Filters for the BSSID (MAC address) of the target AP.
# -w [filename]: Specifies the prefix for the capture file (e.g., 'target_ap').
# Command (Example):
sudo airodump-ng -c 11 --bssid 00:01:02:03:04:05 -w dump wlan0mon
# **What it does:** Focuses the monitor interface on channel 11, captures all packets 
# for BSSID 00:01:02:03:04:05, and saves them to a file starting with 'dump'.

-----------------------------------------------------
STEP 3: WPA/WPA2 HANDSHAKE CAPTURE (aireplay-ng)
-----------------------------------------------------

# To capture the 4-way handshake, a client must (re)connect to the AP. 
# Deauthentication attacks (Deauth) force a client to disconnect and reconnect.

# 3.1 Perform a Deauth Attack (in a separate terminal)
# -0 5: Sends 5 deauthentication packets. Use a small number initially.
# -a [AP_BSSID]: MAC address of the Access Point (target).
# -c [Client_MAC]: MAC address of a connected client (optional, but targeted).
# Command (Example with Client):
sudo aireplay-ng -0 5 -a 00:01:02:03:04:05 -c 00:06:07:08:09:0A wlan0mon
# **What it does:** Sends deauth packets to the specific client to force a re-authentication.
# Look for 'WPA Handshake:' notification in the airodump-ng window.

-----------------------------------------------------
STEP 4: WEP CRACKING: ARP REPLAY ATTACK (aireplay-ng)
-----------------------------------------------------

# WEP is vulnerable to attacks that inject packets to generate lots of IVs (Initialization Vectors) quickly. 

# 4.1 Perform Fake Authentication (Optional, but often needed)
# -1 0: Fake authentication (type 1), 0 seconds delay.
# -e [ESSID]: The name of the AP.
# -a [AP_BSSID]: MAC address of the AP.
# -h [Attacker_MAC]: Your card's MAC address (after monitor mode).
# Command (Example):
sudo aireplay-ng -1 0 -e Target_AP_Name -a 00:01:02:03:04:05 -h 00:0B:C0:FF:EE:DD wlan0mon
# **What it does:** Attempts to associate with the AP to prepare for injection.

# 4.2 Perform ARP Replay Attack
# -3: Specifies the ARP Replay Attack.
# -b [AP_BSSID]: MAC address of the AP.
# Command (Example):
sudo aireplay-ng -3 -b 00:01:02:03:04:05 wlan0mon
# **What it does:** Injects captured ARP packets back into the network to generate 
# a high volume of new data (IVs) for cracking. Monitor the **Data** column in airodump-ng.

-----------------------------------------------------
STEP 5: CRACKING THE CAPTURE FILE (aircrack-ng)
-----------------------------------------------------

# 5.1 Check the Capture File for Handshake/IVs
# The capture file will be named like 'dump-01.cap'.
# Command (Example):
aircrack-ng dump-01.cap
# **What it does:** Reads the packet capture file and displays the handshake count (WPA) or **IVs** count (WEP).

# 5.2 Cracking WPA/WPA2 with Aircrack-ng (Dictionary Attack)
# Requires a successful handshake (1 handshake).
# -a 2: Specifies WPA/WPA2 cracking mode.
# -b [AP_BSSID]: MAC address of the target AP.
# -w [wordlist]: Path to your wordlist file.
# Command (Example):
aircrack-ng -a 2 -b 00:01:02:03:04:05 -w /path/to/wordlist.txt dump-01.cap

# 5.3 Cracking WEP (Requires sufficient IVs)
# Does not require -a 1, as WEP cracking is the default mode.
# Command (Example):
aircrack-ng dump-01.cap
# **What it does:** Automatically attempts to crack the WEP key once enough IVs (usually >10,000) are captured.

-----------------------------------------------------
STEP 6: CLEANUP
-----------------------------------------------------

# 6.1 Stop Monitor Mode and Restore Network Services
# Command:
sudo airmon-ng stop wlan0mon 

# 6.2 Restart NetworkManager
# Required to restore normal Wi-Fi connectivity.
# Command:
sudo service NetworkManager restart

-----------------------------------------------------
ADAPTER SETUP: ALFA AWUS036ACM (DETAILED STEPS)
-----------------------------------------------------

# Complete setup process for Alfa AWUS036ACM adapter on Kali Linux

sudo apt update 
sudo apt upgrade -y 
sudo apt dist-upgrade -y 
sudo reboot now 

# After reboot, continue:
sudo apt update 
sudo apt install realtek-rtl88xxau-dkms 
sudo apt install dkms 
git clone https://github.com/aircrack-ng/rtl8812au 
cd rtl8812au/ 
make 
sudo make install 
lsusb 
iwconfig

# Verify the adapter is recognized and can enter monitor mode
"""

# --- Documentation Content: COMBO_CONTENT (WORDLIST UTILS) ---
COMBO_CONTENT = """
///////////////// WORDLIST AND COMBO CLEANUP UTILITIES //////////////////////

These commands are essential for managing, cleaning, and preparing large wordlists 
for efficient password cracking.

# 1. Check Number of Lines in a Wordlist
wc -l example.txt

# 2. Join Multiple Wordlist/Combo Files into One
# Run this inside the directory containing the files.
cat *.txt > new_combined.txt

# 3. Remove Duplicates from a List (Sorts and removes simultaneously)
cat example.txt | sort | uniq > unique_list.txt

# 4. Extract Only Passwords or Emails from a Combo List (e.g., email:password)
# -d':': Use ':' as the delimiter (separator).
# -f2: Selects the second field (password). Use -f1 to select the first (email).
cat example.txt | cut -d':' -f2 > passwords_only.txt

////////////////////////////////////////////////////////////////////////////////
"""

TEXT_INPUT = 'Text Input - [ PMKID = Only part of the Handshake was acquired ]'
NOTE_CONTENT = "\nText Here:\n\n"

# --- Documentation Content: TOOLS_CONTENT (RESOURCES) ---
TOOLS_CONTENT = """
=====================================================
WIFI ASSESSMENT TOOLS AND RESOURCES
=====================================================

### Core Wireless Attack Tools
* aircrack-ng suite: (airmon-ng, airodump-ng, aireplay-ng, aircrack-ng) - Essential for monitoring, capturing, and cracking.
* wifiphisher / WiFi-Pumpkin: Frameworks for Rogue Wi-Fi Access Point (Evil Twin) attacks and client-side social engineering.
* airgeddon: A multi-use shell script for auditing wireless networks.

### Comprehensive Documentation & Resources
* The Aircrack-ng Documentation: (https://www.aircrack-ng.org/doku.php) - Primary source for tool usage.
* Mathy Vanhoef's Site: (https://www.mathyvanhoef.com/) - Researcher who discovered the KRACK attack.
* Hacker Roadmap - Wireless Testing: (https://github.com/sundowndev/hacker-roadmap#globe_with_meridians-wireless-testing) - High-level guide.
* Wigle.net: Database of wireless networks for location and analysis.
* Literature:
    * A Comprehensive Taxonomy of Wi-Fi Attacks: https://www.ru.nl/publish/pages/769526/mark_vink.pdf

### Wordlist Resources
* SecLists/Passwords: (https://github.com/danielmiessler/SecLists/tree/master/Passwords) - The standard starting point for dictionaries.
* Kaonashi: (https://github.com/kaonashi-passwords/Kaonashi) - Specialized wordlist project.

### Adapter Setup Guide (Example: Alfa AWUS036ACM)

sudo apt update && sudo apt upgrade -y 
sudo apt dist-upgrade -y 
# Driver installation may be required depending on your Kali version.
sudo apt install realtek-rtl88xxau-dkms 
# Or manually install from source if necessary (for advanced users):
# git clone https://github.com/aircrack-ng/rtl8812au
# cd rtl8812au/ && make && sudo make install
# Verify with: lsusb && iwconfig
"""

def write_documentation_files(base_dir: Path):
    """Writes the predefined documentation to text files using context managers."""
    
    files_to_create = [
        (base_dir / "README_RECON_NOTES.txt", TEXT_INPUT),
        (base_dir / "sharkcaps" / "main" / "NOTES.txt", NOTE_CONTENT),
        (base_dir / "word_li" / "combo" / "WORDLIST_UTILS.txt", COMBO_CONTENT),
        (base_dir / "TOOLS_RESOURCES.txt", TOOLS_CONTENT),
        (base_dir / "WIFI_ASSESSMENT_MANUAL.txt", MEAT_CONTENT)
    ]

    for file_path, content in files_to_create:
        try:
            # Use 'with open' to ensure files are closed safely.
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f" [!] Failed to write file {file_path}: {e}")

def main():
    """Main execution function."""
    sub_banner()
    print("Author: Kalistamp")
    print("\n" * 2)

    # 1. Get input for the main directory name
    default_name = datetime.now().strftime("%Y-%m-%d_WIFI_ASSESSMENT")
    print(f"Suggestion: {default_name}")
    main_dir_name = input('Enter Name/Date for Today\'s Work: ')

    if not main_dir_name:
        main_dir_name = default_name

    base_dir = Path(main_dir_name.strip())

    print("\n" * 2)

    # 2. Create directories
    create_directory_structure(base_dir)

    # 3. Write documentation
    write_documentation_files(base_dir)

    print('\n[+] Assessment Kit and Manual Created Successfully.')

if __name__ == "__main__":
    main()
