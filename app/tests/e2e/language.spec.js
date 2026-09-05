// v1.7 — EN / 中文 on the caregiver and kaki screens. The coordinator console
// stays English by design. Every assertion here reads what a person sees.
const { test, expect } = require("@playwright/test");
const { uniq, api, apiLogin, seed, useToken, dateIn, signIn } = require("./helpers");

async function setZh(page) {
  await page.goto("/");
  await page.evaluate(() => { localStorage.clear(); localStorage.setItem("kakis_lang", "zh"); });
  await page.goto("/");
  await page.reload();
}

test.describe("language toggle", () => {
  test("the sign-in screen has a toggle, and the choice survives reload and sign-out/in", async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    await expect(page.locator("#langBtn")).toBeVisible();
    await expect(page.locator("#screen h1")).toContainText("Welcome to Kakis");
    await page.locator("#langBtn").click();
    await expect(page.locator("#screen h1")).toContainText("欢迎使用 Kakis");
    await expect(page.getByRole("button", { name: "发送验证码" })).toBeVisible();
    await page.reload();
    await expect(page.locator("#screen h1")).toContainText("欢迎使用 Kakis");
    // sign in as a new caregiver, in Chinese, then sign out and back in
    const id = uniq("zhcg");
    await page.getByLabel("电邮或手机号码").fill(id);
    await page.getByRole("button", { name: "发送验证码" }).click();
    const code = (await page.locator(".card.warn b.mono").first().textContent()).trim();
    await page.locator("#codeIn").fill(code);
    await page.locator("#nameIn").fill("陈太太");
    await page.locator("#roleG .chip[data-v='caregiver']").click();
    await page.getByRole("button", { name: "登录", exact: true }).click();
    await expect(page.locator("#screen h1")).toContainText("快好了");
    await expect(page.locator("#screen")).toContainText("现在没有需要做的事");
    await page.getByRole("button", { name: "退出登录" }).click();
    await expect(page.locator("#screen h1")).toContainText("欢迎使用 Kakis");
  });

  test("the coordinator sees no toggle and an English console even on a Chinese phone", async ({ browser, request }) => {
    const ctx = await browser.newContext({ locale: "zh-CN" });
    const page = await ctx.newPage();
    const { admin } = await seed(request);
    await useToken(page, admin.token, "#/admin/home");
    await expect(page.locator("#langBtn")).toBeHidden();
    await expect(page.locator("#screen")).toContainText("Today");
    await expect(page.locator("#tabs")).toContainText("Approvals");
    await ctx.close();
  });

  test("a Chinese phone defaults to 中文 on the sign-in screen", async ({ browser }) => {
    const ctx = await browser.newContext({ locale: "zh-SG" });
    const page = await ctx.newPage();
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    await expect(page.locator("#screen h1")).toContainText("欢迎使用 Kakis");
    await ctx.close();
  });
});

test.describe("caregiver screens in 中文", () => {
  test("a caregiver books a planned visit in Chinese; the API still receives English values", async ({ page, request }) => {
    const { cg1 } = await seed(request);
    await useToken(page, cg1.token, "#/care/home");
    await page.evaluate(() => localStorage.setItem("kakis_lang", "zh"));
    await page.reload();
    await expect(page.locator("#screen h1")).toContainText("您好");
    await expect(page.locator("#tabs")).toContainText("预约");
    await page.locator("#tabs button", { hasText: "预约" }).click();
    await expect(page.locator("#screen h1")).toContainText("需要什么帮助");
    await expect(page.locator("#screen")).toContainText("陪伴");
    await page.locator(".bigcard[data-service='Companionship']").click();
    await expect(page.locator("#screen h1")).toContainText("什么时候");
    await page.getByRole("button", { name: /预约，提前安排/ }).click();
    await expect(page.locator("#screen h1")).toContainText("详情");
    await expect(page.locator("#screen")).toContainText("按半小时计费");
    await expect(page.locator("#langG2 .chip[data-v='Mandarin']")).toHaveText("华语");
    await page.locator("#date").fill(dateIn(3));
    await page.getByRole("button", { name: "提交探访申请" }).click();
    await expect(page.locator("#screen")).toContainText("通常一天内配对成功");
    await expect(page.locator("#screen")).toContainText("正在找 Kaki");
    const visits = await api(request, "GET", "/visits", { token: cg1.token });
    expect(visits.body[0].service).toBe("Companionship");
    expect(visits.body[0].languages).toContain("Mandarin");
  });

  test("the door check and start code read in Chinese; a wrong kaki code toasts in Chinese", async ({ page, request }) => {
    const { admin, cg1, k1 } = await seed(request);
    const v = await api(request, "POST", "/visits", { token: cg1.token, data: { service: "Companionship", tier: "planned", date: dateIn(2), start_time: "10:00", end_time: "12:00", languages: ["Mandarin"] } });
    await api(request, "POST", `/admin/visits/${v.body.id}/assign`, { token: admin.token, data: { kaki_id: k1.user.id } });
    await api(request, "POST", `/visits/${v.body.id}/accept`, { token: k1.token });
    await useToken(page, cg1.token, `#/care/visit/${v.body.id}`);
    await page.evaluate(() => localStorage.setItem("kakis_lang", "zh"));
    await page.reload();
    await expect(page.locator("#screen")).toContainText("确认是本人");
    await expect(page.locator("#screen")).toContainText("已确认");
    await expect(page.locator("#screen")).toContainText("门口已核对 Kaki");
    for (let i = 0; i < 4; i++) await page.locator(`#k${i}`).fill("0");
    await page.locator("#verifyK").click();
    await expect(page.locator("#toast")).toContainText(/验证码不对|开始码/);
    const kv = await api(request, "GET", `/visits/${v.body.id}`, { token: k1.token });
    const code = kv.body.kaki_code;
    for (let i = 0; i < 4; i++) await page.locator(`#k${i}`).fill(code[i]);
    await page.locator("#verifyK").click();
    await expect(page.locator("#screen")).toContainText("开始码，Kaki 到达后读给他/她听");
    await expect(page.locator("#screen")).toContainText("照片和验证码已核对");
    // nothing English leaked onto the page apart from names and data
    await expect(page.locator("#screen")).not.toContainText(/Check it's them|Start code|Confirmed|Kaki assigned|Estimated cost/);
  });
});

module.exports = { setZh };
