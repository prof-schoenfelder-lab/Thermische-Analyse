"""MkDocs-Hook: entfernt Antworten aus dem ausgelieferten HTML.

Beim Build werden aus allen Fragen (.numeric-question / .multiple-choice-question)
die Attribute data-answer, data-tolerance und data-correct entfernt und
stattdessen eine stabile data-qid vergeben. Die Antworten landen gesammelt in
answers.json im Projektroot (NICHT im site-Output!) — diese Datei gehört auf
das Backend (siehe backend/DEPLOY.md).

Die qid entspricht dem bisherigen Client-Schema, damit vorhandene
localStorage-Einträge gültig bleiben: <site-pfad>/<seite>:q<i> bzw. :mc<i>.
"""

import json
import os
import re
from urllib.parse import urlsplit

_answers = {}

# Ohne konfiguriertes Backend (AC_BACKEND_URL leer in backend-config.js) bleiben
# die Antworten im HTML — die Prüfung läuft dann rein lokal im Browser.
_strip = None


def _backend_configured(config):
    global _strip
    if _strip is None:
        path = os.path.join(
            os.path.dirname(config["config_file_path"]),
            "docs", "assets", "js", "backend-config.js",
        )
        try:
            with open(path) as f:
                m = re.search(
                    r"^\s*window\.AC_BACKEND_URL\s*=\s*'([^']*)'",
                    f.read(), re.MULTILINE,
                )
            _strip = bool(m and m.group(1).strip())
        except OSError:
            _strip = True
    return _strip

_TAG_RE = re.compile(
    r'<div\b[^>]*class="[^"]*\b(numeric-question|multiple-choice-question)\b[^"]*"[^>]*>'
)
_ATTR_RE = re.compile(r'\s*data-(answer|tolerance|correct)="([^"]*)"')


def _attr(tag, name, default=""):
    m = re.search(r'data-' + name + r'="([^"]*)"', tag)
    return m.group(1) if m else default


def on_page_content(html, page, config, files):
    prefix = urlsplit(config["site_url"]).path.rstrip("/")
    page_path = (prefix + "/" + page.url).rstrip("/")
    counters = {"numeric-question": 0, "multiple-choice-question": 0}

    def replace(m):
        tag, cls = m.group(0), m.group(1)
        idx = counters[cls]
        counters[cls] += 1
        qid = page_path + (":q" if cls == "numeric-question" else ":mc") + str(idx)

        entry = {
            "points": float(_attr(tag, "points", "1") or 1),
            "attempts": int(_attr(tag, "attempts", "5") or 5),
        }
        if cls == "numeric-question":
            try:
                entry["answer"] = float(_attr(tag, "answer").replace(",", "."))
            except ValueError:
                return tag  # kein/kaputtes data-answer: Frage unverändert lassen
            entry["tolerance"] = float(_attr(tag, "tolerance", "0").replace(",", ".") or 0)
        else:
            correct = [s.strip() for s in _attr(tag, "correct").split(",") if s.strip()]
            if not correct:
                return tag
            entry["correct"] = correct
        _answers[qid] = entry

        if not _backend_configured(config):
            return tag[:-1] + ' data-qid="' + qid + '">'
        stripped = _ATTR_RE.sub("", tag)
        return stripped[:-1] + ' data-qid="' + qid + '">'

    return _TAG_RE.sub(replace, html)


def on_post_build(config):
    out = os.path.join(os.path.dirname(config["config_file_path"]), "answers.json")
    with open(out, "w") as f:
        json.dump(_answers, f, indent=1, ensure_ascii=False, sort_keys=True)
    print(f"answers_hook: {len(_answers)} Fragen -> {out} (aufs Backend kopieren!)")

    # Öffentlicher Fragenkatalog (ohne Antworten) für Fortschrittsseite/Badges
    # im lokalen Modus (kein Backend konfiguriert).
    catalog = {
        qid: {"points": e["points"], "attempts": e["attempts"]}
        for qid, e in _answers.items()
    }
    cat_out = os.path.join(config["site_dir"], "assets", "qcatalog.json")
    os.makedirs(os.path.dirname(cat_out), exist_ok=True)
    with open(cat_out, "w") as f:
        json.dump(catalog, f, ensure_ascii=False, sort_keys=True)
