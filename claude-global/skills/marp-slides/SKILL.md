---
name: marp-slides
description: Create or edit a presentation as a Marp Markdown deck (slides/slides.md) with a clean custom theme, speaker notes and numbers kept in sync with the project's app, script and README. Use when the user asks for slides, a deck or a presentation inside a code project, or to update existing Marp slides.
---

# Marp slides

Slides live in the repo as Markdown, so they change together with the code.
The user edits them in VS Code with the **Marp for VS Code** extension.

## New deck

Create `slides/slides.md` starting with front matter like this (adjust colours to the topic):

```markdown
---
marp: true
title: <Talk title>
paginate: true
size: 16:9
style: |
  section { font-family: 'Segoe UI', 'Inter', sans-serif; background: #F4F1EA; color: #16181D;
            font-size: 30px; padding: 60px 80px; }
  h1, h2 { font-weight: 800; }
  h2 { font-size: 52px; margin-bottom: 24px; }
  strong { color: #2F5FC4; }                      /* idea A colour */
  em { color: #B5530F; font-style: normal; font-weight: 700; }   /* idea B colour */
  section.dark { background: #16181D; color: #F4F1EA; }
  section.lead { justify-content: center; }
  section.lead h1 { font-size: 80px; line-height: 1.1; }
  .big { font-size: 64px; font-weight: 800; }
---
```

Use `<!-- _class: lead -->` or `<!-- _class: dark -->` on a slide to change its look.

## Rules for good slides

- One idea per slide; at most ~6 short lines. Big numbers get their own slide with `.big`.
- Use two colours consistently for the two main ideas (e.g. **bold** = A, *em* = B) and say so in a CSS comment.
- Put what the speaker says in a `<!-- speaker notes -->` comment under each slide.
- Every number on a slide must match the app, README and video script. If one changes, update all
  and mention it. If the project has a video script, keep slide numbers referenced there correct.
- Images go in `slides/img/`, referenced with relative paths.

## Preview and export

- VS Code: open the file → preview icon (top right). Export: `Ctrl+Shift+P` → **Marp: Export slide deck…** → PDF or PPTX.
- Command line (needs Node): `npx @marp-team/marp-cli@latest slides/slides.md --pdf --allow-local-files`
- To check a deck yourself, export to HTML or images and look at a few slides before saying it's done.
