/* Body scenes for the CathodeAI page, drawn by the shared Viz renderer (assets/viz.js) from window.CATHODEAI (assets/data.js):
   1. validation: the eleven experimental cathodes as labelled spheres on DSI (x) against reported cycle life (y, log), classes by colour;
   2. polymorphs: the three LiCuO2 end-members as a bar field over their three DSI inputs;
   3. funnel: the eight-layer screen as a stack of discs whose radius follows the count, assembling from the bottom. */
import { Viz } from './viz.js';
import { THREE } from './three-kit.js';
const D = window.CATHODEAI; const f = (v, d = 0) => (+v).toLocaleString('en-US', { maximumFractionDigits: d, minimumFractionDigits: d });
const CAT = { A: 'cyan', B: 'green', C: 'warm', D: 'rose' };

/* ---------- 1. validation ---------- */
Viz.view('[data-viz="validation"]', v => {
  const V = D.validation.filter(x => x.dsi !== undefined); const lg = x => Math.log10(x);
  const A = Viz.axes(v, { size: [4.4, 2.4, 1.4], x: { lo: 0, hi: 1, ticks: [0, .25, .5, .75, 1], label: 'Degradation Screening Index' }, y: { lo: lg(100), hi: lg(20000), ticks: [2, 3, 4], fmt: t => f(Math.pow(10, t)), label: 'reported cycles' }, z: { lo: 0, hi: 1 } });
  const items = V.map((x, i) => { const P = A.map(x.dsi, lg(x.exp_cycles), .5); const m = new THREE.Mesh(new THREE.SphereGeometry(.1, 20, 16), Viz.mat(CAT[x.cat], { emissive: CAT[x.cat], emissiveIntensity: .45, roughness: .3 })); m.position.copy(P); m.userData = x; v.rig.add(m); v.pickables.push(m); const stem = Viz.line(v, [[P.x, A.map(0, lg(100)).y, P.z], [P.x, P.y, P.z]], 'line'); const lab = Viz.label(v, x.name, [P.x, P.y + .2, P.z + .1], { px: 20, scale: .085 }); return { m, stem, lab, i }; });
  // the rank line: a ribbon through the points ordered by DSI shows the monotone trend behind rho = 0.76
  const srt = [...V].sort((a, b) => a.dsi - b.dsi); const rb = Viz.ribbon(v, A, srt.map(x => x.dsi), srt.map(x => lg(x.exp_cycles)), { color: 'violet', width: .05, z: .5, skirt: false, name: 'rank' }); rb.mesh.material.opacity = .35; rb.mesh.material.transparent = true; v.pickables.pop();
  const tag = Viz.label(v, `Spearman ρ = ${D.stats.rho} (p = ${D.stats.p}), n = ${V.length}`, [0, A.map(0, lg(20000)).y + .35, 0], { px: 24, scale: .11, color: 'ink', weight: 700 });
  v.update = vv => { items.forEach((it, i) => { const e = Math.min(1, Math.max(0, (vv.p * 1.6 - i * .05))); it.m.scale.setScalar(Math.max(1e-3, e)); it.lab.material.opacity = e; it.stem.material.opacity = e * .8; it.stem.material.transparent = true; }); rb.draw(Math.max(0, vv.p * 1.3 - .3)); tag.material.opacity = Math.max(0, vv.p * 2 - 1); return false; };
  v.hover = hit => { const x = hit.object.userData; return x && x.name ? `<b>${x.name}: class ${x.cat}</b>DSI ${x.dsi} · ${f(x.exp_cycles)} cycles reported · ΔV/V ${x.dv} % · E<sub>hull,charge</sub> ${Math.round(x.eh * 1000)} meV · E<sub>g</sub> ${x.bg} eV` : null; };
  v.rot = -.3; v.tilt = .1;
}, { camera: [0, 1.8, 7.0], target: [0, -.1, 0], fov: 32 });

