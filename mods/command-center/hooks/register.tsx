import { atom, read, update } from 'claude-code'
import type { Register, RenderChildren } from 'claude-code'
import type { FileStat, View } from '../types'
import type { Short } from './center'

import {
  DRIFT_PROMPTS, DRIFT_TOOLS, findShort, migrate, PAL, QUICK_SHORTS, SHORTS, shortPrompt, age, alerts, bannerCells, bar, burnPerHour, cacheLeft, cachePct, clearWaiting, clipLines, ctxOf, cursorGap, drainCells, driftContextNote, driftNote, editDelta, emptyCenter, fadeCells, finishShells,
  intentCheckPrompt, markChecked, meterCells, meterTone, onAgentTool, onEdit, onMainTurn, onFailure, onMainTool, onPrompt, onResponse, onStep, onTurn, paceNote, questionsIn,
  resetIntent, setCursor, setMainModel, setReply, setVitals, setView, setWaiting, shortModel, sparkCells, spinner, splitPath, startShell, stallLevel, syncAgents, tailTrunc, toneHex, tok, trunc, typicalMs, usd, waitKind, warnOnce,
} from './center'

const PANE = 'command-center'
const TICK_MS = 15_000
let anyRunning = false
const PANE_COLUMNS = 50 // about a quarter of a 200-column terminal; a width the person drags wins
const centerAtom = atom({ plugin: 'command-center', key: 'center' } as const, emptyCenter())

