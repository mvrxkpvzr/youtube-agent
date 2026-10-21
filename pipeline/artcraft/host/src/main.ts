// Headless host for ArtCraft's open-source video editor (@storyteller/ui-video-editor,
// github.com/storytold/artcraft). It drives the editor's public EditorCore API: import media,
// place clips on the timeline, export through the editor's own renderer. No ArtCraft account,
// no network, no credits. The Playwright driver (run_editor.mjs) calls window.artcraft.build().
import { EditorCore, buildDefaultScene, buildElementFromMedia, buildTextElement, createDefaultAdapters,
  mediaTimeFromSeconds, mediaTimeToSeconds, serializeProjectDocument, ZERO_MEDIA_TIME } from "@ve/index";
import { processMediaAssets } from "@ve/lib/media/processing";
import { mediaAssetToData } from "@ve/lib/services/storage/serialization";
import { buildScene } from "@ve/lib/services/renderer/scene-builder";
import { CanvasRenderer } from "@ve/lib/services/renderer/canvas-renderer";
import { initializeGpuRenderer, isGpuAvailable } from "@ve/lib/services/renderer/gpu-renderer";

type Fade = { fade_in_s?: number; fade_out_s?: number };
type Media = { id: string; url: string; name: string; kind: "video" | "image" | "audio" };
type VideoClip = Fade & { media: string; start_s: number; dur_s: number; in_s?: number; fit?: "cover" | "contain";
  zoom_from?: number; zoom_to?: number; scene?: string; layer?: number };
type AudioClip = Fade & { media: string; start_s: number; dur_s: number; in_s?: number; gain_db?: number; scene?: string };
type TextClip = Fade & { content: string; start_s: number; dur_s: number; style?: "subtitle" | "title" | "lower_third"; scene?: string };
export type Timeline = { fps: number; width: number; height: number; duration_s: number; background?: string;
  media: Media[]; video: VideoClip[]; audio: AudioClip[]; text: TextClip[]; filename: string;
  format?: "mp4" | "webm"; quality?: "low" | "medium" | "high" | "very_high" };

const T = (s: number) => mediaTimeFromSeconds({ seconds: Math.max(0, s) });
const log: string[] = [];
const say = (m: string) => { log.push(m); console.log("[artcraft-host] " + m); };

const TEXT_STYLE: Record<string, Record<string, unknown>> = {
  subtitle: { fontSize: 5.2, "transform.positionY": 420, "background.enabled": true, "background.color": "#000000b0",
    "background.paddingX": 28, "background.paddingY": 14, fontWeight: "bold" },
  title: { fontSize: 11, fontWeight: "bold", "transform.positionY": 0 },
  lower_third: { fontSize: 5, "transform.positionY": 380, textAlign: "left", "transform.positionX": -560 },
};

