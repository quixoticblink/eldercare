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

test.describe("booking form (Bucket 1 · 3)", () => {
  test("a refresh keeps the caregiver on the same step; required and optional fields are marked", async ({ page, request }) => {
    const s = await seed(request);
    await useToken(page, s.cg1.token, "#/care/book");
    await page.getByRole("button", { name: /Companionship/ }).click();
    await page.getByRole("button", { name: /Planned/ }).click();
    await expect(page.getByText("Step 3 of 3")).toBeVisible();
    await page.reload();
    await expect(page.getByText("Step 3 of 3")).toBeVisible();
    await expect(page.locator(".appbar")).toContainText("Companionship");
    await expect(page.locator("label", { hasText: "Date" })).toContainText("required");
    await expect(page.locator("label", { hasText: "Time" })).toContainText("required");
    await expect(page.locator("label", { hasText: "Anything the kaki should know" })).toContainText("optional");
    // Back goes to the previous step, not to step 1.
    await page.locator(".appbar .back").click();
    await expect(page.getByText("Step 2 of 3")).toBeVisible();
  });
});

test.describe("urgent window after 5pm (Bucket 1 · 4)", () => {
  test("an urgent booking at 18:30 never offers 2–5pm", async ({ page, request }) => {
    const s = await seed(request);
    await page.clock.install({ time: new Date("2026-09-10T18:30:00+08:00") });
    await useToken(page, s.cg1.token, "#/care/book");
    await page.getByRole("button", { name: /Companionship/ }).click();
    await page.getByRole("button", { name: /Urgent/ }).click();
    await page.getByRole("button", { name: "Skip — just need help" }).click();
    await expect(page.getByRole("button", { name: "Within the hour" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Today, 2–5pm" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Today, 6–9pm" })).toBeVisible();
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
