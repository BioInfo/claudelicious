import { expect, test } from 'claude-code/testing'

import {
  age, cachePct, clipLines, driftNote, editDelta, alerts, bar, burnPerHour, cacheLeft, cursorGap, drainCells, onMainTurn, setCursor, setMainModel, usd, migrate, bannerCells, fadeCells, meterCells, mix, setVitals, sparkCells, spinner, emptyCenter, setView, tailTrunc, trunc, finishShells, intentCheckPrompt, isIntentCandidate, markChecked,
  onAgentTool, onEdit, onMainTool, onPrompt, onStep, onTurn, questionsIn, resetIntent, shortModel, shortPath, startShell,
  findShort, isShortcut, QUICK_SHORTS, SHORTS, shortPrompt, stallLevel, syncAgents, tok, typicalMs, warnOnce, clearWaiting, ctxOf, driftContextNote, onFailure, onResponse, paceNote, setWaiting, waitKind,
} from './center'

const GOAL = 'Build a command center pane that shows subagents and drift'
const u = (i: number, o: number, r: number, w: number, model = 'claude-sonnet-5-5-20261001') => ({
  input_tokens: i, output_tokens: o, cache_read_input_tokens: r, cache_creation_input_tokens: w, model,
})

test('intent: first long prompt is captured, short and slash prompts are not', () => {
  expect(isIntentCandidate(GOAL)).toBe(true)
  expect(isIntentCandidate('yes')).toBe(false)
  expect(isIntentCandidate('/reload-plugins with some long trailing text here')).toBe(false)
  let c = onPrompt(emptyCenter(), 'ok go', 1)
  expect(c.intent).toBe('')
  c = onPrompt(c, GOAL, 2)
  expect(c.intent).toBe(GOAL)
  expect(c.intentSource).toBe('first-prompt')
  const c2 = onPrompt(c, 'Now do something completely different with the router', 3)
  expect(c2.intent).toBe(GOAL)
  expect(c2.prompts).toBe(3)
})

test('intent reset takes the latest prompt and restarts the drift count', () => {
  let c = onPrompt(emptyCenter(), GOAL, 1)
  c = onMainTool(c, 'Read')
  c = onPrompt(c, 'Switch to fixing the status line renderer please', 2)
  c = resetIntent(c, 3)
  expect(c.intent).toBe('Switch to fixing the status line renderer please')
  expect(c.intentSource).toBe('latest-prompt')
  expect(c.toolsSinceIntent).toBe(0)
  expect(resetIntent(emptyCenter(), 1).intent).toBe('')
})

test('drift note: quiet below thresholds, fires at 15 prompts, cleared by a check', () => {
  let c = onPrompt(emptyCenter(), GOAL, 1)
  expect(driftNote(c)).toBe(null)
  for (let i = 0; i < 14; i++) c = onPrompt(c, 'follow up number ' + i, 2)
  expect(driftNote(c)).toBe(null)
  c = onPrompt(c, 'one more follow up', 3)
  expect(driftNote(c)).toBe('15 prompts since the last intent check')
  expect(driftNote(markChecked(c))).toBe(null)
  expect(driftNote(emptyCenter())).toBe(null)
})

test('drift note counts tool calls too', () => {
  let c = onPrompt(emptyCenter(), GOAL, 1)
  for (let i = 0; i < 149; i++) c = onMainTool(c, 'Read')
  expect(driftNote(c)).toBe(null)
  c = onMainTool(c, 'Read')
  expect(driftNote(c)).toBe('150 tool calls since the intent was set')
})

test('intent check prompt carries the intent text', () => {
  expect(intentCheckPrompt(GOAL)).toContain(GOAL)
})

