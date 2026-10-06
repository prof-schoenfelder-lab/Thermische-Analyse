# /// script
# requires-python = ">=3.10"
# dependencies = ["mss", "Pillow", "uiautomation; sys_platform == 'win32'"]
# ///
"""Klickrecorder: zeichnet Mausklicks mit Bildschirmfoto und Elementnamen auf.
Aus der Aufnahme baut aufnahme2tutorial.py eine Klickanleitung.

Start:   uv run klickrecorder.py <Name> [--ohne-tasten]   (oder start_klickrecorder.bat)
Tasten:  Strg+Alt+F  Foto (Bildschirm ohne Klick festhalten, z.B. ein Ergebnis)
         Strg+Alt+K  neues Kapitel (aus jedem Kapitel wird eine Anleitung)
         Strg+Alt+Z  letzten Klick verwerfen (mehrfach: weiter zurück)
         Strg+Alt+P  Pause / weiter
         Strg+Alt+S  Aufnahme beenden
Ausgabe: aufnahmen/<Datum>_<Name>/events.json und frames/*.png

Bewusst zurückhaltend, damit Virenscanner (Sophos) nicht anschlagen:
- keine Hooks; Maustasten und wenige Steuertasten (Strg, Shift, Alt,
  Leertaste, Tab, Enter, Esc, Entf, F2) werden abgefragt (GetAsyncKeyState),
  Buchstaben und Ziffern nie. Die vier Tastenkürzel sind normale
  Windows-Hotkeys (RegisterHotKey). --ohne-tasten fragt nur die Maus ab.
- Fenster-Rechteck je Ereignis: der Konverter graut alles außerhalb des
  Programmfensters und der offenen Menüs aus
- Bildschirmfoto nur bei Klick, Loslassen nach dem Ziehen und bei
  Leertaste/Tab/Enter (zeigt Eingabefeld bzw. getippten Wert), kein Dauermitschnitt
Eingetippter Text steht nicht in der Aufnahme; Werte zeigt das Foto bei Enter.
"""
import ctypes
import ctypes.wintypes as wt
import datetime
import json
import queue
import sys
import threading
import time
from pathlib import Path

if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # echte Pixel für Maus, Foto und UIA
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

import mss
from PIL import Image

try:
    import uiautomation as auto
except ImportError:  # nur unter Windows vorhanden
    auto = None

DOPPELKLICK_S = 0.5
ZIEHEN_PX = 10
VERWEILEN_S = 0.2
TASTEN = {0x01: "left", 0x02: "right", 0x04: "middle"}  # virtuelle Codes der Maustasten
MODTASTEN = {0x11: "Strg", 0x10: "Shift", 0x12: "Alt"}
# Nur Steuertasten, keine Buchstaben und Ziffern: eingetippter Text bleibt ungesehen
STEUERTASTEN = {0x20: "Leertaste", 0x09: "Tab", 0x0D: "Enter", 0x1B: "Esc", 0x2E: "Entf", 0x71: "F2"}
FOTO_BEI = {"Leertaste", "Tab", "Enter"}  # Foto zeigt Eingabefeld bzw. getippten Wert
WERT_BEI = {"Tab", "Enter"}               # Feldinhalt auslesen (Länge, Wert im Detailfenster, Name)
NACHLESEN_S = 0.3                         # danach zeigt das Detailfenster den Wert mit Einheit
HOTKEYS = {1: (0x46, "foto"), 2: (0x4B, "kapitel"), 3: (0x50, "pause"), 4: (0x53, "stopp"),
           5: (0x5A, "verwerfen")}  # F K P S Z
KLICKART = {"left": "klick", "right": "rechtsklick", "middle": "mittelklick"}


