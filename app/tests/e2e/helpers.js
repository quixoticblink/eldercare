// Shared helpers for the Kakis e2e suite. Everything here goes through the
// same surfaces a person uses (the UI) or the same API the frontend calls —
// there is no back door into the database from the tests.
const { expect } = require("@playwright/test");

const TINY_PNG = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==";
let counter = 0;
const RUN = Date.now().toString(36);

/** Unique identifier per run so specs never collide on the shared DB. */
function uniq(prefix) {
  counter += 1;
  return `${prefix}-${RUN}-${counter}@e2e.test`;
}

async function api(request, method, path, { token, data } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await request.fetch(`/api${path}`, { method, headers, data });
  const body = await res.json().catch(() => ({}));
  return { status: res.status(), body };
}

/** Sign in purely through the API (fast path for seeding). */
async function apiLogin(request, identifier, { role = null, name = null } = {}) {
  const req = await api(request, "POST", "/auth/request-code", { data: { identifier } });
  expect(req.status, `request-code ${identifier}: ${JSON.stringify(req.body)}`).toBe(200);
  const ver = await api(request, "POST", "/auth/verify", {
    data: { identifier, code: req.body.dev_code, role, name },
  });
  expect(ver.status, `verify ${identifier}: ${JSON.stringify(ver.body)}`).toBe(200);
  return { token: ver.body.token, user: ver.body.user };
}

/** Sign in through the real screens. Returns the user from /auth/me. */
async function signIn(page, identifier, { role = null, name = null } = {}) {
  await page.goto("/");
  await page.evaluate(() => localStorage.clear());
  await page.goto("/");
  await page.getByLabel("Email or mobile number").fill(identifier);
  await page.getByRole("button", { name: "Send my code" }).click();
  // DEV_MODE shows the code on screen; that is what the seniors saw on 21 Aug too.
  const code = (await page.locator(".card.warn b.mono").first().textContent()).trim();
  await page.locator("#codeIn").fill(code);
  if (name && (await page.locator("#nameIn").count())) {
    await page.locator("#nameIn").fill(name);
    if (role === "caregiver") await page.getByRole("button", { name: /A caregiver/ }).click();
    if (role === "kaki") await page.getByRole("button", { name: /A kaki/ }).click();
  }
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await page.waitForFunction(() => !!localStorage.getItem("kakis_token"));
}

async function approve(request, adminToken, userId, role) {
  const r = await api(request, "POST", `/admin/users/${userId}/approve`, { token: adminToken, data: { role } });
  expect(r.status).toBe(200);
}

/** Admin + two caregivers (with household and plan) + three kakis, all approved. */
async function seed(request) {
  const admin = await apiLogin(request, "admin@e2e.test", { name: "Coordinator" });
  const mk = async (prefix, role, name, extra = {}) => {
    const id = uniq(prefix);
    const u = await apiLogin(request, id, { role, name });
    await approve(request, admin.token, u.user.id, role);
    const again = await apiLogin(request, id); // fresh token after approval
    return { id, token: again.token, user: again.user, ...extra };
  };
  const cg1 = await mk("cg1", "caregiver", "Priya N.");
  const cg2 = await mk("cg2", "caregiver", "Hong Hang");
  const k1 = await mk("k1", "kaki", "Tan Bee Lian");
  const k2 = await mk("k2", "kaki", "Peggy Tien");
  const k3 = await mk("k3", "kaki", "Wong Boon");

  for (const [cg, senior, age, address] of [[cg1, "Mr Nathan", 78, "Blk 261A Toa Payoh"], [cg2, "Mdm Chan", 82, "Blk 170 Toa Payoh"]]) {
    await api(request, "PUT", "/care/household", { token: cg.token, data: { senior_name: senior, senior_age: age, address } });
    await api(request, "PUT", "/care/plan", { token: cg.token, data: { meds: "Metformin 2pm", mobility: "Walks with a stick", languages: ["Mandarin", "English"], contacts: "", notes: "Likes rummy-o" } });
  }
  for (const [k, services, languages] of [[k1, ["Companionship", "Household help"], ["Mandarin", "English"]], [k2, ["Chaperone"], ["English", "Malay"]], [k3, ["Companionship", "Chaperone"], ["Hokkien", "English"]]]) {
    await api(request, "PUT", "/users/me", { token: k.token, data: { services, languages, phone: "" } });
  }
  // Bee Lian has a profile photo (a 1×1 PNG); the others do not.
  await api(request, "PUT", "/users/me/photo", { token: k1.token, data: { data_url: TINY_PNG } });
  return { admin, cg1, cg2, k1, k2, k3 };
}

/** Put a token into the browser so the page loads signed in as that user. */
async function useToken(page, token, hash = "") {
  await page.goto("/");
  await page.evaluate(t => localStorage.setItem("kakis_token", t), token);
  // A hash-only navigation does not reload, so boot() would not run with the
  // new token. Set the hash, then reload so boot() sees both token and route.
  await page.goto("/" + hash);
  await page.reload();
  // App is a top-level const, so it is reachable by name but not as window.App.
  await page.waitForFunction(() => typeof App !== "undefined" && App.user && App.user.id);
}

/** YYYY-MM-DD, n days from today in local time. Bookings open only 30 days ahead. */
function dateIn(n) {
  const d = new Date(); d.setDate(d.getDate() + n);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

module.exports = { uniq, api, apiLogin, signIn, approve, seed, useToken, dateIn, TINY_PNG };
