"""MkDocs-Hook: sammelt die Bausteine für „Mein Spickzettel“ (Spickzettel.md, assets/js/spickzettel.js).

Kernaussagen: Schrittkästen mit data-spickzettel="ja" (die Zusammenfassungen), je Schritt Überschrift (titel)
und Text darunter (text), und Merke-Kästen (!!! merke "Titel") an beliebiger Stelle im Praktikum. Fehlersuche: die Punkte
einer Fehler-Checkliste (CHECKLISTE, in diesem Kurs noch keine), der Begriff in `…` vorne als Titel, der Rest als Text.
Jeder Baustein bekommt im Kurs eine id (kern-…, check-…), damit der Spickzettel dorthin verlinkt.
Ergebnis: assets/spickzettel.json im Site-Ordner, Links relativ zur Site-Wurzel.
"""
import json
import os
import re
from html import unescape

_BLOCK = re.compile(r'<div class="steps"[^>]*data-spickzettel="ja"[^>]*>')
_DIV = re.compile(r'<div\b|</div>')
_SCHRITT = re.compile(r'<div class="step">\s*<p class="step-title"[^>]*>(.*?)</p>(.*?)</div>', re.S)
_ABSATZ = re.compile(r'<p>(.*?)</p>', re.S)
_MERKE = re.compile(r'<div class="admonition merke">\s*<p class="admonition-title">(.*?)</p>(.*?)</div>', re.S)
_PUNKT = re.compile(r'<li class="task-list-item"><input type="checkbox"[^>]*>\s*(.*?)</li>', re.S)
CHECKLISTE = "00_FAQ/Fehler_checkliste/"

_kern, _check = [], []


def _text(html):
    return " ".join(unescape(re.sub(r"<[^>]+>", "", html)).split())


def _id(praefix, text):
    slug = re.sub(r"[^a-z0-9]+", "-", _text(text).lower().translate(str.maketrans("äöüß", "aous")))
    return praefix + "-" + slug.strip("-")[:60]


def on_pre_build(config, **kwargs):
    _kern.clear()  # mkdocs serve baut mehrfach
    _check.clear()


def on_page_content(html, page, config, files, **kwargs):
    if page.url == CHECKLISTE:
        def punkt(m):
            pid = _id("check", m.group(1))
            teile = re.match(r"\s*<code>(.*?)</code>(.*)", m.group(1), re.S)
            titel, text = (_text(teile.group(1)), _text(teile.group(2))) if teile else ("", _text(m.group(1)))
            if text.startswith("(") and text.endswith(")"):
                text = text[1:-1].strip()
            _check.append({"id": pid, "titel": titel, "text": text, "url": page.url + "#" + pid})
            return m.group(0).replace('<li class="task-list-item"', '<li class="task-list-item" id="%s"' % pid, 1)
        return _PUNKT.sub(punkt, html)
    p = re.match(r"P(\d+)_", page.url)
    praktikum = "P" + p.group(1) if p else ""

    def schritt(s):
        kid = _id("kern-" + praktikum.lower() if praktikum else "kern", s.group(1))
        _kern.append({"id": kid, "praktikum": praktikum, "titel": _text(s.group(1)),
                      "text": " ".join(_text(a) for a in _ABSATZ.findall(s.group(2))),
                      "url": page.url + "#" + kid})
        return s.group(0).replace('<div class="step">', '<div class="step" id="%s">' % kid, 1)
    def merke(s):
        kid = _id("kern-" + praktikum.lower() if praktikum else "kern", s.group(1))
        _kern.append({"id": kid, "praktikum": praktikum, "titel": _text(s.group(1)), "text": _text(s.group(2)),
                      "url": page.url + "#" + kid})
        return s.group(0).replace('<div class="admonition merke">', '<div class="admonition merke" id="%s">' % kid, 1)
    html = _MERKE.sub(merke, html)
    teile, pos = [], 0
    for m in _BLOCK.finditer(html):  # alle markierten Kästen der Seite
        tiefe, ende = 0, len(html)
        for t in _DIV.finditer(html, m.start()):
            tiefe += 1 if t.group(0) == "<div" else -1
            if tiefe == 0:
                ende = t.end()
                break
        teile += [html[pos:m.start()], _SCHRITT.sub(schritt, html[m.start():ende])]
        pos = ende
    return "".join(teile) + html[pos:]

def on_post_build(config, **kwargs):
    ziel = os.path.join(config["site_dir"], "assets", "spickzettel.json")
    os.makedirs(os.path.dirname(ziel), exist_ok=True)
    with open(ziel, "w", encoding="utf-8") as f:
        json.dump({"kernaussagen": _kern, "checkliste": _check}, f, ensure_ascii=False, indent=1)