def element_info(c):
    kette, p = [], c
    for _ in range(8):
        if not p:
            break
        kette.append({"typ": p.ControlTypeName, "name": (p.Name or "")[:200],
                      "klasse": p.ClassName, "id": p.AutomationId})
        p = p.GetParentControl()
    r = c.BoundingRectangle
    top = c.GetTopLevelControl()
    return {"typ": c.ControlTypeName, "name": (c.Name or "")[:200],
            "rechteck": [r.left, r.top, r.right, r.bottom],
            "fenster": top.Name if top else "", "kette": kette}


if sys.platform == "win32":
    # eigene Instanzen: Typangaben an ctypes.windll.user32 würden uiautomation stören
    _user32, _dwmapi = ctypes.WinDLL("user32"), ctypes.WinDLL("dwmapi")
    _user32.WindowFromPoint.argtypes = [wt.POINT]
    _user32.WindowFromPoint.restype = wt.HWND
    _user32.GetAncestor.argtypes = [wt.HWND, wt.UINT]
    _user32.GetAncestor.restype = wt.HWND
    _user32.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
    _dwmapi.DwmGetWindowAttribute.argtypes = [wt.HWND, wt.DWORD, ctypes.c_void_p, wt.DWORD]
    _user32.SendMessageTimeoutW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM, wt.UINT, wt.UINT,
                                            ctypes.POINTER(ctypes.c_size_t)]
    _user32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
    _user32.GetWindowLongW.argtypes = [wt.HWND, ctypes.c_int]

    class GUITHREADINFO(ctypes.Structure):
        _fields_ = [("cbSize", wt.DWORD), ("flags", wt.DWORD), ("hwndActive", wt.HWND),
                    ("hwndFocus", wt.HWND), ("hwndCapture", wt.HWND), ("hwndMenuOwner", wt.HWND),
                    ("hwndMoveSize", wt.HWND), ("hwndCaret", wt.HWND), ("rcCaret", wt.RECT)]


def fenster_rechteck(x, y):
    """Rechteck des Fensters unter dem Punkt (Programmfenster oder Menü-Popup), ohne Schatten."""
    if sys.platform != "win32":
        return None
    hwnd = _user32.GetAncestor(_user32.WindowFromPoint(wt.POINT(x, y)), 2)  # GA_ROOT
    if not hwnd:
        return None
    r = wt.RECT()
    if _dwmapi.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(r), ctypes.sizeof(r)):  # 9 = sichtbarer Rahmen
        _user32.GetWindowRect(hwnd, ctypes.byref(r))
    return [r.left, r.top, r.right, r.bottom]


def feldtext():
    """Text des Eingabefelds mit Fokus (Win32 WM_GETTEXT), z.B. Wert im Detailfenster von
    Mechanical, das UI Automation nicht herausgibt. None, wenn kein Eingabefeld den Fokus hat."""
    if sys.platform != "win32":
        return None
    info = GUITHREADINFO(cbSize=ctypes.sizeof(GUITHREADINFO))
    if not _user32.GetGUIThreadInfo(0, ctypes.byref(info)) or not info.hwndFocus:
        return None
    klasse = ctypes.create_unicode_buffer(128)
    _user32.GetClassNameW(info.hwndFocus, klasse, 128)
    if "edit" not in klasse.value.lower() or _user32.GetWindowLongW(info.hwndFocus, -16) & 0x20:  # ES_PASSWORD
        return None
    puffer = ctypes.create_unicode_buffer(256)
    erg = ctypes.c_size_t()
    if not _user32.SendMessageTimeoutW(info.hwndFocus, 0x000D, 256, ctypes.cast(puffer, ctypes.c_void_p).value,
                                       0x0002, 100, ctypes.byref(erg)):  # WM_GETTEXT, SMTO_ABORTIFHUNG
        return None
    return puffer.value


def lese_wert(c):
    """Inhalt eines Eingabefelds über UI Automation (ValuePattern, sonst MSAA-Wert)."""
    for hole in (lambda: c.GetPattern(auto.PatternId.ValuePattern), c.GetLegacyIAccessiblePattern):
        try:
            p = hole()
            if p and p.Value:
                return p.Value[:200]
        except Exception:
            pass
    return ""


