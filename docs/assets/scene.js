/* Hero and sticky scenes for the CathodeAI page. Data: window.CATHODEAI from assets/data.js (built from the cached Materials Project responses). */
import { THREE, createStage, cameraPath } from './three-kit.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
const D = window.CATHODEAI, S = window.SITE, reduced = S.reduced, phone = S.phone;
const viridis = t => { const s = [[68, 1, 84], [59, 82, 139], [33, 145, 140], [94, 201, 98], [253, 231, 37]]; t = Math.max(0, Math.min(1, t)) * (s.length - 1); const i = Math.floor(t), f = t - i, a = s[i], b = s[Math.min(i + 1, s.length - 1)]; return new THREE.Color((a[0] + (b[0] - a[0]) * f) / 255, (a[1] + (b[1] - a[1]) * f) / 255, (a[2] + (b[2] - a[2]) * f) / 255); };
const spriteTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d'); const r = g.createRadialGradient(32, 32, 0, 32, 32, 32); r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(.5, 'rgba(255,255,255,.85)'); r.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = r; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c); })();
const textSprite = (txt, color, w = 1.9) => { const c = document.createElement('canvas'); c.width = 384; c.height = 96; const g = c.getContext('2d'); g.font = '700 40px -apple-system,Segoe UI,Roboto,Helvetica,Arial'; g.fillStyle = color; g.textAlign = 'center'; g.fillText(txt, 192, 62); const m = new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false, depthTest: false }); const s = new THREE.Sprite(m); s.scale.set(w, w / 4, 1); return s; };
// descriptor space -> scene: x = volume change 0..20 %, y = charged-phase hull energy 0..300 meV, z = band gap 0..5 eV
const sx = v => Math.min(v, 20) / 20 * 6 - 3, sy = v => Math.min(v * 1000, 300) / 300 * 4, sz = v => Math.min(v, 5) / 5 * 6 - 3;

