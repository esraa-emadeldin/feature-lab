// Drawing toolkit for the cartoon.
//
// Every frame is drawn from scratch: make_video.py says "draw time t", and each scene
// returns an SVG picture for that moment. Because the picture only depends on t,
// the same t always gives the same frame. That makes the video easy to fix and re-render.
//
// The stage is 1280 x 720 units. (0, 0) is the top-left corner.

// ---------------------------------------------------------------- colours
const INK = "#1f2430";
const RED = "#e4572e";
const GREEN = "#2a9d8f";
const BLUE = "#3a86ff";
const YELLOW = "#fff1a8";
const PAPER = "#fbf7ee";

// ---------------------------------------------------------------- time
let T = 0;          // the current time in seconds, inside the current scene
let WORDS = [];     // when each word is spoken: [{word, start, end}, ...] (from edge-tts)
let SCENE = null;   // the scene being drawn

function clamp01(x) { return Math.max(0, Math.min(1, x)); }
function lerp(a, b, k) { return a + (b - a) * k; }
// Smooth start and smooth stop, so things don't move like robots (except the robot).
function ease(x) { x = clamp01(x); return x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2; }

// How far along an animation that begins at `start` and lasts `dur` seconds is: 0 → 1.
function prog(start, dur = 0.6) { return ease((T - start) / dur); }