def zeile(c):
    """Spaltentexte einer Listenzeile: Kinder-Elemente, sonst MSAA-Beschreibung."""
    texte = []
    try:
        texte = [k.Name for k in c.GetChildren() if k.Name]
    except Exception:
        pass
    try:
        b = c.GetLegacyIAccessiblePattern().Description
        if b:
            texte.append(b)
    except Exception:
        pass
    return texte[:8]


class Recorder:
    def __init__(self, ordner):
        self.ordner = ordner
        (ordner / "frames").mkdir(parents=True, exist_ok=True)
        self.start = datetime.datetime.now()
        self.t0 = time.perf_counter()
        self.events = []
        self.lock = threading.Lock()
        self.kapitel = 1
        self.pause = False
        self.stopp = threading.Event()
        self.unten = {}             # gedrückte Maustaste -> Ereignis
        self.mods = set()           # gerade gehaltene Strg/Shift/Alt
        self.feld = (None, 0.0)     # letzter Text des fokussierten Eingabefelds, Zeitpunkt
        self.tasten = True          # Steuertasten mitschreiben (--ohne-tasten schaltet ab)
        self.letzter_klick = None
        self.maus = (0, 0, 0.0)
        self.verweilt = True
        self.n_frames = 0
        self.foto_q, self.speicher_q, self.uia_q = queue.Queue(), queue.Queue(), queue.Queue()
        self.klick_q = queue.Queue()  # eigene Warteschlange: Klicks nachschlagen, bevor sich ein Menü öffnet

    def zeit(self):
        return round(time.perf_counter() - self.t0, 3)

    def neu(self, art, **daten):
        with self.lock:
            ev = {"nr": len(self.events) + 1, "t": self.zeit(), "kapitel": self.kapitel,
                  "art": art, **daten}
            self.events.append(ev)
        return ev

    def melden(self, ev):
        el = ev.get("element") or {}
        was = " + ".join(ev.get("mods", []) + [ev["taste"]]) if ev["art"] == "taste" else el.get("name", "")
        print(f"  {ev['nr']:4d}  {ev['art']:<12} {was}  [{el.get('typ', '')}]")

    # ---- Maus -------------------------------------------------------------
    def on_click(self, x, y, taste, pressed):
        if self.pause:
            return
        if not pressed:
            ev = self.unten.pop(taste, None)
            if ev:
                ev["t_los"] = self.zeit()
                if abs(x - ev["x"]) > ZIEHEN_PX or abs(y - ev["y"]) > ZIEHEN_PX:
                    ev.update(art="ziehen", taste=taste, x2=x, y2=y)
                    self.foto_q.put((ev, "frame_ende"))       # Ergebnis nach dem Ziehen
                    self.klick_q.put((ev, x, y, "ziel"))      # worauf abgelegt wurde
            return
        t, vor = self.zeit(), self.letzter_klick
        if (taste == "left" and vor and vor["art"] == "klick" and t - vor["t"] < DOPPELKLICK_S
                and abs(x - vor["x"]) < 6 and abs(y - vor["y"]) < 6):
            vor["art"] = "doppelklick"
            return
        self.feld = (None, 0.0)  # neuer Klick: alter Feldtext gilt nicht mehr
        ev = self.neu(KLICKART.get(taste, "klick"), x=x, y=y, fenster_rechteck=fenster_rechteck(x, y))
        if self.mods:
            ev["mods"] = sorted(self.mods)
        self.letzter_klick = self.unten[taste] = ev
        self.foto_q.put((ev, "frame"))
        self.klick_q.put((ev, x, y, "element"))

    def on_move(self, x, y):
        if (x, y) != self.maus[:2]:
            self.maus = (x, y, time.perf_counter())
            self.verweilt = False

    def on_taste(self, name):
        if self.pause:
            return
        x, y, _ = self.maus
        ev = self.neu("taste", taste=name, x=x, y=y, fenster_rechteck=fenster_rechteck(x, y))
        if self.mods:
            ev["mods"] = sorted(self.mods)
        gehalten = next((e for e in self.unten.values() if e), None)
        if gehalten:  # z.B. Leertaste während Pull in SpaceClaim
            ev["waehrend"] = gehalten["nr"]
        if name in FOTO_BEI:
            self.foto_q.put((ev, "frame"))
        if name in WERT_BEI:
            # Mechanical schließt das Feld sofort bei Enter: den zuletzt mitgelesenen Text nehmen
            text, t = self.feld
            if text and time.perf_counter() - t < 2.0:
                ev["wert_direkt"] = text
            self.feld = (None, 0.0)
            # danach per UI Automation das aktive Feld lesen, kurz später den übernommenen Wert
            self.uia_q.put((ev, x, y, "wert"))
            # zweites Foto, wenn das Detailfenster den übernommenen Wert zeigt (beim Enter baut es sich neu auf)
            threading.Timer(NACHLESEN_S, self.foto_q.put, [(ev, "frame_danach")]).start()
            k = self.letzter_klick
            if k and self.zeit() - k["t"] < 60:
                threading.Timer(NACHLESEN_S, self.uia_q.put, [(ev, k["x"], k["y"], "nachlesen")]).start()
        self.melden(ev)

    def abfragen(self):
        """Maus und Steuertasten in einer Schleife alle 10 ms abfragen (statt Hooks).
        Eine Schleife, eine Uhr: Reihenfolge von Klick, Ziehen und Taste stimmt immer."""
        user32 = ctypes.windll.user32
        unten = lambda vk: bool(user32.GetAsyncKeyState(vk) & 0x8000)
        pt = wt.POINT()
        gedrueckt = {vk: False for vk in [*TASTEN, *STEUERTASTEN]}
        runde = 0
        while not self.stopp.is_set():
            runde += 1
            if self.tasten and not self.pause and runde % 2 == 0:  # alle 20 ms: Eingabefeld mitlesen
                text = feldtext()
                if text is not None:
                    self.feld = (text, time.perf_counter())
            user32.GetCursorPos(ctypes.byref(pt))
            self.on_move(pt.x, pt.y)
            self.mods = {name for vk, name in MODTASTEN.items() if unten(vk)}
            for vk in gedrueckt:
                jetzt = unten(vk)
                if jetzt == gedrueckt[vk]:
                    continue
                gedrueckt[vk] = jetzt
                if vk in TASTEN:
                    self.on_click(pt.x, pt.y, TASTEN[vk], jetzt)
                elif jetzt and self.tasten:
                    self.on_taste(STEUERTASTEN[vk])
            time.sleep(0.01)

    def verweilen(self):
        """Maus steht still -> Element nachschlagen (nur Menüeinträge werden notiert)."""
        while not self.stopp.is_set():
            time.sleep(0.05)
            x, y, t = self.maus
            if not self.verweilt and not self.pause and time.perf_counter() - t > VERWEILEN_S:
                self.verweilt = True
                self.uia_q.put((None, x, y, "hover"))

    # ---- Tastenkürzel -----------------------------------------------------
    def hotkeys(self):
        user32 = ctypes.windll.user32
        self.hotkey_thread = ctypes.windll.kernel32.GetCurrentThreadId()
        for hid, (vk, _) in HOTKEYS.items():
            if not user32.RegisterHotKey(None, hid, 0x0002 | 0x0001 | 0x4000, vk):  # Strg+Alt, ohne Wiederholung
                print(f"Warnung: Strg+Alt+{chr(vk)} ist schon belegt")
        msg = wt.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == 0x0312 and msg.wParam in HOTKEYS:  # WM_HOTKEY
                self.hotkey(HOTKEYS[msg.wParam][1])
        for hid in HOTKEYS:
            user32.UnregisterHotKey(None, hid)

    def hotkey(self, was):
        if was == "stopp":
            self.stopp.set()
        elif was == "pause":
            self.pause = not self.pause
            print("  ---- PAUSE ----" if self.pause else "  ---- weiter ----")
        elif was == "verwerfen":
            with self.lock:
                ev = next((e for e in reversed(self.events) if not e.get("verworfen")
                           and e["art"] not in ("hover", "kapitel")), None)
            if ev:
                ev["verworfen"] = True
                print(f"  ---- verworfen: {ev['nr']} {ev['art']} ----")
        elif not self.pause:
            if was == "kapitel":
                self.kapitel += 1
                self.neu("kapitel")
                print(f"  ==== Kapitel {self.kapitel} ====")
            else:
                ev = self.neu("foto", x=self.maus[0], y=self.maus[1],
                              fenster_rechteck=fenster_rechteck(*self.maus[:2]))
                self.foto_q.put((ev, "frame"))
                self.melden(ev)

    # ---- Hintergrund-Threads ----------------------------------------------
    def fotos(self):
        with mss.mss() as sct:
            monitore = sct.monitors[1:]
            while (item := self.foto_q.get()) is not None:
                ev, feld = item
                mon = next((m for m in monitore
                            if m["left"] <= ev["x"] < m["left"] + m["width"]
                            and m["top"] <= ev["y"] < m["top"] + m["height"]), monitore[0])
                shot = sct.grab(mon)
                self.n_frames += 1
                datei = f"frames/{self.n_frames:04d}.png"
                ev[feld] = datei
                ev["t_" + feld] = self.zeit()
                ev["monitor"] = {k: mon[k] for k in ("left", "top", "width", "height")}
                self.speicher_q.put((datei, shot))

    def speichern(self):
        while (item := self.speicher_q.get()) is not None:
            datei, shot = item
            Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX").save(
                self.ordner / datei, compress_level=6)

    def uia(self, q):
        if auto is None:  # ohne Windows: nur leeren
            while q.get() is not None:
                pass
            return
        with auto.UIAutomationInitializerInThread():
            while (item := q.get()) is not None:
                ev, x, y, art = item
                if art in ("wert", "nachlesen"):
                    self.wert_lesen(ev, x, y, art)
                    continue
                try:
                    try:
                        info = element_info(auto.ControlFromPoint(x, y))
                    except Exception:  # UIA meldet gelegentlich kurz einen Fehler: einmal nachfassen
                        time.sleep(0.05)
                        info = element_info(auto.ControlFromPoint(x, y))
                    if art == "ziel":
                        ev["ziel_element"] = info
                        continue
                    if art == "hover":
                        if info["typ"] != "MenuItemControl":
                            continue
                        ev = self.neu("hover", x=x, y=y, element=info, fenster_rechteck=fenster_rechteck(x, y))
                    else:
                        ev["element"] = info
                    self.melden(ev)
                except Exception as e:
                    if ev is not None:
                        ev["element_fehler"] = str(e)

    def wert_lesen(self, ev, x, y, art):
        try:
            c = auto.GetFocusedControl()
            if c.Element.CurrentIsPassword:
                return
            if c.ControlTypeName == "ListItemControl":
                # Detailfenster: Feld schon zu, aktiv ist die Zeile (Name = Beschriftung, Wert in Spalte 2)
                ev["beschriftung"] = c.Name or ""
                ev["zeile"] = zeile(c)
                wert = next((t for t in ev["zeile"] if t != c.Name), "")
                ev["wert" if art == "wert" else "wert_angezeigt"] = wert
            elif art == "wert":
                ev["feld"] = element_info(c)
                # Umbenennen (F2): nach Enter ist der Baumeintrag aktiv, sein Name ist der neue Name
                ev["wert"] = lese_wert(c) or (c.Name if c.ControlTypeName == "TreeItemControl" else "")
            else:
                c = auto.ControlFromPoint(x, y)
                if c.ControlTypeName in ("PaneControl", "WindowControl"):
                    return  # Grafikfenster o.ä.: dort steht kein Wert
                ev["wert_angezeigt"] = (c.Name or lese_wert(c))[:200]
                # Beschriftung links in derselben Zeile (Detailfenster: Name | Wert)
                p = c.GetParentControl()
                if p and p.ControlTypeName in ("ListControl", "TableControl", "DataGridControl", "TreeControl"):
                    ev["beschriftung"] = (auto.ControlFromPoint(p.BoundingRectangle.left + 12, y).Name or "")[:200]
            if art == "wert":
                print(f"        Wert: {ev.get('wert_direkt') or ev.get('wert', '')}  ({ev.get('beschriftung', '')})")
        except Exception as e:
            ev["wert_fehler"] = str(e)

    def schreiben(self):
        with self.lock:
            daten = {"version": 1, "name": self.ordner.name, "start": self.start.isoformat(timespec="seconds"),
                     "events": self.events}
            try:
                inhalt = json.dumps(daten, ensure_ascii=False, indent=1)
            except RuntimeError:  # Ereignis wird gerade ergänzt, beim nächsten Mal
                return
        tmp = self.ordner / "events.json.tmp"
        tmp.write_text(inhalt, encoding="utf-8")
        tmp.replace(self.ordner / "events.json")


