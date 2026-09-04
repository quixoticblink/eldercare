// Kaki-side screens. Feature tasks append tests here.
const { test, expect } = require("@playwright/test");
const { seed, useToken } = require("./helpers");

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
