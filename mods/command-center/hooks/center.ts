import type { AgentStat, Center, FileStat, Limit, View, Waiting } from '../types'

export const STALL_MS = 10 * 60 * 1000
export const STALL_HARD_MS = 20 * 60 * 1000
export const MAX_SHELLS = 40
export const MAX_FILES = 200
export const DRIFT_PROMPTS = 15
export const DRIFT_TOOLS = 150
export const MIN_INTENT_CHARS = 30

export const emptyCenter = (): Center => ({
  view: 'now',
  ctxHist: [],
  cost: null,
  sessionAt: 0,
  lastTurnAt: 0,
  ttlMs: 3600_000,
  cursorAt: null,
  mainModel: '',
  mainEffort: '',
  intent: '',
  intentAt: 0,
  intentSource: '',
  lastPrompt: '',
  prompts: 0,
  promptsAtIntent: 0,
  toolsSinceIntent: 0,
  checkedAtPrompt: 0,
  agents: {},
  shells: [],
  files: {},
  reply: null,
  ctx: null,
  compactAt: null,
  limits: [],
  inline: 0,
  warned: [],
  waiting: null,
  failures: { main: 0, sub: 0, last: '', lastAt: 0 },
})

// State saved by an older build lacks the fields added since; a reload keeps that state, so fill the gaps.
export const migrate = (c: Partial<Center>): Center => ({ ...emptyCenter(), ...c })

export const blankAgent = (now: number): AgentStat => ({
  model: '',
  effort: '',
  steps: 0,
  turns: 0,
  messages: 0,
  input: 0,
  output: 0,
  cacheRead: 0,
  cacheWrite: 0,
  tools: 0,
  lastTool: '',
  startedAt: now,
  lastSeenAt: now,
  ctx: 0,
  ctxPeak: 0,
  endedAt: null,
  type: '',
  description: '',
})

// ---- intent ------------------------------------------------------------------------------

// A prompt worth anchoring on: typed by the person, long enough to state a goal, not a slash command.
export const isIntentCandidate = (text: string): boolean => {
  const t = text.trim()

  return t.length >= MIN_INTENT_CHARS && !t.startsWith('/') && !t.startsWith('<') && !isShortcut(t) && !t.startsWith(INTENT_CHECK_HEAD)
}

// ---- shorts: one-press prompts for the asks that recur ------------------------------------
// Worded from the history file's most frequent asks (tldr, "wait what", "now what plainly",
// "what is waiting on me") plus skills that are rarely called by name.

export type Short = { label: string; prompt: string }
export type ShortGroup = { title: string; shorts: Short[] }

export const SHORTS: ShortGroup[] = [
  {
    title: 'UNDERSTAND',
    shorts: [
      { label: 'TLDR', prompt: 'Give me a TLDR of where this stands: three sentences at most, plain words, no file paths unless I need to act on one.' },
      { label: 'Wait, what?', prompt: 'I did not follow your last reply. Explain it again in plain spoken English: short sentences, no jargon or acronyms, one concrete example. End with what it means for me and whether I need to do anything.' },
      { label: 'Where are we?', prompt: 'Recap this conversation so far: what I asked for, what is done and verified, what is in progress, and what is next. A short list under each, plain words. Say plainly what is unverified.' },
      { label: 'Waiting on me?', prompt: 'What is waiting on me? List every open question, decision or action you need from me across this whole conversation, including ones in earlier replies I may have missed. If nothing is, say so in one line.' },
      { label: 'Now what?', prompt: 'So now what, in plain terms? Give the one next step you recommend, why, and anything I have to do.' },
    ],
  },
  {
    title: 'CHECK',
    shorts: [
      { label: 'Prove it', prompt: 'Show me the evidence for your recent claims: for each, the file, command output or result that proves it. Mark anything you have not actually checked as unverified, and run a check now where it is cheap.' },
      { label: "What's shaky?", prompt: 'What are you least sure about right now? List the assumptions and unverified claims in this session, ranked by how much damage each would do if it is wrong.' },
      { label: 'Red-team it', prompt: 'Red-team your last answer or plan: what bug in your instrument, code or method would produce exactly this result? Test the most likely one, then tell me whether the conclusion holds.' },
      { label: 'Second opinion', prompt: 'Get a second opinion on your current recommendation: make the strongest case against it, then tell me whether it still holds and what would change your mind.' },
    ],
  },
  {
    title: 'DECIDE',
    shorts: [
      { label: 'Your call', prompt: 'Give me your recommendation in one paragraph: what you would do and why, the option you rejected and why, and the part you are least sure of.' },
      { label: 'What could fail?', prompt: 'Premortem: it is six months later and this approach failed badly. Give 3 to 5 concrete ways it failed, each with its mechanism, then the top 2 mitigations.' },
      { label: 'Plan first', prompt: 'Before doing anything else, explain what you plan to do, step by step, in plain words, and wait for my go.' },
    ],
  },
  {
    title: 'MOVE',
    shorts: [
      { label: 'Keep going', prompt: 'Keep going with the plan. Fix rather than report where it is safe; stop only for something that is genuinely my call.' },
      { label: 'Delegate', prompt: 'Hand the remaining mechanical work to subagents with complete work orders, and keep this thread for planning and review.' },
      { label: 'Review diff', prompt: 'Run the code-review skill on the changes made in this session.' },
      { label: 'Past sessions', prompt: 'Search past sessions for earlier work related to what we are doing now, and tell me what is relevant.' },
      { label: 'Wrap up', prompt: 'Wrap this session: write down where things stand (done, in progress, next) in the project notes, then give me the big-picture TLDR of what changed and what it unlocks.' },
    ],
  },
]