test('agent usage sums per agent and keeps agents apart', () => {
  let c = emptyCenter()
  c = onStep(c, 'a', 1000, 'claude-sonnet-5-5', 'high', 7)
  c = onTurn(c, 'a', 2000, u(10, 5, 90, 0))
  c = onTurn(c, 'a', 3000, u(20, 15, 80, 0))
  c = onTurn(c, 'b', 3000, u(1, 1, 0, 0, 'claude-haiku-4-5-20251001'))
  c = onAgentTool(c, 'a', 3500, 'Bash')
  expect(c.agents.a.input).toBe(30)
  expect(c.agents.a.output).toBe(20)
  expect(c.agents.a.cacheRead).toBe(170)
  expect(c.agents.a.tools).toBe(1)
  expect(c.agents.a.lastTool).toBe('Bash')
  expect(c.agents.b.model).toBe('claude-haiku-4-5-20251001')
  expect(cachePct(c.agents.a)).toBe(85)
  expect(onTurn(emptyCenter(), 'x', 1, undefined).agents.x.input).toBe(0)
})

test('syncAgents records the end of a finished agent at its last event, once', () => {
  let c = onStep(emptyCenter(), 'a', 1000, 'm', '', 1)
  c = onAgentTool(c, 'a', 5000, 'Read')
  c = syncAgents(c, [{ id: 'a', type: 'Explore', description: 'scan', status: 'running' }], 9000)
  expect(c.agents.a.endedAt).toBe(null)
  expect(c.agents.a.type).toBe('Explore')
  c = syncAgents(c, [{ id: 'a', type: 'Explore', description: 'scan', status: 'completed' }], 9000)
  expect(c.agents.a.endedAt).toBe(5000)
  const again = syncAgents(c, [{ id: 'a', type: 'Explore', description: 'scan', status: 'completed' }], 99000)
  expect(again).toBe(c)
  expect(syncAgents(c, [{ id: 'zzz', type: 'x', description: '', status: 'running' }], 1)).toBe(c)
})

test('typical duration needs two finished agents of the same type', () => {
  let c = emptyCenter()
  const fin = (id: string, type: string, start: number, end: number) => {
    c = onStep(c, id, start, 'm', '', 1)
    c = onAgentTool(c, id, end, 'x')
    c = syncAgents(c, [{ id, type, description: '', status: 'completed' }], end)
  }
  fin('a', 'Explore', 0, 60_000)
  expect(typicalMs(c, 'Explore')).toBe(null)
  fin('b', 'Explore', 0, 180_000)
  fin('c', 'Plan', 0, 5_000)
  expect(typicalMs(c, 'Explore')).toEqual({ ms: 120_000, n: 2 })
  expect(typicalMs(c, 'Plan')).toBe(null)
})

test('stall levels: ok, quiet past 10 min, stuck past 20, never for finished', () => {
  const c = onAgentTool(emptyCenter(), 'a', 0, 'Read')
  const a = c.agents.a
  expect(stallLevel('running', a, 5 * 60_000)).toBe('ok')
  expect(stallLevel('running', a, 11 * 60_000)).toBe('quiet')
  expect(stallLevel('running', a, 21 * 60_000)).toBe('stuck')
  expect(stallLevel('completed', a, 99 * 60_000)).toBe('ok')
  expect(stallLevel('running', undefined, 99 * 60_000)).toBe('ok')
})

test('shells finish only on a notification that names their id; list is capped', () => {
  let c = startShell(emptyCenter(), 'bg123abc', 'sleep 100', 1000)
  c = startShell(c, 'bg999zzz', 'sleep 200', 1000)
  expect(finishShells(c, 'task bg000000 finished', 5000)).toBe(c)
  const done = finishShells(c, 'Background task bg123abc completed', 5000)
  expect(done.shells[0].doneAt).toBe(5000)
  expect(done.shells[1].doneAt).toBe(null)
  let big = emptyCenter()
  for (let i = 0; i < 60; i++) big = startShell(big, `id${i}xxxx`, 'x', i)
  expect(big.shells.length).toBe(40)
})

