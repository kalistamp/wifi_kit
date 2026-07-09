## Usage: subfolder_ng.py

Generates the standard assessment folder structure and reference manuals
(`WIFI_ASSESSMENT_MANUAL.txt`, `WORDLIST_UTILS.txt`, `TOOLS_RESOURCES.txt`,
capture notes) for a new engagement.


**python3 subfolder_ng.py --name "My-Assessment-v1"**


* `--name` sets the assessment folder name directly and skips the interactive
  prompt. **Pass this flag every time** you run the script in a scripted, CI,
  or automated context — without it, the script will block waiting for input
  on stdin.
* If `--name` is omitted, the script falls back to an interactive prompt with
  a date-stamped default (e.g. `2026-07-08_WIFI_ASSESSMENT`).
* The `templates/` directory next to `subfolder_ng.py` must be present — it
  holds the manual/reference content the script loads at runtime.

## check:

Add to my own Repo? (CHECK !) - https://github.com/lutzenfried/Methodology/blob/main/wireless.md — a structured personal methodology/checklist for wireless assessments; worth comparing against this repo's own workflow.

https://pentestlab.blog/2015/02/03/hirte-attack/ — write-up on the Hirte attack, a WEP client-side attack variant usable when you only have a client and no AP in range.

https://github.com/mgeeky/Penetration-Testing-Tools/tree/master/networks/wpa2-enterprise-utils — utilities focused on WPA2-Enterprise (802.1X) testing, which the aircrack-ng-centric workflow above doesn't cover.

## Phish:

WiFi Pumpkin -	Framework for Rogue Wi-Fi Access Point Attack.

Wifiphisher - Wifiphisher is a rogue Access Point framework for conducting red team engagements or Wi-Fi security testing.

## Evil Twin / Captive Portal Effectiveness (2026)

**Fact-check: are Evil Twin/MITM tools like WiFi-Pumpkin still effective in 2026?**

Your assumption is half right, but the mechanism is different than "providers block the popup."  
What hasn't changed: The OS-level captive portal popup (Apple's CNA, Android's equivalent) still auto-triggers when a device joins a network that looks like it needs a login — nobody has disabled that mechanism. Security vendors are still writing about it as an active, real threat in 2026, and tools like WiFi-Pumpkin and Wifiphisher are explicitly named as still-functional frameworks for automating scanning, spoofing, captive portal setup, and credential capture.

**What has actually changed, and why success rates are down:**

* **HTTPS adoption on captive portals themselves.** A June 2026 audit of five public networks found all five used HTTPS for the captive portal login page, which blocks plain HTTP credential sniffing — the exact technique your WIFIPUMPKIN3.md doc describes ("this would only work with HTTP"). That said, the same audit noted HTTP captive portals remain in use on less-maintained networks like independent restaurants and older hotel systems, so it's inconsistent, not eliminated.

* **Certificate warnings.** A spoofed captive portal on a rogue AP typically can't present a valid cert for the real domain, so a savvy user (or a hardened browser config) will see a warning — several of the 2026 write-ups explicitly tell users to disconnect immediately if a login page throws certificate warnings.

* **Auto-join/auto-reconnect defaults.** iOS and Android both expose per-network auto-join toggles now, and guides are actively telling users to disable auto-join for public networks — this is the thing that most directly weakens Known Beacons/KARMA-style attacks (relevant to your KNOWN_BEACON.md and the Wifiphisher notes), since those rely on the device automatically reconnecting to a spoofed "previously known" SSID.

* **Overall verdict from a 2026 security audit:** rogue/evil-twin attacks are called out as one of two specific threat vectors that remain real and underreported in an otherwise much-safer public WiFi landscape (thanks to ~95% TLS adoption for regular web traffic).

**Bottom line:** these tools aren't obsolete — they're still actively referenced in 2026 threat writeups and still used in authorized red-team engagements — but their success now depends heavily on the target being an older/unpatched device, a non-HTTPS captive portal, or a user who ignores cert warnings. Against a fully patched, security-conscious target they're much less reliable than in the pre-2018 era.

## Sources:

* https://github.com/0x90/wifi-arsenal (FORK: https://github.com/techge/wifi-arsenal) — a broad, curated collection of wireless attack tools and references; good first stop when looking for a specific utility.

* https://github.com/TheWickerMan/Auto-Airodump-NG/blob/master/Auto-Airodump-NG [Tst and Take] — a script that automates/wraps common airodump-ng workflows.

* https://github.com/v1s1t0r1sh3r3/airgeddon/wiki/Screenshots — screenshots/walkthrough of airgeddon, the multi-use wireless auditing shell script referenced in TOOLS_RESOURCES.txt.

* https://github.com/gorvgoyl/clone-wars — collection/list of Evil Twin and rogue-AP style attack tools, relevant to the Phish tools above.

* https://github.com/KasRoudra/PyPhisher — phishing page framework; relevant to social-engineering-style Wi-Fi credential capture rather than handshake cracking.

* https://github.com/AlexLynd/ESP8266-Wardriving — ESP8266-based wardriving/scanning project for cheap dedicated hardware.

* https://pwnagotchi.ai/ — AI-assisted handshake-collection tool that runs on small hardware (e.g. Raspberry Pi) and passively gathers handshakes over time.

* [Hacker_Roadmap](https://github.com/sundowndev/hacker-roadmap#globe_with_meridians-wireless-testing) — high-level index of wireless testing tools and techniques, useful as a jumping-off point.

* [Wigle](https://wigle.net/) — public database of observed wireless networks, searchable by location; useful for wardriving research and coverage mapping.

* https://www.youtube.com/watch?v=QHo2hCzxMr0 — video walkthrough (see video title/description for specifics).

## Wordlists:

* https://github.com/ZKAW/big_wpa_wordlist — large WPA-focused wordlist; see WORDLIST_UTILS.txt for why wordlist strategy (rules/masks) usually matters more than raw size.

* https://github.com/danielmiessler/SecLists/tree/master/Passwords — the standard general-purpose password wordlist collection; a solid default starting point.

* https://github.com/kaonashi-passwords/Kaonashi — specialized/curated wordlist project, complementary to SecLists.

## Setup Alfa AWUS036ACM Adapter (steps):

**sudo apt update 
sudo apt upgrade -y 
sudo apt dist-upgrade -y 
sudo reboot now 
sudo apt update 
sudo apt install realtek-rtl88xxau-dkms 
sudo apt install dkms 
git clone https://github.com/aircrack-ng/rtl8812au 
cd rtl8812au/ 
make 
sudo make install 
lsusb 
iwconfig**


## Literature:

* A Comprehensive Taxonomy of Wi-Fi Attacks: https://www.ru.nl/publish/pages/769526/mark_vink.pdf

* https://github.com/skickar/Hope_2022_Presentation/blob/main/Cyber_Weapons_Hope.pdf

* https://miloserdov.org/?cat=2

* https://blog.elcomsoft.com/2020/03/breaking-wi-fi-passwords/#:~:text=The%20WPA%20standard%20enforces%20the,network%20of%20GPU%2Daccelerated%20computers

* https://www.trickster.dev/post/decrypting-your-own-https-traffic-with-wireshark/

* * *

KRACK is a replay attack on the Wi-Fi Protected Access protocol that secures Wi-Fi connections. It was discovered in 2016 by the Belgian researchers Mathy Vanhoef and Frank Piessens of the University of Leuven. 

* Mathy Vanhoef: https://www.mathyvanhoef.com/

* * *


**Disclaimer: This script is for educational purposes only. Please don’t use this knowledge for malicious purposes**


