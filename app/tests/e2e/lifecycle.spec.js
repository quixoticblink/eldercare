// The whole loop, through the screens: sign up → approve → set up → book →
// match → accept → start code → report. This is the baseline every feature
// task must keep green, and the spec that gets rerun after every migration.
const { test, expect } = require("@playwright/test");
const { uniq, api, apiLogin, signIn, approve, seed, useToken, dateIn } = require("./helpers");

test("caregiver books, kaki serves, report comes back", async ({ page, request }) => {
  const s = await seed(request);

  // A brand-new caregiver signs up through the UI and lands on the waiting screen.
  const cgId = uniq("cg-ui");
  await signIn(page, cgId, { role: "caregiver", name: "Aunty May" });
  await expect(page.getByText("waiting for approval")).toBeVisible();
  const me = await api(request, "GET", "/auth/me", { token: await page.evaluate(() => localStorage.getItem("kakis_token")) });
  await approve(request, s.admin.token, me.body.user.id, "caregiver");
  await page.getByRole("button", { name: "Check again" }).click();

  // Household + care plan.
  await expect(page.getByText("Set up your care circle")).toBeVisible();
  await page.locator("#sn").fill("Mr Lim");
  await page.locator("#sa").fill("80");
  await page.locator("#ad").fill("Blk 261A Toa Payoh");
  await page.getByRole("button", { name: "Continue" }).click();
  await expect(page.getByText("Mr Lim's care plan")).toBeVisible();
  await page.locator("#meds").fill("Amlodipine 8am");
  await page.getByRole("button", { name: "Walks with a stick" }).click();
  await page.getByRole("button", { name: "Save care plan" }).click();
  await expect(page.getByText("Caring for Mr Lim")).toBeVisible();

  // Book: Companionship, planned, tomorrow afternoon.
  await page.getByRole("button", { name: /Book a visit for Mr Lim/ }).click();
  await page.getByRole("button", { name: /Companionship/ }).click();
  await page.getByRole("button", { name: /Planned/ }).click();
  await page.locator("#date").fill(dateIn(1));
  await page.locator("#startT").selectOption("14:00");
  await page.locator("#endT").selectOption("16:00");
  await page.locator("#notes").fill("Likes rummy-o.");
  await page.getByRole("button", { name: "Request this visit" }).click();
  await expect(page).toHaveURL(/#\/care\/visit\//);
  const visitId = page.url().split("/visit/")[1];
  await expect(page.getByText("Finding a kaki")).toBeVisible();
  await expect(page.locator(".appbar")).toContainText("14:00–16:00 · 2 hrs");

  // Coordinator assigns Bee Lian.
  const asg = await api(request, "POST", `/admin/visits/${visitId}/assign`, { token: s.admin.token, data: { kaki_id: s.k1.user.id } });
  expect(asg.status).toBe(200);
  expect(asg.body.assigned_to.name).toBe("Tan Bee Lian");

  // Kaki accepts through the UI; never sees the start code.
  await useToken(page, s.k1.token, "#/kaki/home");
  await page.getByRole("button", { name: /Companionship/ }).first().click();
  await expect(page).toHaveURL(new RegExp(`#/kaki/visit/${visitId}`));
  await page.getByRole("button", { name: "Accept this visit" }).click();
  await expect(page.getByText("Start the visit")).toBeVisible();

  // v1.6 identity both ways. The kaki's page shows THEIR code for the family…
  await expect(page.getByText("Your code for the family")).toBeVisible();
  const kakiCode = (await page.locator(".kakicode").textContent()).replace(/\D/g, "");
  expect(kakiCode).toMatch(/^\d{4}$/);

  // …the caregiver sees the kaki's photo, enters that code, and only then the start code appears.
  const cgToken = (await apiLogin(request, cgId)).token;
  await useToken(page, cgToken, `#/care/visit/${visitId}`);
  await expect(page.locator(".kp-face img")).toBeVisible();
  await expect(page.locator(".codebox")).toHaveCount(0);
  await expect(page.getByText("Check it's them")).toBeVisible();
  for (let i = 0; i < 4; i++) await page.locator(`#k${i}`).fill(kakiCode[i]);
  await page.getByRole("button", { name: "Confirm it's them" }).click();
  await expect(page.locator(".codebox")).toBeVisible();
  const digits = await page.locator(".codebox span").allTextContents();
  expect(digits.join("")).toMatch(/^\d{4}$/);
  const startCode = digits.join("");

  // Kaki must not have it anywhere on their visit page.
  await useToken(page, s.k1.token, `#/kaki/visit/${visitId}`);
  await expect(page.getByText("Start the visit")).toBeVisible();
  const kakiText = await page.locator("#screen").innerText();
  expect(kakiText).not.toContain(startCode);
  const kakiJson = await api(request, "GET", `/visits/${visitId}`, { token: s.k1.token });
  expect(kakiJson.body.otp_code).toBeUndefined();

  // Kaki starts with the code, then completes with a report.
  for (let i = 0; i < 4; i++) await page.locator(`#o${i}`).fill(startCode[i]);
  await page.getByRole("button", { name: "Start visit" }).click();
  await expect(page.getByText("End the visit")).toBeVisible();
  await page.locator("#repTxt").fill("Two rounds of rummy-o. Meds taken.");
  await page.getByRole("button", { name: "Complete visit" }).click();
  await expect(page.getByText("Your report")).toBeVisible();

  // Caregiver sees the report.
  await useToken(page, cgToken, `#/care/visit/${visitId}`);
  await expect(page.getByText("Visit report")).toBeVisible();
  await expect(page.getByText("Two rounds of rummy-o")).toBeVisible();
});