test('edit deltas by tool, and the ledger merges per file', () => {
  expect(editDelta('Write', { file_path: '/a/b.ts', content: 'x\ny\nz' })).toEqual({ path: '/a/b.ts', added: 3, removed: 0 })
  expect(editDelta('Edit', { file_path: '/a/b.ts', old_string: 'a', new_string: 'b\nc' })).toEqual({ path: '/a/b.ts', added: 2, removed: 1 })
  expect(editDelta('MultiEdit', { file_path: '/a/b.ts', edits: [{ old_string: 'a', new_string: 'b' }, { old_string: 'c\nd', new_string: 'e' }] })).toEqual({ path: '/a/b.ts', added: 2, removed: 3 })
  expect(editDelta('Read', { file_path: '/a/b.ts' })).toBe(null)
  expect(editDelta('Edit', {})).toBe(null)
  let c = onEdit(emptyCenter(), '/a/b.ts', 2, 1, 'main', 1)
  c = onEdit(c, '/a/b.ts', 4, 0, 'agent1', 2)
  expect(c.files['/a/b.ts']).toEqual({ edits: 2, added: 6, removed: 1, by: ['main', 'agent1'], lastAt: 2 })
})

test('file ledger drops the oldest entry past the cap', () => {
  let c = emptyCenter()
  for (let i = 0; i < 201; i++) c = onEdit(c, `/f/${i}`, 1, 0, 'main', i)
  expect(Object.keys(c.files).length).toBe(200)
  expect(c.files['/f/0']).toBe(undefined)
})

test('questions: finds asks, skips code blocks and short fragments', () => {
  const reply = 'Done.\n\n- Which of the two pane mods do you want vetted first?\n```\nwhat is this?\n```\nOK?\nShould I commit this to the repo now?'
  expect(questionsIn(reply)).toEqual(['Which of the two pane mods do you want vetted first?', 'Should I commit this to the repo now?'])
  expect(questionsIn('All done.')).toEqual([])
})

test('inline counter resets on dispatch and counts action tools only', () => {
  let c = onMainTool(onMainTool(onMainTool(emptyCenter(), 'Bash'), 'Read'), 'Edit')
  expect(c.inline).toBe(2)
  c = onMainTool(c, 'Agent')
  expect(c.inline).toBe(0)
})

test('warnOnce fires once per key', () => {
  const a = warnOnce(emptyCenter(), 'k')
  expect(a.fresh).toBe(true)
  expect(warnOnce(a.c, 'k').fresh).toBe(false)
})

test('formatters', () => {
  expect(tok(12_400)).toBe('12k')
  expect(tok(2_500_000)).toBe('2.5M')
  expect(age(45_000)).toBe('45s')
  expect(age(10 * 60_000)).toBe('10m')
  expect(age(2 * 3600_000)).toBe('2.0h')
  expect(shortModel('claude-sonnet-5-5-20261001')).toBe('sonnet-5-5')
  expect(shortModel('')).toBe('?')
  expect(shortPath('/Users/me/apps/x/y/z/file.ts', '/Users/me')).toBe('…/y/z/file.ts')
  expect(shortPath('/Users/me/a.ts', '/Users/me')).toBe('~/a.ts')
  expect(clipLines('a\n\n\n\nb\nc', 2)).toEqual(['a', '', 'b'].slice(0, 2))
  expect(clipLines('x'.repeat(200), 3, 10)[0].length).toBe(10)
})

test('waiting: only a question or plan tool counts, set and cleared', () => {
  expect(waitKind('AskUserQuestion')).toBe('question')
  expect(waitKind('ExitPlanMode')).toBe('plan')
  expect(waitKind('Bash')).toBe(null)
  const c = setWaiting(emptyCenter(), 'question', 5)
  expect(c.waiting).toEqual({ kind: 'question', at: 5 })
  expect(clearWaiting(c).waiting).toBe(null)
  const idle = emptyCenter()
  expect(clearWaiting(idle)).toBe(idle)
})

test('failures split main from subagents and keep the last one short', () => {
  let c = onFailure(emptyCenter(), 'Bash', 'exit 1\n  boom '.repeat(40), false, 9)
  c = onFailure(c, 'Read', 'no such file', true, 10)
  expect(c.failures.main).toBe(1)
  expect(c.failures.sub).toBe(1)
  expect(c.failures.last).toBe('Read: no such file')
  expect(onFailure(emptyCenter(), 'Bash', 'x'.repeat(500), false, 1).failures.last.length).toBeLessThan(160)
})

