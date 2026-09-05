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

module.exports = { setZh };
