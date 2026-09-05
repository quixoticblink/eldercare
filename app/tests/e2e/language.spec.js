// v1.7 — EN / 中文 on the caregiver and kaki screens. The coordinator console
// stays English by design. Every assertion here reads what a person sees.
const { test, expect } = require("@playwright/test");
const { uniq, api, approve, seed, useToken, dateIn } = require("./helpers");

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
    await expect(page.locator("#screen")).toContainText("照片和 Kaki 验证码已核对");
    // nothing English leaked onto the page apart from names and data
    await expect(page.locator("#screen")).not.toContainText(/Check it's them|Start code|Confirmed|Kaki assigned|Estimated cost/);
  });
});

test.describe("kaki screens in 中文", () => {
  test("a kaki accepts, shows the kaki code, starts and completes a visit, all in Chinese", async ({ page, request }) => {
    const { admin, cg1, k1 } = await seed(request);
    const v = await api(request, "POST", "/visits", { token: cg1.token, data: { service: "Companionship", tier: "planned", date: dateIn(2), start_time: "10:00", end_time: "12:00", languages: ["Mandarin"] } });
    await api(request, "POST", `/admin/visits/${v.body.id}/assign`, { token: admin.token, data: { kaki_id: k1.user.id } });
    await useToken(page, k1.token, "#/kaki/home");
    await page.evaluate(() => localStorage.setItem("kakis_lang", "zh"));
    await page.reload();
    await expect(page.locator("#screen h1")).toContainText("您的探访");
    await expect(page.locator("#screen")).toContainText("不需要一直开着应用");
    await expect(page.locator("#tabs")).toContainText("我的资料");
    await page.locator(".li", { hasText: "Mr Nathan" }).first().click();
    await expect(page.locator("#screen")).toContainText("已安排 Kaki");
    await expect(page.locator("#screen")).toContainText("您的 Kaki 验证码");
    await page.getByRole("button", { name: "接受这次探访" }).click();
    await expect(page.locator("#toast")).toContainText("已确认");
    await expect(page.locator("#screen")).toContainText("开始探访");
    await expect(page.locator("#screen")).toContainText("我出发了");
    // the family checks the kaki, then reads the start code
    const kc = (await api(request, "GET", `/visits/${v.body.id}`, { token: k1.token })).body.kaki_code;
    const ok = await api(request, "POST", `/visits/${v.body.id}/verify-kaki`, { token: cg1.token, data: { code: kc } });
    const otp = ok.body.otp_code;
    for (let i = 0; i < 4; i++) await page.locator(`#o${i}`).fill(otp[i]);
    await page.locator("#startV").click();
    await expect(page.locator("#toast")).toContainText("探访已开始");
    await expect(page.locator("#screen")).toContainText("结束探访");
    await expect(page.locator("#repChips .chip[data-v='Went well']")).toHaveText("顺利");
    await page.locator("#repTxt").fill("去了巴刹");
    await page.locator("#endV").click();
    await expect(page.locator("#toast")).toContainText("探访已完成");
    await expect(page.locator("#screen")).toContainText("您的报告");
    await expect(page.locator("#screen")).not.toContainText(/Your report|Flag a concern|Completed|Care plan/);
    // the report chip value went to the API in English
    const done = await api(request, "GET", `/visits/${v.body.id}`, { token: cg1.token });
    expect(done.body.report.chips).toContain("Went well");
    // profile and availability
    await page.goto("/#/kaki/profile");
    await expect(page.locator("#screen h1")).toContainText("我的资料");
    await expect(page.locator("#screen")).toContainText("培训与证书");
    await expect(page.locator("#svcG .chip[data-v='Chaperone']")).toHaveText("陪同外出");
    await page.goto("/#/kaki/availability");
    await expect(page.locator("#screen h1")).toContainText("我可以工作的时间");
    await expect(page.locator("label[for='day-Mon']")).toHaveText("周一");
    await expect(page.locator("#exHalf .chip[data-v='morning']")).toHaveText("上午");
  });
});

