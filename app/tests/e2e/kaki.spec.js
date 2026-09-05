// Kaki-side screens. Feature tasks append tests here.
const { test, expect } = require("@playwright/test");
const { seed, useToken, api, dateIn, TINY_PNG } = require("./helpers");

test.describe("kaki home copy (Bucket 1 · 6)", () => {
  test("the kaki is told the app need not stay open", async ({ page, request }) => {
    const s = await seed(request);
    await useToken(page, s.k2.token, "#/kaki/home");
    await expect(page.getByText("You don't need to keep the app open")).toBeVisible();
    await expect(page.getByText("we message you when a visit is assigned")).toBeVisible();
  });
});

test.describe("on the way (Bucket 1 · 7)", () => {
  test("the kaki taps I'm on my way and the caregiver sees it", async ({ page, request }) => {
    const s = await seed(request);
    const v = await api(request, "POST", "/visits", { token: s.cg1.token, data: {
      service: "Companionship", tier: "planned", date: dateIn(6), window: "Morning 9–12", language: "English" } });
    await api(request, "POST", `/admin/visits/${v.body.id}/assign`, { token: s.admin.token, data: { kaki_id: s.k1.user.id } });
    await api(request, "POST", `/visits/${v.body.id}/accept`, { token: s.k1.token });
    await useToken(page, s.k1.token, `#/kaki/visit/${v.body.id}`);
    await page.getByRole("button", { name: "I'm on my way" }).click();
    await expect(page.getByText(/On the way since \d{2}:\d{2}/)).toBeVisible();
    await useToken(page, s.cg1.token, `#/care/visit/${v.body.id}`);
    await expect(page.getByText(/Tan Bee Lian is on the way — since \d{2}:\d{2}/)).toBeVisible();
  });
});

test.describe("start-code copy for the kaki (Bucket 1 · 9)", () => {
  test("the start card says the kaki never sees the code", async ({ page, request }) => {
    const s = await seed(request);
    const v = await api(request, "POST", "/visits", { token: s.cg2.token, data: {
      service: "Chaperone", tier: "planned", date: dateIn(8), window: "Morning 9–12", language: "English" } });
    await api(request, "POST", `/admin/visits/${v.body.id}/assign`, { token: s.admin.token, data: { kaki_id: s.k2.user.id } });
    await api(request, "POST", `/visits/${v.body.id}/accept`, { token: s.k2.token });
    await useToken(page, s.k2.token, `#/kaki/visit/${v.body.id}`);
    await expect(page.getByText("You will never see it in your own app")).toBeVisible();
  });
});

test.describe("availability by hours (Bucket 2 · 1)", () => {
  test("a kaki sets working hours per day instead of a grid", async ({ page, request }) => {
    const s = await seed(request);
    await useToken(page, s.k3.token, "#/kaki/availability");
    await expect(page.locator(".avail-grid")).toHaveCount(0);
    await page.locator("#day-Tue").check();
    await page.locator("#from-Tue").selectOption("09:00");
    await page.locator("#to-Tue").selectOption("13:00");
    await page.getByRole("button", { name: "Save my week" }).click();
    await expect(page.getByText("Availability saved")).toBeVisible();
    await page.reload();
    await expect(page.locator("#day-Tue")).toBeChecked();
    await expect(page.locator("#from-Tue")).toHaveValue("09:00");
    await expect(page.locator("#to-Tue")).toHaveValue("13:00");
    await expect(page.locator("#day-Wed")).not.toBeChecked();
  });
});

test.describe("profile photo (Bucket 2 · 2)", () => {
  test("a kaki adds a photo from the profile and the caregiver sees it on the visit", async ({ page, request }) => {
    const s = await seed(request);
    await useToken(page, s.k2.token, "#/kaki/profile");
    await expect(page.getByText("Add a photo")).toBeVisible();
    await page.locator("#photoIn").setInputFiles({ name: "me.png", mimeType: "image/png",
      buffer: Buffer.from(TINY_PNG.split(",")[1], "base64") });
    await expect(page.getByText("Photo saved")).toBeVisible();
    await page.reload();
    await expect(page.locator(".face img")).toBeVisible();
    const v = await api(request, "POST", "/visits", { token: s.cg2.token, data: {
      service: "Chaperone", tier: "planned", date: dateIn(4), start_time: "09:00", end_time: "11:00", language: "English" } });
    await api(request, "POST", `/admin/visits/${v.body.id}/assign`, { token: s.admin.token, data: { kaki_id: s.k2.user.id } });
    await useToken(page, s.cg2.token, `#/care/visit/${v.body.id}`);
    await expect(page.locator(".kp-face img")).toBeVisible();
  });
});

test.describe("kaki", () => {
  test("home and profile render for an approved kaki", async ({ page, request }) => {
    const s = await seed(request);
    await useToken(page, s.k1.token);
    await expect(page.getByText("Your visits")).toBeVisible();
    await page.goto("/#/kaki/profile");
    await expect(page.getByText("My profile")).toBeVisible();
    await expect(page.getByRole("button", { name: "Companionship" })).toHaveClass(/sel/);
  });
});