// One pane for the whole session. Everything shown is read from the engine's own events:
// nothing here is a model's guess, and "how long to go" is only ever the median of agents of the
// same type that already finished.
export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const s = await $.settings.read()
    const compactAt = typeof s.autoCompactWindow === 'number' ? s.autoCompactWindow : null
    await update($, centerAtom, c => ({ ...migrate(c), compactAt }))
    await $.command.register({ name: 'command-center', description: 'Command center: intent, subagents, jobs, files changed, last reply' })
    void $.ui.open({ id: PANE, title: 'Command center', columns: PANE_COLUMNS })

    $.clock.every(1000, () => {
      if (anyRunning) $.ui.invalidate('ui.render')
    })

    $.clock.every(TICK_MS, async () => {
      const list = await $.agent.list()
      const now = Date.now()
      const cur = await $.fs.stat('.claude/CONTINUITY.md').catch(() => null)
      await update($, centerAtom, c => setCursor(syncAgents(c, list, now), cur && cur.kind === 'file' ? cur.mtimeMs : null))
      const c = await read($, centerAtom)
      for (const a of list) {
        const key = `stuck:${a.id}`
        if (stallLevel(a.status, c.agents[a.id], now) === 'stuck' && !c.warned.includes(key)) {
          await update($, centerAtom, x => warnOnce(x, key).c)
          $.ui.toast(`${a.type} "${a.description.slice(0, 40)}" has been quiet for ${age(now - c.agents[a.id].lastSeenAt)}`)
        }
      }
      $.ui.invalidate('ui.render')
    })

    return next(e)
  })

  on('command.run', { command: 'command-center' }, async $ => {
    await $.ui.open({ id: PANE, title: 'Command center', columns: PANE_COLUMNS, focus: true, closeOnEscape: true })

    return { text: 'Command center opened.' }
  })

  on('prompt.submit', async ($, e, next) => {
    if (e.origin.kind === 'composer') {
      await update($, centerAtom, c => onPrompt(c, e.text, Date.now()))
      const c = await read($, centerAtom)
      const note = driftNote(c)
      const since = c.prompts - Math.max(c.promptsAtIntent, c.checkedAtPrompt)
      const key = `drift:${c.checkedAtPrompt}:${c.promptsAtIntent}:${Math.floor(since / DRIFT_PROMPTS)}:${Math.floor(c.toolsSinceIntent / DRIFT_TOOLS)}`
      if (note && !c.warned.includes(key)) {
        await update($, centerAtom, x => warnOnce(x, key).c)
        $.ui.toast(`${note}: open the command center and press Check intent`)

        return next({ ...e, context: [...(e.context ?? []), driftContextNote(c)] })
      }
    }

    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    const now = Date.now()
    const tool: string = e.tool
    const isSub = e.agentId !== undefined
    const wait = isSub ? null : waitKind(tool)

    if (isSub) {
      await update($, centerAtom, c => onAgentTool(c, e.agentId as string, now, tool))
    } else {
      await update($, centerAtom, c => onMainTool(c, tool))
    }
    if (wait) await update($, centerAtom, c => setWaiting(c, wait, now))

    const ran = await next(e)

    if (wait) await update($, centerAtom, c => clearWaiting(c))

    if ('isError' in ran && ran.isError === true) {
      const why = 'text' in ran && typeof ran.text === 'string' ? ran.text : ''
      await update($, centerAtom, c => onFailure(c, tool, why, isSub, Date.now()))
    }

    if (!isSub && e.tool === 'Bash' && e.run_in_background) {
      const text = 'text' in ran && typeof ran.text === 'string' ? ran.text : ''
      const m = /\b(?:id|ID)[:\s]+([a-z0-9_-]{6,})/.exec(text)
      await update($, centerAtom, c => startShell(c, m?.[1] ?? e.tool_use_id, e.command, Date.now(), m !== null))
    }

    if (e.tool === 'Edit' || e.tool === 'Write' || e.tool === 'MultiEdit') {
      const d = editDelta(e.tool, e as unknown as Record<string, unknown>)
      const failed = 'deny' in ran && ran.deny !== undefined ? true : 'isError' in ran && ran.isError === true
      if (d && !failed) {
        const by = e.agentId ? `sub:${e.agentId.slice(0, 6)}` : 'main'
        await update($, centerAtom, c => onEdit(c, d.path, d.added, d.removed, by, Date.now()))
      }
    }

    return ran
  })

  on('turn.step', async function* ($, e, next) {
    if (e.agentId) await update($, centerAtom, c => onStep(c, e.agentId as string, Date.now(), e.model, String(e.effort ?? ''), e.messageCount))
    else await update($, centerAtom, c => setMainModel(c, e.model, String(e.effort ?? '')))

    const r = yield* next(e)
    if (e.agentId) await update($, centerAtom, c => onResponse(c, e.agentId as string, Date.now(), ctxOf(r.usage)))

    return r
  })

  on('turn.complete', async ($, e, next) => {
    if (e.agentId) {
      await update($, centerAtom, c => onTurn(c, e.agentId as string, Date.now(), e.usage))
    } else if (!e.isAborted && e.answer.trim() !== '') {
      await update($, centerAtom, c => onMainTurn(c, Date.now()))
      await update($, centerAtom, c => setReply(c, e.answer, Date.now(), Math.round(e.durationMs / 1000)))
    } else if (!e.isAborted) {
      await update($, centerAtom, c => onMainTurn(c, Date.now()))
    }

    return next(e)
  })

  on('session.measure', async ($, e, next) => {
    const limits = e.rateLimits.map(l => ({ kind: l.kind, pct: Math.round(l.percentUsed), resetsAt: l.resetsAt }))
    await update($, centerAtom, c => setVitals(c, e.context.tokens ?? null, limits, e.cost?.usd ?? null, Date.now()))

    return next(e)
  })

  on('session.receive', { origin: { kind: 'task-notification' } }, async ($, e, next) => {
    await update($, centerAtom, c => finishShells(c, e.text, Date.now()))

    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const els = $.ui.resolve(e)
    const { Box, Button, Text } = els
    // Raster is the terminal's truecolor cell grid; other surfaces get the plain-text bar.
    const Raster = 'Raster' in els ? els.Raster : null
    const c = migrate(await read($, centerAtom))
    const list = await $.agent.list()
    const now = Date.now()
    const rows = e.viewport?.rows ?? 40
    const width = Math.max(28, (e.props.bodyColumns ?? 50) - 2)
    const iw = width - 4 // inside a bordered card
    const home = (await $.env.get('HOME')) ?? ''
    const go = (v: View) => () => update($, centerAtom, x => setView(x, v))
    const b64 = (w: Uint32Array) => (new Uint8Array(w.buffer) as Uint8Array & { toBase64(): string }).toBase64()

    const running = list.filter(a => a.status === 'running')
    anyRunning = running.length > 0
    const finished = list.filter(a => a.status !== 'running').reverse()
    const openShells = c.shells.filter(s => s.doneAt === null)
    const doneShells = c.shells.filter(s => s.doneAt !== null).reverse()
    const fileList = Object.entries(c.files).sort((a, b) => b[1].lastAt - a[1].lastAt)
    const totalAdd = fileList.reduce((n, [, f]) => n + f.added, 0)
    const totalDel = fileList.reduce((n, [, f]) => n + f.removed, 0)
    const qs = c.reply ? questionsIn(c.reply.text) : []
    const five = c.limits.find(l => l.kind === 'five_hour')
    const seven = c.limits.find(l => l.kind === 'seven_day')
    const ctxPct = c.ctx !== null && c.compactAt ? Math.round((c.ctx / c.compactAt) * 100) : null
    const todo = alerts(c, list, now)
    const cache = cacheLeft(c, now)
    const gap = cursorGap(c)
    const barW = Math.max(8, width - 20)
    const spin = spinner(now)

    // A rounded card: the border carries the tone, the title carries the meaning.
    const Card = (p: { title: string; note?: string; tone?: string; children?: RenderChildren }) => (
      <Box flexDirection="column" borderStyle="round" borderColor={p.tone ?? PAL.line} paddingX={1} marginTop={1}>
        <Text wrap="truncate-end">
          <Text bold color={p.tone ?? PAL.accent}>
            {p.title}
          </Text>
          {p.note ? <Text color={PAL.mute}> {p.note}</Text> : null}
        </Text>
        {p.children}
      </Box>
    )

    const Meter = (p: { label: string; pct: number; note?: string | null }) => (
      <Box>
        <Box width={6}>
          <Text color={PAL.mute}>{p.label}</Text>
        </Box>
        {Raster ? (
          <Raster key={`m-${p.label}`} columns={barW} rows={1} cells={b64(meterCells(p.pct, barW))} />
        ) : (
          <Text color={toneHex(meterTone(p.pct))}>{bar(p.pct, barW)}</Text>
        )}
        <Text bold color={toneHex(meterTone(p.pct))}>
          {' '}
          {String(p.pct).padStart(3)}%
        </Text>
      </Box>
    )

    const tab = (v: View, hotkey: string, icon: string, label: string, n?: number) => (
      <Box marginRight={1}>
        <Button variant={c.view === v ? 'primary' : undefined} hotkey={hotkey} onPress={go(v)}>
          {`${label}${n !== undefined && n > 0 ? ` ${n}` : ''}`}
        </Button>
      </Box>
    )
    const stop = (id: string, what: string) => async () => {
      const r = await $.tool.call({ tool: 'TaskStop', task_id: id, consent: `The user pressed Stop on this ${what} in the command center.` })
      $.ui.toast('deny' in r && r.deny !== undefined ? `Stop refused: ${r.deny}` : 'isError' in r && r.isError === true ? 'Stop failed' : 'Stop sent')
    }

    const send = (s: Short) => async () => {
      await $.prompt.submit({ text: shortPrompt(s), asUser: true })
      $.ui.toast(`Sent: ${s.label}`)
    }
    // Click only, no letter keys: typing while the pane has focus would fire a run of prompts.
    const ShortButton = (p: { s: Short }) => (
      <Box marginRight={1}>
        <Button onPress={send(p.s)}>
          {p.s.label}
        </Button>
      </Box>
    )

    const AgentCard = (p: { a: (typeof list)[number] }) => {
      const a = p.a
      const s = c.agents[a.id]
      const level = stallLevel(a.status, s, now)
      const typical = typicalMs(c, a.type)
      const up = s ? (s.endedAt ?? now) - s.startedAt : 0
      const pct = s ? cachePct(s) : null
      const live = a.status === 'running'
      const ok = /complet|done|success/i.test(a.status)
      const tone = level === 'stuck' ? PAL.bad : level === 'quiet' ? PAL.warn : live ? PAL.good : ok ? PAL.line : PAL.bad

      return (
        <Box flexDirection="column" borderStyle="round" borderColor={tone} paddingX={1} marginTop={1}>
          <Text wrap="truncate-end">
            <Text color={live ? PAL.good : ok ? PAL.mute : PAL.bad}>{live ? spin : ok ? '✓' : '✗'} </Text>
            <Text bold={live} color={live ? undefined : PAL.mute}>
              {a.type}
            </Text>
            <Text color={PAL.mute}> {age(up)}</Text>
            {level === 'quiet' ? <Text color={PAL.warn}> quiet {age(now - (s?.lastSeenAt ?? now))}</Text> : null}
            {level === 'stuck' ? <Text color={PAL.bad}> stuck? {age(now - (s?.lastSeenAt ?? now))}</Text> : null}
          </Text>
          <Text color={PAL.mute} wrap="truncate-end">
            {trunc(a.description, iw)}
          </Text>
          {s ? (
            <Box flexDirection="column">
              <Text color={PAL.data} wrap="truncate-end">
                {shortModel(s.model)}
                {s.effort ? ` ${s.effort}` : ''}
                <Text color={PAL.mute}>
                  {' '}
                  · ctx {tok(s.ctx)} · {s.tools} tools{s.lastTool ? ` (${s.lastTool})` : ''}
                </Text>
              </Text>
              <Text color={PAL.mute} wrap="truncate-end">
                {s.turns > 0 ? `in ${tok(s.input)} out ${tok(s.output)}` : 'tokens counted when it finishes'}
                {pct !== null ? ` · cache ${pct}%` : ''}
                {live ? ` · idle ${age(now - s.lastSeenAt)}` : ''}
                {live && typical ? ` · typ ${age(typical.ms)}` : ''}
              </Text>
            </Box>
          ) : (
            <Text color={PAL.mute}>started before this mod loaded</Text>
          )}
          {level !== 'ok' ? (
            <Box>
              <Button onPress={stop(a.id, 'agent')}>Stop this agent</Button>
            </Box>
          ) : null}
        </Box>
      )
    }

    const ShellRow = (p: { s: (typeof c.shells)[number] }) => (
      <Box flexDirection="column">
        <Text wrap="truncate-end">
          <Text color={p.s.doneAt === null ? PAL.good : PAL.mute}>{p.s.doneAt === null ? spin : '✓'} </Text>
          <Text color={PAL.mute}>{age((p.s.doneAt ?? now) - p.s.startedAt)} </Text>
          <Text>{trunc(p.s.command.replace(/\s+/g, ' '), iw - 8)}</Text>
        </Text>
        {p.s.doneAt === null && p.s.stoppable ? (
          <Box marginLeft={2}>
            <Button onPress={stop(p.s.id, 'background shell')}>Stop</Button>
          </Box>
        ) : null}
      </Box>
    )

    const FileRow = (p: { path: string; f: FileStat }) => {
      const { dir, base } = splitPath(p.path, home)

      return (
        <Box flexDirection="column">
          <Text wrap="truncate-end">
            <Text color={PAL.good}>+{p.f.added}</Text>
            <Text color={PAL.bad}> −{p.f.removed} </Text>
            <Text bold color={PAL.data}>
              {trunc(base, iw - 10)}
            </Text>
          </Text>
          <Text color={PAL.mute} wrap="truncate-end">
            {tailTrunc(dir, iw - 14)} · ×{p.f.edits} {age(now - p.f.lastAt)}
          </Text>
        </Box>
      )
    }

    const body = () => {
      if (c.view === 'jobs') {
        const cap = Math.max(3, Math.floor((rows - 14) / 6))

        return (
          <Box flexDirection="column">
            <Card title="SUBAGENTS" note={`${running.length} running · ${list.length} total`} tone={running.length > 0 ? PAL.good : undefined}>
              {list.length === 0 && <Text color={PAL.mute}>None.</Text>}
            </Card>
            {running.map(a => (
              <AgentCard a={a} />
            ))}
            {finished.slice(0, cap).map(a => (
              <AgentCard a={a} />
            ))}
            {finished.length > cap ? <Text color={PAL.mute}>+{finished.length - cap} older</Text> : null}
            <Card title="BACKGROUND SHELLS" note={`${openShells.length} open · ${c.shells.length} started`} tone={openShells.length > 0 ? PAL.good : undefined}>
              {c.shells.length === 0 && <Text color={PAL.mute}>None.</Text>}
              {openShells.map(s => (
                <ShellRow s={s} />
              ))}
              {doneShells.slice(0, 3).map(s => (
                <ShellRow s={s} />
              ))}
            </Card>
          </Box>
        )
      }

      if (c.view === 'files') {
        const cap = Math.max(6, Math.floor((rows - 14) / 2))

        return (
          <Card title="FILES CHANGED" note={`${fileList.length} · +${totalAdd} −${totalDel}`} tone={PAL.data}>
            {fileList.length === 0 && <Text color={PAL.mute}>None this session.</Text>}
            {fileList.slice(0, cap).map(([p, f]) => (
              <FileRow path={p} f={f} />
            ))}
            {fileList.length > cap ? <Text color={PAL.mute}>+{fileList.length - cap} older</Text> : null}
          </Card>
        )
      }

      if (c.view === 'shorts') {
        return (
          <Box flexDirection="column">
            <Text color={PAL.mute} wrap="wrap">
              Click one to send it as your next prompt.
            </Text>
            {SHORTS.map(g => (
              <Card title={g.title}>
                <Box flexWrap="wrap">
                  {g.shorts.map(s => (
                    <ShortButton s={s} />
                  ))}
                </Box>
              </Card>
            ))}
          </Box>
        )
      }

      if (c.view === 'reply') {
        const lines = c.reply ? clipLines(c.reply.text, Math.max(8, rows - 16), 4000) : [] // Text wraps long lines itself; this tab must not cut them

        return (
          <Box flexDirection="column">
            {qs.length > 0 ? (
              <Card title="OPEN QUESTIONS FOR YOU" tone={PAL.warn}>
                {qs.map(q => (
                  <Text color={PAL.warn}>▸ {q}</Text>
                ))}
              </Card>
            ) : null}
            <Card title="LAST REPLY" note={c.reply ? `${age(now - c.reply.at)} ago · took ${c.reply.seconds}s` : ''}>
              {!c.reply && <Text color={PAL.mute}>None yet.</Text>}
              {lines.map(l => (
                <Text color={PAL.mute}>{l}</Text>
              ))}
            </Card>
          </Box>
        )
      }

      return (
        <Box flexDirection="column">
          <Card title="INTENT" tone={PAL.accent}>
            {c.intent === '' ? (
              <Text color={PAL.mute}>None yet. The first real prompt becomes the intent.</Text>
            ) : (
              <Box flexDirection="column">
                {clipLines(c.intent, 3, iw).map(l => (
                  <Text>{l}</Text>
                ))}
                <Text color={PAL.mute} wrap="truncate-end">
                  {age(now - c.intentAt)} ago · {c.prompts - c.promptsAtIntent} prompts · {c.toolsSinceIntent} tools since
                </Text>
                {c.cursorAt !== null ? (
                  <Text color={gap && gap.behindMs > 30 * 60_000 ? PAL.warn : PAL.mute} wrap="truncate-end">
                    cursor {age(now - c.cursorAt)} old{gap ? ` · ${gap.files} file${gap.files > 1 ? 's' : ''} edited since` : ' · current'}
                  </Text>
                ) : null}
              </Box>
            )}
            <Box marginTop={1}>
              <Box marginRight={1}>
                <Button
                  variant="primary"
                  hotkey="i"
                  onPress={async () => {
                    await update($, centerAtom, x => markChecked(x))
                    await $.prompt.submit({ text: intentCheckPrompt(c.intent), asUser: true })
                  }}
                >
                  Check intent
                </Button>
              </Box>
              <Button hotkey="s" onPress={() => update($, centerAtom, x => resetIntent(x, Date.now()))}>
                Use latest prompt
              </Button>
            </Box>
          </Card>

          <Box marginTop={1} flexWrap="wrap">
            {QUICK_SHORTS.map(l => findShort(l)).map(s => (s ? <ShortButton s={s} /> : null))}
            <Button plain dimColor onPress={go('shorts')}>
              more →
            </Button>
          </Box>

          <Card title="RUNNING" note={`${running.length} agents · ${openShells.length} shells`} tone={running.length + openShells.length > 0 ? PAL.good : undefined}>
            {running.length + openShells.length === 0 && <Text color={PAL.mute}>Nothing running.</Text>}
            {running.slice(0, 4).map(a => {
              const s = c.agents[a.id]
              const level = stallLevel(a.status, s, now)

              return (
                <Text wrap="truncate-end">
                  <Text color={level === 'stuck' ? PAL.bad : level === 'quiet' ? PAL.warn : PAL.good}>{spin} </Text>
                  <Text bold>{a.type} </Text>
                  <Text color={PAL.mute}>
                    {s ? age(now - s.startedAt) : ''} {trunc(a.description, iw - a.type.length - 9)}
                  </Text>
                </Text>
              )
            })}
            {openShells.slice(0, 3).map(s => (
              <Text wrap="truncate-end">
                <Text color={PAL.good}>{spin} </Text>
                <Text color={PAL.mute}>{age(now - s.startedAt)} </Text>
                <Text>{trunc(s.command.replace(/\s+/g, ' '), iw - 8)}</Text>
              </Text>
            ))}
            {running.length > 4 || openShells.length > 3 ? (
              <Button plain dimColor onPress={go('jobs')}>
                all jobs →
              </Button>
            ) : null}
          </Card>

          <Card title="FILES" note={`${fileList.length} · +${totalAdd} −${totalDel}`} tone={PAL.data}>
            {fileList.length === 0 && <Text color={PAL.mute}>None this session.</Text>}
            {fileList.slice(0, 3).map(([p, f]) => (
              <Text wrap="truncate-end">
                <Text color={PAL.good}>+{f.added}</Text>
                <Text color={PAL.bad}> −{f.removed} </Text>
                <Text color={PAL.data}>{trunc(splitPath(p, home).base, iw - 14)}</Text>
                <Text color={PAL.mute}> {age(now - f.lastAt)}</Text>
              </Text>
            ))}
            {fileList.length > 3 ? (
              <Button plain dimColor onPress={go('files')}>
                {`all ${fileList.length} files →`}
              </Button>
            ) : null}
          </Card>

          <Card title="LAST REPLY" note={c.reply ? `${age(now - c.reply.at)} ago` : ''}>
            {!c.reply && <Text color={PAL.mute}>None yet.</Text>}
            {c.reply ? clipLines(c.reply.text, 3, iw).map(l => <Text color={PAL.mute}>{l}</Text>) : null}
            {c.reply ? (
              <Button plain dimColor onPress={go('reply')}>
                read all →
              </Button>
            ) : null}
          </Card>
        </Box>
      )
    }

    return (
      <Box flexDirection="column">
        {Raster ? (
          <Box flexDirection="column">
            <Raster key="banner" columns={width} rows={1} cells={b64(bannerCells(`◆ COMMAND CENTER${c.inline > 0 ? `  ${c.inline} inline` : ''}`, width))} />
            <Raster key="fade" columns={width} rows={1} cells={b64(fadeCells(width))} />
          </Box>
        ) : (
          <Text bold color={PAL.accent}>
            ◆ COMMAND CENTER{c.inline > 0 ? `  ${c.inline} inline` : ''}
          </Text>
        )}
        {ctxPct !== null && c.ctx !== null ? <Meter label="ctx" pct={ctxPct} /> : <Text color={PAL.mute}>ctx {c.ctx !== null ? tok(c.ctx) : 'n/a'}</Text>}
        {Raster && c.ctxHist.length > 1 ? (
          <Box>
            <Box width={6}>
              <Text color={PAL.mute}> </Text>
            </Box>
            <Raster key="spark" columns={barW} rows={1} cells={b64(sparkCells(c.ctxHist, barW, c.compactAt ?? undefined))} />
            <Text color={PAL.mute}> {c.ctx !== null ? tok(c.ctx) : ''}</Text>
          </Box>
        ) : null}
        <Text wrap="truncate-end">
          <Text color={PAL.cream} bold>
            {c.cost !== null ? usd(c.cost) : '$–'}
          </Text>
          <Text color={PAL.mute}>
            {burnPerHour(c, now) !== null ? ` · ${usd(burnPerHour(c, now) as number)}/h` : ''}
            {c.mainModel ? ` · ${shortModel(c.mainModel)}${c.mainEffort ? ` ${c.mainEffort}` : ''}` : ''}
          </Text>
        </Text>
        {cache ? (
          <Box>
            <Box width={6}>
              <Text color={PAL.mute}>cache</Text>
            </Box>
            {Raster ? <Raster key="cache" columns={Math.max(4, barW - 4)} rows={1} cells={b64(drainCells(cache.ms / c.ttlMs, Math.max(4, barW - 4)))} /> : null}
            <Text color={cache.warm ? (cache.ms < 5 * 60_000 ? PAL.warn : PAL.good) : PAL.bad}>{cache.warm ? ` ${age(cache.ms)}` : ' cold'}</Text>
          </Box>
        ) : null}
        {five ? <Meter label="5h" pct={five.pct} /> : null}
        {five && paceNote(five, now) && paceNote(five, now) !== 'resets first' ? <Text color={PAL.warn}>      5h {paceNote(five, now)}</Text> : null}
        {seven ? <Meter label="7d" pct={seven.pct} /> : null}
        {seven && paceNote(seven, now) && paceNote(seven, now) !== 'resets first' ? <Text color={PAL.warn}>      7d {paceNote(seven, now)}</Text> : null}

        {todo.length > 0 ? (
          <Box flexDirection="column" borderStyle="round" borderColor={todo.some(t => t.tone === 'red') ? PAL.bad : PAL.warn} paddingX={1} marginTop={1}>
            <Text bold color={todo.some(t => t.tone === 'red') ? PAL.bad : PAL.warn}>
              NEEDS YOU
            </Text>
            {todo.slice(0, 4).map(t => (
              <Box>
                <Text color={t.tone === 'red' ? PAL.bad : PAL.warn}>▸ </Text>
                <Button plain onPress={go(t.view)}>
                  {trunc(t.text, iw - 3)}
                </Button>
              </Box>
            ))}
          </Box>
        ) : null}

        <Box marginTop={1} flexWrap="wrap">
          {tab('now', '1', '◈', 'Now')}
          {tab('jobs', '2', '▶', 'Jobs', running.length + openShells.length)}
          {tab('files', '3', '▤', 'Files', fileList.length)}
          {tab('reply', '4', '✉', 'Reply', qs.length)}
          {tab('shorts', '5', '⚡', 'Shorts')}
        </Box>

        {body()}
      </Box>
    )
  }).catch(async ($, e, next) => {
    const { Text } = $.ui.resolve(e)

    return <Text color="red">Command center could not draw: {next.error.message ?? next.error.kind}. Run claude --debug for the cause.</Text>
  })
}
