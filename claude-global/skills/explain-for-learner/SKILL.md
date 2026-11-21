---
name: explain-for-learner
description: Explain code, a change that was just made, an error, or a concept to someone who is learning to program - plain words, small examples from their own code, and one thing to try. Use when the user asks "explain", "what did you do", "why", "how does this work", "I don't understand", or after a bigger change when a walkthrough would help them learn.
---

# Explain for a learner

The user is learning. The goal is that they understand and could do it themselves next time.

## Shape of an explanation

1. **The big picture (1–2 sentences):** what this code or change does, in everyday words.
2. **Step by step:** walk through it in the order things happen, quoting short pieces of *their* code
   with `file:line` references. One idea per step.
3. **New words:** define each new term once, in one sentence, with a tiny example
   (e.g. "a *virtual environment* is a private folder of packages just for this project").
4. **Why this way:** one or two sentences on why this approach, and the simpler/other option you didn't pick.
5. **Try it yourself:** one small, safe thing they can change or run to see it work
   (a command, a number to tweak, a print to add), and what they should expect to see.

## Rules

- Short sentences. No jargon without a definition. No walls of text: use the steps above.
- Explain errors by saying what the message means, where it came from, and how the fix addresses it.
- Don't change code while explaining unless asked.
- If they seem stuck on the same idea, try a different angle (an analogy, a drawing in text, a smaller example).
