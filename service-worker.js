// ══════════════════════════════════════════════════
//  PLAN YOUR TRIP INDIA — Service Worker v2
//  Full offline support + background sync
// ══════════════════════════════════════════════════

const CACHE_VERSION = 'pyti-v4';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`;

const STATIC_ASSETS = [
  './',
  './index.html',
  './style.css',
  './script.js',
  './manifest.json',
  './logo.svg',
  'https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Lora:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
];

// ── INSTALL ──────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('[SW] Pre-caching static assets');
        return Promise.allSettled(STATIC_ASSETS.map(url => cache.add(url).catch(e => console.warn('[SW] Cache failed for:', url, e))));
      })
      .then(() => self.skipWaiting())
  );
});

// ── ACTIVATE ─────────────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(k => k !== STATIC_CACHE && k !== DYNAMIC_CACHE)
          .map(k => {
            console.log('[SW] Deleting old cache:', k);
            return caches.delete(k);
          })
      )
    ).then(() => self.clients.claim())
  );
});

// ── FETCH ────────────────────────────────────────
self.addEventListener('fetch', event => {
  const { request } = event;

  // Skip non-GET and browser-extension requests
  if (request.method !== 'GET') return;
  if (request.url.startsWith('chrome-extension://')) return;

  // Cache-first for static assets
  if (isStaticAsset(request.url)) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Network-first for images (with cache fallback)
  if (isImageRequest(request.url)) {
    event.respondWith(networkFirstWithCache(request, DYNAMIC_CACHE));
    return;
  }

  // Network-first for everything else
  event.respondWith(networkFirst(request));
});

function isStaticAsset(url) {
  return STATIC_ASSETS.some(asset => url.includes(asset)) ||
    url.endsWith('.css') || url.endsWith('.js') || url.endsWith('.json');
}

function isImageRequest(url) {
  return url.includes('unsplash.com') || url.includes('images.') ||
    url.match(/\.(jpg|jpeg|png|gif|webp|svg)(\?.*)?$/i);
}

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return offlineFallback(request);
  }
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok && response.type !== 'opaque') {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    return cached || offlineFallback(request);
  }
}

async function networkFirstWithCache(request, cacheName) {
  try {
    const response = await fetch(request);
    if (response.ok || response.type === 'opaque') {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    return cached || offlineFallback(request);
  }
}

function offlineFallback(request) {
  if (request.headers.get('Accept')?.includes('text/html')) {
    return caches.match('./index.html');
  }
  return new Response('Offline — Please connect to the internet.', {
    status: 503,
    headers: { 'Content-Type': 'text/plain' },
  });
}

// ── BACKGROUND SYNC ──────────────────────────────
self.addEventListener('sync', event => {
  if (event.tag === 'sync-contact') {
    event.waitUntil(syncContactMessages());
  }
});

async function syncContactMessages() {
  // Placeholder for real sync logic when reconnected
  console.log('[SW] Background sync triggered');
}

// ── PUSH NOTIFICATIONS ───────────────────────────
self.addEventListener('push', event => {
  if (!event.data) return;
  const data = event.data.json();
  event.waitUntil(
    self.registration.showNotification(data.title || 'Plan Your Trip India', {
      body: data.body || 'Your trip plan is ready!',
      icon: 'https://img.icons8.com/fluency/192/india.png',
      badge: 'https://img.icons8.com/fluency/96/india.png',
      data: { url: data.url || './' },
    })
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(clients.openWindow(event.notification.data?.url || './'));
});

console.log('[SW] Plan Your Trip India Service Worker v2 loaded');
