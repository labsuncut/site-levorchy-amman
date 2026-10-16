// LEVORCHY: small, dependency-free behaviour for every page.
// Language switch, menu, intro, the scroll runway, reveals, filters, gallery dots, lazy map.
(() => {
  const html = document.documentElement;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  $$('[data-year]').forEach((el) => { el.textContent = new Date().getFullYear(); });

  // ---------- Language ----------
  $$('[data-lang-toggle]').forEach((b) => b.addEventListener('click', () => {
    const ar = html.lang !== 'ar';
    html.lang = ar ? 'ar' : 'en';
    html.dir = ar ? 'rtl' : 'ltr';
    try { localStorage.setItem('lev-lang', html.lang); } catch (e) {}
    window.dispatchEvent(new Event('resize'));
  }));

  // ---------- Menu ----------
  const menuBtn = $('.menu-btn'), nav = $('#nav');
  if (menuBtn && nav) {
    const set = (open) => { nav.classList.toggle('open', open); menuBtn.setAttribute('aria-expanded', open); document.body.style.overflow = open ? 'hidden' : ''; };
    menuBtn.addEventListener('click', () => set(!nav.classList.contains('open')));
    $$('a', nav).forEach((a) => a.addEventListener('click', () => set(false)));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') set(false); });
  }

  // ---------- Intro (home page, once per visit) ----------
  const intro = $('#intro');
  if (intro) {
    let seen = false; try { seen = sessionStorage.getItem('lev-intro') === '1'; } catch (e) {}
    const end = () => { intro.classList.add('done'); try { sessionStorage.setItem('lev-intro', '1'); } catch (e) {} };
    if (seen || calm) { intro.remove(); }
    else { intro.addEventListener('click', end); setTimeout(end, 2600); }
  }

  // ---------- Reveal on scroll ----------
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => entries.forEach((en) => {
      if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
    }), { rootMargin: '0px 0px -8% 0px' });
    $$('.reveal').forEach((el) => io.observe(el));
  } else $$('.reveal').forEach((el) => el.classList.add('in'));

  // ---------- Call bar: shows after the first screen ----------
  const bar = $('.call-bar');
  if (bar) {
    const tick = () => bar.classList.toggle('visible', scrollY > innerHeight * 0.6);
    addEventListener('scroll', tick, { passive: true }); tick();
  }

  // ---------- Runway ----------
  // Each look walks from the far end of the runway toward you as you scroll. When she arrives the
  // camera moves in on her (per-look focus point and zoom), a close-up photo fades in so the
  // embroidery can be read, then she walks out of frame and the next look is already on her way.
  const runway = $('#runway');
  if (runway) {
    const looks = $$('[data-look]', runway);
    const count = $('[data-count]', runway);
    if (calm) runway.classList.add('still');
    else {
      const parts = looks.map((l) => ({
        frame: $('.look-photo', l), walk: $('.walk', l), detail: $('.detail', l), zoom: Number(l.dataset.zoom) || 1.4,
      }));
      const S = 1.5;                                             // distance between looks, in "steps"
      const ease = (x) => 1 - Math.pow(1 - x, 3);
      const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
      const smooth = (a, b, x) => { const k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k); };
      let ticking = false;
      const draw = () => {
        ticking = false;
        const r = runway.getBoundingClientRect();
        const p = clamp(-r.top / (runway.offsetHeight - innerHeight));
        const pos = 0.45 + p * ((looks.length - 1) * S + 0.95);  // ends with the last look up close
        const front = clamp(Math.round((pos - 1.25) / S), 0, looks.length - 1);
        looks.forEach((l, i) => {
          const t = pos - i * S;                                 // 0 far away, 1 arrived, 1.5 leaving, 2.1 gone
          const { frame, walk, detail, zoom } = parts[i];
          if (t <= 0 || t >= 2.1) { frame.style.opacity = 0; l.classList.remove('show', 'on', 'detail-on'); return; }
          let scale, y, op, blur;
          if (t < 1) {
            const k = ease(t);
            scale = 0.2 + 0.8 * k; y = -16 * (1 - k); op = clamp(t * 2.4); blur = (1 - k) * 6;
          } else if (t < 1.5) {
            scale = 1; y = 0; op = 1; blur = 0;
          } else {
            const k = (t - 1.5) / 0.6;
            scale = 1 + 0.3 * k; y = 14 * k * k; op = clamp(1 - k * 1.8); blur = k * 4;
          }
          const z = 1 + (zoom - 1) * smooth(0.35, 1.05, t);      // the camera moves in on her
          frame.style.opacity = op.toFixed(3);
          frame.style.filter = blur > 0.2 ? `blur(${blur.toFixed(1)}px)` : 'none';
          frame.style.transform = `translate(-50%, calc(-50% + ${y.toFixed(2)}vh)) scale(${scale.toFixed(4)})`;
          frame.style.zIndex = Math.round(t * 100);
          walk.style.transform = `scale(${z.toFixed(4)})`;
          const d = detail ? smooth(1.1, 1.3, t) : 0;
          if (detail) detail.style.opacity = d.toFixed(3);
          l.classList.toggle('detail-on', d > 0.5);
          const lit = i === front && t > 0.6 && t < 1.95;
          l.classList.toggle('show', lit);
          l.classList.toggle('on', lit);
        });
        if (count) count.textContent = String(front + 1).padStart(2, '0');
      };
      const req = () => { if (!ticking) { ticking = true; requestAnimationFrame(draw); } };
      addEventListener('scroll', req, { passive: true });
      addEventListener('resize', req);
      draw();
    }
  }

  // ---------- Collection filters ----------
  const grid = $('[data-grid]');
  if (grid) {
    const chips = $$('[data-filter]');
    const cards = $$('.card', grid);
    const shown = $('[data-shown]');
    const apply = (f) => {
      chips.forEach((c) => c.setAttribute('aria-pressed', c.dataset.filter === f));
      const [kind, val] = f.split(':');
      let n = 0;
      cards.forEach((c) => {
        const ok = f === 'all' || (kind === 'col' ? c.dataset.col === val : c.dataset.type === val);
        c.hidden = !ok; if (ok) { n++; c.classList.add('in'); }
      });
      if (shown) shown.textContent = n;
    };
    chips.forEach((c) => c.addEventListener('click', () => {
      apply(c.dataset.filter);
      history.replaceState(null, '', c.dataset.filter.startsWith('col:') ? '#' + c.dataset.filter.slice(4) : location.pathname);
    }));
    const h = location.hash.slice(1);
    if (h && chips.some((c) => c.dataset.filter === 'col:' + h)) apply('col:' + h);
  }

  // ---------- Look gallery dots (phone) ----------
  const slides = $('[data-slides]');
  if (slides) {
    const dots = $$('[data-dot]');
    const mark = () => {
      const i = Math.round(Math.abs(slides.scrollLeft) / slides.clientWidth);
      dots.forEach((d, k) => d.setAttribute('aria-current', k === i));
    };
    dots.forEach((d) => d.addEventListener('click', () => {
      const w = slides.clientWidth * Number(d.dataset.dot);
      slides.scrollTo({ left: html.dir === 'rtl' ? -w : w, behavior: 'smooth' });
    }));
    slides.addEventListener('scroll', () => requestAnimationFrame(mark), { passive: true });
    mark();
  }

  // ---------- Map loads only when it comes near ----------
  const map = $('iframe[data-src]');
  if (map) {
    const load = () => { if (map.src === 'about:blank') map.src = map.dataset.src; };
    if ('IntersectionObserver' in window) new IntersectionObserver((e, o) => { if (e[0].isIntersecting) { load(); o.disconnect(); } }, { rootMargin: '400px' }).observe(map);
    else load();
  }
})();
