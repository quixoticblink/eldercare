// v1.8 — the befrienders' round (Lions Befrienders, 11 Sept). Small fixes,
// each one behind a test that drives the real screens.
const { test, expect } = require("@playwright/test");
const { api, seed, useToken, dateIn } = require("./helpers");

test.describe("service mismatch on assign (L9.1)", () => {
  test("the console warns when the kaki does not offer the service, and records the override", async ({ page, request }) => {
    const { admin, cg1, k2 } = await seed(request);          // k2 = Peggy Tien, Chaperone only
    const v = await api(request, "POST", "/visits", { token: cg1.token, data: { service: "Household help", tier: "planned", date: dateIn(2), start_time: "10:00", end_time: "12:00", languages: ["English"] } });
    await useToken(page, admin.token, "#/admin/requests");
    const row = page.locator(`input[name="pick-${v.body.id}"][value="${k2.user.id}"]`);
    await expect(row).toHaveAttribute("data-svc-ok", "0");
    await expect(page.locator(".pick-row", { has: row })).toContainText("does not offer Household help");
    // first: refuse the override → nothing assigned
    page.once("dialog", d => { expect(d.message()).toContain("has NOT offered Household help"); d.dismiss(); });
    await row.check();
    await page.locator(`button[onclick="AdminView.confirmAssign('${v.body.id}')"]`).click();
    await page.waitForTimeout(400);
    expect((await api(request, "GET", `/visits/${v.body.id}`, { token: cg1.token })).body.status).toBe("requested");
    // then: accept it → assigned, and the API refused the plain call meanwhile
    const plain = await api(request, "POST", `/admin/visits/${v.body.id}/assign`, { token: admin.token, data: { kaki_id: k2.user.id } });
    expect(plain.status).toBe(409); expect(plain.body.error).toBe("service_mismatch");
    page.once("dialog", d => d.accept());
    await row.check();
    await page.locator(`button[onclick="AdminView.confirmAssign('${v.body.id}')"]`).click();
    await expect(page.locator("#toast")).toContainText("Assigned to Peggy Tien");
    expect((await api(request, "GET", `/visits/${v.body.id}`, { token: cg1.token })).body.status).toBe("assigned");
  });

  test("a kaki who offers the service is assigned with the ordinary confirm", async ({ page, request }) => {
    const { admin, cg1, k1 } = await seed(request);          // k1 = Bee Lian, Companionship + Household help
    const v = await api(request, "POST", "/visits", { token: cg1.token, data: { service: "Household help", tier: "planned", date: dateIn(2), start_time: "10:00", end_time: "12:00", languages: ["English"] } });
    await useToken(page, admin.token, "#/admin/requests");
    const row = page.locator(`input[name="pick-${v.body.id}"][value="${k1.user.id}"]`);
    await expect(row).toHaveAttribute("data-svc-ok", "1");
    page.once("dialog", d => { expect(d.message()).not.toContain("NOT offered"); d.accept(); });
    await row.check();
    await page.locator(`button[onclick="AdminView.confirmAssign('${v.body.id}')"]`).click();
    await expect(page.locator("#toast")).toContainText("Assigned to Tan Bee Lian");
  });
});

