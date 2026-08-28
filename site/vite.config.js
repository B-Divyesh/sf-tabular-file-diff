import { resolve } from "node:path";
import { readFileSync } from "node:fs";
import { defineConfig } from "vite";

const siteRoot = import.meta.dirname;
const outputRoot = resolve(siteRoot, "../dist/site");
const publicRoutes = new Set(["/", "/demo", "/demo/", "/privacy", "/privacy/", "/terms", "/terms/", "/404.html"]);

const preview404 = {
  name: "tdiff-preview-404",
  configurePreviewServer(server) {
    server.middlewares.use((request, response, next) => {
      const pathname = new URL(request.url ?? "/", "http://localhost").pathname;
      const acceptsHtml = request.headers.accept?.includes("text/html");
      if (request.method === "GET" && acceptsHtml && !publicRoutes.has(pathname) && !pathname.includes(".")) {
        response.statusCode = 404;
        response.setHeader("Content-Type", "text/html; charset=utf-8");
        response.end(readFileSync(resolve(outputRoot, "404.html")));
        return;
      }
      next();
    });
  }
};

export default defineConfig({
  appType: "mpa",
  root: resolve(siteRoot),
  publicDir: resolve(siteRoot, "public"),
  plugins: [preview404],
  build: {
    outDir: outputRoot,
    emptyOutDir: true,
    target: "es2022",
    cssCodeSplit: true,
    rollupOptions: {
      input: {
        main: resolve(siteRoot, "index.html"),
        demo: resolve(siteRoot, "demo/index.html"),
        privacy: resolve(siteRoot, "privacy/index.html"),
        terms: resolve(siteRoot, "terms/index.html"),
        notFound: resolve(siteRoot, "404.html")
      }
    }
  }
});
