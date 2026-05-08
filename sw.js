/**
 * EduCore Service Worker
 * Handles pre-caching, fetch interception, and background sync.
 */

const CACHE_NAME = 'educore-static-v2';
const STATIC_ASSETS = [
    '/',
    '/static/css/style.css',
    '/static/js/db.js',
    '/static/js/sync.js',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png',
    '/offline/',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css',
    'https://cdn.jsdelivr.net/npm/tom-select@2.2.2/dist/css/tom-select.bootstrap5.css',
    'https://unpkg.com/htmx.org@1.9.10'
];

// 1. Install Event - Pre-cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('Pre-caching static assets');
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

// 2. Activate Event - Cleanup old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.filter((key) => key !== CACHE_NAME)
                    .map((key) => caches.delete(key))
            );
        })
    );
    self.clients.claim();
});

// 3. Fetch Event - Network-first for API, Cache-first for static
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // API calls: Network-first with cache fallback
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(event.request)
                .then((response) => {
                    // Update cache with fresh API data
                    const responseClone = response.clone();
                    caches.open('api-cache').then((cache) => {
                        cache.put(event.request, responseClone);
                    });
                    return response;
                })
                .catch(() => {
                    // Fallback to cache if network fails
                    return caches.match(event.request);
                })
        );
        return;
    }

    // Static assets: Cache-first
    event.respondWith(
        caches.match(event.request).then((cachedResponse) => {
            if (cachedResponse) return cachedResponse;

            return fetch(event.request).then((response) => {
                // Don't cache non-GET requests or responses from other origins
                if (event.request.method !== 'GET' || !response || response.status !== 200) {
                    return response;
                }

                const responseToCache = response.clone();
                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(event.request, responseToCache);
                });

                return response;
            }).catch(() => {
                // If everything fails and it's a page navigation, show offline page
                if (event.request.mode === 'navigate') {
                    return caches.match('/offline/');
                }
            });
        })
    );
});

// 4. Background Sync - Flush the queue when back online
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-queue') {
        console.log('Background Sync triggered');
        // The actual syncing logic is in sync.js, but we could trigger it from here too
        // if we use a more complex message passing system.
    }
});
