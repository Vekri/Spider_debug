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

const root = document.querySelector("#root")
const fileInput = document.querySelector("#file")
const countEl = document.querySelector("#count")
const filenameEl = document.querySelector("#filename")
const noteEl = document.querySelector("#note")
const listEl = document.querySelector("#list")
const downloadBtn = document.querySelector("#download")

const state = {
  name: "buggy_code.py",
  text: "",
  creature: "spider",
  runId: 0,
  report: null,
  usingUpload: false,
}

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

function crawlerName(creature) {
  return creature === "rat" ? "Rat" : "Spider"
}

function waitingText(fixes) {
  const name = crawlerName(state.creature).toLowerCase()
  const count = fixes.length
  if (!count) return "No spelling mistakes in this file."
  const noun = count === 1 ? "mistake is" : "mistakes are"
  return count + " spelling " + noun + " marked in red. Click Debug code and the " + name + " will crawl in and fix each one."
}

function renderLines(text, fixes) {
  const at = new Map()
  for (const fix of fixes) at.set(fix.start, fix)
  const lines = root.querySelector("#lines")
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
      html += '<span class="word bad" data-fix="' + escAttr(fix.corrected) + '" data-line="' + String(fix.line) + '">' + esc(fix.original) + "</span>"
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
    while (next < text.length && text[next] !== "\n" && !at.has(next)) next += 1
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
  page.scrollTo({ top: Math.max(0, y - page.clientHeight * 0.35), behavior: "smooth" })
}

function audioBox() {
  const AudioCtx = window.AudioContext || window.webkitAudioContext
  if (!AudioCtx) return null
  if (!window.__spellCrawlerMusic) {
    const ctx = new AudioCtx()
    const master = ctx.createGain()
    master.gain.value = 0.08
    master.connect(ctx.destination)
    window.__spellCrawlerMusic = { ctx, master, timer: null, step: 0, kind: "" }
  }
  return window.__spellCrawlerMusic
}

function unlockAudio() {
  const box = audioBox()
  if (box && box.ctx.state === "suspended") box.ctx.resume()
}

window.addEventListener("pointerdown", unlockAudio, true)

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

async function play(runKey) {
  const page = root.querySelector("#page")
  const creature = root.querySelector("#creature")
  const status = root.querySelector("#status")
  const bar = root.querySelector("#bar")
  const words = [...root.querySelectorAll(".word")]
  const name = crawlerName(state.creature)
  try {
    await startMusic(state.creature)
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
    for (let index = 0; index < words.length; index += 1) {
      if (root.dataset.viewKey !== runKey) return
      const word = words[index]
      if (!word.isConnected) return
      root.querySelectorAll(".row.active").forEach((row) => row.classList.remove("active"))
      const row = word.closest(".row")
      if (row) row.classList.add("active")
      word.classList.add("fixing")
      status.textContent = name + " on line " + word.dataset.line + ': "' + word.textContent + '" becomes "' + (word.dataset.fix || "") + '" (' + (index + 1) + " of " + words.length + ")"
      moveTo(page, creature, word)
      await sleep(560)
      if (!word.isConnected || root.dataset.viewKey !== runKey) return
      word.textContent = word.dataset.fix || word.textContent
      word.classList.remove("bad", "fixing")
      word.classList.add("good")
      bar.style.width = ((index + 1) / words.length) * 100 + "%"
      await sleep(160)
    }
    if (root.dataset.viewKey !== runKey) return
    creature.classList.remove("walking")
    status.textContent = name + " finished. " + words.length + " spelling " + (words.length === 1 ? "mistake" : "mistakes") + " corrected."
  } finally {
    if (root.dataset.viewKey === runKey) stopMusic()
  }
}

