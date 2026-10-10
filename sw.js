const CACHE = "ironlog-cache-v4";
const ASSETS = ["/training-log/", "/training-log/index.html", "/training-log/manifest.webmanifest"];

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

  const isManifest = url.pathname === "/training-log/manifest.webmanifest";
  const isAppShell = url.pathname === "/training-log/" || url.pathname === "/training-log/index.html";
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
        return hit || caches.match("/training-log/index.html");
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
