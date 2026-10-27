import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";
import type {
  Event,
  State,
  Forecast,
  Investigation,
  Narrative,
  Scenario,
  Attribution,
} from "./types";
import "./style.css";

const tabs = [
  "Match Centre",
  "Intelligence",
  "Scenario Lab",
  "Broadcast & Recaps",
];
const pct = (n: number) => `${(n * 100).toFixed(1)}%`;
const clock = (s: number) =>
  `${Math.floor(s / 60)
    .toString()
    .padStart(2, "0")}:${(s % 60).toString().padStart(2, "0")}`;
async function api<T>(path: string, body?: unknown): Promise<T> {
  const r = await fetch(
    `/api${path}`,
    body === undefined
      ? {}
      : {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        },
  );
  if (!r.ok) {
    const e = await r.json();
    throw Error(
      typeof e.detail === "string"
        ? e.detail
        : "Request could not be completed",
    );
  }
  return r.json();
}
function AttributionView({ data }: { data: Attribution }) {
  return (
    <section className="attribution">
      <h3>What moved the home-win forecast?</h3>
      <p>
        State {data.previous_sequence} → {data.source_sequence} · {data.samples}{" "}
        continuations per comparison
      </p>
      {data.contributions.map((c) => (
        <div className="factor" key={c.factor}>
          <span>{c.factor}</span>
          <div className="factor-track">
            <i
              style={{
                width: `${Math.min(100, Math.abs(c.home) * 200)}%`,
                background: c.home >= 0 ? "#96b942" : "#45aecb",
              }}
            />
          </div>
          <b>
            {c.home >= 0 ? "+" : ""}
            {(c.home * 100).toFixed(1)} pp
          </b>
        </div>
      ))}
      <p>
        <b>Net change {(data.delta * 100).toFixed(1)} pp</b> · residual{" "}
        {(data.residual * 100).toFixed(6)} pp ·{" "}
        {data.verified ? "Reconciled" : "Provisional"}
      </p>
      <small>
        {data.limitation} {data.uncertainty}
      </small>
    </section>
  );
}
function App() {
  const [seed, setSeed] = useState(26),
    [events, setEvents] = useState<Event[]>([]),
    [head, setHead] = useState(0),
    [cursor, setCursor] = useState<number | null>(null),
    [playing, setPlaying] = useState(false);
  const [state, setState] = useState<State | null>(null),
    [fc, setFc] = useState<Forecast | null>(null),
    [history, setHistory] = useState<Forecast[]>([]),
    [tab, setTab] = useState(0),
    [profile, setProfile] = useState("viewer"),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(""),
    [investigations, setInvestigations] = useState<Investigation[]>([]),
    [focused, setFocused] = useState<Investigation | null>(null),
    [recap, setRecap] = useState<Narrative | null>(null),
    [branch, setBranch] = useState<Scenario | null>(null),
    [decomposition, setDecomposition] = useState<Attribution | null>(null),
    [action, setAction] = useState("press"),
    [value, setValue] = useState(0.8),
    [team, setTeam] = useState(0),
    [player, setPlayer] = useState(""),
    [replacement, setReplacement] = useState(""),
    [role, setRole] = useState("FW"),
    [filter, setFilter] = useState("all"),
    [health, setHealth] = useState("Checking services…");
  const seq = cursor ?? head,
    fixture = useRef(seed),
    requested = useRef(new Set<string>()),
    selection = useRef(seq);
  fixture.current = seed;
  selection.current = seq;
  useEffect(() => {
    let active = true;
    setEvents([]);
    setHead(0);
    setCursor(null);
    setPlaying(false);
    setState(null);
    setFc(null);
    setHistory([]);
    setInvestigations([]);
    setFocused(null);
    setBranch(null);
    setRecap(null);
    setError("");
    setBusy("");
    requested.current.clear();
    api<{ events: Event[]; initial: State }>(`/matches/${seed}`)
      .then((r) => {
        if (active) {
          setEvents(r.events);
          setState(r.initial);
        }
      })
      .catch((e) => active && setError(e.message));
    return () => {
      active = false;
    };
  }, [seed]);
  useEffect(() => {
    api<{ ai: string }>("/health")
      .then((h) => setHealth(h.ai))
      .catch(() => setHealth("API unavailable"));
  }, []);
  useEffect(() => {
    if (!playing || !events.length) return;
    const stream = new EventSource(`/api/matches/${seed}/stream?after=${head}`);
    stream.addEventListener("match", (ev) => {
      const e: Event = JSON.parse((ev as MessageEvent).data);
      setHead((old) => Math.max(old, e.sequence));
      if (e.kind === "fulltime") {
        setPlaying(false);
        stream.close();
      }
    });
    stream.onerror = () => {
      stream.close();
      setPlaying(false);
      setError(
        "Playback connection interrupted. Press Play to resume from the last event.",
      );
    };
    return () => stream.close();
  }, [playing, seed, events.length]);
  useEffect(() => {
    let active = true;
    if (!events.length) return;
    api<{ state: State }>(`/matches/${seed}/states/${seq}`)
      .then((r) => active && setState(r.state))
      .catch((e) => active && setError(e.message));
    return () => {
      active = false;
    };
  }, [seed, seq, events.length]);
  const forecastSeq =
    playing && cursor === null ? Math.floor(seq / 20) * 20 : seq;
  useEffect(() => {
    let active = true;
    setFc(null);
    setRecap(null);
    if (!events.length) return;
    api<Forecast>(`/matches/${seed}/forecasts/${forecastSeq}`)
      .then((r) => {
        if (active) {
          setFc(r);
          setHistory((old) =>
            [...old.filter((f) => f.source_sequence !== forecastSeq), r].sort(
              (a, b) => a.source_sequence - b.source_sequence,
            ),
          );
        }
      })
      .catch((e) => active && setError(e.message));
    return () => {
      active = false;
    };
  }, [seed, forecastSeq, events.length]);
  useEffect(() => {
    if (!events.length) return;
    let active = true;
    api<Investigation[]>(`/matches/${seed}/investigations?sequence=${seq}`)
      .then((r) => active && setInvestigations(r))
      .catch((e) => active && setError(e.message));
    return () => {
      active = false;
    };
  }, [seed, seq, events.length, busy]);
  async function poll<T>(
    path: string,
    body: unknown,
    label: string,
  ): Promise<T> {
    setBusy(label);
    setError("");
    try {
      let j = await api<{ job_id?: string; status: string; result?: T }>(
        path,
        body,
      );
      if (!j.job_id) return j as T;
      for (let n = 0; n < 180; n++) {
        if (j.status === "completed") return j.result!;
        if (j.status === "failed")
          throw Error(
            "Job failed. Inspect the service configuration and retry.",
          );
        await new Promise((r) => setTimeout(r, 500));
        j = await api(`/jobs/${encodeURIComponent(j.job_id!)}`);
      }
      throw Error(
        "Job is still running. Reopen this checkpoint to retrieve its result.",
      );
    } finally {
      setBusy("");
    }
  }
  async function investigate(at = seq, automatic = false) {
    const currentSeed = seed;
    try {
      const result = await poll<Investigation>(
        `/matches/${seed}/investigations/${at}`,
        {},
        "Investigating pinned evidence…",
      );
      if (fixture.current === currentSeed) {
        setFocused(result);
        setInvestigations((old) => [
          ...old.filter((x) => x.investigation_id !== result.investigation_id),
          result,
        ]);
        if (!automatic) setTab(1);
      }
    } catch (e) {
      setError((e as Error).message);
    }
  }
  useEffect(() => {
    const event = events[head - 1];
    if (!event || busy) return;
    const key = `${seed}:${head}`;
    if (
      (event.outcome === "goal" ||
        event.outcome === "red" ||
        event.kind === "halftime") &&
      !requested.current.has(key)
    ) {
      requested.current.add(key);
      void investigate(head, true);
    }
  }, [head, busy]);
  async function explain() {
    const pinnedSeed = seed,
      pinnedSeq = seq;
    setBusy("Attributing forecast change…");
    setError("");
    try {
      const result = await api<Attribution>(
        `/matches/${seed}/attribution/${seq}?previous=${Math.max(0, seq - 20)}`,
      );
      if (fixture.current === pinnedSeed && selection.current === pinnedSeq)
        setDecomposition(result);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy("");
    }
  }
  async function simulate() {
    const source = seq,
      currentSeed = seed;
    try {
      const result = await poll<Scenario>(
        `/matches/${seed}/scenarios`,
        {
          sequence: seq,
          team,
          category: ["goal", "red_card", "injury"].includes(action)
            ? "circumstance"
            : "tactical",
          action,
          value,
          player: player || null,
          replacement: replacement || null,
          role: action === "role" ? role : null,
          samples: 128,
          seed: 710,
        },
        "Running paired simulations…",
      );
      if (fixture.current === currentSeed && selection.current === source)
        setBranch(result);
    } catch (e) {
      setError((e as Error).message);
    }
  }
  useEffect(() => {
    setBranch(null);
    setDecomposition(null);
    setPlayer("");
    setReplacement("");
  }, [seed, seq]);
  useEffect(() => {
    if (tab !== 3 || !events.length) return;
    let active = true;
    api<Narrative>(`/matches/${seed}/recap/${seq}?profile=${profile}`)
      .then((r) => active && setRecap(r))
      .catch((e) => active && setError(e.message));
    return () => {
      active = false;
    };
  }, [tab, seq, profile, seed, events.length]);
  function exportRecap() {
    if (!recap) return;
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(recap, null, 2)], { type: "application/json" }),
    );
    const a = document.createElement("a");
    a.href = url;
    a.download = `trajectan-${seed}-state-${seq}-${profile}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }
  function seek(n: number) {
    setCursor(n);
    setPlaying(false);
  }
  const shownEvents = events.slice(0, seq),
    selected = shownEvents.at(-1),
    latest = investigations.filter((i) => i.source_sequence <= seq).at(-1),
    visibleFocus = focused && focused.source_sequence <= seq ? focused : latest;
  const prob = (f: Forecast | null) =>
    f ? (
      <div className="probabilities">
        <div>
          <b>{pct(f.probabilities.home)}</b>
          <span>Northbridge</span>
        </div>
        <div>
          <b>{pct(f.probabilities.draw)}</b>
          <span>Draw</span>
        </div>
        <div>
          <b>{pct(f.probabilities.away)}</b>
          <span>Harbour</span>
        </div>
      </div>
    ) : (
      <p className="muted" role="status">
        Calculating model probabilities…
      </p>
    );
  return (
    <>
      <header>
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            setTab(0);
          }}
        >
          <span className="brand-mark">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M5 19L19 5M5 5H19V19" />
            </svg>
          </span>{" "}
          TRAJECTAN<span className="brand-caption">THE GAME, EXPLAINED.</span>
        </a>
        <div className="header-right">
          <span className="synthetic">SYNTHETIC MATCH LAB</span>
          <select
            aria-label="Seeded fixture"
            value={seed}
            onChange={(e) => setSeed(+e.target.value)}
          >
            {[26, 77, 2026].map((s) => (
              <option key={s} value={s}>
                Demo fixture · seed {s}
              </option>
            ))}
          </select>
        </div>
      </header>
      <nav aria-label="Workspaces">
        {tabs.map((t, i) => (
          <button
            key={t}
            className={tab === i ? "active" : ""}
            onClick={() => setTab(i)}
          >
            <span>0{i + 1}</span>
            {t}
          </button>
        ))}
        <select
          aria-label="Audience mode"
          value={profile}
          onChange={(e) => setProfile(e.target.value)}
        >
          <option value="viewer">Viewer · plain language</option>
          <option value="analyst">Analyst · detailed evidence</option>
        </select>
      </nav>
      <main>
        <div className="eyebrow">
          MATCH INTELLIGENCE / {tabs[tab].toUpperCase()}{" "}
          <span>MODEL v1.0 · FICTIONAL TEAMS</span>
        </div>
        <section className="scoreboard">
          <div>
            <span className="badge">
              {cursor === null ? "PLAYBACK HEAD" : "HISTORICAL MOMENT"} · STATE{" "}
              {seq}
            </span>
            <h1>
              The match.
              <br />
              <em>The meaning.</em>
            </h1>
          </div>
          <div className="fixture">
            <div>
              <span className="crest lime">N</span>
              <h2>
                Northbridge <small>FC · HOME</small>
              </h2>
            </div>
            <div className="score">
              <strong>
                {state?.sequence === seq ? state.score.join(" : ") : "— : —"}
              </strong>
              <span>
                {state?.sequence === seq ? clock(state.second) : "Loading…"} ·{" "}
                {state?.phase === "finished"
                  ? "FULL TIME"
                  : `HALF ${state?.period ?? 1}`}
              </span>
            </div>
            <div>
              <span className="crest cyan">H</span>
              <h2>
                Harbour <small>ATHLETIC · AWAY</small>
              </h2>
            </div>
          </div>
        </section>
        <div className="playback">
          <button
            className="primary"
            disabled={!events.length || head >= events.length}
            onClick={() => {
              setCursor(null);
              setPlaying(!playing);
            }}
          >
            {playing ? "Pause" : "Play match"}
          </button>
          <button
            disabled={!events.length}
            onClick={() => {
              setPlaying(false);
              setCursor(null);
              setHead(Math.min(events.length, head + 1));
            }}
          >
            Step →
          </button>
          <input
            aria-label="Historical match position"
            type="range"
            min="0"
            max={events.length}
            value={seq}
            onChange={(e) => seek(+e.target.value)}
          />
          <span>
            {seq} / {events.length}
          </span>
          <button
            onClick={() => {
              setCursor(null);
              setPlaying(false);
            }}
          >
            Return to live
          </button>
          <button
            onClick={() =>
              seek(events.find((e) => e.kind === "halftime")?.sequence ?? 0)
            }
          >
            Half-time
          </button>
          <button onClick={() => seek(events.length)}>Full-time</button>
        </div>
        {error && (
          <div className="error" role="alert">
            {error}
            <button onClick={() => setError("")}>Dismiss</button>
          </div>
        )}
        {busy && (
          <div className="notice" role="status">
            ◌ {busy} Playback remains available.
          </div>
        )}
        <div className="service">
          {health.includes("unavailable") ? "○" : "◉"} {health}. Outputs below
          identify their execution source.
        </div>
        {tab === 0 && (
          <>
            <div className="main-grid">
              <section className="pitch-card">
                <div className="section-top">
                  <div>
                    <span className="eyebrow">ON THE PITCH</span>
                    <h2>
                      {selected
                        ? `${selected.kind === "shot" ? "Shot" : selected.kind.charAt(0).toUpperCase() + selected.kind.slice(1)} · ${selected.outcome}`
                        : "Ready for kickoff"}
                    </h2>
                  </div>
                  <span className="badge">OBSERVED · SYNTHETIC</span>
                </div>
                <svg
                  className="pitch"
                  viewBox="0 0 105 68"
                  role="img"
                  aria-label="Football pitch showing the selected possession and recent shots"
                >
                  <defs>
                    <pattern
                      id="stripes"
                      width="21"
                      height="68"
                      patternUnits="userSpaceOnUse"
                    >
                      <rect
                        width="10.5"
                        height="68"
                        fill="#ffffff"
                        opacity=".025"
                      />
                    </pattern>
                  </defs>
                  <rect width="105" height="68" rx="1" fill="#203d3b" />
                  <rect width="105" height="68" fill="url(#stripes)" />
                  <g fill="none" stroke="#91aca0" strokeWidth=".3">
                    <rect x="3" y="3" width="99" height="62" />
                    <path d="M52.5 3V65" />
                    <circle cx="52.5" cy="34" r="9.15" />
                    <path d="M3 14H19.5V54H3 M102 14H85.5V54H102 M3 25H8.5V43H3 M102 25H96.5V43H102" />
                  </g>
                  {shownEvents
                    .filter(
                      (e) =>
                        e.possession_id === selected?.possession_id &&
                        e.kind === "pass",
                    )
                    .slice(-10)
                    .map((e) => (
                      <line
                        key={e.event_id}
                        x1={e.start[0] * 0.99 + 3}
                        y1={e.start[1] * 0.62 + 3}
                        x2={e.end[0] * 0.99 + 3}
                        y2={e.end[1] * 0.62 + 3}
                        stroke="#c9f15a"
                        strokeWidth=".6"
                        strokeDasharray={e.outcome === "complete" ? "" : "1 1"}
                      />
                    ))}
                  {shownEvents
                    .filter((e) => e.kind === "shot")
                    .slice(-12)
                    .map((e) => (
                      <circle
                        key={e.event_id}
                        tabIndex={0}
                        role="button"
                        aria-label={`Inspect shot at ${clock(e.second)}`}
                        onClick={() => seek(e.sequence)}
                        onKeyDown={(k) => k.key === "Enter" && seek(e.sequence)}
                        cx={3 + e.start[0] * 0.99}
                        cy={3 + e.start[1] * 0.62}
                        r={e.outcome === "goal" ? 1.6 : 1}
                        fill={e.team === 0 ? "#c9f15a" : "#45aecb"}
                      >
                        <title>
                          {clock(e.second)} · {e.outcome} · model xG{" "}
                          {e.xg.toFixed(2)}
                        </title>
                      </circle>
                    ))}
                  {state?.sequence === seq && (
                    <circle
                      cx={3 + state.ball[0] * 0.99}
                      cy={3 + state.ball[1] * 0.62}
                      r="1.4"
                      fill="white"
                      stroke="#11182b"
                      strokeWidth=".5"
                    />
                  )}
                </svg>
                <div className="pitch-caption">
                  <span>
                    ● Northbridge <span className="cyan-text">● Harbour</span> ·
                    White: ball
                  </span>
                  <span>Possession path · normalized coordinates</span>
                </div>
                <div className="stats">
                  {[
                    ["Shots", state?.shots],
                    ["Model xG", state?.xg.map((n) => n.toFixed(2))],
                    ["Passes completed", state?.completed],
                  ].map(([name, v]) => (
                    <div key={String(name)}>
                      <b>
                        {(v as (string | number)[] | undefined)?.[0] ?? "—"}
                      </b>
                      <span>{String(name)}</span>
                      <b>
                        {(v as (string | number)[] | undefined)?.[1] ?? "—"}
                      </b>
                    </div>
                  ))}
                </div>
              </section>
              <aside className="insight-card">
                <span className="eyebrow">THE INTELLIGENCE DESK</span>
                <div className="orbit">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M5 19L19 5M5 5H19V19" />
                  </svg>
                </div>
                <h2>
                  Every turning point
                  <br />
                  has a story.
                </h2>
                <p>
                  {latest?.narratives[profile]?.text ??
                    "Follow a moment from the event log to its forecast, evidence and a verified explanation. Goals and dismissals trigger investigations automatically during playback."}
                </p>
                <span className="badge">
                  {latest
                    ? latest.status.toUpperCase()
                    : "EVIDENCE BEFORE EXPLANATION"}
                </span>
                <button
                  className="primary"
                  disabled={!!busy || !state}
                  onClick={() => investigate()}
                >
                  Investigate this moment →
                </button>
                <button onClick={() => setTab(2)}>
                  Explore a tactical alternative →
                </button>
                <small>
                  Local analysis uses deterministic tools and templates. No live
                  AI execution is claimed.
                </small>
              </aside>
            </div>
            <div className="bottom-grid">
              <section className="paper">
                <div className="section-top">
                  <div>
                    <span className="eyebrow">WHERE THE GAME COULD GO</span>
                    <h2>Outcome forecast</h2>
                  </div>
                  <span className="badge light">MODEL ESTIMATE</span>
                </div>
                {prob(fc)}
                <button disabled={!!busy || seq === 0} onClick={explain}>
                  Explain forecast change →
                </button>
                {decomposition && <AttributionView data={decomposition} />}
                <div
                  className="chart"
                  role="img"
                  aria-label="Home, draw and away probabilities at visited match states"
                >
                  <ResponsiveContainer width="100%" height={160}>
                    <AreaChart
                      data={history
                        .filter((f) => f.source_sequence <= seq)
                        .map((f) => ({
                          sequence: f.source_sequence,
                          ...f.probabilities,
                        }))}
                    >
                      <XAxis dataKey="sequence" tick={{ fontSize: 11 }} />
                      <YAxis
                        domain={[0, 1]}
                        tickFormatter={pct}
                        tick={{ fontSize: 11 }}
                        width={48}
                      />
                      <Tooltip formatter={(v) => pct(Number(v))} />
                      <Area
                        type="monotone"
                        dataKey="home"
                        stroke="#668426"
                        fill="#c9f15a"
                        fillOpacity={0.2}
                      />
                      <Area
                        type="monotone"
                        dataKey="draw"
                        stroke="#89919b"
                        fill="none"
                      />
                      <Area
                        type="monotone"
                        dataKey="away"
                        stroke="#27869e"
                        fill="none"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
                <small>
                  {fc
                    ? `${fc.samples} continuations · state ${fc.source_sequence} · seed ${fc.seed} · home SE ${pct(fc.standard_errors.home)}`
                    : "Forecasts appear as you visit match states."}{" "}
                  · Synthetic model, not real-match calibration.
                </small>
              </section>
              <section className="paper timeline">
                <div className="section-top">
                  <h2>Match timeline</h2>
                  <select
                    aria-label="Timeline filter"
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                  >
                    <option value="all">All events</option>
                    <option value="shot">Shots</option>
                    <option value="foul">Discipline</option>
                  </select>
                </div>
                <div className="event-list">
                  {shownEvents
                    .filter((e) => filter === "all" || e.kind === filter)
                    .slice(-50)
                    .reverse()
                    .map((e) => (
                      <button key={e.event_id} onClick={() => seek(e.sequence)}>
                        <span>{clock(e.second)}</span>
                        <b>{e.outcome === "goal" ? "● GOAL" : e.kind}</b>
                        <span>
                          {e.player ?? "Match control"} · {e.outcome}
                        </span>
                        <small>#{e.sequence} →</small>
                      </button>
                    ))}
                  {seq === 0 && (
                    <p className="muted">
                      Press Play to begin the seeded match.
                    </p>
                  )}
                </div>
              </section>
            </div>
          </>
        )}
        {tab === 1 && (
          <div className="intelligence-grid">
            <section className="paper">
              <span className="eyebrow">INVESTIGATION MEMORY</span>
              <h2>Follow the evidence.</h2>
              <p>
                Every result is pinned to a historical state. Rejected and
                inconclusive findings remain inspectable.
              </p>
              <button
                className="primary"
                disabled={!!busy}
                onClick={() => investigate()}
              >
                Investigate state {seq}
              </button>
              {investigations
                .filter((i) => i.source_sequence <= seq)
                .map((i) => (
                  <button
                    className="memory"
                    key={i.investigation_id}
                    onClick={() => setFocused(i)}
                  >
                    <b>Moment #{i.source_sequence}</b>
                    <span>{i.status} →</span>
                  </button>
                ))}
            </section>
            <section className="paper">
              <span className="eyebrow">EXECUTION TRACE</span>
              {visibleFocus ? (
                <>
                  <h2>
                    State {visibleFocus.source_sequence} · {visibleFocus.status}
                  </h2>
                  <p className="notice">{visibleFocus.execution_mode}</p>
                  <p>
                    {visibleFocus.narratives[profile]?.text ??
                      "No verified narrative was published for this investigation."}
                  </p>
                  <ol className="trace">
                    {visibleFocus.trace.map((t, i) => (
                      <li key={i}>
                        <span>{t.stage}</span>
                        <b>{t.operation}</b>
                        <p>
                          {t.detail}{" "}
                          {t.duration_ms > 0 && `· ${t.duration_ms} ms`}
                        </p>
                      </li>
                    ))}
                  </ol>
                  <h3>Source events</h3>
                  <div className="evidence">
                    {visibleFocus.evidence_ids.map((id) => (
                      <button
                        key={id}
                        onClick={() => {
                          seek(Number(id.split(":").at(-1)));
                          setTab(0);
                        }}
                      >
                        #{id.split(":").at(-1)}
                      </button>
                    ))}
                  </div>
                  {visibleFocus.observations.explain_forecast_change !=
                    null && (
                    <AttributionView
                      data={
                        visibleFocus.observations
                          .explain_forecast_change as Attribution
                      }
                    />
                  )}
                  <details>
                    <summary>Raw tool evidence</summary>
                    <pre>
                      {JSON.stringify(visibleFocus.observations, null, 2)}
                    </pre>
                  </details>
                  {visibleFocus.relations.map((r, i) => (
                    <p key={i}>
                      {r.type} {r.target}
                    </p>
                  ))}
                </>
              ) : (
                <div className="empty">
                  <h2>A clear trail from question to answer.</h2>
                  <p>
                    Investigate the selected moment to see actual tool calls,
                    evidence checks, and publication status.
                  </p>
                </div>
              )}
            </section>
          </div>
        )}
        {tab === 2 && (
          <div className="intelligence-grid">
            <section className="paper">
              <span className="eyebrow">SCENARIO LAB / CHECKPOINT #{seq}</span>
              <h2>
                What changes
                <br />
                the possibilities?
              </h2>
              <p>
                Branch from this immutable moment. Compare paired continuations
                under the same model.
              </p>
              <label>
                Team
                <select
                  value={team}
                  onChange={(e) => {
                    setTeam(+e.target.value);
                    setPlayer("");
                    setReplacement("");
                  }}
                >
                  <option value="0">Northbridge FC</option>
                  <option value="1">Harbour Athletic</option>
                </select>
              </label>
              <label>
                Intervention
                <select
                  value={action}
                  onChange={(e) => setAction(e.target.value)}
                >
                  <optgroup label="Tactical choices">
                    <option value="press">Pressing intensity</option>
                    <option value="compactness">Compactness</option>
                    <option value="directness">Attacking directness</option>
                    <option value="substitution">Substitution</option>
                    <option value="role">Outfield role</option>
                  </optgroup>
                  <optgroup label="Hypothetical circumstances">
                    <option value="goal">Additional goal</option>
                    <option value="red_card">Player sent off</option>
                    <option value="injury">Player injured</option>
                  </optgroup>
                </select>
              </label>
              {["press", "compactness", "directness"].includes(action) && (
                <label>
                  Intensity · {Math.round(value * 100)}%
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step=".05"
                    value={value}
                    onChange={(e) => setValue(+e.target.value)}
                  />
                </label>
              )}
              {["red_card", "injury", "substitution", "role"].includes(
                action,
              ) && (
                <label>
                  Active player
                  <select
                    value={player}
                    onChange={(e) => setPlayer(e.target.value)}
                  >
                    <option value="">Choose a player</option>
                    {state?.teams[team].players
                      .filter((p) => p.active && p.available)
                      .map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.name} · {p.role}
                        </option>
                      ))}
                  </select>
                </label>
              )}
              {action === "substitution" && (
                <label>
                  Replacement
                  <select
                    value={replacement}
                    onChange={(e) => setReplacement(e.target.value)}
                  >
                    <option value="">Choose a substitute</option>
                    {state?.teams[team].players
                      .filter((p) => !p.active && p.available)
                      .map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.name}
                        </option>
                      ))}
                  </select>
                </label>
              )}
              {action === "role" && (
                <label>
                  New role
                  <select
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                  >
                    {["DF", "MF", "FW"].map((r) => (
                      <option key={r}>{r}</option>
                    ))}
                  </select>
                </label>
              )}
              <p className="notice">
                {["goal", "red_card", "injury"].includes(action)
                  ? "Hypothetical circumstance — this is not a tactical decision."
                  : "Tactical experiment — benefits and costs depend on the match state."}
              </p>
              <button
                className="primary"
                disabled={!!busy || state?.phase === "finished"}
                onClick={simulate}
              >
                Run paired simulation →
              </button>
              {state?.phase === "finished" && (
                <p>Choose a checkpoint before full time.</p>
              )}
            </section>
            <section className="paper">
              <span className="eyebrow">
                HYPOTHETICAL / AUTHORITATIVE HISTORY UNCHANGED
              </span>
              <h2>A different route to full time.</h2>
              {branch ? (
                <>
                  <h3>Baseline</h3>
                  {prob(branch.baseline)}
                  <h3>With intervention</h3>
                  {prob(branch.alternative)}
                  <div className="scenario-deltas">
                    {Object.entries(branch.delta).map(([k, v]) => (
                      <div key={k}>
                        <span>{k}</span>
                        <strong>
                          {v >= 0 ? "+" : ""}
                          {(v * 100).toFixed(1)}
                          <small> pp</small>
                        </strong>
                        <small>
                          Paired SE {pct(branch.delta_standard_errors[k])}
                        </small>
                      </div>
                    ))}
                  </div>
                  <p>{branch.label}</p>
                  <small>
                    128 paired continuations · seed 710 · checkpoint{" "}
                    {branch.source_sequence}
                  </small>
                </>
              ) : (
                <div className="empty">
                  <div className="fork">
                    ↗<br />↘
                  </div>
                  <p>
                    Choose a change and run the comparison.
                    <br />
                    The source event history stays intact.
                  </p>
                </div>
              )}
            </section>
          </div>
        )}
        {tab === 3 && (
          <div className="broadcast-grid">
            <section>
              <span className="eyebrow">READY FOR THE STUDIO</span>
              <h2 className="big-title">
                One match.
                <br />A story for every viewer.
              </h2>
              <p>
                Verified facts, tailored depth. Switch audience mode to compare
                the same match evidence.
              </p>
              <button
                className="primary"
                disabled={!recap}
                onClick={exportRecap}
              >
                Export verified overlay ↓
              </button>
              <p className="service">
                Source: deterministic verified recap renderer.
              </p>
            </section>
            <section className="broadcast">
              <div className="broadcast-top">
                TRAJECTAN <span>SYNTHETIC / {profile.toUpperCase()}</span>
              </div>
              <div className="broadcast-body">
                <span className="badge">
                  MATCH INSIGHT · {state ? clock(state.second) : "00:00"}
                </span>
                <h2>{recap?.headline ?? "Preparing your recap…"}</h2>
                <p>{recap?.text}</p>
              </div>
              <div className="broadcast-footer">
                VERIFIED AGAINST EVENT LOG <span>STATE #{seq}</span>
              </div>
            </section>
            <section className="paper recap">
              <h2>Defining moments</h2>
              {recap?.moments?.length ? (
                recap.moments.map((e) => (
                  <button
                    className="memory"
                    key={e.event_id}
                    onClick={() => seek(e.sequence)}
                  >
                    <b>
                      {clock(e.second)} · {e.outcome}
                    </b>
                    <span>
                      {e.player} · event #{e.sequence} →
                    </span>
                  </button>
                ))
              ) : (
                <p>No goals or dismissals before this checkpoint.</p>
              )}
              <small>
                Half-time and full-time buttons select the corresponding recap.
                Later events never enter an earlier summary.
              </small>
            </section>
          </div>
        )}
        <footer>
          <b>TRAJECTAN →</b>
          <span>
            Observe → Detect → Investigate → Forecast → Experiment → Verify →
            Communicate
          </span>
          <span>All match data is synthetic.</span>
        </footer>
      </main>
    </>
  );
}
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
