// Hook scene as YouTube-style motion graphics, timed to Ava's voice (words.json from edge-tts).
import React from "react";
import {
  AbsoluteFill, Audio, Composition, interpolate, spring, staticFile,
  useCurrentFrame, useVideoConfig,
} from "remotion";
import words from "./words.json";

const FPS = 30;
const BG = "#0f172a", INK = "#f8fafc", GOOD = "#22c55e", BAD = "#ef4444", ACCENT = "#facc15", BLUE = "#38bdf8";

// Frame when a word is spoken (nth = which time it appears).
const at = (word: string, nth = 1) => {
  let seen = 0;
  for (const w of words) if (w.word.toLowerCase().startsWith(word) && ++seen === nth) return Math.round(w.start * FPS);
  throw new Error(`word ${word} not found`);
};
const END = Math.round((words[words.length - 1].end + 0.8) * FPS);

// 0 → 1 with a bouncy spring, starting at frame `from`.
const usePop = (from: number) => {
  const frame = useCurrentFrame(), { fps } = useVideoConfig();
  return spring({ frame: frame - from, fps, config: { damping: 12 } });
};

const Pill: React.FC<{ label: string; color: string; from: number; y: number; junkAt?: number }> = ({ label, color, from, y, junkAt }) => {
  const frame = useCurrentFrame();
  const pop = usePop(from);
  const red = junkAt !== undefined && frame >= junkAt;
  const fall = junkAt !== undefined ? Math.max(0, frame - junkAt - 18) : 0;
  return (
    <div style={{
      position: "absolute", left: 640 - 210, top: y + fall * fall * 0.9, width: 420, height: 78,
      transform: `translateX(${(1 - pop) * -300}px) scale(${pop}) rotate(${fall * 2}deg)`,
      opacity: interpolate(fall, [0, 25], [1, 0], { extrapolateRight: "clamp" }),
      borderRadius: 40, border: `5px solid ${red ? BAD : color}`, background: red ? "#450a0a" : "#1e293b",
      color: INK, fontSize: 40, fontWeight: 700, display: "flex", alignItems: "center", justifyContent: "center",
      textDecoration: red ? `line-through ${BAD} 6px` : "none",
    }}>{label}</div>
  );
};

const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const title = usePop(0), titleUp = usePop(at("imagine"));
  const model = usePop(at("model")), answer = usePop(at("better", 2) + 10);
  const confused = frame >= at("shoe") && frame < at("fewer");
  const happy = frame >= at("better", 2);
  const shake = confused ? Math.sin(frame * 1.3) * 6 : 0;
  return (
    <AbsoluteFill style={{ background: BG, fontFamily: "Inter, Segoe UI, Arial, sans-serif" }}>
      <Audio src={staticFile("hook.mp3")} />
      {/* Title: big in the middle, then shrinks to the top */}
      <div style={{
        position: "absolute", width: "100%", textAlign: "center", color: INK, fontWeight: 900,
        top: interpolate(titleUp, [0, 1], [300, 40]), fontSize: interpolate(titleUp, [0, 1], [86, 46]),
        transform: `scale(${title})`,
      }}>Is <span style={{ color: ACCENT }}>more data</span> always better?</div>

      {/* The student (emoji keeps it simple) */}
      <div style={{ position: "absolute", left: 90, top: 270, fontSize: 150, transform: `scale(${usePop(at("student"))})` }}>🧑‍🎓</div>

      {/* Features flying in */}
      <Pill label="study hours" color={GOOD} from={at("study") - 4} y={170} />
      <Pill label="sleep" color={GOOD} from={at("sleep") - 4} y={270} />
      <Pill label="shoe size" color={GOOD} from={at("shoe") - 4} y={370} junkAt={at("fewer")} />
      <Pill label="favourite colour" color={GOOD} from={at("favourite") - 4} y={470} junkAt={at("fewer")} />

      {/* The model */}
      <div style={{
        position: "absolute", left: 960, top: 260, width: 240, height: 200, borderRadius: 28,
        border: `6px solid ${happy ? GOOD : BLUE}`, background: "#0b2537", color: INK,
        display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
        fontSize: 40, fontWeight: 800, transform: `scale(${model}) translateX(${shake}px)`,
      }}>
        <div style={{ fontSize: 80 }}>{happy ? "😄" : confused ? "😵‍💫" : "🤖"}</div>model
      </div>

      {/* The answer */}
      <div style={{
        position: "absolute", bottom: 50, width: "100%", textAlign: "center", fontSize: 52, fontWeight: 900,
        color: ACCENT, transform: `translateY(${(1 - answer) * 120}px)`, opacity: answer,
      }}>Fewer, better features beat more data</div>
    </AbsoluteFill>
  );
};

export const MyComposition = () => (
  <Composition id="Hook" component={Hook} durationInFrames={END} fps={FPS} width={1280} height={720} />
);
