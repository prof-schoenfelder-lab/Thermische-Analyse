// Zentrale Backend-Konfiguration für Antwortprüfung/Punkte-Synchronisation.
// Leer = lokaler Modus: Fragen funktionieren rein im Browser (localStorage),
// es gibt keinen Server-Abgleich und keinen OPAL-Login-Hinweis.
// Sobald ein eigenes Backend für diesen Kurs deployt ist (analog
// Strukturmechanik, z.B. unter /thermo/ auf fing-spool), hier eintragen:
// window.AC_BACKEND_URL = 'https://fing-spool.htwk-leipzig.de/thermo';
window.AC_BACKEND_URL = '';
// Direktlink zum LTI-Baustein im OPAL-Kurs (Login-Einstieg für Punkte-Sync)
// TODO: eintragen, sobald der OPAL-Kurs für diesen Kurs angelegt ist.
window.AC_OPAL_URL = '';