def main():
    args = [a for a in sys.argv[1:] if a != "--ohne-tasten"]
    name = "_".join(args).strip() or "aufnahme"
    ordner = Path(__file__).resolve().parent / "aufnahmen" / f"{datetime.datetime.now():%Y-%m-%d_%H%M}_{name}"
    rec = Recorder(ordner)
    rec.tasten = "--ohne-tasten" not in sys.argv
    threads = {f.__name__: threading.Thread(target=f, daemon=True)
               for f in (rec.fotos, rec.speichern, rec.verweilen, rec.abfragen, rec.hotkeys)}
    threads["uia"] = threading.Thread(target=rec.uia, args=(rec.uia_q,), daemon=True)
    threads["uia_klick"] = threading.Thread(target=rec.uia, args=(rec.klick_q,), daemon=True)
    for th in threads.values():
        th.start()
    if auto is None:
        print("Hinweis: uiautomation fehlt, Elementnamen werden nicht erfasst.")
    print(f"Aufnahme läuft -> {ordner}")
    print("Strg+Alt+F Foto | Strg+Alt+K Kapitel | Strg+Alt+Z verwerfen | Strg+Alt+P Pause | Strg+Alt+S Ende")
    print("Steuertasten (Strg, Shift, Leertaste, Enter, ...):", "an" if rec.tasten else "aus (--ohne-tasten)", "\n")
    try:
        while not rec.stopp.wait(5):
            rec.schreiben()  # Zwischenstand sichern
    except KeyboardInterrupt:
        rec.stopp.set()
    ctypes.windll.user32.PostThreadMessageW(rec.hotkey_thread, 0x0012, 0, 0)  # WM_QUIT
    threads["abfragen"].join()
    rec.foto_q.put(None)
    threads["fotos"].join()
    rec.speicher_q.put(None)
    rec.uia_q.put(None)
    rec.klick_q.put(None)
    print("Speichere Bilder ...")
    threads["speichern"].join()
    threads["uia"].join(timeout=5)
    threads["uia_klick"].join(timeout=5)
    rec.schreiben()
    print(f"\nFertig: {len(rec.events)} Ereignisse, {rec.n_frames} Bilder in\n  {ordner}")
    print("Weiter mit:  python aufnahme2tutorial.py <dieser Ordner>")


if __name__ == "__main__":
    main()
