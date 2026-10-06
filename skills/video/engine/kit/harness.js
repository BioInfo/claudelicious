/* mvid scene harness. Load order: tokens.css, theme.css, gsap (+plugins), audio/cues.js (optional), harness.js.
   Contract:
   - exactly one paused timeline, registered SYNCHRONOUSLY at window.__timelines[<data-composition-id>]
     (and window.__timeline), then populated after document.fonts.ready so measurements use real glyphs;
   - padded to data-duration so the timeline length equals the composition length;
   - ?t=<sec>|end[,<sec>...] seeks for stills (last wins); ?play=1 plays for eyeballing;
   - errors land in <html data-jserror>, readiness in <html data-ready="1">.
   No rAF, no Date, no unseeded random. MV.rng(seed) is the only randomness allowed. */
(function(){
  var html = document.documentElement;
  window.addEventListener('error', function(e){ html.dataset.jserror = (e.message || (e.target && e.target.src ? 'load failed: ' + e.target.src : 'error')); }, true);
  window.addEventListener('unhandledrejection', function(e){ html.dataset.jserror = String(e.reason); });

  function lines(){ return (window.CUES && window.CUES.lines) || []; }
  function line(i){ var L = lines(); for (var k = 0; k < L.length; k++) if (L[k].i === i) return L[k]; return null; }

  var MV = {
    /* MV.scene(build) or MV.scene(id, build). build(tl, MV) adds tweens; id defaults to data-composition-id. */
    scene: function(id, build){
      if (typeof id === 'function') { build = id; id = null; }
      var root = document.querySelector('[data-composition-id]');
      id = id || (root ? root.dataset.compositionId : 'main');
      var tl = gsap.timeline({paused:true});
      window.__timeline = tl;
      window.__timelines = window.__timelines || {};
      window.__timelines[id] = tl;
      MV.tl = tl; MV.root = root;
      var ready = (document.fonts && document.fonts.ready) ? document.fonts.ready : Promise.resolve();
      ready.then(function(){
        build(tl, MV);
        var dur = MV.duration();
        if (dur && tl.duration() < dur) tl.set({}, {}, dur);
        var q = new URLSearchParams(location.search);
        if (q.get('t') !== null) q.get('t').split(',').forEach(function(v){ tl.seek(v === 'end' ? tl.duration() : parseFloat(v), false); });
        else tl.seek(0, false);
        if (q.get('play')) tl.play(0);
        html.dataset.ready = '1';
      }).catch(function(e){ html.dataset.jserror = String(e); throw e; });
      return tl;
    },
    /* declared composition length: data-duration, else CUES.total */
    duration: function(){
      var r = MV.root || document.querySelector('[data-composition-id]');
      if (r && r.dataset.duration) return parseFloat(r.dataset.duration);
      return window.CUES ? window.CUES.total : 0;
    },
    /* resolved value of a theme/tokens variable on #root (respects .cream): MV.tok('accent') -> "#4f8cff" */
    tok: function(name){
      var r = MV.root || document.querySelector('[data-composition-id]') || html;
      return getComputedStyle(r).getPropertyValue('--' + name.replace(/^--/, '')).trim();
    },
    hasCues: function(){ return lines().length > 0; },
    /* start of narration line i (1-based, cues.json "i"). fallback used when no cues.js is loaded. */
    cue: function(i, fallback){ var l = line(i); if (l) return l.start; if (fallback !== undefined) return fallback; throw new Error('MV.cue: no line ' + i); },
    /* end of narration line i */
    cueEnd: function(i, fallback){ var l = line(i); if (l) return l.start + l.dur; if (fallback !== undefined) return fallback; throw new Error('MV.cueEnd: no line ' + i); },
    /* start of word n (0-based) in line i. Negative n counts from the end (-1 = last word). */
    word: function(i, n, fallback){
      var l = line(i);
      if (l && l.words && l.words.length) { var w = l.words[n < 0 ? l.words.length + n : n]; if (w) return w.start; }
      if (fallback !== undefined) return fallback;
      throw new Error('MV.word: no word ' + n + ' in line ' + i);
    },
    /* first word in line i whose text matches (case-insensitive, punctuation stripped) */
    wordOf: function(i, text, fallback){
      var l = line(i), t = String(text).toLowerCase();
      if (l && l.words) for (var k = 0; k < l.words.length; k++) if (l.words[k].w.toLowerCase().replace(/[^\w%$.-]/g, '') === t) return l.words[k].start;
      if (fallback !== undefined) return fallback;
      throw new Error('MV.wordOf: "' + text + '" not in line ' + i);
    },
    /* seeded PRNG (mulberry32). Same seed -> same sequence -> same pixels on every seek. */
    rng: function(seed){
      var a = seed >>> 0;
      return function(){ a = (a + 0x6D2B79F5) >>> 0; var t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
    },
    /* mm:ss.ff timecode for t seconds at fps */
    timecode: function(t, fps){ fps = fps || 30; var s = Math.max(0, t), m = Math.floor(s / 60), ss = Math.floor(s % 60), f = Math.floor((s % 1) * fps);
      return (m < 10 ? '0' : '') + m + ':' + (ss < 10 ? '0' : '') + ss + ':' + (f < 10 ? '0' : '') + f; },
    /* Drive the corner HUD from timeline time: progress bar scaleX 0->1 over the scene and a mono timecode.
       opts: {bar:'#hudBar i', tc:'#hudTc', offset: seconds already elapsed in the film, total: film length} */
    hud: function(tl, opts){
      opts = opts || {}; var dur = MV.duration() || tl.duration();
      /* film.js in the scene dir (written by mvid scene/render) places the scene in the film, so the HUD runs on film time */
      var F = window.MV_FILM, root = document.getElementById('root'), id = root && root.getAttribute('data-composition-id');
      var fo = (F && F.offsets && id in F.offsets) ? F.offsets[id] : 0;
      var off = opts.offset != null ? opts.offset : fo, total = opts.total || (F && F.total) || dur, fps = opts.fps || 30;
      var bar = document.querySelector(opts.bar || '#hudBar i'), tc = document.querySelector(opts.tc || '#hudTc');
      var p = {t:0};
      tl.fromTo(p, {t:0}, {t:dur, duration:dur, ease:'none', immediateRender:true, onUpdate:function(){
        if (bar) bar.style.transform = 'scaleX(' + Math.min(1, (off + p.t) / total) + ')';
        if (tc) tc.textContent = MV.timecode(off + p.t, fps);
      }}, 0);
      return tl;
    }
  };
  window.MV = MV;
})();