// Shown on the Now tab as well, because they are the asks typed most often.
export const QUICK_SHORTS = ['TLDR', 'Wait, what?', 'Waiting on me?']

const SHORT_HEAD = '(Shortcut: '
export const shortPrompt = (s: Short): string => `${SHORT_HEAD}${s.label}) ${s.prompt}`
export const isShortcut = (text: string): boolean => text.trim().startsWith(SHORT_HEAD)
export const findShort = (label: string): Short | undefined => SHORTS.flatMap(g => g.shorts).find(s => s.label === label)

export const onPrompt = (c: Center, text: string, now: number): Center => {
  const next: Center = { ...c, prompts: c.prompts + 1, lastPrompt: text.slice(0, 600) }

  if (c.intent === '' && isIntentCandidate(text)) {
    return { ...next, intent: text.trim().slice(0, 600), intentAt: now, intentSource: 'first-prompt', promptsAtIntent: next.prompts, toolsSinceIntent: 0 }
  }

  return next
}

export const resetIntent = (c: Center, now: number): Center =>
  c.lastPrompt === ''
    ? c
    : { ...c, intent: c.lastPrompt, intentAt: now, intentSource: 'latest-prompt', promptsAtIntent: c.prompts, toolsSinceIntent: 0, checkedAtPrompt: c.prompts }

export const markChecked = (c: Center): Center => ({ ...c, checkedAtPrompt: c.prompts })

const INTENT_CHECK_HEAD = 'Intent check.'
export const intentCheckPrompt = (intent: string): string =>
  `${INTENT_CHECK_HEAD} The original intent this session was:\n\n"${intent}"\n\nIn a short list: what is done and verified, what is not done, and what we did that was off that intent. Name files or results for each item, and say plainly where something is unverified.`

// Prompts and tool calls since the intent was set, and since the last check.
export const driftNote = (c: Center): string | null => {
  if (c.intent === '') return null
  const since = c.prompts - Math.max(c.promptsAtIntent, c.checkedAtPrompt)

  if (since >= DRIFT_PROMPTS) return `${since} prompts since the last intent check`
  if (c.toolsSinceIntent >= DRIFT_TOOLS && c.checkedAtPrompt < c.promptsAtIntent + 1) return `${c.toolsSinceIntent} tool calls since the intent was set`

  return null
}

// ---- subagents ---------------------------------------------------------------------------

type Usage = {
  input_tokens: number
  output_tokens: number
  cache_read_input_tokens: number
  cache_creation_input_tokens: number
  model?: string
}

const withAgent = (c: Center, id: string, now: number, fn: (a: AgentStat) => Partial<AgentStat>): Center => {
  const a = c.agents[id] ?? blankAgent(now)

  return { ...c, agents: { ...c.agents, [id]: { ...a, ...fn(a), lastSeenAt: now } } }
}

export const onStep = (c: Center, id: string, now: number, model: string, effort: string, messages: number): Center =>
  withAgent(c, id, now, a => ({ model, effort, messages, steps: a.steps + 1 }))

