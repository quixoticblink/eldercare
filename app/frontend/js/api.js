/* M-CORE · api.js — the only file that talks to the network. */
const Api = (() => {
  const base = (window.KAKIS_API || "") + "/api";
  const tokenKey = "kakis_token";

  const getToken = () => localStorage.getItem(tokenKey) || "";
  const setToken = t => t ? localStorage.setItem(tokenKey, t) : localStorage.removeItem(tokenKey);

  async function call(method, path, body) {
    const headers = { "Content-Type": "application/json" };
    const t = getToken();
    if (t) headers["Authorization"] = "Bearer " + t;
    let res;
    try {
      res = await fetch(base + path, {
        method, headers, body: body === undefined ? undefined : JSON.stringify(body),
      });
    } catch (e) {
      throw new Error("Can't reach Kakis — check your connection");
    }
    let data = {};
    try { data = await res.json(); } catch (e) {}
    if (!res.ok) {
      if (res.status === 401) { setToken(null); }
      throw new Error(data.detail || "Something went wrong");
    }
    return data;
  }

  return {
    getToken, setToken,
    get: p => call("GET", p),
    post: (p, b) => call("POST", p, b ?? {}),
    put: (p, b) => call("PUT", p, b),
    del: p => call("DELETE", p),
  };
})();