async function build(tl: Timeline) {
  log.length = 0;
  await initializeGpuRenderer(); // the compositor needs WebGPU (the editor UI awaits this before mounting too)
  if (!isGpuAvailable()) throw new Error("WebGPU unavailable: the ArtCraft compositor cannot render");
  say("WebGPU ready");
  EditorCore.reset();
  const editor = EditorCore.initialize({ adapters: createDefaultAdapters() });
  const scene = buildDefaultScene({ name: "Main scene", isMain: true });
  const now = new Date();
  const project = { metadata: { id: "agent-" + tl.filename, name: tl.filename, duration: ZERO_MEDIA_TIME, createdAt: now, updatedAt: now },
    scenes: [scene], currentSceneId: scene.id, version: 1,
    settings: { fps: { numerator: tl.fps, denominator: 1 } as never, canvasSize: { width: tl.width, height: tl.height },
      background: { type: "color", color: tl.background ?? "#000000" } } } as never;
  editor.project.setActiveProject({ project });
  editor.scenes.initializeScenes({ scenes: [scene], currentSceneId: scene.id });

  // 1) Media import: the same processing path as a file dropped into the editor's assets panel.
  const files = await Promise.all(tl.media.map(async (m) => {
    const r = await fetch(m.url); if (!r.ok) throw new Error(`media ${m.id}: HTTP ${r.status}`);
    const b = await r.blob(); return new File([b], m.name, { type: b.type });
  }));
  const assets = await processMediaAssets({ files, toast: editor.adapters.toast, mediaSource: editor.adapters.mediaSource });
  if (assets.length !== tl.media.length) throw new Error(`imported ${assets.length}/${tl.media.length} media files`);
  const byId = new Map<string, any>();
  tl.media.forEach((m, i) => { byId.set(m.id, assets[i]); });
  for (const a of assets) await editor.media.addMediaAsset({ asset: a });
  say(`imported ${assets.length} media`);

  const tracks = () => editor.scenes.getActiveScene().tracks;
  const lastId = (kind: "main" | "audio" | "text") => {
    const t = tracks();
    const list = kind === "main" ? [t.main] : kind === "audio" ? t.audio : t.overlay.filter((x: any) => x.type === "text");
    for (const tr of list) { const e = tr.elements[tr.elements.length - 1]; if (e) return { trackId: tr.id, el: e }; }
    throw new Error("element not inserted");
  };
  const findNew = (before: Set<string>) => {
    const t = tracks();
    for (const tr of [t.main, ...t.overlay, ...t.audio]) for (const e of tr.elements) if (!before.has(e.id)) return { trackId: tr.id, el: e };
    throw new Error("element not inserted");
  };
  const ids = () => { const t = tracks(); return new Set([t.main, ...t.overlay, ...t.audio].flatMap((tr: any) => tr.elements.map((e: any) => e.id))); };
  const fades = (trackId: string, elementId: string, path: string, dur: number, f: Fade, on: number, off: number) => {
    const kf: any[] = [];
    if (f.fade_in_s) kf.push({ time: 0, value: off }, { time: f.fade_in_s, value: on });
    if (f.fade_out_s) kf.push({ time: Math.max(0, dur - f.fade_out_s), value: on }, { time: dur, value: off });
    if (kf.length) editor.timeline.upsertKeyframes({ keyframes: kf.map((k) => ({ trackId, elementId, propertyPath: path,
      time: T(k.time), value: k.value, interpolation: "linear" as never })) });
  };

  const trim = (el: any, inS: number, dur: number, src: number) => {
    if (inS + dur > src + 0.05) throw new Error(`${el.name}: ${inS}+${dur} s is past the end of the source (${src} s)`);
    el.trimStart = T(inS); el.trimEnd = T(Math.max(0, src - inS - dur)); el.sourceDuration = T(src); el.duration = T(dur);
  };

  // 2) Visual clips, in order: layer 0 on the main track, layer 1 on a video track above it (crossfades overlap the two).
  // An empty track is pruned straight away, so the upper track comes from the editor's own "first free video track" rule:
  // a crossfading clip overlaps the main track's previous clip, which leaves only the track above it.
  const placementFor = (layer = 0) => layer ? { mode: "auto" as const, trackType: "video" as const } : { mode: "explicit" as const, trackId: tracks().main.id };
  for (const c of [...tl.video].sort((a, b) => a.start_s - b.start_s)) {
    const a = byId.get(c.media); if (!a) throw new Error(`unknown media ${c.media}`);
    const before = ids();
    // trimmed before insertion, like a clip cut in the timeline: [in_s, in_s + dur_s] of the source at start_s
    const el: any = buildElementFromMedia({ mediaId: a.id, mediaType: a.type, name: c.scene ? `${c.scene} ${a.name}` : a.name,
      duration: T(c.dur_s), startTime: T(c.start_s) });
    if (a.type === "video") trim(el, c.in_s ?? 0, c.dur_s, a.duration ?? c.dur_s);
    editor.timeline.insertElement({ element: el, placement: placementFor(c.layer) });
    const { trackId, el: ins } = findNew(before);
    const w = a.width ?? tl.width, h = a.height ?? tl.height;
    const contain = Math.min(tl.width / w, tl.height / h), cover = Math.max(tl.width / w, tl.height / h);
    const s = (c.fit ?? "cover") === "cover" ? cover / contain : 1;
    const z0 = c.zoom_from ?? 1, z1 = c.zoom_to ?? z0;
    editor.timeline.updateElements({ updates: [{ trackId, elementId: ins.id, patch: {
      params: { ...ins.params, "transform.scaleX": s * z0, "transform.scaleY": s * z0, volume: a.type === "video" ? -60 : ins.params.volume } } }] } as never);
    if (z1 !== z0) for (const p of ["transform.scaleX", "transform.scaleY"]) editor.timeline.upsertKeyframes({ keyframes: [
      { trackId, elementId: ins.id, propertyPath: p, time: T(0), value: s * z0, interpolation: "linear" as never },
      { trackId, elementId: ins.id, propertyPath: p, time: T(c.dur_s), value: s * z1, interpolation: "linear" as never }] });
    fades(trackId, ins.id, "opacity", c.dur_s, c, 1, 0);
  }
  say(`placed ${tl.video.length} visual clips`);

  // 3) Audio clips (narration per scene, music beds) on audio tracks.
  for (const c of tl.audio) {
    const a = byId.get(c.media); if (!a) throw new Error(`unknown media ${c.media}`);
    const before = ids();
    const el: any = buildElementFromMedia({ mediaId: a.id, mediaType: "audio", name: a.name, duration: T(c.dur_s), startTime: T(c.start_s) });
    trim(el, c.in_s ?? 0, c.dur_s, a.duration ?? c.dur_s);
    editor.timeline.insertElement({ element: el, placement: { mode: "auto", trackType: "audio" } });
    const { trackId, el: ins } = findNew(before);
    const g = c.gain_db ?? 0;
    editor.timeline.updateElements({ updates: [{ trackId, elementId: ins.id, patch: { params: { ...ins.params, volume: g } } }] } as never);
    fades(trackId, ins.id, "volume", c.dur_s, c, g, -60);
  }
  say(`placed ${tl.audio.length} audio clips`);

  // 4) Titles / burned-in subtitles as text elements.
  for (const c of tl.text) {
    const before = ids();
    const el = buildTextElement({ raw: { name: c.content.slice(0, 24), duration: T(c.dur_s),
      params: { ...(TEXT_STYLE[c.style ?? "subtitle"] ?? {}), content: c.content } as never }, startTime: T(c.start_s) });
    editor.timeline.insertElement({ element: el, placement: { mode: "auto", trackType: "text" } });
    const { trackId, el: ins } = findNew(before);
    fades(trackId, ins.id, "opacity", c.dur_s, c, 1, 0);
  }
  say(`placed ${tl.text.length} text elements`);

  // The editor sizes the canvas (and fps) from the first visual clip, as when a user drops one in; the plan decides.
  editor.project.updateSettings({ settings: { canvasSize: { width: tl.width, height: tl.height },
    fps: { numerator: tl.fps, denominator: 1 } as never }, pushHistory: false } as never);

  // 5) Read the timeline back from the editor so the driver can check it against the plan.
  const t = tracks();
  const readback = [t.main, ...t.overlay, ...t.audio].map((tr: any) => ({ type: tr.type, elements: tr.elements.map((e: any) => ({
    name: e.name, type: e.type, start_s: mediaTimeToSeconds({ time: e.startTime }), dur_s: mediaTimeToSeconds({ time: e.duration }),
    in_s: mediaTimeToSeconds({ time: e.trimStart }), content: e.params?.content, volume_db: e.params?.volume })) }));
  const total = editor.timeline.getTotalDuration();
  const doc = serializeProjectDocument({ project: editor.project.getActive() as never, media: editor.media.getAssets().map(mediaAssetToData) });

  // Probe: render single frames through the editor's renderer and measure them (catches a black compositor).
  const probe = async (sec: number) => {
    const scene = buildScene({ tracks: tracks(), mediaAssets: editor.media.getAssets(), duration: total,
      canvasSize: { width: tl.width, height: tl.height }, background: { type: "color", color: tl.background ?? "#000000" } } as never);
    const r = new CanvasRenderer({ width: tl.width, height: tl.height, fps: { numerator: tl.fps, denominator: 1 } as never });
    const c = document.createElement("canvas"); c.width = 160; c.height = 90;
    await r.renderToCanvas({ node: scene as never, time: Math.round(sec * 120000), targetCanvas: c });
    const d = c.getContext("2d")!.getImageData(0, 0, 160, 90).data; let m = 0; for (let i = 0; i < d.length; i += 4) m += d[i] + d[i + 1] + d[i + 2];
    return m / (d.length / 4) / 3;
  };
  if ((tl as any).probe) for (const sec of (tl as any).probe) say(`probe t=${sec}s mean=${(await probe(sec)).toFixed(1)}`);

  // 6) Export with the editor's own SceneExporter, then hand the file to the editor's download sink.
  const t0 = performance.now();
  const res = await editor.project.export({ options: { format: tl.format ?? "mp4", quality: tl.quality ?? "high", includeAudio: true } });
  if (!res.success || !res.buffer) throw new Error("export failed: " + (res.error ?? (res.cancelled ? "cancelled" : "no buffer")));
  say(`exported ${res.buffer.byteLength} bytes in ${((performance.now() - t0) / 1000).toFixed(1)} s`);
  const mime = (tl.format ?? "mp4") === "mp4" ? "video/mp4" : "video/webm";
  await editor.adapters.exportSink.accept({ blob: new Blob([res.buffer], { type: mime }), filename: tl.filename, mime } as never, { saveToDisk: true });
  return { ok: true, bytes: res.buffer.byteLength, total_s: mediaTimeToSeconds({ time: total }), fps: tl.fps, width: tl.width, height: tl.height, readback, project: doc, log };
}

(window as any).artcraft = { build, ready: true };
