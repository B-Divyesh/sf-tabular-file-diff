const CACHE = "tdiff-shell-v5";
const SHELL = ["/", "/demo/", "/privacy/", "/terms/", "/404.html", "/data-limited-hero.webp", "/favicon.svg", "/apple-touch-icon.png", "/playground/worker.js", "/playground/pyodide/pyodide.js"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key)))));
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET" || new URL(event.request.url).origin !== self.location.origin) return;
  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request).then((response) => {
        if (response.ok) caches.open(CACHE).then((cache) => cache.put(event.request, response.clone()));
        return response;
      }).catch(async () => (await caches.match(event.request, { ignoreVary: true })) || (await caches.match("/")))
    );
    return;
  }
  event.respondWith(
    caches.match(event.request, { ignoreVary: true }).then((cached) => cached || fetch(event.request).then((response) => {
      if (response.ok) caches.open(CACHE).then((cache) => cache.put(event.request, response.clone()));
      return response;
    }).catch(() => caches.match("/")))
  );
});
