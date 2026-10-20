// Service Worker der Hilfe-App: zeigt Push-Nachrichten an, ein Tipp öffnet die App
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));

self.addEventListener('push', e => {
  let d = {};
  try { d = e.data ? e.data.json() : {}; } catch (err) { d = { titel: 'Hilfe FEM-TD', text: e.data ? e.data.text() : '' }; }
  e.waitUntil(self.registration.showNotification(d.titel || 'Hilfe FEM-TD', {
    body: d.text || '',
    icon: 'icon-192.png',
    tag: 'hilfe-' + Date.now(),
  }));
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(ws => {
    for (const w of ws) if (w.url.indexOf('/thermo/hilfe/') !== -1) return w.focus();
    return self.clients.openWindow('./');
  }));
});