// The moment a word is spoken. at("shoe") = when the voice says "shoe".
// Use nth=2 for the second time the word appears.
function at(word, nth = 1) {
  const want = word.toLowerCase();
  let seen = 0;
  for (const w of WORDS) {
    const clean = w.word.toLowerCase().replace(/[^a-z0-9%.']/g, "");
    if (clean.startsWith(want) && ++seen === nth) return w.start;
  }
  throw new Error(`Scene "${SCENE.id}": the word "${word}" (#${nth}) is not in the narration`);
}

// ---------------------------------------------------------------- hand-drawn lines
// A tiny random-number generator with a seed, so the "random" wobble is the same every render.
function rng(seed) {
  return function () {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
// "Boiling" lines: the wobble changes 8 times a second, like in hand-drawn cartoons.
let shapeCount = 0;
function nextRandom() {
  shapeCount++;
  return rng(shapeCount * 9973 + Math.floor(T * 8) * 7919);
}

// Turn a list of points into a slightly shaky, smooth SVG path.
function wobbly(points, jitter = 1.3, closed = false) {
  const r = nextRandom();
  const shake = () => (r() - 0.5) * 2 * jitter;
  if (closed) points = [...points, points[0]];
  const pts = [];
  for (let i = 0; i < points.length - 1; i++) {
    const [x1, y1] = points[i], [x2, y2] = points[i + 1];
    const steps = Math.max(1, Math.round(Math.hypot(x2 - x1, y2 - y1) / 30)); // a wobble every ~30 units
    for (let k = 0; k < steps; k++) {
      pts.push([lerp(x1, x2, k / steps) + shake(), lerp(y1, y2, k / steps) + shake()]);
    }
  }
  const last = points[points.length - 1];
  pts.push(closed ? pts[0] : [last[0] + shake(), last[1] + shake()]);
  // Curves through the midpoints make the line smooth instead of zig-zag.
  let d = `M${pts[0][0].toFixed(1)} ${pts[0][1].toFixed(1)}`;
  for (let i = 1; i < pts.length - 1; i++) {
    const mx = (pts[i][0] + pts[i + 1][0]) / 2, my = (pts[i][1] + pts[i + 1][1]) / 2;
    d += ` Q${pts[i][0].toFixed(1)} ${pts[i][1].toFixed(1)} ${mx.toFixed(1)} ${my.toFixed(1)}`;
  }
  const end = pts[pts.length - 1];
  return d + ` L${end[0].toFixed(1)} ${end[1].toFixed(1)}`;
}

// Draw a path. p = how much of it is drawn so far (0 = nothing, 1 = all).
// The "draw-on" trick: a dashed line whose dash slides along the path.
function stroke(d, { p = 1, w = 4, color = INK, fill = "none" } = {}) {
  if (p <= 0.001) return "";
  const fillOpacity = fill === "none" ? 1 : clamp01((p - 0.6) / 0.4); // fill fades in near the end
  return `<path d="${d}" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="${1 - p}"
    stroke="${color}" stroke-width="${w}" fill="${fill}" fill-opacity="${fillOpacity}"
    stroke-linecap="round" stroke-linejoin="round"/>`;
}

// ---------------------------------------------------------------- basic shapes
function line(x1, y1, x2, y2, o = {}) { return stroke(wobbly([[x1, y1], [x2, y2]]), o); }
function poly(points, o = {}) { return stroke(wobbly(points, 1.3, o.closed), o); }
function circle(cx, cy, r, o = {}) {
  const pts = [];
  for (let i = 0; i < 20; i++) {
    const a = (i / 20) * Math.PI * 2 - 2;
    pts.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]);
  }
  return stroke(wobbly(pts, Math.min(1.3, r / 8), true), o);
}
function rect(x, y, w, h, o = {}) { return poly([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], { ...o, closed: true }); }
function dot(x, y, r = 4, color = INK) { return `<circle cx="${x}" cy="${y}" r="${r}" fill="${color}"/>`; }

// Handwritten text that appears letter by letter as p goes from 0 to 1.
function text(str, x, y, { size = 40, p = 1, anchor = "middle", color = INK, opacity = 1 } = {}) {
  if (p <= 0) return "";
  const shown = str.slice(0, Math.ceil(clamp01(p) * str.length));
  const safe = shown.replace(/&/g, "&amp;").replace(/</g, "&lt;");
  return `<text x="${x}" y="${y}" font-family="Hand" font-size="${size}" fill="${color}"
    text-anchor="${anchor}" opacity="${opacity}">${safe}</text>`;
}

// Move / turn / grow a group of shapes.
function group(content, { x = 0, y = 0, s = 1, rot = 0, opacity = 1 } = {}) {
  if (opacity <= 0) return "";
  return `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})" opacity="${opacity}">${content}</g>`;
}

// The part of p that belongs to a slice [a, b] of a bigger animation (for drawing pieces in order).
function part(p, a, b) { return clamp01((p - a) / (b - a)); }

// ---------------------------------------------------------------- stick figures
// A pose is four limbs. Each limb is two angles in degrees: [upper part, lower part].
// 0 = pointing straight down, 90 = straight out to the side, 180 = straight up.
// Negative angles point inwards (across the body).
const POSES = {
  stand: { la: [22, 10], ra: [22, 10], ll: [8, 4], rl: [8, 4] },
  shrug: { la: [60, 150], ra: [60, 150], ll: [8, 4], rl: [8, 4] },
  wave:  { la: [22, 10], ra: [110, 165], ll: [8, 4], rl: [8, 4] },
  point: { la: [22, 10], ra: [80, 88], ll: [8, 4], rl: [8, 4] },
  hold:  { la: [22, 10], ra: [35, 100], ll: [8, 4], rl: [8, 4] },
  cheer: { la: [125, 155], ra: [125, 155], ll: [16, 8], rl: [16, 8] },
  think: { la: [22, 10], ra: [25, -150], ll: [8, 4], rl: [8, 4] },
  hips:  { la: [50, -40], ra: [50, -40], ll: [12, 8], rl: [12, 8] },
};
function mixPose(a, b, k) {
  const out = {};
  for (const limb in a) out[limb] = [lerp(a[limb][0], b[limb][0], k), lerp(a[limb][1], b[limb][1], k)];
  return out;
}
// A list of [time, poseName] → the pose right now, blending smoothly from one to the next.
function poseAt(keys, dur = 0.35) {
  let pose = POSES[keys[0][1]];
  for (const [t, name] of keys.slice(1)) pose = mixPose(pose, POSES[name], prog(t, dur));
  return pose;
}
// A list of [time, value] → the latest value whose time has come (for moods, labels...).
function stepAt(keys) {
  let value = keys[0][1];
  for (const [t, v] of keys) if (T >= t) value = v;
  return value;
}

// One arm or leg: from a joint, out along two angles. side = -1 (screen left) or +1 (right).
function limb(x, y, [a1, a2], side, len, p) {
  const r = Math.PI / 180;
  const x1 = x + side * Math.sin(a1 * r) * len, y1 = y + Math.cos(a1 * r) * len;
  const x2 = x1 + side * Math.sin(a2 * r) * len, y2 = y1 + Math.cos(a2 * r) * len;
  return { svg: poly([[x, y], [x1, y1], [x2, y2]], { p, w: 5 }), hand: [x2, y2] };
}

// A face. mood: happy, neutral, confused, sad, surprised, dizzy, worried.
function face(cx, cy, mood, p) {
  if (p <= 0) return "";
  const blink = mood !== "dizzy" && (T + cx * 0.013) % 3.3 < 0.12;
  let s = "";
  if (mood === "dizzy") {
    for (const ex of [-10, 10]) s += line(cx + ex - 5, cy - 9, cx + ex + 5, cy + 1, { w: 3 }) + line(cx + ex + 5, cy - 9, cx + ex - 5, cy + 1, { w: 3 });
  } else if (blink) {
    s += line(cx - 14, cy - 4, cx - 6, cy - 4, { w: 3 }) + line(cx + 6, cy - 4, cx + 14, cy - 4, { w: 3 });
  } else {
    const r = mood === "surprised" ? 5 : 3.5;
    s += dot(cx - 10, cy - 4, r) + dot(cx + 10, cy - 4, r);
  }
  if (mood === "happy") s += stroke(`M${cx - 11} ${cy + 7} Q${cx} ${cy + 19} ${cx + 11} ${cy + 7}`, { w: 3 });
  if (mood === "neutral") s += line(cx - 7, cy + 11, cx + 7, cy + 11, { w: 3 });
  if (mood === "sad") s += stroke(`M${cx - 10} ${cy + 15} Q${cx} ${cy + 6} ${cx + 10} ${cy + 15}`, { w: 3 });
  if (mood === "surprised") s += circle(cx, cy + 12, 5, { w: 3 });
  if (mood === "confused" || mood === "worried" || mood === "dizzy") {
    s += poly([[cx - 10, cy + 12], [cx - 4, cy + 9], [cx + 2, cy + 13], [cx + 9, cy + 9]], { w: 3 });
  }
  if (mood === "confused") s += line(cx + 5, cy - 16, cx + 16, cy - 20, { w: 3 }); // one raised eyebrow
  if (mood === "worried") s += line(cx - 15, cy - 15, cx - 5, cy - 12, { w: 3 }) + line(cx + 5, cy - 12, cx + 15, cy - 15, { w: 3 });
  return group(s, { opacity: clamp01(p * 2) });
}

// A stick figure standing with its feet at (x, y). It is about 220 units tall at s = 1.
//   pose: a POSES object (use poseAt), mood: see face(), p: how much is drawn (0 → 1)
//   head: "round" for a person, "robot" for the model. hair: true adds a little tuft.
// Returns {svg, hand} — hand is where the right hand is (in stage units), to hold things.
function stickman({ x, y, pose = POSES.stand, mood = "happy", p = 1, s = 1, head = "round", hair = false, tilt = 0 }) {
  const bob = Math.sin(T * 2.4 + x) * 2; // gentle breathing
  const hip = -85, neck = -160, shoulder = -140;
  let svg = "";
  // Pieces appear in this order: head, body, then arms and legs.
  const pHead = part(p, 0, 0.35), pBody = part(p, 0.3, 0.55), pLimbs = part(p, 0.5, 1);
  let h = "";
  if (head === "robot") {
    h += rect(-40, -66, 80, 62, { p: pHead, w: 5, fill: "#e8eef9" });
    h += line(0, -66, 0, -86, { p: pHead, w: 4 }) + (pHead > 0.9 ? dot(0, -90, 6, RED) : "");
    h += face(0, -36, mood, pHead);
  } else {
    h += circle(0, -30, 28, { p: pHead, w: 5, fill: PAPER });
    if (hair) h += poly([[-12, -56], [-6, -68], [0, -58], [6, -70], [12, -57]], { p: pHead, w: 4 });
    h += face(0, -30, mood, pHead);
  }
  svg += line(0, neck, 0, hip, { p: pBody, w: 5 });
  const left = limb(0, shoulder, pose.la, -1, 34, pLimbs);
  const right = limb(0, shoulder, pose.ra, 1, 34, pLimbs);
  const lleg = limb(0, hip, pose.ll, -1, 46, pLimbs);
  const rleg = limb(0, hip, pose.rl, 1, 46, pLimbs);
  svg += left.svg + right.svg + lleg.svg + rleg.svg;
  // The head is painted last, so raised arms go behind it instead of across the face.
  svg += group(h, { y: neck + 2, rot: tilt });
  return {
    svg: group(svg, { x, y: y + bob, s }),
    hand: [x + right.hand[0] * s, y + bob + right.hand[1] * s],
  };
}

// ---------------------------------------------------------------- little icons (about 60 x 60)
const ICONS = {
  clock: (p) => circle(0, 0, 24, { p, w: 4 }) + line(0, 0, 0, -15, { p, w: 4 }) + line(0, 0, 11, 6, { p, w: 4 }),
  moon: (p) => stroke("M8 -24 A24 24 0 1 0 22 10 A18 18 0 1 1 8 -24 Z", { p, w: 4 }) + text("z", 20, -14, { size: 22, p }) + text("z", 30, -26, { size: 16, p }),
  shoe: (p) => poly([[-26, -14], [-26, 12], [28, 12], [28, 2], [6, -4], [-6, -16]], { p, w: 4, closed: true, fill: "#f4c9b8" }) + line(-26, 6, 28, 6, { p, w: 3 }),
  palette: (p) => circle(0, 0, 25, { p, w: 4, fill: "#f6e7cf" }) + (p > 0.8 ? dot(-10, -8, 5, RED) + dot(5, -13, 5, BLUE) + dot(12, 2, 5, GREEN) : "") + circle(-6, 10, 5, { p, w: 3 }),
  book: (p) => rect(-24, -18, 48, 36, { p, w: 4 }) + line(0, -18, 0, 18, { p, w: 3 }),
  grade: (p) => text("A+", 0, 14, { size: 44, p, color: GREEN }),
  calendar: (p) => rect(-22, -18, 44, 38, { p, w: 4 }) + line(-22, -8, 22, -8, { p, w: 3 }) + check(0, 6, p),
};

// A sticky note with an icon and a label. Centre at (x, y).
function card(label, icon, x, y, { p = 1, rot = 0, s = 1, fill = YELLOW } = {}) {
  const c = rect(-80, -55, 160, 110, { p, w: 3.5, fill }) + group(ICONS[icon](part(p, 0.3, 1)), { y: -10 }) +
    text(label, 0, 42, { size: 26, p: part(p, 0.5, 1) });
  return group(c, { x, y, rot, s });
}

// Simple marks.
function check(x, y, p, color = GREEN) { return poly([[x - 18, y], [x - 4, y + 16], [x + 22, y - 18]], { p, w: 7, color }); }
function cross(x, y, size, p, color = RED) {
  return line(x - size, y - size, x + size, y + size, { p: part(p, 0, 0.5), w: 7, color }) +
         line(x + size, y - size, x - size, y + size, { p: part(p, 0.5, 1), w: 7, color });
}
function arrow(x1, y1, x2, y2, p, color = INK) {
  const a = Math.atan2(y2 - y1, x2 - x1), k = 18;
  const head = [[x2 - k * Math.cos(a - 0.5), y2 - k * Math.sin(a - 0.5)], [x2, y2], [x2 - k * Math.cos(a + 0.5), y2 - k * Math.sin(a + 0.5)]];
  return line(x1, y1, x2, y2, { p: part(p, 0, 0.7), w: 5, color }) + poly(head, { p: part(p, 0.7, 1), w: 5, color });
}
function sparkle(x, y, size, p, color = "#f4a300") {
  return line(x - size, y, x + size, y, { p, w: 4, color }) + line(x, y - size, x, y + size, { p, w: 4, color });
}
function sweat(x, y, p) { return stroke(`M${x} ${y} Q${x - 8} ${y + 14} ${x} ${y + 18} Q${x + 8} ${y + 14} ${x} ${y} Z`, { p, w: 3, color: BLUE, fill: "#cfe3ff" }); }

// ---------------------------------------------------------------- captions
// Split the narration into short pieces and show each piece while it is being said.
function captions() {
  if (!WORDS.length) return "";
  const pieces = [];
  for (const clause of SCENE.say.split(/(?<=[.?!,:…])\s+/)) {
    const words = clause.split(/\s+/);
    for (let i = 0; i < words.length; i += 9) pieces.push(words.slice(i, i + 9).join(" "));
  }
  // Match pieces to the voice by counting words (edge-tts may split words a bit differently).
  const total = pieces.reduce((n, piece) => n + piece.split(/\s+/).length, 0);
  let count = 0, current = "";
  for (const piece of pieces) {
    const idx = Math.min(WORDS.length - 1, Math.round((count / total) * WORDS.length));
    if (T >= WORDS[idx].start - 0.1) current = piece;
    count += piece.split(/\s+/).length;
  }
  return `<rect x="140" y="652" width="1000" height="50" rx="14" fill="${PAPER}" opacity="0.85"/>` +
    text(current, 640, 688, { size: 32, color: "#444" });
}

// ---------------------------------------------------------------- the stage
const SCENES = [];

function loadScene(index, words) {
  SCENE = SCENES[index];
  WORDS = words;
}

function drawAt(t) {
  T = t;
  shapeCount = 0;
  const svg = document.getElementById("stage");
  svg.innerHTML = `<rect width="1280" height="720" fill="${PAPER}"/>` + SCENE.draw() + captions();
}
