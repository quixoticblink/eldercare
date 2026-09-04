// Caregiver-side screens. Feature tasks append tests here.
const { test, expect } = require("@playwright/test");
const { seed, useToken, signIn, uniq } = require("./helpers");

test.describe("sign-in and approval (Bucket 1 · 1, 2)", () => {
  test("the sign-in field has no placeholder number, only a hint", async ({ page }) => {
    await page.goto("/");
    const field = page.getByLabel("Email or mobile number");
    await expect(field).toHaveAttribute("placeholder", "");
    await expect(page.locator(".f-hint")).toHaveText("Email address, or mobile number like 9123 4567");
  });

  test("the waiting screen says there is nothing to do", async ({ page }) => {
    await signIn(page, uniq("wait"), { role: "caregiver", name: "Aunty Rose" });
    await expect(page.getByRole("heading", { name: "Nothing to do right now" })).toBeVisible();
    await expect(page.getByText("we'll message you when you're approved")).toBeVisible();
  });
});

test.describe("caregiver", () => {
  test("home renders for an approved caregiver", async ({ page, request }) => {
    const s = await seed(request);
    await useToken(page, s.cg1.token);
    await expect(page.getByText("Caring for Mr Nathan")).toBeVisible();
    await expect(page.getByRole("button", { name: /Book a visit for Mr Nathan/ })).toBeVisible();
  });
});
