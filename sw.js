self.addEventListener('push', function(e){
  var d = {};
  try { d = e.data ? e.data.json() : {} } catch(err) {}
  e.waitUntil(self.registration.showNotification(d.title || '小狗日记', {
    body: d.body || '',
    icon: './icon-192.png',
    data: { url: './index.html' }
  }));
});
self.addEventListener('notificationclick', function(e){
  e.notification.close();
  var url = (e.notification.data && e.notification.data.url) || './index.html';
  e.waitUntil(clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(l){
    for (var i = 0; i < l.length; i++) {
      if (l[i].url.indexOf(self.location.origin) === 0 && 'focus' in l[i]) return l[i].focus();
    }
    if (clients.openWindow) return clients.openWindow(url);
  }));
});
self.addEventListener('install', function(){ self.skipWaiting() });
self.addEventListener('activate', function(e){ e.waitUntil(self.clients.claim()) });
