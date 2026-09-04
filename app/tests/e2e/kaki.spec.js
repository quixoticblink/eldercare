// Kaki-side screens. Feature tasks append tests here.
const { test, expect } = require("@playwright/test");
const { seed, useToken, api } = require("./helpers");

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
      service: "Companionship", tier: "planned", date: "2026-12-04", window: "Morning 9–12", language: "English" } });
    await api(request, "POST", `/admin/visits/${v.body.id}/assign`, { token: s.admin.token, data: { kaki_id: s.k1.user.id } });
    await api(request, "POST", `/visits/${v.body.id}/accept`, { token: s.k1.token });
    await useToken(page, s.k1.token, `#/kaki/visit/${v.body.id}`);
    await page.getByRole("button", { name: "I'm on my way" }).click();
    await expect(page.getByText(/On the way since \d{2}:\d{2}/)).toBeVisible();
    await useToken(page, s.cg1.token, `#/care/visit/${v.body.id}`);
    await expect(page.getByText(/Tan Bee Lian is on the way — since \d{2}:\d{2}/)).toBeVisible();
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