test.describe("urgent bookings with a duration (L10.3)", () => {
  test("an urgent booking takes hours and prices them", async ({ page, request }) => {
    const { cg1 } = await seed(request);
    await useToken(page, cg1.token, "#/care/book");
    await page.locator(".bigcard[data-service='Companionship']").click();
    await page.getByRole("button", { name: /Urgent/ }).click();
    await page.getByRole("button", { name: "Skip — just need help" }).click();
    await expect(page.locator("#hrsG .chip.sel")).toHaveAttribute("data-v", "2");
    await page.locator("#hrsG .chip[data-v='4']").click();
    await page.getByRole("button", { name: "Request this visit" }).click();
    await expect(page).toHaveURL(/#\/care\/visit\//);
    await expect(page.locator("#screen h1")).toContainText("4 hrs");
    const id = page.url().split("/visit/")[1];
    const v = await api(request, "GET", `/visits/${id}`, { token: cg1.token });
    expect(v.body.hours).toBe(4);
    expect(v.body.estimate.hours).toBe(4);
  });
});

test.describe("kaki profile and availability (L9.2, L9.3, L9.4)", () => {
  test("two gender options, one availability door, dated exceptions read as optional", async ({ page, request }) => {
    const { k1 } = await seed(request);
    await useToken(page, k1.token, "#/kaki/profile");
    await expect(page.locator("#genG .chip")).toHaveCount(2);
    await expect(page.locator("#screen")).not.toContainText("Prefer not to say");
    await expect(page.locator("#screen")).not.toContainText("Good standing");
    await expect(page.locator("#screen")).toContainText("When I'm free");
    await page.locator(".li", { hasText: "When I'm free" }).click();
    await expect(page.locator("#screen h1")).toContainText("When I'm free");
    await expect(page.locator("#screen")).toContainText("This is all you need to fill in");
    await expect(page.locator("#screen")).toContainText("Different on a date?");
    await expect(page.locator("#screen")).not.toContainText("Am I working?");
    await expect(page.locator("#exAvail .chip[data-v='Not available']")).toHaveText("Day off");
    await expect(page.locator("#exAvail .chip[data-v='Extra availability']")).toHaveText("Extra day");
  });
});

test.describe("plainer screens (L10.13)", () => {
  test("care plan can be skipped on first setup; cost is behind a toggle; role chips are plain", async ({ page, request }) => {
    const { cg2, admin, k1 } = await seed(request);
    // role chips on a fresh sign-in
    await page.goto("/"); await page.evaluate(() => localStorage.clear()); await page.reload();
    await page.getByLabel("Email or mobile number").fill(`plain-${Date.now()}@e2e.test`);
    await page.getByRole("button", { name: "Send my code" }).click();
    await expect(page.locator("#roleG .chip[data-v='caregiver']")).toHaveText("I'm booking for someone I care for");
    await expect(page.locator("#roleG .chip[data-v='kaki']")).toHaveText("I want to help as a kaki");
    await expect(page.locator("#screen")).not.toContainText("Trusted respite when a need arises");
    // a new household can skip the plan
    const fresh = await api(request, "POST", "/auth/request-code", { data: { identifier: `skip-${Date.now()}@e2e.test` } });
    const ver = await api(request, "POST", "/auth/verify", { data: { identifier: fresh.body.identifier, code: fresh.body.dev_code, role: "caregiver", name: "Skipper" } });
    await api(request, "POST", `/admin/users/${ver.body.user.id}/approve`, { token: admin.token, data: { role: "caregiver" } });
    const again = await api(request, "POST", "/auth/request-code", { data: { identifier: fresh.body.identifier } });
    const tok = (await api(request, "POST", "/auth/verify", { data: { identifier: fresh.body.identifier, code: again.body.dev_code } })).body.token;
    await useToken(page, tok, "#/care/home");
    await expect(page.locator("#screen h1")).toContainText("Who are you caring for?");
    await page.locator("#sn").fill("Mdm Ong"); await page.locator("#ad").fill("Blk 170");
    await page.getByRole("button", { name: "Continue" }).click();
    await page.getByRole("button", { name: "Skip for now" }).click();
    await expect(page.locator("#screen")).toContainText("Caring for Mdm Ong");
    // cost toggle on a visit page
    const v = await api(request, "POST", "/visits", { token: cg2.token, data: { service: "Companionship", tier: "planned", date: dateIn(2), start_time: "10:00", end_time: "12:00", languages: ["English"] } });
    await useToken(page, cg2.token, `#/care/visit/${v.body.id}`);
    await expect(page.locator("#costBox")).toBeHidden();
    await expect(page.getByText("Family pays (est.)")).toBeHidden();
    await page.getByRole("button", { name: "Show cost" }).click();
    await expect(page.locator("#costBox")).toBeVisible();
    await expect(page.getByText("Family pays (est.)")).toBeVisible();
    await page.getByRole("button", { name: "Hide cost" }).click();
    await expect(page.locator("#costBox")).toBeHidden();
  });
});
