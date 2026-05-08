/**
 * EduCore Service Worker
 * Handles pre-caching, fetch interception, and background sync.
 */

const CACHE_NAME = 'educore-static-v18';
const CORE_ROUTES = [
    '/',
    '/analytics/dashboard/',
    '/attendance/',
    '/fees/',
    '/notifications/',
    '/academics/classes/',
    '/offline/'
];

const STATIC_ASSETS = [
    ...CORE_ROUTES,
    '/static/css/style.css',
    '/static/js/db.js',
    '/static/js/sync.js',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css',
    'https://cdn.jsdelivr.net/npm/tom-select@2.2.2/dist/css/tom-select.bootstrap5.css',
    'https://cdn.jsdelivr.net/npm/tom-select@2.2.2/dist/js/tom-select.complete.min.js',
    'https://unpkg.com/htmx.org@1.9.10'
];

// 1. Install
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return Promise.allSettled(
                STATIC_ASSETS.map(url => {
                    return fetch(url).then(response => {
                        if (response.ok) return cache.put(url, response);
                    }).catch(() => {});
                })
            );
        })
    );
    self.skipWaiting();
});

// 2. Activate
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.filter((key) => key !== CACHE_NAME && !key.startsWith('api-'))
                    .map((key) => caches.delete(key))
            );
        }).then(() => self.clients.claim())
    );
});

// 3. Fetch - Instant Offline Shell
self.addEventListener('fetch', (event) => {
    try {
        const url = new URL(event.request.url);
        if (url.origin !== self.location.origin && !url.hostname.includes('cdn') && !url.hostname.includes('unpkg')) return;

        // Handle POST/PUT/DELETE requests offline
        if (event.request.method !== 'GET') {
            event.respondWith(
                fetch(event.request).catch(() => {
                    // If network fails (Server down), return a fake success 200
                    // This allows sync.js to handle the offline storage without the browser showing an error
                    return new Response(JSON.stringify({ status: 'offline_queued' }), {
                        status: 200,
                        headers: { 'Content-Type': 'application/json' }
                    });
                })
            );
            return;
        }

        // DEFINE isHtmlRequest (This was missing in v13)
        const isHtmlRequest = event.request.mode === 'navigate' || 
                             (event.request.headers.get('accept') && 
                              event.request.headers.get('accept').includes('text/html'));

        if (isHtmlRequest) {
            event.respondWith(
                caches.match(event.request, { ignoreSearch: true }).then((cachedResponse) => {
                    // Try to get fresh data from network
                    const networkFetch = fetch(event.request).then((networkResponse) => {
                        if (networkResponse.ok) {
                            const copy = networkResponse.clone();
                            caches.open(CACHE_NAME).then(cache => cache.put(event.request, copy));
                        }
                        return networkResponse;
                    }).catch((err) => {
                        // If network fails, we'll return the cached response (if we have one)
                        // or fallback to the dashboard
                        if (cachedResponse) return cachedResponse;
                        return caches.match('/analytics/dashboard/') || caches.match('/offline/');
                    });

                    // If we have a cached version, show it instantly while the network update happens
                    // This is the "Stale-While-Revalidate" pattern for pages
                    return cachedResponse || networkFetch;
                })
            );
            return;
        }

        // Assets & API
        event.respondWith(
            caches.match(event.request).then((cachedResponse) => {
                if (cachedResponse) return cachedResponse;
                return fetch(event.request).then((response) => {
                    if (response.ok && event.request.method === 'GET') {
                        const copy = response.clone();
                        caches.open(url.pathname.startsWith('/api/') ? 'api-cache' : CACHE_NAME).then(cache => cache.put(event.request, copy));
                    }
                    return response;
                }).catch(() => {
                    if (url.pathname.endsWith('.js')) return new Response('console.log("Offline")', { headers: {'Content-Type': 'application/javascript'} });
                    return new Response('', { status: 200 });
                });
            })
        );
    } catch (e) {
        console.error("SW Fetch Error:", e);
    }
});

// 4. Background Sync - Flush the queue when back online
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-queue') {
        console.log('Background Sync triggered');
        // The actual syncing logic is in sync.js, but we could trigger it from here too
        // if we use a more complex message passing system.
    }
});
