/* Muskoka Digital Boost — progressive enhancement only.
   Every value this file touches is already correct in the HTML. */
(function () {
  'use strict';

  // (no-js class no longer used; reveal is additive)

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── Mobile nav ─────────────────────────────────────────── */
  var toggle = document.querySelector('.nav-toggle');
  var links = document.getElementById('nav-links');

  if (toggle && links) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      links.classList.toggle('is-open', !open);
    });

    links.addEventListener('click', function (e) {
      if (e.target.closest('a')) {
        toggle.setAttribute('aria-expanded', 'false');
        links.classList.remove('is-open');
      }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && links.classList.contains('is-open')) {
        toggle.setAttribute('aria-expanded', 'false');
        links.classList.remove('is-open');
        toggle.focus();
      }
    });
  }

  /* ── Nav shadow on scroll ───────────────────────────────── */
  var nav = document.querySelector('.site-nav');
  if (nav) {
    var onScroll = function () {
      nav.classList.toggle('is-scrolled', window.scrollY > 8);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ── Scroll reveal ────────────────────────────────────────────
     The .reveal elements are VISIBLE in CSS by default. We only opt
     into the hidden-then-fade-in behaviour after confirming we can
     actually reveal them again. A failure anywhere here leaves the
     content on screen rather than blanking the page. */
  var revealables = document.querySelectorAll('.reveal');

  if (revealables.length && 'IntersectionObserver' in window && !reduced) {
    var show = function (el) { el.classList.add('is-visible'); };

    document.documentElement.classList.add('js-anim');

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        io.unobserve(el);
        var delay = parseInt(el.getAttribute('data-delay') || '0', 10);
        if (delay) { setTimeout(function () { show(el); }, delay); } else { show(el); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });

    revealables.forEach(function (el) { io.observe(el); });

    // Failsafe: if anything above misbehaves, nothing stays hidden.
    setTimeout(function () {
      revealables.forEach(show);
    }, 3000);
  }

  /* ── Count-up ───────────────────────────────────────────────
     Enhancement ONLY. The final text is already in the DOM; we
     read it, animate up to it, and restore it verbatim. If this
     code never runs, the correct number is still on screen.   */
  var counters = document.querySelectorAll('[data-countup]');

  if (counters.length && 'IntersectionObserver' in window && !reduced) {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        co.unobserve(el);

        var finalText = el.textContent;
        var match = finalText.match(/-?[\d.,]+/);
        if (!match) return;

        var raw = match[0];
        var target = parseFloat(raw.replace(/,/g, ''));
        if (!isFinite(target)) return;

        var decimals = (raw.split('.')[1] || '').length;
        var grouped = raw.indexOf(',') !== -1;
        var start = performance.now();
        var DURATION = 1100;

        var format = function (n) {
          var s = n.toFixed(decimals);
          if (grouped) s = Number(s).toLocaleString('en-CA', {
            minimumFractionDigits: decimals, maximumFractionDigits: decimals
          });
          return finalText.replace(raw, s);
        };

        var tick = function (now) {
          var p = Math.min((now - start) / DURATION, 1);
          var eased = 1 - Math.pow(1 - p, 3);
          if (p < 1) {
            el.textContent = format(target * eased);
            requestAnimationFrame(tick);
          } else {
            el.textContent = finalText; // exact original string
          }
        };
        requestAnimationFrame(tick);
      });
    }, { threshold: 0.5 });

    counters.forEach(function (el) { co.observe(el); });
  }

  /* ── Contact form → mailto fallback ─────────────────────────
     No backend is configured. Rather than a button that silently
     does nothing, compose a prefilled email. Swap the handler for
     a real endpoint (Formspree / Netlify Forms) when there is one. */
  var form = document.getElementById('quote-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = new FormData(form);
      var get = function (k) { return (data.get(k) || '').toString().trim(); };

      var lines = [
        'Name: ' + get('name'),
        'Business: ' + get('business'),
        'Phone: ' + get('phone'),
        'Email: ' + get('email'),
        'Project type: ' + get('project'),
        'Budget: ' + get('budget'),
        '',
        'Details:',
        get('details')
      ];

      var subject = 'Website quote request' + (get('business') ? ' — ' + get('business') : '');
      window.location.href = 'mailto:asuter@muskokadigitalboost.ca'
        + '?subject=' + encodeURIComponent(subject)
        + '&body=' + encodeURIComponent(lines.join('\n'));

      var status = document.getElementById('form-status');
      if (status) {
        status.hidden = false;
        status.textContent = 'Opening your email app with the details filled in. '
          + 'If nothing happens, email asuter@muskokadigitalboost.ca or call (437) 225-1540.';
      }
    });
  }
})();
