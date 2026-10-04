export type AgentStat = {
  model: string
  effort: string
  steps: number
  turns: number
  messages: number
  input: number
  output: number
  cacheRead: number
  cacheWrite: number
  tools: number
  lastTool: string
  startedAt: number
  lastSeenAt: number
  ctx: number
  ctxPeak: number
  endedAt: number | null
  type: string
  description: string
}

export type ShellStat = { id: string; command: string; startedAt: number; doneAt: number | null; stoppable: boolean }

export type FileStat = { edits: number; added: number; removed: number; by: string[]; lastAt: number }

export type Reply = { text: string; at: number; seconds: number }

export type Limit = { kind: string; pct: number; resetsAt?: string }

export type Waiting = { kind: 'question' | 'plan'; at: number }

export type Failures = { main: number; sub: number; last: string; lastAt: number }

export type View = 'now' | 'jobs' | 'files' | 'reply' | 'shorts'

export type Center = {
  view: View
  ctxHist: number[]
  cost: number | null
  sessionAt: number
  lastTurnAt: number
  ttlMs: number
  cursorAt: number | null
  mainModel: string
  mainEffort: string
  intent: string
  intentAt: number
  intentSource: 'first-prompt' | 'latest-prompt' | ''
  lastPrompt: string
  prompts: number
  promptsAtIntent: number
  toolsSinceIntent: number
  checkedAtPrompt: number
  agents: Record<string, AgentStat>
  shells: ShellStat[]
  files: Record<string, FileStat>
  reply: Reply | null
  ctx: number | null
  compactAt: number | null
  limits: Limit[]
  inline: number
  warned: string[]
  waiting: Waiting | null
  failures: Failures
}

declare module 'claude-code' {
  interface PluginState {
    'command-center': { center: Center }
  }
}