test('drift context note names the intent and the reason', () => {
  let c = onPrompt(emptyCenter(), GOAL, 1)
  for (let i = 0; i < 15; i++) c = onPrompt(c, 'follow up ' + i, 2)
  const note = driftContextNote(c)
  expect(note).toContain(GOAL)
  expect(note).toContain('15 prompts')
})

test('per-response context sums cached and uncached input; zero is ignored', () => {
  expect(ctxOf({ input_tokens: 10, cache_read_input_tokens: 90, cache_creation_input_tokens: 5 })).toBe(105)
  expect(ctxOf(null)).toBe(0)
  let c = onResponse(emptyCenter(), 'a', 1, 105)
  c = onResponse(c, 'a', 2, 60)
  expect(c.agents.a.ctx).toBe(60)
  expect(c.agents.a.ctxPeak).toBe(105)
  const same = emptyCenter()
  expect(onResponse(same, 'a', 1, 0)).toBe(same)
})

test('pace: needs an old-enough window, reads a fast burn as full-in, a slow one as resets-first', () => {
  const now = Date.parse('2026-10-03T12:00:00Z')
  const hours = (h: number) => new Date(now + h * 3600_000).toISOString()
  // 5h window with 1h left: 4h elapsed.
  expect(paceNote({ kind: 'five_hour', pct: 85, resetsAt: hours(1) }, now)).toBe('full in ~42m')
  expect(paceNote({ kind: 'five_hour', pct: 30, resetsAt: hours(1) }, now)).toBe('resets first')
  expect(paceNote({ kind: 'five_hour', pct: 40, resetsAt: hours(4.95) }, now)).toBe(null)
  expect(paceNote({ kind: 'five_hour', pct: 100, resetsAt: hours(1) }, now)).toBe('at the limit')
  expect(paceNote({ kind: 'spend_limit', pct: 50, resetsAt: hours(1) }, now)).toBe(null)
  expect(paceNote({ kind: 'five_hour', pct: 50 }, now)).toBe(null)
})

test('narrow layout: meters, truncation and tab state', () => {
  expect(bar(50, 10)).toBe('█████░░░░░')
  expect(bar(150, 4)).toBe('████')
  expect(bar(-5, 4)).toBe('░░░░')
  expect(trunc('abcdefgh', 5)).toBe('abcd…')
  expect(trunc('abc', 5)).toBe('abc')
  expect(tailTrunc('~/apps/claude-mods/command-center/hooks', 12)).toBe('…enter/hooks')
  const c = emptyCenter()
  expect(c.view).toBe('now')
  expect(setView(c, 'files').view).toBe('files')
  expect(setView(c, 'now')).toBe(c)
})

test('alerts: the person comes first, then stuck agents, and a quiet session raises none', () => {
  const now = 10_000_000
  expect(alerts(emptyCenter(), [], now)).toEqual([])
  let c = emptyCenter()
  c = onStep(c, 'a', now - 25 * 60_000, 'm', '', 1)
  c = { ...c, waiting: { kind: 'plan', at: now - 5000 } }
  const out = alerts(c, [{ id: 'a', type: 'Explore', description: 'x', status: 'running' }], now)
  expect(out.map(x => x.text.split(' ')[0])).toEqual(['Plan', '1'])
  expect(out[0].tone).toBe('red')
  expect(out[1].view).toBe('jobs')
  // finished agents never read as stuck
  expect(alerts(c, [{ id: 'a', type: 'Explore', description: 'x', status: 'completed' }], now).length).toBe(1)
})

const validCells = (w: Uint32Array, n: number) => {
  expect(w.length).toBe(n * 3)
  for (let i = 0; i < n; i++) {
    const cp = w[i * 3] as number
    expect(cp >= 0x20 && cp <= 0xffff).toBe(true) // printable BMP, the only thing a Raster accepts
    expect((w[i * 3 + 1] as number) <= 0x01000000).toBe(true)
    expect((w[i * 3 + 2] as number) <= 0x01000000).toBe(true)
  }
}

