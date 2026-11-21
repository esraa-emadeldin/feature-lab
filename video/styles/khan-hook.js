// Hook scene in khan-explainer style: a blackboard lesson drawn to Ava's recorded voice.
scene({
  audio: 'hook.mp3',
  beats: [
    { at: 0.0, say: 'Is more data always better?', draw: p => {
        write('Is more data always better?', 640, 95, seg(p, 0, .85), { size: 60, color: C.yellow, center: true });
        stroke(curve([330, 115], [950, 113], [640, 124]), seg(p, .85, 1), { color: C.yellow, width: 4 });
    } },
    { at: 2.0, say: 'Imagine predicting whether a student will pass an exam.', draw: p => {
        // a quick chalk student
        stroke(oval(200, 300, 32, 32), seg(p, 0, .2));
        stroke(line([200, 332], [200, 440]), seg(p, .2, .3));
        stroke(line([200, 360], [160, 405]), seg(p, .3, .35));
        stroke(line([200, 360], [245, 395]), seg(p, .35, .4));
        stroke(line([200, 440], [170, 510]), seg(p, .4, .45));
        stroke(line([200, 440], [230, 510]), seg(p, .45, .5));
        write('student', 200, 555, seg(p, .5, .7), { size: 30, center: true });
        write('pass?', 290, 300, seg(p, .7, 1), { size: 40, color: C.orange });
    } },
    { at: 5.15, say: 'You could give the model everything:', draw: p => {
        stroke(box(960, 250, 230, 150), seg(p, 0, .4), { color: C.blue });
        write('MODEL', 1075, 340, seg(p, .4, .7), { size: 46, color: C.blue, center: true });
        write('everything!', 1075, 450, seg(p, .7, 1), { size: 30, center: true });
    } },
    { at: 7.1, say: 'study hours, sleep…', draw: p => {
        write('study hours', 470, 260, seg(p, 0, .5), { size: 38, color: C.green });
        write('sleep', 470, 330, seg(p, .5, 1), { size: 38, color: C.green });
    } },
    { at: 9.0, say: 'and also shoe size and favourite colour.', draw: p => {
        write('shoe size', 470, 400, seg(p, 0, .45), { size: 38, color: C.pink });
        write('favourite colour', 470, 470, seg(p, .45, .85), { size: 38, color: C.pink });
        write('??', 1210, 245, seg(p, .85, 1), { size: 48, color: C.pink });
        arrow([780, 360], [945, 330], seg(p, .85, 1));
    } },
    { at: 11.5, say: "Today we'll see why fewer,", draw: p => {
        stroke(line([460, 390], [640, 390]), seg(p, 0, .4), { color: C.red, width: 6 });
        stroke(line([460, 460], [745, 460]), seg(p, .4, .8), { color: C.red, width: 6 });
    } },
    { at: 13.4, say: 'better features can beat more data.', draw: p => {
        stroke(ring({ x: 465, y: 225, w: 210, h: 120 }, 18), seg(p, 0, .35), { color: C.green });
        write('fewer, better features  >  more data', 640, 650, seg(p, .35, .9), { size: 44, color: C.yellow, center: true });
        check(1195, 330, seg(p, .9, 1), { size: 40, color: C.green });
    } },
  ],
});
