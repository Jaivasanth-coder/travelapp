// ProShop Service Worker
// Caches the app shell so it loads instantly and works offline.
// API calls are always fetched live (network-first).

const CACHE_NAME = 'proshop-v1';

// Files to cache on install (app shell)
const SHELL_URLS = [
  '/',
  '/index.html',
  'https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Lato:wght@300;400;700&display=swap',
  'https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js'
];

// ── Install: cache the app shell ──────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(SHELL_URLS).catch(err => {
        console.warn('SW: Some shell files could not be cached:', err);
      });
    })
  );
  self.skipWaiting();
});

// ── Activate: remove old caches ───────────────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// ── Fetch: network-first for API, cache-first for app shell ──────────
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Always go live for API calls — never serve stale order/product data
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request).catch(() =>
        new Response(JSON.stringify({ error: 'Offline – please check your connection' }), {
          headers: { 'Content-Type': 'application/json' }
        })
      )
    );
    return;
  }

  // Cache-first for app shell (HTML, fonts, QRCode lib)
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).then(response => {
        // Cache valid GET responses
        if (event.request.method === 'GET' && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => {
        // Offline fallback for navigation requests
        if (event.request.mode === 'navigate') {
          return caches.match('/') || caches.match('/index.html');
        }
      });
    })
  );
});
