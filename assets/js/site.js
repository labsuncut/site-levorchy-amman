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
  // Each look starts small at the far end of the runway, walks toward you as you scroll,
  // pauses in the spotlight with its name, then passes out of frame.
  const runway = $('#runway');
  if (runway) {
    const looks = $$('[data-look]', runway);
    const count = $('[data-count]', runway);
    if (calm) runway.classList.add('still');
    else {
      const photos = looks.map((l) => $('.look-photo', l));
      const ease = (x) => 1 - Math.pow(1 - x, 3);
      let ticking = false;
      const draw = () => {
        ticking = false;
        const r = runway.getBoundingClientRect();
        const total = runway.offsetHeight - innerHeight;
        const p = Math.min(1, Math.max(0, -r.top / total));     // 0..1 through the section
        const pos = -0.65 + p * (looks.length - 0.2);             // first look already walking in, last one ends in the spotlight
        let front = 0;
        looks.forEach((l, i) => {
          const t = pos - i + 1;                                  // 0 far away, 1 in the spotlight, 1.6 gone
          const ph = photos[i];
          if (t <= 0 || t >= 1.7) { ph.style.opacity = 0; l.classList.remove('show', 'on'); return; }
          let scale, y, op, blur;
          if (t < 1) {
            const k = ease(t);
            scale = 0.22 + 0.78 * k; y = -14 * (1 - k); op = Math.min(1, t * 2.2); blur = (1 - k) * 6;
          } else {
            const k = (t - 1) / 0.7;                              // walks past and out
            scale = 1 + 0.55 * k; y = 18 * k * k; op = 1 - k * k; blur = k * 3;
          }
          ph.style.opacity = op.toFixed(3);
          ph.style.filter = blur > 0.2 ? `blur(${blur.toFixed(1)}px)` : 'none';
          ph.style.transform = `translate(-50%, calc(-50% + ${y.toFixed(2)}vh)) scale(${scale.toFixed(4)})`;
          ph.style.zIndex = Math.round(t * 100);
          const inFront = t >= 0.6 && t < 1.6;                    // exactly one look holds the spotlight
          l.classList.toggle('show', inFront);
          l.classList.toggle('on', inFront);
          if (inFront) front = i;
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
