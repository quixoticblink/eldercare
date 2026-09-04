// Kaki-side screens. Feature tasks append tests here.
const { test, expect } = require("@playwright/test");
const { seed, useToken } = require("./helpers");

test.describe("kaki home copy (Bucket 1 · 6)", () => {
  test("the kaki is told the app need not stay open", async ({ page, request }) => {
    const s = await seed(request);
    await useToken(page, s.k2.token, "#/kaki/home");
    await expect(page.getByText("You don't need to keep the app open")).toBeVisible();
    await expect(page.getByText("we message you when a visit is assigned")).toBeVisible();
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
