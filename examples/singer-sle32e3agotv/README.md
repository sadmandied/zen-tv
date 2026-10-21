# Singer Smart TV 32" (SLE32E3AGOTV) Debloat & Clean Launcher

## Device Overview
* **Model:** SINGER ANDROID TV (`SLE32E3AGOTV`)
* **Hardware / Board:** `sunnyvale` (OEM: Skyworth / MediaTek)
* **OS Version:** Android TV 14 (API level 34)
* **Build ID:** `UKNV.260125.001`
* **Stock Launcher:** `com.google.android.tvlauncher`
* **Tuner / Live TV App:** `com.mediatek.wwtv.tvcenter`

---

## What Was Done

### 1. Telemetry, Ads & Manufacturer Bloat Disabled
The following 16 packages were safely disabled for user 0 (`pm disable-user --user 0`). Nothing is permanently deleted, and everything is 100% reversible:
* **Manufacturer Tracking & Ads (Skyworth/Coocaa):**
  * `com.smartdevice.recommendation` (Coocaa recommendation banners and telemetry)
  * `com.smartdevice.leanbacklauncher.customizer` (Partner sponsored ad rows)
  * `com.Smartdevice.emanual` (On-screen manual)
  * `fusion.android.tv.demo` (Retail store demo mode)
  * `com.mstar.android.tv.disclaimercustomization`
* **Android Ad & Personalization Services:**
  * `com.android.adservices.api`
  * `com.android.ondevicepersonalization.services`
  * `com.android.federatedcompute.services`
  * `com.google.android.feedback`
  * `com.android.tv.feedbackconsent`
  * `com.google.android.partnersetup`
* **Unneeded TV Background Services:**
  * `com.google.android.tvrecommendations`
  * `com.cltv.fast` (FAST streaming channels)
  * `com.android.healthconnect.controller`
  * `com.android.health.connect.backuprestore`
  * `com.google.android.play.games`
* **Stock Launcher:**
  * `com.google.android.tvlauncher` (Replaced with `com.gathin.tvhome`)

### 2. Services Preserved & Functional
* **Google Assistant / Voice Search:** `com.google.android.katniss`
* **Chromecast built-in:** `com.google.android.apps.mediashell`
* **Live TV & Tuner / HDMI Inputs:** `com.mediatek.wwtv.tvcenter`, `com.mediatek.tvinput`
* **System Updates (OTA):** `com.mediatek.tv.service`
* **Keyboards & Remotes:** `org.liskovsoft.androidtv.rukeyboard`, `com.google.android.inputmethod.latin`, `com.mediatek.autopair`
* **Play Store & Core Services:** `com.android.vending`, `com.google.android.gms`

### 3. Apple TV-Style Minimal Launcher
* Compiled and installed `com.gathin.tvhome` (v2.3, SDK 34).
* Dock row configured with 4 apps:
  1. **Live TV** (com.mediatek.wwtv.tvcenter)
  2. **YouTube** (com.google.android.youtube.tv)
  3. **Deepto Play** (com.gotipath.deeptotvapp)
  4. **Jellyfin** (org.jellyfin.androidtv)
* **Live TV** is mapped to the *Inputs* button at the top and available in the app grid.
* AdGuard Private DNS (`dns.adguard-dns.com`) enabled system-wide.

---

## How to Restore to Factory Stock

If you ever want to revert everything back to stock:

```powershell
tools\restore.ps1 -TvHost 192.168.0.193 examples\singer-sle32e3agotv\debloat.txt
```

To re-enable the stock launcher manually:
```bash
tools/tv.py 'pm enable com.google.android.tvlauncher'
tools/tv.py 'cmd package set-home-activity --user 0 com.google.android.tvlauncher/com.google.android.tvlauncher.MainActivity'
```

To re-enable any individual app (e.g., Play Games):
```bash
tools/tv.py 'pm enable com.google.android.play.games'
```

To reset Private DNS back to default:
```bash
tools/tv.py 'settings put global private_dns_mode opportunistic'
```

---

## Customizing the Launcher

### Changing Dock Order
Edit `launcher/app/src/main/res/values/config.xml` under `<string-array name="dock_apps">`, then rebuild and install:
```powershell
launcher\build-and-install.ps1 -TvHost 192.168.0.193
```

---

## Security Best Practice (Done when finished)
Turn off **USB debugging** on your TV (*Settings → System → Developer options → USB debugging → OFF*) so port `5555` is closed to the local network.
