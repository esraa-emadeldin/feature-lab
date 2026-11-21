// The scenes of the video, in order.
//
// Each scene has:
//   id   - a short name (use it with: python video/make_video.py --only <id>)
//   say  - what the voice reads. Copied from docs/video-script.md, keep them in sync!
//   draw - returns the picture for the current time T. Use at("word") to make
//          something happen exactly when that word is spoken.

// ============================================================ 1 · Hook (0:00–0:20)
SCENES.push({
  id: "hook",
  say: "Is more data always better? Imagine predicting whether a student will pass an exam. " +
       "You could give the model everything: study hours, sleep… and also shoe size and favourite colour. " +
       "Today we'll see why fewer, better features can beat more data.",
  draw() {
    let s = "";

    // --- Title at the top: a question first, then the answer at the end.
    const fadeQuestion = 1 - prog(at("imagine"), 0.4);
    s += text("Is more data always better?", 640, 100, { size: 66, p: prog(0, 1.4), opacity: fadeQuestion });
    s += text("Fewer, better features beat more data!", 640, 100, { size: 60, p: prog(at("fewer"), 1.6), color: GREEN });

    // --- The student (left). Shrugs at "better?", holds the exam, then hands over features.
    const student = stickman({
      x: 220, y: 580, hair: true, p: prog(0.2, 1.2),
      pose: poseAt([[0, "stand"], [at("better"), "shrug"], [at("imagine"), "hold"],
                    [at("everything"), "point"], [at("beat"), "cheer"]]),
      mood: stepAt([[0, "happy"], [at("better"), "confused"], [at("imagine"), "happy"]]),
    });
    s += student.svg;
    // Question marks above the student while they wonder.
    const wonder = prog(at("better"), 0.3) * (1 - prog(at("imagine"), 0.3));
    s += text("?", 170, 330, { size: 60, opacity: wonder, color: BLUE }) + text("?", 270, 310, { size: 48, opacity: wonder, color: BLUE });
    // The exam paper in the student's hand, from "student" until "everything".
    const paper = prog(at("student"), 0.4) * (1 - prog(at("everything"), 0.3));
    s += group(rect(-35, -45, 70, 90, { w: 3, fill: "#ffffff" }) + text("EXAM", 0, -15, { size: 20 }) +
               text("pass?", 0, 15, { size: 20, color: RED }), { x: student.hand[0] + 20, y: student.hand[1] - 30, opacity: paper, rot: 8 });

    // --- The model (a robot, right). Happy with good features, confused by silly ones.
    const robotMood = stepAt([[0, "neutral"], [at("study"), "happy"], [at("shoe"), "confused"],
                              [at("colour"), "dizzy"], [at("fewer"), "happy"]]);
    const dizzy = robotMood === "dizzy" ? Math.sin(T * 9) * 8 : 0;
    const robot = stickman({
      x: 1060, y: 580, head: "robot", mood: robotMood, tilt: dizzy, p: prog(at("model"), 1),
      pose: poseAt([[0, "stand"], [at("shoe"), "think"], [at("colour"), "hips"], [at("beat"), "cheer"]]),
    });
    s += robot.svg;
    s += text("the model", 1060, 630, { size: 30, p: prog(at("model") + 0.6, 0.6) });
    if (robotMood === "confused") s += text("?", 1110, 330, { size: 70, color: RED });
    if (robotMood === "dizzy") s += sweat(1010, 350, 1) + sweat(1120, 340, 1);
    if (T > at("beat")) s += sparkle(980, 330, 14, prog(at("beat"), 0.3)) + sparkle(1145, 300, 18, prog(at("beat") + 0.15, 0.3));

    // --- Feature cards fly from the student into a 2 x 2 pile in the middle.
    const cards = [
      { label: "study hours", icon: "clock",   x: 545, y: 300, word: "study", junk: false, rot: -4 },
      { label: "sleep",       icon: "moon",    x: 735, y: 300, word: "sleep", junk: false, rot: 3 },
      { label: "shoe size",   icon: "shoe",    x: 545, y: 455, word: "shoe",  junk: true,  rot: 5 },
      { label: "fav. colour", icon: "palette", x: 735, y: 455, word: "colour", junk: true, rot: -3 },
    ];
    for (const c of cards) {
      const start = at(c.word) - 0.2;
      const fly = prog(start, 0.55);
      if (fly <= 0) continue;
      // Fly along an arc from the student's hand to the card's place.
      let x = lerp(320, c.x, fly), y = lerp(400, c.y, fly) - Math.sin(fly * Math.PI) * 120;
      let rot = c.rot * fly;
      if (c.junk) {
        // At "fewer" a red X appears, then at "better" the junk card falls off the screen.
        const fall = Math.max(0, T - at("better", 2));
        y += 0.5 * 2200 * fall * fall;
        rot += fall * 240;
        s += card(c.label, c.icon, x, y, { p: prog(start, 0.9), rot, s: lerp(0.4, 1, fly), fill: fall > 0 ? "#ffd9cf" : YELLOW });
        if (T > at("fewer")) s += cross(x, y, 55, prog(at("fewer"), 0.4));
      } else {
        s += card(c.label, c.icon, x, y, { p: prog(start, 0.9), rot, s: lerp(0.4, 1, fly) });
        if (T > at("better", 2)) s += check(x + 62, y - 50, prog(at("better", 2), 0.35));
      }
    }
    return s;
  },
});
