const CACHE = "ironlog-cache-v6";
const BASE = new URL("./", self.location.href);
const ASSETS = [
  new URL("./", BASE).href,
  new URL("./index.html", BASE).href,
  new URL("./manifest.webmanifest", BASE).href,
  new URL("./icon-192.png", BASE).href,
  new URL("./icon-512.png", BASE).href
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE)
      .then(cache => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;

  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  const manifestUrl = new URL("./manifest.webmanifest", BASE);
  const rootUrl = new URL("./", BASE);
  const indexUrl = new URL("./index.html", BASE);

  const isManifest = url.pathname === manifestUrl.pathname;
  const isAppShell = url.pathname === rootUrl.pathname || url.pathname === indexUrl.pathname;
  const isNavigation = event.request.mode === "navigate";

  if (isManifest || isAppShell || isNavigation) {
    event.respondWith(
      fetch(event.request).then(response => {
        if (response.ok) {
          caches.open(CACHE).then(cache => cache.put(event.request, response.clone()));
        }
        return response;
      }).catch(async () => {
        const hit = await caches.match(event.request);
        return hit || caches.match(indexUrl.href);
      })
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then(hit => hit || fetch(event.request).then(response => {
      if (response.ok) {
        caches.open(CACHE).then(cache => cache.put(event.request, response.clone()));
      }
      return response;
    }))
  );
});
