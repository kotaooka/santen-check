// 問題の作り方とルールの検算。不一致があれば終了コード 1 で終わる。
// 使い方：node tests/test.js
"use strict";
const fs = require("fs");
const path = require("path");

const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
// 2つ目の <script>（本体）のうち、画面に触れない「問題の作り方」までを取り出して読み込む
const body = html.split("<script>\n")[1].split("</script>")[0];
const pure = body.split("/* ====== 効果音")[0];
const G = new Function(pure + "\nreturn { makeShift, describe, category, DAYS, BOXES, BOSS_FROM, QUIET, DMG_CATCH, DMG_SHIP, CLAIM, CATCH, SHIP, OVER, MULT, PARTS, COLORS };")();

let fail = 0;
const check = (ok, msg) => { if (!ok) { fail++; console.error("NG: " + msg); } };
const N = 3000;   // 1日あたりに作るシフトの数

for (const [di, day] of G.DAYS.entries()) {
  let defects = 0, noQuiet = 0, minMargin = Infinity;
  for (let s = 0; s < N; s++) {
    const sh = G.makeShift(day);
    check(sh.boxes.length === G.BOXES, `第${di + 1}日：箱の数`);
    sh.boxes.forEach((b, i) => {
      // 練習：1・2箱目は正常、3箱目は異常
      if (i < 2) check(!b.defect, `第${di + 1}日：${i + 1}箱目は正常のはず`);
      if (i === 2) check(!!b.defect, `第${di + 1}日：3箱目は異常のはず`);
      if (!b.defect) {
        // 正常の箱は三点が完全に一致している
        const t = b.truth, l = b.label, p = b.part;
        check(l.pn === t.pn && l.qty === t.qty && l.color === t.color && l.rev === t.rev, "正常の箱でラベルが指示と違う");
        check(p.pn === t.pn && p.rev === t.rev && p.count === t.qty && !p.foreign && p.pieces.every(x => x.type === t.type && x.side === t.side && x.color === t.color), "正常の箱で現品が指示と違う");
        check(b.sheetColorName === t.color.name, "正常の箱で指示書の色名が違う");
        return;
      }
      defects++;
      // 異常には必ず説明があり、画面に出る違いがある
      check(G.describe(b).length > 0 && !!G.category(b), "異常の説明がない");
      const t = b.truth, l = b.label, p = b.part;
      const visible = b.sheetColorName !== t.color.name || l.pn !== t.pn || l.qty !== t.qty || l.color !== t.color || l.rev !== t.rev
        || p.pn !== t.pn || p.rev !== t.rev || p.count !== t.qty || !!p.foreign || b.defect.field === "blur"
        || p.pieces.some(x => x.type !== t.type || x.side !== t.side || x.color !== t.color);
      check(visible, `見えない異常：${JSON.stringify(b.defect)}`);
      check(p.pieces.length === p.count, "現品の個数と絵の数が違う");
    });
    // 静かな区間（QUIET 箱続けて正常）がある（監査区間より前）
    const end = day.boss ? G.BOSS_FROM : G.BOXES;
    let run = 0, ok = false;
    for (let i = 0; i < end; i++) { run = sh.boxes[i].defect ? 0 : run + 1; if (run >= G.QUIET) ok = true; }
    if (!ok) noQuiet++;
    // 監査：全問正解なら必ず倒せる
    if (day.boss) {
      const most = sh.boxes.slice(G.BOSS_FROM).reduce((a, b) => a + (b.defect ? G.DMG_CATCH : G.DMG_SHIP), 0);
      const hp = Math.round(most * (day.bossK || 0.8));
      minMargin = Math.min(minMargin, most - hp);
      check(sh.boxes.slice(G.BOSS_FROM).filter(b => b.defect).length === 3, "監査区間の異常が3つでない");
    }
  }
  check(noQuiet === 0, `第${di + 1}日：静かな区間のないシフトが ${noQuiet} 件`);
  if (day.boss) check(minMargin > 0, `第${di + 1}日：全問正解でも監査に負けるシフトがある`);
  console.log(`第${di + 1}日 ${day.name}：異常 ${(defects / N).toFixed(1)} 箱/日、監査の余裕 最小 ${day.boss ? minMargin : "－"}`);
}

// 得点の釣り合い：何も見ずに全部出荷・全部赤箱は、全問正解より必ず低い（簡易シミュレーション）
function play(day, strat) {
  const sh = G.makeShift(day);
  let lvl = day.startLvl, streak = 0, score = 0, claims = [], cc = 0;
  for (let i = 0; i < sh.boxes.length; i++) {
    claims.filter(c => c <= i).forEach(() => { score += G.CLAIM; cc++; lvl = 1; streak = 0; });
    claims = claims.filter(c => c > i);
    if (cc >= day.claimMax) return score + claims.length * G.CLAIM;
    const ng = !!sh.boxes[i].defect, ch = strat(ng), m = G.MULT[lvl - 1];
    if (ch === "ok") { score += Math.round((G.SHIP + 25) * m); if (ng) claims.push(i + 3); streak++; if (streak % 3 === 0) lvl = Math.min(5, lvl + 1); }
    else if (ng) { score += Math.round((G.CATCH + 25) * m); streak++; if (streak % 3 === 0) lvl = Math.min(5, lvl + 1); }
    else { score += G.OVER; lvl = Math.max(1, lvl - 1); streak = 0; }
  }
  return score + claims.length * G.CLAIM;
}
const avg = (day, f) => { let t = 0; for (let i = 0; i < 1000; i++) t += play(day, f); return t / 1000; };
for (const [di, day] of G.DAYS.entries()) {
  const perfect = avg(day, ng => ng ? "ng" : "ok"), allOk = avg(day, () => "ok"), allNg = avg(day, () => "ng");
  check(allOk < perfect * 0.5, `第${di + 1}日：全部出荷 ${allOk.toFixed(0)} が全問正解 ${perfect.toFixed(0)} に近すぎる`);
  check(allNg < perfect * 0.5, `第${di + 1}日：全部赤箱 ${allNg.toFixed(0)} が全問正解 ${perfect.toFixed(0)} に近すぎる`);
  // 何も見ずに全部赤箱では、監査に（ほぼ）合格できない
  if (day.boss) {
    let pass = 0;
    for (let s = 0; s < 3000; s++) {
      const box = G.makeShift(day).boxes.slice(G.BOSS_FROM);
      const most = box.reduce((a, b) => a + (b.defect ? G.DMG_CATCH : G.DMG_SHIP), 0);
      let hp = Math.round(most * (day.bossK || 0.8)); const max = hp; let strikes = 0;
      for (const b of box) {
        if (b.defect) hp = Math.max(0, hp - G.DMG_CATCH); else { hp = Math.min(max, hp + G.DMG_CATCH); strikes++; }
        if (hp === 0) { pass++; break; }
        if (strikes >= 3) break;
      }
    }
    check(pass / 3000 < 0.1, `第${di + 1}日：全部赤箱で監査に ${(pass / 30).toFixed(1)}% 合格できてしまう`);
  }
}

if (fail) { console.error(`\n${fail} 件の不一致`); process.exit(1); }
console.log("\nすべて一致");