test('raster cells: every builder emits cells the engine will accept', () => {
  for (const w of [1, 8, 37, 80]) {
    validCells(meterCells(0, w), w)
    validCells(meterCells(63, w), w)
    validCells(meterCells(100, w), w)
    validCells(bannerCells('◆ COMMAND CENTER  3 inline', w), w)
    validCells(fadeCells(w), w)
    validCells(sparkCells([5, 90, 40], w), w)
    validCells(sparkCells([], w), w)
  }
  validCells(Uint32Array.of(spinner(0).codePointAt(0) as number, 0, 0), 1)
})

test('meter fill: empty is all track, full is all blocks, half lands mid-bar', () => {
  const full = (w: Uint32Array, n: number) => Array.from({ length: n }, (_, i) => w[i * 3]).filter(cp => cp === 0x2588).length
  expect(full(meterCells(0, 10), 10)).toBe(0)
  expect(full(meterCells(100, 10), 10)).toBe(10)
  expect(full(meterCells(50, 10), 10)).toBe(5)
  expect(full(meterCells(55, 10), 10)).toBe(5) // the extra half cell is a partial block, not a full one
  expect(meterCells(55, 10)[5 * 3]).toBe(0x258c)
  // out-of-range input clamps instead of overflowing the row
  expect(full(meterCells(900, 10), 10)).toBe(10)
})

test('colour mix and context history', () => {
  expect(mix(0x000000, 0xffffff, 0)).toBe(0x000000)
  expect(mix(0x000000, 0xffffff, 1)).toBe(0xffffff)
  expect(mix(0x000000, 0xff0000, 0.5)).toBe(0x800000)
  let c = setVitals(emptyCenter(), 100, [])
  c = setVitals(c, 100, [])
  c = setVitals(c, 200, [])
  expect(c.ctxHist).toEqual([100, 200]) // a repeat reading adds nothing
  expect(setVitals(c, null, []).ctxHist).toEqual([100, 200])
  let h = emptyCenter()
  for (let i = 1; i <= 100; i++) h = setVitals(h, i, [])
  expect(h.ctxHist.length).toBe(60)
  expect(h.ctxHist[59]).toBe(100)
})

const MIN = 60_000

test('cache clock: unknown before a turn, counts down, cold after the TTL; a subscription gets an hour, an API key five minutes', () => {
  const t0 = 1_000_000_000
  expect(cacheLeft(emptyCenter(), t0)).toBe(null)
  const sub = onMainTurn(setVitals(emptyCenter(), 1, [{ kind: 'five_hour', pct: 1 }]), t0)
  expect(cacheLeft(sub, t0 + 20 * MIN)).toEqual({ ms: 40 * MIN, warm: true })
  expect(cacheLeft(sub, t0 + 61 * MIN)).toEqual({ ms: 0, warm: false })
  const api = onMainTurn(setVitals(emptyCenter(), 1, []), t0)
  expect(cacheLeft(api, t0 + 6 * MIN)?.warm).toBe(false)
})

test('cache alert: only on a big idle context close to expiry', () => {
  const t0 = 1_000_000_000
  const base = onMainTurn(setVitals(emptyCenter(), 150_000, [{ kind: 'five_hour', pct: 1 }]), t0)
  const near = t0 + 57 * MIN
  expect(alerts(base, [], near).some(a => a.text.startsWith('Cache goes cold'))).toBe(true)
  expect(alerts(base, [], t0 + 10 * MIN).some(a => a.text.startsWith('Cache'))).toBe(false) // plenty left
  expect(alerts(setVitals(base, 20_000, [{ kind: 'five_hour', pct: 1 }]), [], near).some(a => a.text.startsWith('Cache'))).toBe(false) // small context
  expect(alerts(base, [{ id: 'a', type: 'T', description: '', status: 'running' }], near).some(a => a.text.startsWith('Cache'))).toBe(false) // work in flight
  expect(alerts(base, [], t0 + 70 * MIN).some(a => a.text.startsWith('Cache'))).toBe(false) // already cold: nothing left to save
})

