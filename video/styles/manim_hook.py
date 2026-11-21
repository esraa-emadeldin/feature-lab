"""Hook scene in Manim (3Blue1Brown) style, timed to Ava's voice."""
import json
from pathlib import Path
from manim import *

HERE = Path(__file__).parent
WORDS = json.load(open(HERE / "hook-words.json"))


def at(word, nth=1):
    """When `word` is spoken (seconds)."""
    seen = 0
    for w in WORDS:
        if w["word"].lower().startswith(word.lower()):
            seen += 1
            if seen == nth:
                return w["start"]
    raise ValueError(word)


def tag(label, color):
    """A rounded box with a label: one feature."""
    text = Text(label, font_size=30)
    box = RoundedRectangle(corner_radius=0.15, width=text.width + 0.6, height=0.75, color=color)
    return VGroup(box, text)


class Hook(Scene):
    def until(self, t):
        """Wait until time t in the video (so animations land on the right word)."""
        if t > self.time:
            self.wait(t - self.time)

    def construct(self):
        self.add_sound(str(HERE / "hook.mp3"))

        title = Text("Is more data always better?", font_size=56)
        self.play(Write(title), run_time=1.6)
        self.until(at("imagine"))
        self.play(title.animate.scale(0.6).to_edge(UP), run_time=0.6)

        student = VGroup(Circle(0.35, color=WHITE), Line(DOWN * 0.35, DOWN * 1.3),
                         Line(DOWN * 0.6, DOWN * 0.9 + LEFT * 0.4), Line(DOWN * 0.6, DOWN * 0.9 + RIGHT * 0.4),
                         Line(DOWN * 1.3, DOWN * 1.9 + LEFT * 0.3), Line(DOWN * 1.3, DOWN * 1.9 + RIGHT * 0.3))
        student.move_to(LEFT * 5.3 + DOWN * 0.2)
        exam = Text("pass?", font_size=30, color=ORANGE).next_to(student, UP)
        self.until(at("student"))
        self.play(Create(student), FadeIn(exam, shift=UP * 0.2), run_time=0.9)

        model = VGroup(RoundedRectangle(corner_radius=0.2, width=2.6, height=1.6, color=BLUE),
                       Text("model", font_size=40, color=BLUE)).move_to(RIGHT * 4.6 + DOWN * 0.2)
        self.until(at("model"))
        self.play(GrowFromCenter(model), run_time=0.6)

        feats = [("study hours", "study", GREEN), ("sleep", "sleep", GREEN),
                 ("shoe size", "shoe", RED_B), ("favourite colour", "favourite", RED_B)]
        tags, arrows = [], []
        for i, (label, word, color) in enumerate(feats):
            t = tag(label, color).move_to(LEFT * 1.4 + UP * (1.2 - i * 1.0))
            a = Arrow(t.get_right(), model.get_left(), buff=0.15, stroke_width=3, color=GREY_B)
            self.until(at(word) - 0.15)
            self.play(FadeIn(t, shift=RIGHT * 0.5), GrowArrow(a), run_time=0.45)
            tags.append(t); arrows.append(a)
        q = Text("??", font_size=48, color=RED_B).next_to(model, UP)
        self.play(FadeIn(q, scale=1.5), Wiggle(model), run_time=0.6)

        # Junk features get crossed out and drop away.
        self.until(at("fewer"))
        crosses = [Cross(tags[i], stroke_color=RED, stroke_width=6) for i in (2, 3)]
        self.play(*[Create(c) for c in crosses], run_time=0.5)
        self.play(*[FadeOut(VGroup(tags[i], arrows[i], crosses[k]), shift=DOWN * 2)
                    for k, i in enumerate((2, 3))], FadeOut(q), run_time=0.6)

        self.until(at("better", 2))
        self.play(*[Indicate(tags[i], color=GREEN) for i in (0, 1)],
                  model.animate.set_color(GREEN), run_time=0.7)
        answer = Text("fewer, better features  >  more data", font_size=40, color=YELLOW).to_edge(DOWN, buff=0.8)
        self.play(Write(answer), run_time=1.0)
        self.until(WORDS[-1]["end"] + 0.8)
