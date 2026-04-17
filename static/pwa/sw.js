// EduCore Service Worker — v1.0
const CACHE_NAME = 'educore-v1';
const OFFLINE_URL = '/offline/';

const PRECACHE_URLS = [
  '/', '/offline/', '/analytics/dashboard/',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache =>
      cache.addAll(PRECACHE_URLS).catch(e => console.warn('Pre-cache error:', e))
    ).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  if (request.method !== 'GET') return;
  if (url.pathname.includes('/api/') || url.pathname.includes('/admin/')) return;

  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).then(res => {
        caches.open(CACHE_NAME).then(c => c.put(request, res.clone()));
        return res;
      }).catch(() => caches.match(request).then(c => c || caches.match(OFFLINE_URL)))
    );
    return;
  }

  if (url.pathname.startsWith('/static/') || url.hostname.includes('cdn.jsdelivr.net')) {
    event.respondWith(
      caches.match(request).then(c => c || fetch(request).then(res => {
        caches.open(CACHE_NAME).then(cache => cache.put(request, res.clone()));
        return res;
      }))
    );
    return;
  }

  event.respondWith(
    fetch(request).then(res => {
      if (res.ok) caches.open(CACHE_NAME).then(c => c.put(request, res.clone()));
      return res;
    }).catch(() => caches.match(request).then(c => c || caches.match(OFFLINE_URL)))
  );
});

self.addEventListener('sync', event => {
  if (event.tag === 'sync-attendance') event.waitUntil(syncAttendance());
});

async function syncAttendance() {
  try {
    const db = await new Promise((res, rej) => {
      const r = indexedDB.open('educore_attendance', 1);
      r.onupgradeneeded = e => e.target.result.createObjectStore('records', {keyPath:'id'});
      r.onsuccess = e => res(e.target.result);
      r.onerror = e => rej(e.target.error);
    });
    const records = await new Promise((res, rej) => {
      const tx = db.transaction('records','readonly');
      const req = tx.objectStore('records').getAll();
      req.onsuccess = e => res(e.target.result);
      req.onerror = e => rej(e.target.error);
    });
    if (!records.length) return;
    const sessions = {};
    records.forEach(r => {
      const key = r.classId+'_'+r.date;
      if (!sessions[key]) sessions[key] = {class_section_id:r.classId, date:r.date, records:[]};
      sessions[key].records.push({student_id:r.studentId, status:r.status, notes:r.notes||''});
    });
    const resp = await fetch('/attendance/api/sync/', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({sessions: Object.values(sessions)})
    });
    if (resp.ok) {
      const tx = db.transaction('records','readwrite');
      records.forEach(r => tx.objectStore('records').delete(r.id));
      console.log('Offline attendance synced.');
    }
  } catch(e) { console.error('Sync error:', e); }
}