// ---------- hero: 787-material scatter with a fly-through to the 11 validation cathodes ----------
(function () {
  const canvas = document.getElementById('heroCanvas'); if (!canvas) return;
  const st = createStage(canvas, { fov: 42, bloom: { strength: .5, radius: .5, threshold: .75 }, dof: { aperture: .0007, maxblur: .004 }, exposure: 1.0, env: false });
  if (st.failed) return; const { scene, camera } = st;
  const ctr = new OrbitControls(camera, canvas); ctr.enableDamping = true; ctr.enableZoom = false; ctr.enablePan = false; ctr.autoRotate = !reduced; ctr.autoRotateSpeed = .5;
  const M = D.materials, N = M.length, pos = new Float32Array(N * 3), col = new Float32Array(N * 3);
  // light theme: the top of viridis is pale yellow, so the map is compressed to 0.05 to 0.78 (purple to green) on the pale stage
  const paint = dark => { for (let i = 0; i < N; i++) { const m = M[i]; pos[3 * i] = sx(m[1]); pos[3 * i + 1] = sy(m[2]); pos[3 * i + 2] = sz(m[3]); const c = viridis(dark ? m[4] : .05 + .73 * m[4]); col[3 * i] = c.r; col[3 * i + 1] = c.g; col[3 * i + 2] = c.b; } }; paint(st.dark);
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const mat = new THREE.PointsMaterial({ size: phone ? .22 : .3, vertexColors: true, map: spriteTex, transparent: true, alphaTest: .08, depthWrite: false, sizeAttenuation: true, opacity: .95, blending: st.dark ? THREE.AdditiveBlending : THREE.NormalBlending });
  const cloud = new THREE.Group(); const pts = new THREE.Points(geo, mat); cloud.add(pts); scene.add(cloud);
  const lineMat = new THREE.LineBasicMaterial({ color: 0x8b98a9, transparent: true, opacity: .6 });
  const edges = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(6, 4, 6)), lineMat); edges.position.y = 2; cloud.add(edges);
  const labels = new THREE.Group(); cloud.add(labels);
  function makeAxisLabels(dark) { while (labels.children.length) { const s = labels.children.pop(); s.material.map.dispose(); s.material.dispose(); } const c = dark ? '#e6edf3' : '#0b1220'; const a = textSprite('ΔV/V 0 → 20 %', c, 2.2); a.position.set(0, -.4, 3.5); const b = textSprite('E_hull,charge 0 → 300 meV', c, 2.6); b.position.set(-3.7, 2, 3.5); b.material.rotation = Math.PI / 2; const d = textSprite('band gap 0 → 5 eV', c, 2.2); d.position.set(3.6, -.4, 0); labels.add(a, b, d); }
  makeAxisLabels(st.dark); st.onTheme = dark => { makeAxisLabels(dark); paint(dark); geo.attributes.color.needsUpdate = true; mat.blending = dark ? THREE.AdditiveBlending : THREE.NormalBlending; mat.needsUpdate = true; lineMat.color.set(st.pal.muted); st.dirty = true; };
  // the 11 validation cathodes: bloomed markers at their descriptor coordinates, ordered from least to most durable
  const V = [...D.validation].filter(v => v.dv !== undefined).sort((a, b) => a.exp_cycles - b.exp_cycles);
  const CAT = { A: 0x22d3ee, B: 0x34d399, C: 0xf59e0b, D: 0xf87171 };
  const markers = V.map(v => { const g = new THREE.Group(); const m = new THREE.Mesh(new THREE.SphereGeometry(.11, 16, 12), new THREE.MeshBasicMaterial({ color: CAT[v.cat] })); const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: spriteTex, color: CAT[v.cat], transparent: true, opacity: .55, depthWrite: false })); halo.scale.set(.6, .6, 1); g.add(m, halo); const lab = textSprite(`${v.name} · ${v.exp_cycles.toLocaleString()} cycles`, '#ffffff', 1.35); lab.position.y = .3; g.add(lab); g.position.set(sx(v.dv), sy(v.eh), sz(v.bg)); g.userData = { v, m, halo, lab }; cloud.add(g); return g; });
  // camera path: overview, then a thread through the validation markers
  const wide = () => st.wide !== false; const off = () => wide() ? 2.6 : 0;
  const pts3 = [[6.8, 4.6, 8.8], [3.8, 4.2, 6.2]]; const tg3 = [[-.4, 1.2, 0], [-.4, 1.4, 0]];
  markers.forEach((g, i) => { const p = g.position; pts3.push([p.x + (i % 2 ? 1.3 : -1.3), p.y + .9, p.z + 1.8]); tg3.push([p.x, p.y, p.z]); });
  pts3.push([2.5, 5.2, 8.5]); tg3.push([0, 1.4, 0]);
  const path = cameraPath(pts3, tg3); const pos3 = new THREE.Vector3(), tgt3 = new THREE.Vector3(); let dragging = false, lastT = -1;
  const focusEl = document.getElementById('heroFocus');
  canvas.addEventListener('pointerdown', () => dragging = true); addEventListener('pointerup', () => setTimeout(() => dragging = false, 2500)); ctr.addEventListener('change', () => st.dirty = true);
  // hover picking (desktop only)
  const ray = new THREE.Raycaster(); ray.params.Points.threshold = .12; const mouse = new THREE.Vector2(-2, -2), tip = document.getElementById('tip'); let mx = 0, my = 0, hover = -1, frame = 0;
  if (!phone && tip) { canvas.addEventListener('pointermove', e => { const r = canvas.getBoundingClientRect(); mx = e.clientX - r.left; my = e.clientY - r.top; mouse.set(mx / r.width * 2 - 1, -(my / r.height) * 2 + 1); st.dirty = true; }); canvas.addEventListener('pointerleave', () => { mouse.set(-2, -2); tip.style.opacity = 0; }); }
  cloud.position.set(off(), 0, 0); path.at(reduced ? 1 : 0, pos3, tgt3); camera.position.copy(pos3).add(new THREE.Vector3(off(), 0, 0)); ctr.target.copy(tgt3).add(new THREE.Vector3(off(), 0, 0)); ctr.update();
  st.loop((t) => {
    const T = S.hero.t; let changed = false; cloud.position.x = off();
    path.at(reduced ? 1 : T, pos3, tgt3); pos3.x += off(); tgt3.x += off();
    if (!dragging && camera.position.distanceToSquared(pos3) > 1e-6) { camera.position.lerp(pos3, reduced ? 1 : .08); changed = true; }
    ctr.target.lerp(tgt3, .08); ctr.autoRotate = !reduced && T < .12 && !dragging; if (ctr.autoRotate || dragging) changed = true; ctr.update();
    // which marker is the camera visiting: segment index along the path
    const seg = Math.max(0, Math.min(markers.length - 1, Math.round((T * (pts3.length - 1)) - 2)));
    const visiting = T > .1 && T < .97 ? seg : -1;
    markers.forEach((g, i) => { const on = i === visiting; const s = on ? 1.6 : 1; if (Math.abs(g.userData.m.scale.x - s) > .01) { g.userData.m.scale.setScalar(s); g.userData.halo.scale.setScalar(on ? 1.2 : .6); changed = true; } g.userData.lab.visible = on || T < .1 || T > .97; });
    if (focusEl) { const v = visiting >= 0 ? markers[visiting].userData.v : null; const txt = v ? `${v.name}: ${v.exp_cycles.toLocaleString()} cycles reported · ΔV/V ${v.dv} % · E_hull,charge ${Math.round(v.eh * 1000)} meV · E_g ${v.bg} eV · DSI ${v.dsi} (class ${v.cat})` : '787 oxide cathodes coloured by DSI. Scroll to fly to the eleven validation cathodes.'; if (focusEl.textContent !== txt) focusEl.textContent = txt; }
    st.setBloom(.4 + .3 * S.hero.glow);
    if (st.bokeh) st.bokeh.uniforms.focus.value = camera.position.distanceTo(ctr.target);
    if (!phone && tip && ++frame % 2 === 0 && mouse.x > -1.5) { ray.setFromCamera(mouse, camera); const hit = ray.intersectObject(pts)[0]; if (hit && hit.index !== hover) { hover = hit.index; const m = M[hover]; tip.innerHTML = `<b>${m[0]}</b><br>ΔV/V ${m[1]} % · E<sub>hull,ch</sub> ${Math.round(m[2] * 1000)} meV · E<sub>g</sub> ${m[3]} eV<br>DSI ${m[4].toFixed(2)} · class ${m[5]} · ${m[6].toLocaleString()} Wh/L`; tip.style.left = mx + 'px'; tip.style.top = my + 'px'; tip.style.opacity = 1; } else if (!hit) { hover = -1; tip.style.opacity = 0; } else { tip.style.left = mx + 'px'; tip.style.top = my + 'px'; } }
    if (Math.abs(T - lastT) > 1e-4) { lastT = T; changed = true; }
    return changed;
  });
})();