test('burn rate waits ten minutes; cost never invents a zero', () => {
  const t0 = 1_000_000_000
  const c = setVitals(emptyCenter(), 1, [], 3, t0)
  expect(burnPerHour(c, t0 + 5 * MIN)).toBe(null)
  expect(burnPerHour(c, t0 + 60 * MIN)).toBe(3)
  expect(burnPerHour(emptyCenter(), t0)).toBe(null)
  expect(setVitals(c, 2, [], null, t0 + MIN).cost).toBe(3) // a reading with no cost keeps the last one
  expect(usd(3)).toBe('$3.00')
  expect(usd(412.4)).toBe('$412')
})

test('cursor gap: silent when current or unknown, counts files edited after the cursor', () => {
  const t0 = 1_000_000_000
  expect(cursorGap(emptyCenter())).toBe(null)
  let c = setCursor(emptyCenter(), t0)
  c = onEdit(c, '/a', 1, 0, 'main', t0 - MIN)
  expect(cursorGap(c)).toBe(null)
  c = onEdit(onEdit(c, '/b', 1, 0, 'main', t0 + 45 * MIN), '/c', 1, 0, 'main', t0 + 50 * MIN)
  expect(cursorGap(c)).toEqual({ behindMs: 50 * MIN, files: 2 })
  expect(alerts(c, [], t0 + 51 * MIN).some(a => a.text.startsWith('Cursor 50m behind 2'))).toBe(true)
  expect(alerts(onEdit(setCursor(emptyCenter(), t0), '/x', 1, 0, 'main', t0 + 5 * MIN), [], t0 + 6 * MIN).some(a => a.text.startsWith('Cursor'))).toBe(false)
  expect(setMainModel(c, 'm', 'high').mainModel).toBe('m')
})

test('drain bar cells are valid at every fill', () => {
  for (const f of [0, 0.05, 0.5, 1, 2, -1]) {
    const w = drainCells(f, 12)
    expect(w.length).toBe(36)
    for (let i = 0; i < 12; i++) expect((w[i * 3] as number) >= 0x20 && (w[i * 3] as number) <= 0xffff).toBe(true)
  }
})

test('state saved by an older build is filled out, and what it held is kept', () => {
  const old = { intent: 'keep me', prompts: 4, agents: {}, files: {}, shells: [], limits: [], warned: [] } as never
  const m = migrate(old)
  expect(m.intent).toBe('keep me')
  expect(m.prompts).toBe(4)
  expect(m.ctxHist).toEqual([]) // a field the old build never wrote
  expect(m.view).toBe('now')
  expect(setVitals(m, 5, []).ctxHist).toEqual([5]) // the reducers that crashed on the missing array now work
})

test('shorts: unique labels, no letter keys, quick row resolves', () => {
  const all = SHORTS.flatMap(g => g.shorts)
  expect(new Set(all.map(s => s.label)).size).toBe(all.length)
  for (const s of all) expect('hotkey' in s).toBe(false)
  for (const s of all) expect(s.prompt.length > 20).toBe(true)
  for (const l of QUICK_SHORTS) expect(findShort(l) !== undefined).toBe(true)
})

test('shorts: a pressed short or intent check never becomes the intent', () => {
  const tldr = findShort('TLDR')
  if (!tldr) throw new Error('TLDR short missing')
  let c = onPrompt(emptyCenter(), shortPrompt(tldr), 1)
  expect(isShortcut(shortPrompt(tldr))).toBe(true)
  expect(c.intent).toBe('')
  c = onPrompt(c, intentCheckPrompt('anything long enough to count as an intent here'), 2)
  expect(c.intent).toBe('')
  c = onPrompt(c, GOAL, 3)
  expect(c.intent).toBe(GOAL)
})
