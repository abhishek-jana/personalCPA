// When running via Vite dev server, calls are proxied to http://localhost:8000
// When running via FastAPI unified serving, relative paths work directly.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export { API_BASE_URL };
