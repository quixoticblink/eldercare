// Coordinator screens. Feature tasks append tests here.
const { test, expect } = require("@playwright/test");
const { seed, useToken, api } = require("./helpers");

test.describe("coordinator", () => {
  test("today console and matching roster render", async ({ page, request }) => {
    const s = await seed(request);
    const v = await api(request, "POST", "/visits", { token: s.cg1.token, data: {
      service: "Companionship", tier: "planned", date: "2026-10-06", window: "Afternoon 2–5", language: "Mandarin", notes: "" } });
    expect(v.status).toBe(200);
    await useToken(page, s.admin.token);
    await expect(page.getByText("Coordinator console")).toBeVisible();
    await page.goto("/#/admin/requests");
    await expect(page.getByText("Choose one kaki")).toBeVisible();
    await expect(page.getByText("Tan Bee Lian")).toBeVisible();
  });
});
