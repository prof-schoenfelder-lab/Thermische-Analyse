# /// script
# requires-python = ">=3.10"
# dependencies = ["mss", "Pillow", "uiautomation; sys_platform == 'win32'"]
# ///
"""Klickrecorder: zeichnet Mausklicks mit Bildschirmfoto und Elementnamen auf.
Aus der Aufnahme baut aufnahme2tutorial.py eine Klickanleitung.

Start:   uv run klickrecorder.py <Name>      (oder start_klickrecorder.bat)
Tasten:  Strg+Alt+F  Foto (Bildschirm ohne Klick festhalten, z.B. ein Ergebnis)
         Strg+Alt+K  neues Kapitel (aus jedem Kapitel wird eine Anleitung)
         Strg+Alt+P  Pause / weiter
         Strg+Alt+S  Aufnahme beenden
Ausgabe: aufnahmen/<Datum>_<Name>/events.json und frames/*.png

Bewusst zurückhaltend, damit Virenscanner (Sophos) nicht anschlagen:
- keine Tastatur-Aufzeichnung und keine Hooks; die Maustasten werden
  abgefragt (GetAsyncKeyState), die vier Tastenkürzel sind normale
  Windows-Hotkeys (RegisterHotKey)
- Bildschirmfoto nur im Moment eines Klicks, kein Dauermitschnitt
Eingetippte Werte stehen deshalb nicht in der Aufnahme; sie kommen beim
Nacharbeiten aus der Aufgabenstellung.
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
VERWEILEN_S = 0.35
TASTEN = {0x01: "left", 0x02: "right", 0x04: "middle"}  # virtuelle Codes der Maustasten
HOTKEYS = {1: (0x46, "foto"), 2: (0x4B, "kapitel"), 3: (0x50, "pause"), 4: (0x53, "stopp")}  # F K P S
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
        self.letzter_klick = None
        self.maus = (0, 0, 0.0)
        self.verweilt = True
        self.n_frames = 0
        self.foto_q, self.speicher_q, self.uia_q = queue.Queue(), queue.Queue(), queue.Queue()

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
        print(f"  {ev['nr']:4d}  {ev['art']:<12} {el.get('name', '')}  [{el.get('typ', '')}]")

    # ---- Maus -------------------------------------------------------------
    def on_click(self, x, y, taste, pressed):
        if self.pause:
            return
        if not pressed:
            ev = self.unten.pop(taste, None)
            if ev and (abs(x - ev["x"]) > ZIEHEN_PX or abs(y - ev["y"]) > ZIEHEN_PX):
                ev.update(art="ziehen", taste=taste, x2=x, y2=y)
            return
        t, vor = self.zeit(), self.letzter_klick
        if (taste == "left" and vor and vor["art"] == "klick" and t - vor["t"] < DOPPELKLICK_S
                and abs(x - vor["x"]) < 6 and abs(y - vor["y"]) < 6):
            vor["art"] = "doppelklick"
            return
        ev = self.neu(KLICKART.get(taste, "klick"), x=x, y=y)
        self.letzter_klick = self.unten[taste] = ev
        self.foto_q.put(ev)
        self.uia_q.put((ev, x, y, "element"))

    def on_move(self, x, y):
        if (x, y) != self.maus[:2]:
            self.maus = (x, y, time.perf_counter())
            self.verweilt = False

    def maus_abfragen(self):
        """Maustasten und Position alle 10 ms abfragen (statt Hook)."""
        user32 = ctypes.windll.user32
        pt, gedrueckt = wt.POINT(), {t: False for t in TASTEN.values()}
        while not self.stopp.is_set():
            user32.GetCursorPos(ctypes.byref(pt))
            self.on_move(pt.x, pt.y)
            for vk, taste in TASTEN.items():
                jetzt = bool(user32.GetAsyncKeyState(vk) & 0x8000)
                if jetzt != gedrueckt[taste]:
                    gedrueckt[taste] = jetzt
                    self.on_click(pt.x, pt.y, taste, jetzt)
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
        elif not self.pause:
            if was == "kapitel":
                self.kapitel += 1
                self.neu("kapitel")
                print(f"  ==== Kapitel {self.kapitel} ====")
            else:
                ev = self.neu("foto", x=self.maus[0], y=self.maus[1])
                self.foto_q.put(ev)
                self.melden(ev)

    # ---- Hintergrund-Threads ----------------------------------------------
    def fotos(self):
        with mss.mss() as sct:
            monitore = sct.monitors[1:]
            while (ev := self.foto_q.get()) is not None:
                mon = next((m for m in monitore
                            if m["left"] <= ev["x"] < m["left"] + m["width"]
                            and m["top"] <= ev["y"] < m["top"] + m["height"]), monitore[0])
                shot = sct.grab(mon)
                self.n_frames += 1
                datei = f"frames/{self.n_frames:04d}.png"
                ev["frame"] = datei
                ev["monitor"] = {k: mon[k] for k in ("left", "top", "width", "height")}
                self.speicher_q.put((datei, shot))

    def speichern(self):
        while (item := self.speicher_q.get()) is not None:
            datei, shot = item
            Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX").save(
                self.ordner / datei, compress_level=6)

    def uia(self):
        if auto is None:  # ohne Windows: nur leeren
            while self.uia_q.get() is not None:
                pass
            return
        with auto.UIAutomationInitializerInThread():
            while (item := self.uia_q.get()) is not None:
                ev, x, y, art = item
                try:
                    info = element_info(auto.ControlFromPoint(x, y))
                    if art == "hover":
                        if info["typ"] != "MenuItemControl":
                            continue
                        ev = self.neu("hover", x=x, y=y, element=info)
                    else:
                        ev["element"] = info
                    self.melden(ev)
                except Exception as e:
                    if ev is not None:
                        ev["element_fehler"] = str(e)

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
    name = "_".join(sys.argv[1:]).strip() or "aufnahme"
    ordner = Path(__file__).resolve().parent / "aufnahmen" / f"{datetime.datetime.now():%Y-%m-%d_%H%M}_{name}"
    rec = Recorder(ordner)
    threads = {f: threading.Thread(target=f, daemon=True)
               for f in (rec.fotos, rec.speichern, rec.uia, rec.verweilen, rec.maus_abfragen, rec.hotkeys)}
    for th in threads.values():
        th.start()
    if auto is None:
        print("Hinweis: uiautomation fehlt, Elementnamen werden nicht erfasst.")
    print(f"Aufnahme läuft -> {ordner}")
    print("Strg+Alt+F Foto | Strg+Alt+K Kapitel | Strg+Alt+P Pause | Strg+Alt+S Ende\n")
    try:
        while not rec.stopp.wait(5):
            rec.schreiben()  # Zwischenstand sichern
    except KeyboardInterrupt:
        rec.stopp.set()
    ctypes.windll.user32.PostThreadMessageW(rec.hotkey_thread, 0x0012, 0, 0)  # WM_QUIT
    threads[rec.maus_abfragen].join()
    rec.foto_q.put(None)
    threads[rec.fotos].join()
    rec.speicher_q.put(None)
    rec.uia_q.put(None)
    print("Speichere Bilder ...")
    threads[rec.speichern].join()
    threads[rec.uia].join(timeout=5)
    rec.schreiben()
    print(f"\nFertig: {len(rec.events)} Ereignisse, {rec.n_frames} Bilder in\n  {ordner}")
    print("Weiter mit:  python aufnahme2tutorial.py <dieser Ordner>")


if __name__ == "__main__":
    main()