// ---------- sticky: LiCuO2 polymorph crystals ----------
(function () {
  const canvas = document.getElementById('xtalCanvas'); if (!canvas) return; const label = document.getElementById('xtalLabel');
  const st = createStage(canvas, { fov: 38, envIntensity: .7 }); if (st.failed) return; const { scene, camera } = st; camera.position.set(0, 6, 19);
  const ctr = new OrbitControls(camera, canvas); ctr.enableDamping = true; ctr.enableZoom = false; ctr.enablePan = false; ctr.autoRotate = !reduced; ctr.autoRotateSpeed = 1.1;
  const hemi = new THREE.HemisphereLight(0xffffff, 0x223355, .9); scene.add(hemi); const dl = new THREE.DirectionalLight(0xffffff, 1.5); dl.position.set(5, 8, 6); scene.add(dl); st.onTheme = () => { hemi.intensity = .9 * st.lights; dl.intensity = 1.5 * st.lights; }; st.onTheme();
  const EL = { Li: { c: 0xb06cff, r: .55 }, Cu: { c: 0xf59e0b, r: .62 }, O: { c: 0xf87171, r: .48 } }; const sph = new THREE.SphereGeometry(1, 24, 18); let group = null, cur = .001;
  function build(Sx) {
    if (group) { scene.remove(group); group.traverse(o => { if (o.geometry && o.geometry !== sph) o.geometry.dispose(); if (o.material) o.material.dispose(); }); }
    group = new THREE.Group(); const L = Sx.lattice, atoms = []; const rep = Sx.sites.length <= 4 ? [2, 2, 2] : [2, 2, 1];
    for (let a = 0; a < rep[0]; a++) for (let b = 0; b < rep[1]; b++) for (let c = 0; c < rep[2]; c++) for (const s of Sx.sites) { const f = [s.abc[0] + a, s.abc[1] + b, s.abc[2] + c]; atoms.push({ el: s.el, p: new THREE.Vector3(f[0] * L[0][0] + f[1] * L[1][0] + f[2] * L[2][0], f[0] * L[0][1] + f[1] * L[1][1] + f[2] * L[2][1], f[0] * L[0][2] + f[1] * L[1][2] + f[2] * L[2][2]) }); }
    const cen = atoms.reduce((v, a) => v.add(a.p), new THREE.Vector3()).multiplyScalar(1 / atoms.length); atoms.forEach(a => a.p.sub(cen));
    const byEl = {}; atoms.forEach(a => (byEl[a.el] = byEl[a.el] || []).push(a));
    for (const el in byEl) { const inst = new THREE.InstancedMesh(sph, new THREE.MeshStandardMaterial({ color: EL[el].c, roughness: .35, metalness: .1 }), byEl[el].length); const m4 = new THREE.Matrix4(); byEl[el].forEach((a, i) => { m4.makeScale(EL[el].r, EL[el].r, EL[el].r).setPosition(a.p); inst.setMatrixAt(i, m4); }); group.add(inst); }
    const segs = []; for (let i = 0; i < atoms.length; i++) for (let j = i + 1; j < atoms.length; j++) { const a = atoms[i], b = atoms[j]; const pair = a.el + b.el; const cut = (pair === 'CuO' || pair === 'OCu') ? 2.2 : (pair === 'LiO' || pair === 'OLi') ? 2.35 : 0; if (cut && a.p.distanceTo(b.p) < cut) segs.push(a.p.x, a.p.y, a.p.z, b.p.x, b.p.y, b.p.z); }
    group.add(new THREE.LineSegments(new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute(segs, 3)), new THREE.LineBasicMaterial({ color: 0x8b98a9, transparent: true, opacity: .7 })));
    const c = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]].map(f => new THREE.Vector3(f[0] * L[0][0] + f[1] * L[1][0] + f[2] * L[2][0], f[0] * L[0][1] + f[1] * L[1][1] + f[2] * L[2][1], f[0] * L[0][2] + f[1] * L[1][2] + f[2] * L[2][2]).sub(cen));
    const e = [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [0, 4], [1, 5], [2, 6], [3, 7]];
    group.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(e.flatMap(([i, j]) => [c[i], c[j]])), new THREE.LineBasicMaterial({ color: 0x22d3ee, transparent: true, opacity: .9 })));
    cur = reduced ? 1 : .001; group.scale.setScalar(cur); scene.add(group); st.dirty = true;
    if (label) label.innerHTML = `<b>${Sx.sg}</b>${Sx.id} · E<sub>hull</sub> ${Sx.ehull_meV} meV/atom · DSI ${Sx.dsi} (class ${Sx.dsi_class})`;
  }
  build(D.structures[0]); document.addEventListener('xtal', e => build(D.structures[+e.detail]));
  ctr.addEventListener('change', () => st.dirty = true);
  st.loop(() => { ctr.update(); let ch = ctr.autoRotate; if (group && Math.abs(1 - cur) > 1e-3) { cur += (1 - cur) * .08; group.scale.setScalar(cur); ch = true; } return ch; });
})();
