// Caregiver-side screens. Feature tasks append tests here.
const { test, expect } = require("@playwright/test");
const { seed, useToken } = require("./helpers");

test.describe("caregiver", () => {
  test("home renders for an approved caregiver", async ({ page, request }) => {
    const s = await seed(request);
    await useToken(page, s.cg1.token);
    await expect(page.getByText("Caring for Mr Nathan")).toBeVisible();
    await expect(page.getByRole("button", { name: /Book a visit for Mr Nathan/ })).toBeVisible();
  });
});
