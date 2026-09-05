// Caregiver-side screens. Feature tasks append tests here.
const { test, expect } = require("@playwright/test");
const { seed, useToken, signIn, uniq, api, dateIn } = require("./helpers");

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

test.describe("time to match (Bucket 1 · 5)", () => {
  test("a requested visit says how long matching usually takes", async ({ page, request }) => {
    const s = await seed(request);
    const v = await api(request, "POST", "/visits", { token: s.cg1.token, data: {
      service: "Companionship", tier: "urgent", date: "today", window: "Within the hour", language: "English" } });
    await useToken(page, s.cg1.token, `#/care/visit/${v.body.id}`);
    await expect(page.getByText("Usually matched within the hour")).toBeVisible();
    await expect(page.getByText("We'll message you the moment a kaki is confirmed")).toBeVisible();
  });
});

test.describe("languages (Bucket 1 · 8)", () => {
  test("the booking starts from the care plan's languages and allows more than one", async ({ page, request }) => {
    const s = await seed(request);   // cg1's plan: Mandarin, English
    await useToken(page, s.cg1.token, "#/care/book");
    await page.getByRole("button", { name: /Companionship/ }).click();
    await page.getByRole("button", { name: /Planned/ }).click();
    const group = page.locator("#langG2");
    await expect(group.getByRole("button", { name: "Mandarin" })).toHaveClass(/sel/);
    await expect(group.getByRole("button", { name: "English" })).toHaveClass(/sel/);
    await expect(group.getByRole("button", { name: "Cantonese" })).toBeVisible();
    await group.getByRole("button", { name: "Cantonese" }).click();
    await expect(group.getByRole("button", { name: "Mandarin" })).toHaveClass(/sel/);   // multi-select keeps the others
    await page.locator("#date").fill(dateIn(7));
    await page.getByRole("button", { name: "Morning 9–12" }).click();
    await page.getByRole("button", { name: "Request this visit" }).click();
    await expect(page).toHaveURL(/#\/care\/visit\//);
    await expect(page.locator(".appbar, .row").first()).toBeVisible();
    await expect(page.getByText("English, Mandarin, Cantonese")).toBeVisible();
  });
});

test.describe("care plan, profile, start-code copy (Bucket 1 · 9)", () => {
  test("care plan sits above visits, has Bedridden and split contacts; profile is editable; start code explains itself", async ({ page, request }) => {
    const s = await seed(request);
    const v = await api(request, "POST", "/visits", { token: s.cg1.token, data: {
      service: "Companionship", tier: "planned", date: dateIn(8), window: "Morning 9–12", language: "English" } });
    await api(request, "POST", `/admin/visits/${v.body.id}/assign`, { token: s.admin.token, data: { kaki_id: s.k1.user.id } });

    await useToken(page, s.cg1.token, "#/care/home");
    const screen = await page.locator("#screen").textContent();   // innerText would be uppercased by the eyebrow style
    expect(screen.indexOf("Care plan")).toBeLessThan(screen.indexOf("Current visits"));
    await page.getByRole("button", { name: /care plan/ }).click();
    await expect(page.getByRole("button", { name: "Bedridden" })).toBeVisible();
    await page.locator("#cName").fill("Ravi");
    await page.locator("#cRel").fill("Son");
    await page.locator("#cPhone").fill("9111 2222");
    await page.getByRole("button", { name: "Save care plan" }).click();
    await expect(page.getByText("Caring for Mr Nathan")).toBeVisible();

    await page.getByRole("button", { name: /Your profile/ }).click();
    await page.locator("#pname").fill("Priya Nathan");
    await page.getByRole("button", { name: "Save profile" }).click();
    await expect(page.getByText("Profile saved")).toBeVisible();

    await page.goto(`/#/care/visit/${v.body.id}`);
    await expect(page.getByText("Only you can see this code")).toBeVisible();
  });
});

test.describe("'Other' trigger and booking horizon (Bucket 1 · 10)", () => {
  test("a caregiver can type their own reason; the date picker stops at the horizon", async ({ page, request }) => {
    const s = await seed(request);
    await useToken(page, s.cg1.token, "#/care/book");
    await page.getByRole("button", { name: /Companionship/ }).click();
    await page.getByRole("button", { name: /Soon/ }).click();
    await page.locator("#otherTxt").fill("Cataract op");
    await page.getByRole("button", { name: "Other — tell us" }).click();
    await expect(page.locator(".appbar")).toContainText("Other: Cataract op");
    await page.getByRole("button", { name: "Request this visit" }).click();
    await expect(page.locator(".pill.gold", { hasText: "Other: Cataract op" })).toBeVisible();

    await page.goto("/#/care/book");
    await page.getByRole("button", { name: /Companionship/ }).click();
    await page.getByRole("button", { name: /Planned/ }).click();
    const max = await page.locator("#date").getAttribute("max");
    const expected = new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10);
    expect(max).toBe(expected);
    await expect(page.getByText("up to 30 days ahead")).toBeVisible();
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