/* ---------- 2. LiCuO2 polymorphs ---------- */
Viz.view('[data-viz="polymorphs"]', v => {
  const P = D.structures; const metrics = [['ΔV/V, %', x => x.dv, 50, 'hot'], ['E_hull,charge, meV/atom', x => x.ehull_charge_meV, 300, 'violet'], ['DSI × 100', x => x.dsi * 100, 100, 'cyan']];
  const A = Viz.axes(v, { size: [3.6, 2.2, 2.8], x: { lo: -.5, hi: 2.5, ticks: [] }, y: { lo: 0, hi: 1, ticks: [], label: '' }, z: { lo: -.5, hi: 2.5, ticks: [] } });
  const items = []; metrics.forEach(([name, fn, max, col], mi) => P.forEach((s, pi) => items.push({ x: pi, z: mi, y: fn(s) / max, color: col, s, name, raw: fn(s), max })));
  const B = Viz.bars(v, A, items, { width: .5, depth: .5 });
  P.forEach((s, pi) => Viz.label(v, `${s.sg}\nclass ${s.dsi_class}`, [A.map(pi, 0, 0).x, A.map(0, 0).y - .3, A.map(0, 0, -.5).z - .1], { px: 20, scale: .09, bg: false, color: 'ink', weight: 700 }));
  metrics.forEach(([name], mi) => Viz.label(v, name, [A.map(2.5, 0, 0).x + .3, A.map(0, 0).y + .05, A.map(0, 0, mi).z], { px: 19, scale: .085, bg: false }));
  items.forEach(it => { const p = A.map(it.x, it.y, it.z); it.lab = Viz.label(v, it.z === 2 ? it.s.dsi.toFixed(2) : it.z === 0 ? `${it.raw} %` : `${it.raw}`, [p.x, p.y + .16, p.z], { px: 19, scale: .085 }); });
  v.update = vv => { B.draw(vv.p); items.forEach(it => it.lab.material.opacity = Math.max(0, vv.p * 2 - 1)); return false; };
  v.hover = hit => { const it = items[hit.instanceId]; return it ? `<b>LiCuO₂ ${it.s.sg}, class ${it.s.dsi_class}</b>${it.name.split(',')[0]}: ${it.z === 2 ? it.s.dsi : it.raw}${it.z === 0 ? ' %' : it.z === 1 ? ' meV/atom' : ''}` : null; };
  v.rot = -.5; v.tilt = .12;
}, { camera: [0, 2.4, 7.2], target: [0, -.2, 0], fov: 32 });

/* ---------- 3. the funnel ---------- */
Viz.view('[data-viz="funnel"]', v => {
  const F = [['Li insertion electrodes', D.stats.n_screened], ...D.funnel.slice(1).map(x => [x[0], x[1]]), ['Discovery zone', 26]];
  const n0 = F[0][1]; const parts = [], labels = []; const H = .32, GAP = .1; const top = (F.length - 1) * (H + GAP) / 2;
  F.forEach(([name, count], i) => { const r = .3 + 1.45 * Math.sqrt(count / n0); const col = i === F.length - 1 ? 'hot' : i === 0 ? 'cool' : ['blue', 'cyan', 'green', 'violet', 'warm'][(i - 1) % 5]; const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, H, 64), Viz.mat(col, { roughness: .35, metalness: .25, emissive: col, emissiveIntensity: .12 })); m.position.y = top - i * (H + GAP); m.userData = { name, count }; v.rig.add(m); v.pickables.push(m); parts.push({ mesh: m, from: [0, 2.5, 0], delay: i / F.length * .7, span: .3 }); labels.push(Viz.label(v, `${f(count)}  ${name}`, [r + .2, m.position.y, 0], { px: 19, scale: .08, bg: false, color: 'ink', weight: i === F.length - 1 ? 800 : 600 })); });
  v.rig.position.x = -1.2;
  const ex = Viz.exploded(v, parts);
  v.update = vv => { ex.draw(vv.p); labels.forEach((l, i) => l.material.opacity = Math.max(0, (vv.p - i / F.length * .7 - .15) * 4)); return false; };
  v.hover = hit => { const u = hit.object.userData; return u && u.name ? `<b>${f(u.count)} entries</b>${u.name}` : null; };
  v.spin = 0; v.tilt = .05;
}, { camera: [0, .8, 7.6], target: [0, -.1, 0], fov: 32, orbit: true });
