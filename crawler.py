"""On-screen spider or rat that walks through spelling mistakes."""

from __future__ import annotations

import streamlit as st

_HTML = """
<div id="root">
  <div id="status"></div>
  <div id="track"><div id="bar"></div></div>
  <div id="page">
    <div id="creature" aria-hidden="true"><div id="bug"></div></div>
    <div id="lines"></div>
  </div>
</div>
"""

_CSS = """
#root {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
  border: 1px solid var(--st-border-color);
  border-radius: var(--st-base-radius);
  background: var(--st-code-background-color);
  color: var(--st-code-text-color);
}
#status {
  flex: none;
  min-height: 44px;
  padding: 10px 14px;
  box-sizing: border-box;
  background: var(--st-secondary-background-color);
  color: var(--st-text-color);
  font-family: var(--st-font, sans-serif);
  font-size: 14px;
  line-height: 1.45;
  border-bottom: 1px solid var(--st-border-color);
}
#track {
  flex: none;
  height: 4px;
  background: var(--st-border-color);
}
#bar {
  height: 100%;
  width: 0%;
  background: var(--st-green-color);
  transition: width 0.25s ease;
}
#page {
  position: relative;
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 8px 0 24px;
}
#lines {
  font-family: var(--st-code-font, ui-monospace, monospace);
  font-size: 14px;
  line-height: 1.7;
}
.row {
  display: flex;
  align-items: flex-start;
  min-height: 1.7em;
  padding-right: 16px;
}
.row.active {
  background: color-mix(in srgb, var(--st-primary-color) 16%, transparent);
}
.gutter {
  flex: none;
  width: 52px;
  padding: 0 10px 0 0;
  text-align: right;
  color: color-mix(in srgb, var(--st-text-color) 45%, transparent);
  user-select: none;
}
.code {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  min-height: 1.7em;
}
.word {
  border-radius: 4px;
  padding: 0 2px;
}
.word.bad {
  color: var(--st-red-color);
  background: var(--st-red-background-color);
  text-decoration: underline wavy var(--st-red-color);
  text-underline-offset: 3px;
}
.word.fixing {
  outline: 2px solid var(--st-yellow-color);
  background: var(--st-yellow-background-color);
  color: var(--st-yellow-color);
}
.word.good {
  color: var(--st-green-text-color);
  background: var(--st-green-background-color);
  text-decoration: none;
  animation: pop 0.35s ease;
}
@keyframes pop {
  from { transform: scale(1.18); }
  to { transform: scale(1); }
}
#creature {
  position: absolute;
  left: 0;
  top: 0;
  width: 92px;
  height: 68px;
  z-index: 6;
  pointer-events: none;
  transition: transform 0.72s cubic-bezier(0.22, 0.8, 0.2, 1);
  filter: drop-shadow(0 8px 5px rgba(0, 0, 0, 0.5));
}
#bug {
  width: 92px;
  height: 68px;
}
#creature.walking #bug {
  animation: hop 0.16s ease-in-out infinite alternate;
}
#creature.walking .leg {
  transform-box: fill-box;
  transform-origin: center;
  animation: kick 0.16s ease-in-out infinite alternate;
}
#creature.walking .leg:nth-child(odd) {
  animation-delay: 0.08s;
}
@keyframes hop {
  from { transform: translateY(0); }
  to { transform: translateY(-5px); }
}
@keyframes kick {
  from { transform: rotate(-12deg); }
  to { transform: rotate(12deg); }
}
"""