// One response's context size: everything the request carried, cached or not.
export const ctxOf = (u: { input_tokens: number; cache_read_input_tokens: number; cache_creation_input_tokens: number } | null | undefined): number =>
  u ? u.input_tokens + u.cache_read_input_tokens + u.cache_creation_input_tokens : 0

export const onResponse = (c: Center, id: string, now: number, ctx: number): Center =>
  ctx <= 0 ? c : withAgent(c, id, now, a => ({ ctx, ctxPeak: Math.max(a.ctxPeak, ctx) }))

export const onAgentTool = (c: Center, id: string, now: number, tool: string): Center =>
  withAgent(c, id, now, a => ({ tools: a.tools + 1, lastTool: tool }))

export const onTurn = (c: Center, id: string, now: number, u: Usage | undefined): Center =>
  withAgent(c, id, now, a => ({
    turns: a.turns + 1,
    model: u?.model || a.model,
    input: a.input + (u?.input_tokens ?? 0),
    output: a.output + (u?.output_tokens ?? 0),
    cacheRead: a.cacheRead + (u?.cache_read_input_tokens ?? 0),
    cacheWrite: a.cacheWrite + (u?.cache_creation_input_tokens ?? 0),
  }))

type Listed = { id: string; type: string; description: string; status: string }

// Fold the engine's agent list into our stats: labels, and the end time of anything no longer running.
export const syncAgents = (c: Center, list: Listed[], now: number): Center => {
  let agents = c.agents
  let changed = false

  for (const l of list) {
    const a = agents[l.id]
    if (!a) continue
    const ended = l.status !== 'running' && a.endedAt === null ? a.lastSeenAt : a.endedAt
    if (a.type !== l.type || a.description !== l.description || a.endedAt !== ended) {
      agents = { ...agents, [l.id]: { ...a, type: l.type, description: l.description, endedAt: ended } }
      changed = true
    }
  }

  return changed ? { ...c, agents } : c
}

export const median = (xs: number[]): number => {
  const s = xs.slice().sort((a, b) => a - b)
  const m = Math.floor(s.length / 2)

  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2
}

// "How long to go" is not knowable. What we can say is how long finished agents of the same type took.
export const typicalMs = (c: Center, type: string): { ms: number; n: number } | null => {
  const done = Object.values(c.agents)
    .filter(a => a.type === type && a.endedAt !== null && a.endedAt > a.startedAt)
    .map(a => (a.endedAt as number) - a.startedAt)

  return done.length >= 2 ? { ms: median(done), n: done.length } : null
}

export type Stall = 'ok' | 'quiet' | 'stuck'

export const stallLevel = (status: string, a: AgentStat | undefined, now: number): Stall => {
  if (status !== 'running' || !a) return 'ok'
  const idle = now - a.lastSeenAt

  return idle > STALL_HARD_MS ? 'stuck' : idle > STALL_MS ? 'quiet' : 'ok'
}

// ---- shells ------------------------------------------------------------------------------

// `stoppable` is true only when the id came from the engine's own result: a made-up id must not reach TaskStop.
export const startShell = (c: Center, id: string, command: string, now: number, stoppable = false): Center => ({
  ...c,
  shells: [...c.shells, { id, command: command.slice(0, 300), startedAt: now, doneAt: null, stoppable }].slice(-MAX_SHELLS),
})

export const finishShells = (c: Center, text: string, now: number): Center => {
  let hit = false
  const shells = c.shells.map(s => {
    if (s.doneAt === null && s.id && text.includes(s.id)) {
      hit = true

      return { ...s, doneAt: now }
    }

    return s
  })

  return hit ? { ...c, shells } : c
}

// ---- files -------------------------------------------------------------------------------

const lines = (s: unknown): number => (typeof s === 'string' && s !== '' ? s.split('\n').length : 0)

type EditInput = {
  file_path?: unknown
  old_string?: unknown
  new_string?: unknown
  content?: unknown
  edits?: unknown
}

export const editDelta = (tool: string, input: EditInput): { path: string; added: number; removed: number } | null => {
  const path = typeof input.file_path === 'string' ? input.file_path : ''
  if (!path) return null
  if (tool === 'Write') return { path, added: lines(input.content), removed: 0 }
  if (tool === 'Edit') return { path, added: lines(input.new_string), removed: lines(input.old_string) }
  if (tool === 'MultiEdit' && Array.isArray(input.edits)) {
    let added = 0
    let removed = 0
    for (const e of input.edits as EditInput[]) {
      added += lines(e.new_string)
      removed += lines(e.old_string)
    }

    return { path, added, removed }
  }

  return null
}