function showReport(report, animate) {
  const fixes = report.fixes || []
  const runKey = [state.name, state.runId, animate ? "go" : "wait", state.creature, fixes.length].join("|")
  if (root.dataset.viewKey === runKey) return
  root.dataset.viewKey = runKey
  root.querySelector("#bug").innerHTML = state.creature === "rat" ? RAT : SPIDER
  root.querySelector("#bar").style.width = "0%"
  renderLines(report.text || state.text, fixes)
  const creature = root.querySelector("#creature")
  creature.classList.remove("walking")
  creature.style.transition = "none"
  creature.style.transform = "translate(14px, 10px)"
  countEl.textContent = String(fixes.length)
  filenameEl.textContent = state.name
  downloadBtn.disabled = !report.corrected || !fixes.length
  listEl.innerHTML = fixes.length
    ? "<table><thead><tr><th>Line</th><th>Mistake</th><th>Correction</th></tr></thead><tbody>" +
      fixes.map((fix) => "<tr><td>" + fix.line + "</td><td>" + esc(fix.original) + "</td><td>" + esc(fix.corrected) + "</td></tr>").join("") +
      "</tbody></table>"
    : "<p>Nothing to correct in this file.</p>"
  const notes = []
  if (report.trimmed) notes.push("Only the first 150,000 characters are checked.")
  if (report.limited) notes.push("The crawl shows the first 80 mistakes so each fix stays visible.")
  noteEl.hidden = notes.length === 0
  noteEl.textContent = notes.join(" ")
  if (!animate) {
    stopMusic()
    root.querySelector("#status").textContent = waitingText(fixes)
    return
  }
  root.querySelector("#status").textContent = crawlerName(state.creature) + " is on the way."
  play(runKey)
}

async function inspect(animate) {
  const response = await fetch("/api/spell", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: state.text, filename: state.name }),
  })
  if (!response.ok) throw new Error("Spelling check failed.")
  state.report = await response.json()
  showReport(state.report, animate)
}

async function loadSample(name) {
  state.usingUpload = false
  state.name = name
  fileInput.value = ""
  const response = await fetch("/samples/" + name)
  state.text = await response.text()
  state.report = null
  await inspect(false)
}

document.querySelector("#samples").addEventListener("click", (event) => {
  const button = event.target.closest("button")
  if (!button) return
  document.querySelectorAll("#samples button").forEach((item) => item.classList.toggle("on", item === button))
  loadSample(button.dataset.sample).catch((error) => {
    root.querySelector("#status").textContent = error.message
  })
})

document.querySelector("#creatures").addEventListener("click", (event) => {
  const button = event.target.closest("button")
  if (!button) return
  state.creature = button.dataset.creature
  document.querySelectorAll("#creatures button").forEach((item) => item.classList.toggle("on", item === button))
  if (state.report) showReport(state.report, false)
})

fileInput.addEventListener("change", () => {
  const file = fileInput.files && fileInput.files[0]
  if (!file) return
  state.usingUpload = true
  state.name = file.name
  document.querySelectorAll("#samples button").forEach((item) => item.classList.remove("on"))
  const reader = new FileReader()
  reader.onload = () => {
    state.text = String(reader.result || "")
    inspect(false).catch((error) => {
      root.querySelector("#status").textContent = error.message
    })
  }
  reader.readAsText(file)
})

document.querySelector("#debug").addEventListener("click", () => {
  state.runId += 1
  inspect(true).catch((error) => {
    root.querySelector("#status").textContent = error.message
  })
})

downloadBtn.addEventListener("click", () => {
  if (!state.report || !state.report.corrected) return
  const blob = new Blob([state.report.corrected], { type: "text/plain" })
  const link = document.createElement("a")
  const dot = state.name.lastIndexOf(".")
  link.download = dot > 0 ? state.name.slice(0, dot) + ".corrected" + state.name.slice(dot) : state.name + ".corrected.txt"
  link.href = URL.createObjectURL(blob)
  link.click()
  URL.revokeObjectURL(link.href)
})

loadSample("buggy_code.py").catch((error) => {
  root.querySelector("#status").textContent = error.message
})