_JS = r"""
const SPIDER = `
<svg viewBox="0 0 92 68" width="92" height="68" aria-hidden="true">
  <g class="legs" fill="none" stroke="#d5deea" stroke-width="3.2" stroke-linecap="round">
    <path class="leg" d="M34 32 C18 20 10 16 4 8"/>
    <path class="leg" d="M36 36 C18 34 8 42 4 56"/>
    <path class="leg" d="M40 28 C24 10 16 6 10 2"/>
    <path class="leg" d="M42 40 C26 52 16 60 12 66"/>
    <path class="leg" d="M62 28 C74 12 82 8 90 4"/>
    <path class="leg" d="M64 38 C78 46 84 56 90 64"/>
    <path class="leg" d="M58 26 C72 14 80 12 88 16"/>
    <path class="leg" d="M60 42 C74 50 82 54 88 50"/>
  </g>
  <ellipse cx="34" cy="36" rx="16" ry="13" fill="#e8eef6"/>
  <ellipse cx="56" cy="34" rx="13" ry="11" fill="#f4f7fb"/>
  <circle cx="60" cy="30" r="2.1" fill="#1b1e24"/>
  <circle cx="67" cy="32" r="2.1" fill="#1b1e24"/>
  <circle cx="60.6" cy="29.4" r="0.7" fill="#e5c07b"/>
  <circle cx="67.6" cy="31.4" r="0.7" fill="#e5c07b"/>
  <circle cx="28" cy="32" r="2.4" fill="#98c379"/>
</svg>`

const RAT = `
<svg viewBox="0 0 92 68" width="92" height="68" aria-hidden="true">
  <path d="M18 40 C6 28 4 18 14 16" fill="none" stroke="#c7b4a4" stroke-width="3" stroke-linecap="round"/>
  <ellipse cx="46" cy="40" rx="24" ry="14" fill="#e6d3c4"/>
  <ellipse cx="70" cy="36" rx="14" ry="11" fill="#efdfd2"/>
  <ellipse cx="62" cy="22" rx="6" ry="7" fill="#efdfd2"/>
  <ellipse cx="74" cy="20" rx="6" ry="7" fill="#efdfd2"/>
  <ellipse cx="62" cy="23" rx="3" ry="4" fill="#e7a0b0"/>
  <ellipse cx="74" cy="21" rx="3" ry="4" fill="#e7a0b0"/>
  <circle cx="76" cy="35" r="1.7" fill="#1b1e24"/>
  <circle cx="83" cy="38" r="2.2" fill="#e07a93"/>
  <path d="M80 40 C86 44 88 48 84 50" fill="none" stroke="#c9b3a6" stroke-width="1"/>
</svg>`

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function esc(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
}

function escAttr(value) {
  return esc(value).replace(/"/g, "&quot;")
}

function crawlerName(data) {
  return data && data.creature === "rat" ? "Rat" : "Spider"
}

function waitingText(data) {
  const name = crawlerName(data).toLowerCase()
  const count = (data.fixes || []).length
  if (!data.text) {
    return "Open a file to begin."
  }
  if (!count) {
    return "No spelling mistakes in this file."
  }
  const noun = count === 1 ? "mistake is" : "mistakes are"
  return (
    count +
    " spelling " +
    noun +
    " marked in red. Click Debug code and the " +
    name +
    " will crawl in and fix each one."
  )
}

function renderLines(lines, text, fixes) {
  const at = new Map()
  for (const fix of fixes) {
    at.set(fix.start, fix)
  }
  let html = ""
  let lineNo = 1
  let index = 0
  const open = () => {
    html += '<div class="row"><span class="gutter">' + lineNo + '</span><span class="code">'
  }
  const close = () => {
    html += "</span></div>"
    lineNo += 1
  }
  open()
  while (index < text.length) {
    const fix = at.get(index)
    if (fix) {
      html +=
        '<span class="word bad" data-fix="' +
        escAttr(fix.corrected) +
        '" data-line="' +
        String(fix.line) +
        '">' +
        esc(fix.original) +
        "</span>"
      index = fix.end
      continue
    }
    if (text[index] === "\n") {
      close()
      open()
      index += 1
      continue
    }
    let next = index + 1
    while (next < text.length && text[next] !== "\n" && !at.has(next)) {
      next += 1
    }
    html += esc(text.slice(index, next))
    index = next
  }
  close()
  lines.innerHTML = html
}

function contentPoint(page, target) {
  const pageRect = page.getBoundingClientRect()
  const rect = target.getBoundingClientRect()
  return {
    x: rect.left - pageRect.left + page.scrollLeft,
    y: rect.top - pageRect.top + page.scrollTop,
  }
}

function moveTo(page, creature, target) {
  const point = contentPoint(page, target)
  const x = Math.max(0, point.x - 40)
  const y = Math.max(0, point.y - 24)
  creature.style.transform = "translate(" + x + "px, " + y + "px)"
  const top = y - page.clientHeight * 0.35
  page.scrollTo({ top: Math.max(0, top), behavior: "smooth" })
}

const TUNES = {
  spider: {
    notes: [523.25, 659.25, 783.99, 659.25, 587.33, 523.25, 440.0, 493.88],
    bass: [261.63, 196.0, 220.0, 174.61],
    pace: 320,
  },
  rat: {
    notes: [392.0, 493.88, 587.33, 493.88, 440.0, 392.0, 329.63, 349.23],
    bass: [196.0, 146.83, 164.81, 130.81],
    pace: 280,
  },
}

function audioBox() {
  const AudioCtx = window.AudioContext || window.webkitAudioContext
  if (!AudioCtx) return null
  if (!window.__spellCrawlerMusic) {
    const ctx = new AudioCtx()
    const master = ctx.createGain()
    master.gain.value = 0.08
    master.connect(ctx.destination)
    window.__spellCrawlerMusic = { ctx: ctx, master: master, timer: null, step: 0, kind: "" }
  }
  return window.__spellCrawlerMusic
}

function unlockAudio() {
  const box = audioBox()
  if (box && box.ctx.state === "suspended") box.ctx.resume()
}

if (!window.__spellCrawlerAudio) {
  window.__spellCrawlerAudio = true
  window.addEventListener("pointerdown", unlockAudio, true)
}

function playTone(box, freq, time, duration, type, level) {
  const osc = box.ctx.createOscillator()
  const gain = box.ctx.createGain()
  osc.type = type
  osc.frequency.setValueAtTime(freq, time)
  gain.gain.setValueAtTime(0.0001, time)
  gain.gain.exponentialRampToValueAtTime(level, time + 0.03)
  gain.gain.exponentialRampToValueAtTime(0.0001, time + duration)
  osc.connect(gain)
  gain.connect(box.master)
  osc.start(time)
  osc.stop(time + duration + 0.05)
}

function stopMusic() {
  const box = window.__spellCrawlerMusic
  if (!box || !box.timer) return
  window.clearInterval(box.timer)
  box.timer = null
  box.kind = ""
}

async function startMusic(kind) {
  const box = audioBox()
  if (!box) return
  await box.ctx.resume()
  if (box.timer && box.kind === kind) return
  stopMusic()
  const tune = TUNES[kind] || TUNES.spider
  box.kind = kind
  box.step = 0
  const tick = () => {
    if (box.ctx.state !== "running") return
    const time = box.ctx.currentTime
    const note = tune.notes[box.step % tune.notes.length]
    const bass = tune.bass[Math.floor(box.step / 2) % tune.bass.length]
    playTone(box, note, time, 0.24, "triangle", 0.2)
    if (box.step % 2 === 0) playTone(box, bass, time, 0.36, "sine", 0.11)
    box.step += 1
  }
  tick()
  box.timer = window.setInterval(tick, tune.pace)
}

async function play(root, data, runKey) {
  const page = root.querySelector("#page")
  const creature = root.querySelector("#creature")
  const status = root.querySelector("#status")
  const bar = root.querySelector("#bar")
  const words = [...root.querySelectorAll(".word")]
  const name = crawlerName(data)
  const tune = data.creature === "rat" ? "rat" : "spider"

  try {
    await startMusic(tune)
    root.dataset.music = window.__spellCrawlerMusic && window.__spellCrawlerMusic.ctx.state === "running" ? "playing" : "blocked"

    creature.style.transition = "none"
    creature.style.transform = "translate(-110px, 16px)"
    creature.classList.add("walking")
    await sleep(50)
    if (root.dataset.viewKey !== runKey) return
    creature.style.transition = "transform 0.72s cubic-bezier(0.22, 0.8, 0.2, 1)"

    if (!words.length) {
      status.textContent = name + " is crawling through the file."
      const firstLine = root.querySelector(".code")
      if (firstLine) moveTo(page, creature, firstLine)
      await sleep(900)
      if (root.dataset.viewKey !== runKey) return
      creature.classList.remove("walking")
      status.textContent = "No spelling mistakes. This file is already clean."
      return
    }

    status.textContent = name + " enters the file."
    await sleep(180)
    if (root.dataset.viewKey !== runKey) return

    for (let index = 0; index < words.length; index += 1) {
      if (root.dataset.viewKey !== runKey) return
      const word = words[index]
      if (!word.isConnected) return
      root.querySelectorAll(".row.active").forEach((row) => row.classList.remove("active"))
      const row = word.closest(".row")
      if (row) row.classList.add("active")
      word.classList.add("fixing")
      const from = word.textContent
      const to = word.dataset.fix || from
      status.textContent =
        name +
        " on line " +
        word.dataset.line +
        ': "' +
        from +
        '" becomes "' +
        to +
        '" (' +
        (index + 1) +
        " of " +
        words.length +
        ")"
      moveTo(page, creature, word)
      await sleep(560)
      if (!word.isConnected || root.dataset.viewKey !== runKey) return
      word.textContent = to
      word.classList.remove("bad", "fixing")
      word.classList.add("good")
      bar.style.width = ((index + 1) / words.length) * 100 + "%"
      await sleep(160)
    }

    if (root.dataset.viewKey !== runKey) return
    creature.classList.remove("walking")
    const noun = words.length === 1 ? "mistake" : "mistakes"
    status.textContent = name + " finished. " + words.length + " spelling " + noun + " corrected."
  } finally {
    if (root.dataset.viewKey === runKey) {
      stopMusic()
      root.dataset.music = "stopped"
    }
  }
}

export default function (component) {
  const { data, parentElement } = component
  const root = parentElement.querySelector("#root")
  if (!root || !data) return

  const fixes = data.fixes || []
  const runKey = [
    data.digest || "",
    data.runId || 0,
    data.animate ? "go" : "wait",
    data.creature || "spider",
    fixes.length,
  ].join("|")

  if (root.dataset.viewKey === runKey) return
  root.dataset.viewKey = runKey

  const bug = root.querySelector("#bug")
  const status = root.querySelector("#status")
  const bar = root.querySelector("#bar")
  const lines = root.querySelector("#lines")
  bug.innerHTML = data.creature === "rat" ? RAT : SPIDER
  bar.style.width = "0%"
  renderLines(lines, data.text || "", fixes)

  const creature = root.querySelector("#creature")
  creature.classList.remove("walking")
  creature.style.transition = "none"
  creature.style.transform = "translate(14px, 10px)"

  if (!data.animate) {
    stopMusic()
    root.dataset.music = "stopped"
    status.textContent = waitingText(data)
    return
  }

  status.textContent = crawlerName(data) + " is on the way."
  play(root, data, runKey)
}
"""

_CRAWLER = st.components.v2.component(
    "spell_crawler",
    html=_HTML,
    css=_CSS,
    js=_JS,
)


def spell_crawler(
    *,
    text: str,
    fixes: list[dict[str, object]],
    creature: str,
    run_id: int,
    animate: bool,
    digest: str,
) -> None:
    """Mount the code stage. The crawler fixes each marked word on screen."""
    _CRAWLER(
        data={
            "text": text,
            "fixes": fixes,
            "creature": creature,
            "runId": run_id,
            "animate": animate,
            "digest": digest,
        },
        key="spell-crawler",
        width="stretch",
        height=540,
    )