export const onEdit = (c: Center, path: string, added: number, removed: number, by: string, now: number): Center => {
  const f: FileStat = c.files[path] ?? { edits: 0, added: 0, removed: 0, by: [], lastAt: now }
  const files = {
    ...c.files,
    [path]: { edits: f.edits + 1, added: f.added + added, removed: f.removed + removed, by: f.by.includes(by) ? f.by : [...f.by, by], lastAt: now },
  }
  const keys = Object.keys(files)
  if (keys.length > MAX_FILES) {
    const oldest = keys.sort((a, b) => files[a].lastAt - files[b].lastAt)[0]
    delete files[oldest]
  }

  return { ...c, files }
}

export const shortPath = (p: string, home = ''): string => {
  const q = home && p.startsWith(home) ? `~${p.slice(home.length)}` : p
  const parts = q.split('/')

  return parts.length > 4 ? `…/${parts.slice(-3).join('/')}` : q
}

// ---- last reply --------------------------------------------------------------------------

// Sentences in the reply that ask the person something: the thing most easily scrolled past.
export const questionsIn = (text: string, max = 3): string[] => {
  const out: string[] = []
  const withoutCode = text.replace(/```[\s\S]*?```/g, ' ')

  for (const raw of withoutCode.split(/\n+/)) {
    const line = raw.replace(/^[\s>*#\-\d.)]+/, '').trim()
    if (line.endsWith('?') && line.length > 12) out.push(line.slice(0, 220))
    if (out.length >= max) break
  }

  return out
}

export const setReply = (c: Center, text: string, now: number, seconds: number): Center => ({ ...c, reply: { text, at: now, seconds } })

// ---- vitals and counters -----------------------------------------------------------------

export const MAX_HIST = 60

// The context history only grows when the number moves, so a quiet session draws a flat line, not a fake one.
// A subscription reports rate-limit windows and caches for an hour; without them the cache lives five minutes.
export const setVitals = (c: Center, ctx: number | null, limits: Limit[], cost: number | null = null, now = 0): Center => {
  const last = c.ctxHist[c.ctxHist.length - 1]
  const hist = ctx !== null && ctx !== last ? [...c.ctxHist, ctx].slice(-MAX_HIST) : c.ctxHist

  return {
    ...c,
    ctx,
    limits,
    ctxHist: hist,
    cost: cost ?? c.cost,
    sessionAt: c.sessionAt === 0 && now > 0 ? now : c.sessionAt,
    ttlMs: limits.length > 0 ? 3600_000 : 300_000,
  }
}

export const onMainTurn = (c: Center, now: number): Center => ({ ...c, lastTurnAt: now })

export const setMainModel = (c: Center, model: string, effort: string): Center =>
  c.mainModel === model && c.mainEffort === effort ? c : { ...c, mainModel: model, mainEffort: effort }

export const setCursor = (c: Center, at: number | null): Center => (c.cursorAt === at ? c : { ...c, cursorAt: at })

// Time left before the prompt cache expires. Null until the main thread has answered once.
export const cacheLeft = (c: Center, now: number): { ms: number; warm: boolean } | null => {
  if (c.lastTurnAt === 0) return null
  const ms = c.ttlMs - (now - c.lastTurnAt)

  return { ms: Math.max(0, ms), warm: ms > 0 }
}

// Dollars per hour, once the session is old enough for the rate to mean something.
export const burnPerHour = (c: Center, now: number): number | null => {
  if (c.cost === null || c.sessionAt === 0 || now - c.sessionAt < 10 * 60_000) return null

  return c.cost / ((now - c.sessionAt) / 3600_000)
}

export const usd = (n: number): string => (n >= 100 ? `$${Math.round(n)}` : `$${n.toFixed(2)}`)

// Edits made after the continuity cursor was last written: the cursor does not describe them.
export const cursorGap = (c: Center): { behindMs: number; files: number } | null => {
  if (c.cursorAt === null) return null
  const newer = Object.values(c.files).filter(f => f.lastAt > (c.cursorAt as number))
  if (newer.length === 0) return null

  return { behindMs: Math.max(...newer.map(f => f.lastAt)) - (c.cursorAt as number), files: newer.length }
}

const DISPATCHERS = new Set(['Agent', 'Workflow', 'Monitor'])
const ACTION_TOOLS = new Set(['Bash', 'Edit', 'Write', 'NotebookEdit', 'MultiEdit'])

export const onMainTool = (c: Center, tool: string): Center => {
  if (DISPATCHERS.has(tool)) return { ...c, inline: 0, toolsSinceIntent: c.toolsSinceIntent + 1 }

  return { ...c, inline: ACTION_TOOLS.has(tool) ? c.inline + 1 : c.inline, toolsSinceIntent: c.toolsSinceIntent + 1 }
}

export const warnOnce = (c: Center, key: string): { c: Center; fresh: boolean } =>
  c.warned.includes(key) ? { c, fresh: false } : { c: { ...c, warned: [...c.warned, key].slice(-60) }, fresh: true }

// ---- waiting on the person, and failed calls ----------------------------------------------

// A question or a plan the model put to the person is a tool call with no answer yet.
export const waitKind = (tool: string): Waiting['kind'] | null =>
  tool === 'AskUserQuestion' ? 'question' : tool === 'ExitPlanMode' ? 'plan' : null

export const setWaiting = (c: Center, kind: Waiting['kind'], now: number): Center => ({ ...c, waiting: { kind, at: now } })

export const clearWaiting = (c: Center): Center => (c.waiting === null ? c : { ...c, waiting: null })

export const onFailure = (c: Center, tool: string, text: string, isSub: boolean, now: number): Center => ({
  ...c,
  failures: {
    main: c.failures.main + (isSub ? 0 : 1),
    sub: c.failures.sub + (isSub ? 1 : 0),
    last: `${tool}: ${text.replace(/\s+/g, ' ').slice(0, 140)}`,
    lastAt: now,
  },
})

// What the model reads at a drift threshold, so it re-anchors as well as the person.
export const driftContextNote = (c: Center): string =>
  `command-center: ${driftNote(c) ?? 'long session'}. The intent for this session was: "${c.intent}". If the current request has moved away from it, say so in one line and ask whether to continue or return to the intent.`

// ---- limit pace --------------------------------------------------------------------------

const WINDOW_MS: Record<string, number> = { five_hour: 5 * 3600_000, seven_day: 7 * 24 * 3600_000 }

// Average use since the window opened, projected forward: cycle-averaged, as a slope over a few
// recent samples reads a burst as the whole trend. Null until the window is old enough to say.
export const paceNote = (l: Limit, now: number): string | null => {
  const win = WINDOW_MS[l.kind]
  if (!win || !l.resetsAt) return null
  const resets = Date.parse(l.resetsAt)
  if (Number.isNaN(resets)) return null
  if (l.pct >= 100) return 'at the limit'
  const elapsed = win - (resets - now)
  if (elapsed < 10 * 60_000 || l.pct <= 0) return null
  const toFull = ((100 - l.pct) / l.pct) * elapsed

  return now + toFull >= resets ? 'resets first' : `full in ~${age(toFull)}`
}

// ---- formatting --------------------------------------------------------------------------

export const tok = (n: number): string => (n >= 1e6 ? `${(n / 1e6).toFixed(1)}M` : n >= 1e3 ? `${Math.round(n / 1e3)}k` : String(n))

export const age = (ms: number): string => {
  const s = Math.max(0, Math.round(ms / 1000))

  return s < 90 ? `${s}s` : s < 5400 ? `${Math.round(s / 60)}m` : `${(s / 3600).toFixed(1)}h`
}

export const shortModel = (id: string): string => id.replace(/^claude-/, '').replace(/-\d{8}$/, '') || '?'

export const cachePct = (a: AgentStat): number | null => {
  const total = a.input + a.cacheRead + a.cacheWrite

  return total > 0 ? Math.round((a.cacheRead / total) * 100) : null
}

export const clipLines = (text: string, max: number, width = 110): string[] => {
  const out: string[] = []
  for (const raw of text.split('\n')) {
    const l = raw.trimEnd()
    if (l === '' && (out.length === 0 || out[out.length - 1] === '')) continue
    out.push(l.length > width ? `${l.slice(0, width - 1)}…` : l)
    if (out.length >= max) break
  }

  return out
}

// ---- narrow-pane layout ------------------------------------------------------------------

export const setView = (c: Center, view: View): Center => (c.view === view ? c : { ...c, view })

export const trunc = (s: string, w: number): string => (s.length > w ? `${s.slice(0, Math.max(1, w - 1))}…` : s)

// A fixed-width meter: filled cells for the share used.
export const bar = (pct: number, w: number): string => {
  const f = Math.max(0, Math.min(w, Math.round((pct / 100) * w)))

  return '█'.repeat(f) + '░'.repeat(w - f)
}

export const meterTone = (pct: number): 'green' | 'yellow' | 'red' => (pct >= 90 ? 'red' : pct >= 70 ? 'yellow' : 'green')

export const splitPath = (p: string, home = ''): { dir: string; base: string } => {
  const q = home && p.startsWith(home) ? `~${p.slice(home.length)}` : p
  const i = q.lastIndexOf('/')

  return i < 0 ? { dir: '', base: q } : { dir: q.slice(0, i), base: q.slice(i + 1) }
}

// Keeps the tail of a directory, the part that tells two files of the same name apart.
export const tailTrunc = (s: string, w: number): string => (s.length > w ? `…${s.slice(s.length - Math.max(1, w - 1))}` : s)

export type Alert = { tone: 'red' | 'yellow'; text: string; view: View }

// Everything that wants the person, most urgent first. The pane shows these before anything else.
export const alerts = (c: Center, list: Listed[], now: number): Alert[] => {
  const out: Alert[] = []

  if (c.waiting) out.push({ tone: 'red', text: `${c.waiting.kind === 'plan' ? 'Plan needs approval' : 'Question open'} ${age(now - c.waiting.at)}`, view: 'now' })

  const stuck = list.filter(a => stallLevel(a.status, c.agents[a.id], now) === 'stuck').length
  const quiet = list.filter(a => stallLevel(a.status, c.agents[a.id], now) === 'quiet').length
  if (stuck > 0) out.push({ tone: 'red', text: `${stuck} agent${stuck > 1 ? 's' : ''} stuck`, view: 'jobs' })
  else if (quiet > 0) out.push({ tone: 'yellow', text: `${quiet} agent${quiet > 1 ? 's' : ''} quiet`, view: 'jobs' })

  const failed = c.failures.main + c.failures.sub
  if (failed > 0) out.push({ tone: 'yellow', text: `${failed} failed call${failed > 1 ? 's' : ''}: ${c.failures.last.slice(0, 60)}`, view: 'now' })

  const drift = driftNote(c)
  if (drift) out.push({ tone: 'yellow', text: `Drift: ${drift}`, view: 'now' })

  if (c.reply && questionsIn(c.reply.text).length > 0) out.push({ tone: 'yellow', text: 'Last reply asks you something', view: 'reply' })

  // Rule: compacting is far cheaper before an idle break than after the cache has gone.
  const cache = cacheLeft(c, now)
  if (cache && cache.warm && cache.ms < 5 * 60_000 && (c.ctx ?? 0) > 100_000 && list.every(a => a.status !== 'running'))
    out.push({ tone: 'yellow', text: `Cache goes cold in ${age(cache.ms)}: compact or wrap now`, view: 'now' })

  const gap = cursorGap(c)
  if (gap && gap.behindMs > 30 * 60_000) out.push({ tone: 'yellow', text: `Cursor ${age(gap.behindMs)} behind ${gap.files} edited file${gap.files > 1 ? 's' : ''}`, view: 'now' })

  return out
}

// ---- palette and raster cells ------------------------------------------------------------

// Run Data Run: navy ground, cream text, one orange accent, cyan for data only. Teal and rose are
// the brand's good/bad lifted for a dark terminal; gold is the warning, so orange stays the accent.
export const PAL = {
  accent: '#F97316',
  data: '#00C0E0',
  good: '#3FA9BD',
  warn: '#FBBF24',
  bad: '#E0607A',
  cream: '#F5F0E8',
  mute: '#9FB6CF',
  line: '#1D3A66',
} as const

export const toneHex = (t: 'green' | 'yellow' | 'red'): string => (t === 'red' ? PAL.bad : t === 'yellow' ? PAL.warn : PAL.good)

export const DEFAULT_COLOR = 0x01000000
const TRACK = 0x13315f
const NAVY = 0x0e2856

export const mix = (a: number, b: number, t: number): number => {
  const k = Math.max(0, Math.min(1, t))
  const ch = (sh: number) => Math.round(((a >> sh) & 255) * (1 - k) + ((b >> sh) & 255) * k)

  return (ch(16) << 16) | (ch(8) << 8) | ch(0)
}

const GOOD = 0x3fa9bd
const WARN = 0xfbbf24
const BAD = 0xe0607a
const ORANGE = 0xf97316
const CREAM = 0xf5f0e8

// Teal through gold to rose: the end of a full meter reads as danger before the number does.
export const heat = (t: number): number => (t < 0.6 ? mix(GOOD, WARN, t / 0.6) : mix(WARN, BAD, (t - 0.6) / 0.4))

const LEFT_EIGHTHS = [' ', '\u258F', '\u258E', '\u258D', '\u258C', '\u258B', '\u258A', '\u2589']
const cell = (cells: Uint32Array, i: number, cp: string, fg: number, bg: number) => {
  cells[i * 3] = cp.codePointAt(0) as number
  cells[i * 3 + 1] = fg
  cells[i * 3 + 2] = bg
}

// One row, `w` cells: a heat-gradient fill to `pct`, eighth-cell precision, on a dark track.
export const meterCells = (pct: number, w: number): Uint32Array => {
  const out = new Uint32Array(w * 3)
  const eighths = Math.round((Math.max(0, Math.min(100, pct)) / 100) * w * 8)

  for (let i = 0; i < w; i++) {
    const left = eighths - i * 8
    const fg = heat(i / Math.max(1, w - 1))
    if (left >= 8) cell(out, i, '\u2588', fg, TRACK)
    else if (left > 0) cell(out, i, LEFT_EIGHTHS[left] as string, fg, TRACK)
    else cell(out, i, ' ', DEFAULT_COLOR, TRACK)
  }

  return out
}

const SPARK = ['\u2581', '\u2582', '\u2583', '\u2584', '\u2585', '\u2586', '\u2587', '\u2588']

// The last `w` readings, scaled to `ceil` (or their own max), each bar tinted by how full it is.
export const sparkCells = (vals: number[], w: number, ceil?: number): Uint32Array => {
  const out = new Uint32Array(w * 3)
  const tail = vals.slice(-w)
  const top = Math.max(1, ceil ?? Math.max(...tail, 1))
  const pad = w - tail.length

  for (let i = 0; i < w; i++) {
    const v = i < pad ? null : (tail[i - pad] as number)
    if (v === null) cell(out, i, '\u2581', TRACK, DEFAULT_COLOR)
    else {
      const f = Math.min(1, v / top)
      cell(out, i, SPARK[Math.min(7, Math.floor(f * 8))] as string, heat(f), DEFAULT_COLOR)
    }
  }

  return out
}

// A one-row title bar: cream lettering on a navy sweep, the first glyph the one orange focal.
export const bannerCells = (text: string, w: number): Uint32Array => {
  const out = new Uint32Array(w * 3)
  const label = ` ${text} `

  for (let i = 0; i < w; i++) {
    const bg = mix(0x0a1f44, NAVY, i / Math.max(1, w - 1))
    const ch = i < label.length ? (label[i] as string) : ' '
    cell(out, i, ch, i === 1 ? ORANGE : CREAM, bg)
  }

  return out
}

// A hairline that fades from orange into the navy line colour.
export const fadeCells = (w: number): Uint32Array => {
  const out = new Uint32Array(w * 3)
  for (let i = 0; i < w; i++) cell(out, i, '\u2594', mix(ORANGE, 0x1d3a66, Math.min(1, (i / Math.max(1, w - 1)) * 1.6)), DEFAULT_COLOR)

  return out
}

// A drain bar for the cache clock: full when freshly cached, empty when cold.
export const drainCells = (frac: number, w: number): Uint32Array => {
  const out = meterCells(0, w)
  const eighths = Math.round(Math.max(0, Math.min(1, frac)) * w * 8)
  for (let i = 0; i < w; i++) {
    const left = eighths - i * 8
    const fg = frac < 0.1 ? BAD : frac < 0.3 ? WARN : GOOD
    if (left >= 8) cell(out, i, '\u2588', fg, TRACK)
    else if (left > 0) cell(out, i, LEFT_EIGHTHS[left] as string, fg, TRACK)
  }

  return out
}

export const spinner = (now: number): string => ['\u280B', '\u2819', '\u2839', '\u2838', '\u283C', '\u2834', '\u2826', '\u2827', '\u2807', '\u280F'][Math.floor(now / 120) % 10] as string