// English labels that must never appear on a caregiver or kaki screen in 中文.
// Names, addresses, service values inside data, and the word Kaki are allowed.
const LEAKS = /Welcome to Kakis|Send my code|Sign in\b|Check again|Set up your care circle|Continue|Save care plan|Caring for|Book a visit|What do they need|When\?|The details|Request this visit|Finding a kaki|Kaki assigned|Confirmed|Happening now|Completed|Cancelled|Check it's them|Start code|Estimated cost|Family pays|Visit report|Private care note|Your visits|Accept this visit|I'm on my way|Start the visit|Start visit|End the visit|Complete visit|Your report|Flag a concern|My profile|Save profile|When I can work|Nothing to do right now|Care plan|Your profile|Current visits|Recent|Step \d of \d|Usually matched|Kaki checked at the door|Requested|Home|Visits|Impact|Profile|Sign out/;
const noLeak = async page => {
  const txt = await page.locator("#screen").innerText();
  const nav = await page.locator("#tabs").innerText().catch(() => "");
  expect(txt + " " + nav, "English leaked: " + (txt + " " + nav).match(LEAKS)).not.toMatch(LEAKS);
};

test("中文 lifecycle: caregiver signs up, books; the English console assigns; the kaki serves; nothing leaks", async ({ page, browser, request }) => {
  const s = await seed(request);
  // a new caregiver, in Chinese, from the sign-in screen
  await setZh(page);
  const cgId = uniq("zh-life");
  await page.getByLabel("电邮或手机号码").fill(cgId);
  await page.getByRole("button", { name: "发送验证码" }).click();
  const code = (await page.locator(".card.warn b.mono").first().textContent()).trim();
  await page.locator("#codeIn").fill(code);
  await page.locator("#nameIn").fill("李太太");
  await page.locator("#roleG .chip[data-v='caregiver']").click();
  await page.getByRole("button", { name: "登录", exact: true }).click();
  await expect(page.locator("#screen")).toContainText("现在没有需要做的事");
  await noLeak(page);
  const me = await api(request, "GET", "/auth/me", { token: await page.evaluate(() => localStorage.getItem("kakis_token")) });
  expect(me.body.user.lang).toBe("zh");                      // the choice followed the person to the server
  await approve(request, s.admin.token, me.body.user.id, "caregiver");
  await page.getByRole("button", { name: "再查看一次" }).click();
  await expect(page.locator("#screen h1")).toContainText("设置您的照护圈");
  await noLeak(page);
  await page.locator("#sn").fill("林先生");
  await page.locator("#sa").fill("80");
  await page.locator("#ad").fill("Blk 261A Toa Payoh");
  await page.getByRole("button", { name: "继续" }).click();
  await expect(page.locator("#screen h1")).toContainText("林先生 的照护计划");
  await noLeak(page);
  await page.locator("#meds").fill("Amlodipine 8am");
  await page.locator("#mobG .chip[data-v='Walks with a stick']").click();
  await page.locator("#cName").fill("小明"); await page.locator("#cPhone").fill("91234567");
  await page.getByRole("button", { name: "保存照护计划" }).click();
  await expect(page.locator("#screen")).toContainText("照顾 林先生");
  await noLeak(page);
  // book
  await page.getByRole("button", { name: /为 林先生 预约探访/ }).click();
  await noLeak(page);
  await page.locator(".bigcard[data-service='Companionship']").click();
  await noLeak(page);
  await page.getByRole("button", { name: /预约，提前安排/ }).click();
  await noLeak(page);
  await page.locator("#date").fill(dateIn(1));
  await page.locator("#startT").selectOption("14:00");
  await page.locator("#endT").selectOption("16:00");
  await page.locator("#notes").fill("Likes rummy-o.");
  await page.getByRole("button", { name: "提交探访申请" }).click();
  await expect(page).toHaveURL(/#\/care\/visit\//);
  const visitId = page.url().split("/visit/")[1];
  await expect(page.locator("#screen")).toContainText("正在找 Kaki");
  await noLeak(page);
  // the coordinator's console is English, whatever the phone says
  const adminCtx = await browser.newContext({ locale: "zh-CN" });
  const adminPage = await adminCtx.newPage();
  await useToken(adminPage, s.admin.token, "#/admin/requests");
  await expect(adminPage.locator("#langBtn")).toBeHidden();
  await expect(adminPage.locator("#screen")).toContainText(/Matching|match/i);
  await adminCtx.close();
  await api(request, "POST", `/admin/visits/${visitId}/assign`, { token: s.admin.token, data: { kaki_id: s.k1.user.id } });
  // the kaki, in Chinese, on another phone
  const kCtx = await browser.newContext();
  const kPage = await kCtx.newPage();
  await useToken(kPage, s.k1.token, "#/kaki/home");
  await kPage.evaluate(() => localStorage.setItem("kakis_lang", "zh"));
  await kPage.reload();
  await noLeak(kPage);
  await kPage.locator(".li", { hasText: "林先生" }).first().click();
  await noLeak(kPage);
  await kPage.getByRole("button", { name: "接受这次探访" }).click();
  await expect(kPage.locator("#screen")).toContainText("我出发了");
  await kPage.getByRole("button", { name: "我出发了" }).click();
  await expect(kPage.locator("#screen")).toContainText("已出发");
  await noLeak(kPage);
  const kakiCode = (await kPage.locator(".codebox.kakicode span").allTextContents()).join("");
  // the family checks the kaki at the door
  await page.reload();
  await expect(page.locator("#screen")).toContainText("正在路上");
  await expect(page.locator("#screen")).toContainText("确认是本人");
  await noLeak(page);
  for (let i = 0; i < 4; i++) await page.locator(`#k${i}`).fill(kakiCode[i]);
  await page.locator("#verifyK").click();
  await expect(page.locator("#screen")).toContainText("开始码，Kaki 到达后读给他/她听");
  await expect(page.locator(".codebox span").first()).toBeVisible();
  await noLeak(page);
  const otp = (await page.locator(".codebox span").allTextContents()).join("");
  for (let i = 0; i < 4; i++) await kPage.locator(`#o${i}`).fill(otp[i]);
  await kPage.locator("#startV").click();
  await expect(kPage.locator("#screen")).toContainText("结束探访");
  await noLeak(kPage);
  await kPage.locator("#repTxt").fill("去了巴刹，下午 2 点吃了药。");
  await kPage.locator("#endV").click();
  await expect(kPage.locator("#screen")).toContainText("您的报告");
  await noLeak(kPage);
  await kPage.goto("/#/kaki/impact"); await noLeak(kPage);
  await kCtx.close();
  // the family reads the report, in Chinese, with the kaki's own words untouched
  await page.reload();
  await expect(page.locator("#screen")).toContainText("探访报告");
  await expect(page.locator("#screen")).toContainText("去了巴刹，下午 2 点吃了药。");
  await expect(page.locator("#screen")).toContainText("顺利");
  await noLeak(page);
  await page.goto("/#/care/visits"); await noLeak(page);
  // and back to English with one tap, which the server also learns
  await page.locator("#langBtn").click();
  await expect(page.locator("#screen h1")).toContainText("Visits");
  await expect(page.locator("#screen")).toContainText("History");
  const after = await api(request, "GET", "/auth/me", { token: await page.evaluate(() => localStorage.getItem("kakis_token")) });
  expect(after.body.user.lang).toBe("en");
});

test("the help panel answers a Chinese question in Chinese, signed out and signed in", async ({ page, request }) => {
  await setZh(page);
  await page.locator("#helpBtn").click();
  await expect(page.locator("#helpTitle")).toHaveText("需要帮忙吗？");
  await expect(page.locator("#chatLog")).toContainText("Kakis 小帮手");
  await page.locator("#helpQuick .chip", { hasText: "开始码" }).click();
  await expect(page.locator("#chatLog .msg.bot").last()).toContainText("开始码");
  await expect(page.locator("#chatLog .msg.bot").last()).not.toContainText(/start code/i);
  const { cg1 } = await seed(request);
  await useToken(page, cg1.token, "#/care/home");
  await page.locator("#helpBtn").click();
  await page.locator("#chatInput").fill("怎样取消探访？");
  await page.locator("#chatSend").click();
  await expect(page.locator("#chatLog .msg.bot").last()).toContainText("取消");
});

module.exports = { setZh };
