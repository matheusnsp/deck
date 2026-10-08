# Deck

🇧🇷 [Versão em português](README.md)

A button panel on your phone to control the computer.
The computer can be a **Mac, Windows or Linux**; the panel opens on **any phone** (iPhone, Samsung and other Android) or in the browser of another computer/tablet.

You build the buttons **in a visual editor on the computer**; the phone just mirrors them, instantly. It comes with pages for **favorites, DJ (what's playing), modes, apps, sites, media, productivity, calls and system**, in a 4×2 grid, made for using the phone **in landscape**.

**Start here:** on Mac and Linux, paste the Terminal line from the Deck website (it downloads, clears and starts); or download `deck.zip`, unzip it and double-click the start file for your system (section 1). Then scan the QR code with the phone (section 2) and build the buttons (section 3). The full guide, from download to use on any device, lives inside the deck itself: **How to use**, in the editor's sidebar (`http://localhost:8787/guia`).

The interface is in **Portuguese or English**: it follows the computer's language, and you can change it in **Settings › Language** in the editor (it applies to the editor, the phone and the guide). The start files are named in Portuguese — `Iniciar` means Start.

---

## 1 · Start on the computer

| System | Needs | How to start |
|---|---|---|
| **Mac** | nothing (if it asks for the "command line developer tools", accept) | double-click `Iniciar no Mac.command` (or Terminal in the folder → `python3 server.py`, which never shows a warning) |
| **Windows** | Python 3 — [python.org](https://www.python.org/downloads/), check **Add python.exe to PATH** | double-click `Iniciar no Windows.bat` |
| **Linux** | Python 3 (already included) | `./iniciar-linux.sh` or `python3 server.py` |

**Security warning the first time** (only with the zip downloaded by the browser; the Terminal line from the site doesn't go through this):

- **Mac:** "Apple could not verify this item is free of malware", with Move to Trash / Done buttons. Click **Done**, go to **System Settings › Privacy & Security**, scroll to the bottom and click **Open Anyway** (it shows up for about an hour after the attempt). Once only. On macOS 14 or earlier, right-click › **Open** is enough.
- **Windows:** "The publisher could not be verified" or "Windows protected your PC": untick **Always ask before opening this file** and click **Run** (or **More info › Run anyway**). If it keeps asking, right-click the `.bat` › Properties › **Unblock**.
- **Linux:** no warning. If `./iniciar-linux.sh` doesn't run, `chmod +x iniciar-linux.sh`.

When it starts, the **editor** opens in the browser (`http://localhost:8787/editar`) — if it's already open in some tab, the deck doesn't open another. Keep the terminal window open while you use it.

To make the editor an app with its own window (no tabs or address bar): in Safari, **File › Add to Dock**; in Chrome/Edge, menu **⋮ › Cast, save and share › Install page as app**.

---

## 2 · Connect the phone

In the editor, click **Connect phone** (or open `http://localhost:8787/parear`).

1. Phone on the **same Wi-Fi** as the computer.
2. Open the **camera**, point it at the QR code and tap the link.
3. Save it to the home screen to open it as an app:
   - **iPhone:** Share › Add to Home Screen
   - **Android/Samsung:** menu ⋮ › Add to Home screen — and use the **full screen** button in the corner (hides the bars and keeps it landscape)

On a Mac, the QR code comes **by name** (`YourMac.local`): that link keeps working even if the computer's IP changes. Android doesn't open by name — there, tap **By IP**.

### Four ways to connect

The **Connect phone** window has four tabs. The deck works through any of them: it only needs a network path between the phone and the computer.

| Tab | When | How |
|---|---|---|
| **Wi-Fi** | both on the same network | the usual way; just scan |
| **USB cable** | at the desk, no router needed (zero lag and it charges the phone) | iPhone: Settings › **Personal Hotspot** › Allow Others to Join, then plug in the cable. Android: **USB tethering** (on a Mac, only Android 14+) |
| **Bluetooth** | no cable and no router (slower, but plenty) | Personal Hotspot (or Bluetooth tethering) on, pair the two and, on the Mac, Bluetooth menu › phone › **Connect to Network** |
| **Computer's network** | no Wi-Fi at all, or the phone plan has no hotspot | Mac: **Internet Sharing** over Bluetooth PAN. Windows: **Mobile hotspot**. Linux: Wi-Fi hotspot |

The same window lists the connected phones: **Disconnect** removes a device right away (it sees the notice and only comes back when you click **Allow again**), and **Generate a new link** disconnects everyone at once — the ones you want back scan the QR code again.

On each tab the deck detects by itself when the phone shows up through that path and shows the right QR code. USB cable and Bluetooth use the phone's **Personal Hotspot**, which has to be enabled on your carrier plan (almost all are). With the cable connected, the computer may start using the phone's internet — on a Mac, System Settings › Network › ⋯ › **Set Service Order** and keep Wi-Fi above "iPhone USB".

---

## 3 · Choose the buttons (editor)

Everything at `http://localhost:8787/editar`, which only opens on the computer itself:

- **Click an empty space (+)** and choose what the button does: app, site, keyboard shortcut, text, media, volume, microphone, power, mode, call or go to another page.
- **App:** pick from the list of installed apps — the button gets **the app's own icon from the computer**.
- **Power:** shut down, restart, sleep or lock the computer. Shut down, restart and sleep ask for a **second tap** on the phone by default. Turning on a computer that's off from the phone isn't possible (nothing is running on it to receive the request): prefer **Sleep** — it wakes with any key and, on a Mac with "Wake for network access" on and an Apple TV, HomePod or Apple router on the network, it wakes by itself when Deck opens on the phone (the deck announces itself on the network for that).
- **Site:** type an address or pick from the **tabs open right now** (Mac), the **bookmarks** and the **most visited sites** of the computer's browsers. The button gets **the site's own icon** — and, when the site has an official app (WhatsApp, YouTube, Notion…), the deck also fetches **the app's official icon** and uses it instead of white or tiny icons. You can choose which browser opens it and, on a Mac, if the tab is already open the button just **brings it to the front** instead of opening another.
- **Keyboard shortcut:** click the field and press the keys.
- **Drag** the buttons to change their order; drop one on a tab at the top to move it to another page. **+ Page** creates more pages — on the phone, swipe sideways.
- **Pages:** drag them in the sidebar (or in the tabs at the top) to change their order — from the keyboard, ⌥/Alt+↑/↓. The **eye** next to the name hides the page from the phone without deleting it (click again to show it); in `config.json`, `"oculta": true` on the page.
- Name, emoji or your own image, color and confirmation (second tap) live in the right-hand panel.

Everything saves by itself to `config.json` (a copy of the previous one stays in `.config-anterior.json`). Ctrl/⌘+Z undoes. If a `config.local.json` exists in the folder, the deck uses it instead — handy to keep your buttons out of Git while `config.json` stays the example.

---

## 4 · Button types

| Type | Does | Mac | Windows | Linux |
|---|---|:-:|:-:|:-:|
| App | opens a program | ✓ | ✓ | ✓ |
| Site | opens a browser tab (or brings the open tab to the front¹) | ✓ | ✓ | ✓ |
| Keyboard shortcut | presses keys, e.g. `ctrl+shift+t` | ✓ | ✓ | ✓² |
| Text | types a ready-made phrase | ✓ | ✓ | ✓² |
| Media | play/pause, next, previous | ✓ | ✓ | ✓³ |
| Volume | up, down, mute or a value | ✓ | ✓ | ✓⁴ |
| Microphone | mutes/unmutes (lights the MUTE lamp) | ✓ | ✓ | ✓⁴ |
| Power | shut down, restart, sleep, lock (with a second tap) | ✓ | ✓ | ✓⁵ |
| Go to page | switches the page on the phone | ✓ | ✓ | ✓ |
| Mode | Do Not Disturb, opens and closes apps, volume and a timer on the phone (section 5) | ✓⁶ | ✓⁶ | ✓⁶ |
| Call | answer, decline, mute, camera and hang up in the meeting app (section 5) | ✓ | ✓ | ✓⁷ |

¹ on a Mac, with Safari, Chrome, Edge, Brave, Arc, Vivaldi or Opera; on Windows and Linux it opens a new tab ·
² needs `xdotool` (or `wtype` on Wayland) · ³ `playerctl` · ⁴ `pactl` or `wpctl` (included in most distros) · ⁵ `systemctl`/`loginctl` (systemd) ·
⁶ Do Not Disturb turns on through the Shortcuts app on a Mac and through GNOME on Linux; on Windows the mode only reminds you · ⁷ needs `xdotool` (X11)

If you prefer editing `config.json` by hand you still can (the editor and the phone follow along): there are also `comando` (shell command), `sequencia` (sequence), `esperar` (wait), and on a Mac `atalho` (Shortcuts app) and `applescript`. The keys in the file are in Portuguese (`paginas`, `botoes`, `titulo`, `teclas`, `texto`…) and so are the values of `midia`, `volume` and `energia` (`play`/`proxima`/`anterior`, `subir`/`descer`/`mudo`, `desligar`/`reiniciar`/`suspender`/`bloquear`); the editor writes them for you. Per-system values: `"app": { "mac": "Safari", "windows": "Microsoft Edge", "linux": "Firefox" }`.

---

## 5 · DJ, modes and calls

**DJ (mini player).** The **DJ** page shows full screen whatever is playing on the computer — Spotify, Music, YouTube in the browser or any other player — with artwork, time, back, play/pause, skip and volume; tap the bar to jump to another point. Songs show the album artwork and YouTube videos show the video's thumbnail in full (16:9). On the other pages a mini player shows up in the corner (tap it to open the DJ). Any page can become a player in the editor: **Page › Page type › Player**.

| System | Where the DJ reads from |
|---|---|
| Mac | the same "Now Playing" as Control Center; if macOS hides it, it reads Spotify and Music directly. The YouTube thumbnail comes from the open tab (Safari, Chrome, Edge, Brave, Arc, Vivaldi or Opera) |
| Windows | Windows 10/11 media controls (the same as the taskbar volume flyout) |
| Linux | `playerctl` (any MPRIS player); the YouTube thumbnail comes from the video's address |

**Modes.** One tap gets the computer ready for the moment: turns on **Do Not Disturb**, opens apps and sites, closes distractions, sets the volume, switches page and shows a big **timer** on the phone (pause, +5 min, end, minimize). Another tap turns it off and undoes Do Not Disturb; only one mode is on at a time. Focus (25 min), Work, Study (50 min), Home and Break (5 min) come ready.

| System | Do Not Disturb |
|---|---|
| Mac | through the **Shortcuts** app (macOS 12+): create the shortcuts `Deck Focus On` and `Deck Focus Off` once, with the **Set Focus** action › Do Not Disturb › On / Off. Without them, the mode does the rest and explains on the phone |
| Windows | Windows doesn't let programs turn it on: the mode does the rest and reminds you on the phone to turn it on with Win+N |
| Linux | on GNOME, by itself |

**Calls.** Answer, decline, mute, camera and hang up: the deck brings the meeting window to the front and presses the app's own shortcut — Zoom, Teams, Meet, Webex, Discord and Slack. In automatic, it uses the open meeting (Meet, Zoom, Teams, Webex or FaceTime); for Discord and Slack, choose the app on the button. With no meeting open, mute silences the computer's microphone. On a Mac, FaceTime and iPhone calls reach the phone with **Answer** and **Decline** when the deck has any Call button (it reads the Notification Center alert — experimental, it may stop working if macOS changes that alert).

In `config.json`: `{"tipo": "modo", "nao_perturbe": true, "minutos": 25, "volume": 30, "abrir": ["Notion", "gmail.com"], "fechar": ["WhatsApp"], "pagina": "DJ"}`, `{"tipo": "chamada", "chamada": "mudo", "app": "zoom"}` and, on a page, `"tipo": "player"` or `"oculta": true`.

---

## 6 · Permissions (first time only)

| System | What shows up | What to do |
|---|---|---|
| Mac | "Terminal wants to control System Events" | Allow |
| Mac | "Terminal wants to control Safari/Chrome" | Allow — that's what lists the open tabs and brings a tab to the front |
| Mac | "Terminal wants to control Spotify/Music" | Allow — the DJ uses it to read and control those apps |
| Mac | the mode doesn't turn on Do Not Disturb | create the `Deck Focus On` and `Deck Focus Off` shortcuts in the Shortcuts app (section 5) |
| Mac | keys/text/media don't work | System Settings › Privacy & Security › **Accessibility** → enable Terminal, close and reopen Terminal |
| Windows | Firewall alert for Python | tick **Private networks** › Allow (the Wi-Fi must be set as a private network) |
| Linux | `ufw` firewall on | `sudo ufw allow 8787/tcp` |

---

## 7 · If it doesn't connect

- **The app opens with a black screen** (or "could not connect"): the phone isn't finding the computer at the saved address. Close the app on the phone (swipe up) and open it again with the deck on. If it persists, the address changed — open **Connect phone** in the editor: it warns when the computer's IP or name changed and shows the new QR code. To stop it from happening again, use the link **by name** (default on a Mac) or the USB cable.
- Check that the phone and the computer are **on the same Wi-Fi**. Guest Wi-Fi and company networks usually block devices from each other — in that case, use the **USB cable** or **Bluetooth** (section 2).
- On a Mac, if the **Firewall** is blocking Python, the Connect phone window warns you: System Settings › Network › Firewall › Options › Python › **Allow incoming connections** (or click Allow in the prompt that appears when the deck starts).
- To keep the phone's screen from dimming, raise the **auto-lock** time while you use it.

---

## 8 · Security and privacy

- The editor and the QR code page only open on the computer itself (`localhost`).
- Only whoever has the phone link (with the secret key) presses the buttons, and even then only the buttons you created — the phone never sends free-form commands. The key lives in your user's data folder; to change it and disconnect everyone: `--novo-link`.
- Site suggestions come from the bookmarks and history of **this** computer's browsers and never leave it. Site icons are downloaded from the site itself; to find the app's official icon, the deck queries the App Store's public search (just the site's name) and, if needed, Google's icon service (just the domain). Nothing about you is sent; icons are kept in the data folder for 7 days.
- The deck keeps in your user's data folder only the address each phone used to open it (to warn when the computer's IP or name changes); none of it leaves the computer.
- The DJ keeps the artwork of the latest songs in the data folder; when the player only gives a link to the artwork (Spotify read directly on a Mac, some players on Linux), the deck downloads the image from that link. What's playing is not sent anywhere.
- Use it on a trusted network (home/office): the local connection is not encrypted.

**Options:** `--porta 9000` (port) · `--parear` (open the QR page) · `--novo-link` (new link) · `--sem-navegador` (don't open the editor) · `--idioma en` (language: auto, pt or en) · `--config other.json`

Credits: QR code generator [qrcode-generator](https://github.com/kazuhikoarase/qrcode-generator) (MIT).
