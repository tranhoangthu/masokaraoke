const CACHE_NAME = 'karaoke-vn-v2.4.1';
const CORE_ASSETS = [
  './',
  './index.html',
  './style.css',
  './app.js',
  './version.json',
  './manifest.json',
  './favicon.png',
  './icons/favicon-32.png',
  './icons/icon-192.png',
  './icons/hoangthulogo.jpg',
  './icons/ic_launcher_list.png',
  './icons/header_logo.png',
  './icons/header_karaoke.png',
  './icons/ic_back_to_menu.png',
  './icons/menu_favorite.png',
  './icons/menu_lyric.png',
  './icons/arirang5.png',
  './icons/arirang7.png',
  './icons/sonca6.png',
  './icons/musiccore5.png',
  './icons/paramax5.png',
  './icons/Logo-Paramax.jpg',
  './icons/california6.png',
  './icons/vietktv6.png',
  './icons/vitekvtb6.png',
  './icons/ic_vitek.png',
  './icons/DONGHAI.jpg',
  './data/arirang.js',
  './data/musiccore.js',
  './data/california.js',
  './data/vietktv.js',
  './data/paramax.js',
  './data/vitek.js',
  './data/acnos.js',
  './data/donghai.js',
  './sweetalert2.all.min.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(CORE_ASSETS).catch((err) => {
        console.warn('Some assets failed to precache:', err);
      });
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);

  // Network-first for version.json so update checks are always live
  if (url.pathname.endsWith('version.json')) {
    event.respondWith(
      fetch(event.request)
        .then((res) => {
          if (res && res.status === 200) {
            const clone = res.clone();
            caches.open(CACHE_NAME).then((c) => c.put(event.request, clone));
          }
          return res;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  if (url.origin !== self.location.origin) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        return cached || fetch(event.request).catch(() => null);
      })
    );
    return;
  }

  // Stale-while-revalidate for local assets
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        fetch(event.request)
          .then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200) {
              caches.open(CACHE_NAME).then((cache) => cache.put(event.request, networkResponse));
            }
          })
          .catch(() => {});
        return cachedResponse;
      }

      return fetch(event.request).then((networkResponse) => {
        if (!networkResponse || networkResponse.status !== 200) {
          return networkResponse;
        }
        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
        return networkResponse;
      }).catch(() => {
        if (event.request.destination === 'document') {
          return caches.match('./index.html');
        }
      });
    })
  );
});
