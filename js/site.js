/* FM Recycling — progressive enhancement only.
   Nothing here is required for the page to be correct or readable. */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── Mobile nav ─────────────────────────────────────────── */
  var toggle = document.querySelector('.nav-toggle');
  var links = document.getElementById('nav-links');

  if (toggle && links) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      toggle.setAttribute('aria-label', open ? 'Open menu' : 'Close menu');
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

  /* ── Scroll reveal ──────────────────────────────────────────
     .reveal elements are visible in CSS by default. The hidden
     state is only opted into once we know we can undo it, with a
     timed failsafe. A thrown error cannot blank the page. */
  var revealables = document.querySelectorAll('.reveal');
  if (revealables.length && 'IntersectionObserver' in window && !reduced) {
    var show = function (el) { el.classList.add('is-visible'); };
    document.documentElement.classList.add('js-anim');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        io.unobserve(el);
        var d = parseInt(el.getAttribute('data-delay') || '0', 10);
        if (d) { setTimeout(function () { show(el); }, d); } else { show(el); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    revealables.forEach(function (el) { io.observe(el); });
    setTimeout(function () { revealables.forEach(show); }, 3000);
  }

  /* ── Yard open/closed ───────────────────────────────────────
     The HTML already states the hours in full. This only adds a
     live "open now / closed" read-out on top, computed in the
     yard's own timezone rather than the visitor's, so someone
     checking from another province still gets Orillia's answer.
     If any of it fails, the static hours remain correct. */
  var YARD_TZ = 'America/Toronto';

  // [openMinutes, closeMinutes] by weekday index (0 = Sunday), null = closed
  var HOURS = [null, [480, 1020], [480, 1020], [480, 1020], [480, 1020], [480, 1020], [480, 720]];

  // Dates the yard is closed regardless of weekday (YYYY-MM-DD, Toronto local)
  var CLOSURES = ['2026-07-31', '2026-08-01', '2026-08-03'];

  function yardNow() {
    // Read the wall clock in Toronto without depending on the visitor's offset
    var fmt = new Intl.DateTimeFormat('en-CA', {
      timeZone: YARD_TZ, weekday: 'short', hour: '2-digit', minute: '2-digit',
      year: 'numeric', month: '2-digit', day: '2-digit', hour12: false
    });
    var parts = {};
    fmt.formatToParts(new Date()).forEach(function (p) { parts[p.type] = p.value; });
    var days = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
    return {
      dow: days[parts.weekday],
      minutes: parseInt(parts.hour, 10) * 60 + parseInt(parts.minute, 10),
      iso: parts.year + '-' + parts.month + '-' + parts.day
    };
  }

  function hhmm(m) {
    var h = Math.floor(m / 60), mm = m % 60;
    var ap = h >= 12 ? 'pm' : 'am';
    var h12 = h % 12 === 0 ? 12 : h % 12;
    return h12 + (mm ? ':' + String(mm).padStart(2, '0') : '') + ap;
  }

  var el = document.querySelector('[data-yard-state]');
  if (el && window.Intl && Intl.DateTimeFormat.supportedLocalesOf) {
    try {
      var now = yardNow();
      if (typeof now.dow === 'number' && !isNaN(now.minutes)) {
        var closedToday = CLOSURES.indexOf(now.iso) !== -1;
        var today = closedToday ? null : HOURS[now.dow];
        var open = !!today && now.minutes >= today[0] && now.minutes < today[1];

        var label;
        if (open) {
          label = 'Open now · closes ' + hhmm(today[1]);
        } else if (today && now.minutes < today[0]) {
          label = 'Closed · opens ' + hhmm(today[0]);
        } else {
          // find the next open day
          var next = null;
          for (var i = 1; i <= 7; i++) {
            var d = (now.dow + i) % 7;
            if (HOURS[d]) { next = { d: d, h: HOURS[d] }; break; }
          }
          var names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
          label = next
            ? 'Closed · opens ' + (next.d === (now.dow + 1) % 7 ? 'tomorrow' : names[next.d]) +
              ' ' + hhmm(next.h[0])
            : 'Closed';
        }

        el.textContent = '';
        var dot = document.createElement('span');
        dot.className = 'dot';
        el.appendChild(dot);
        el.appendChild(document.createTextNode(label));
        el.classList.add(open ? 'is-open' : 'is-closed');
        el.hidden = false;
      }
    } catch (err) { /* static hours stand on their own */ }
  }

  // Mark today's row in any hours table
  try {
    var d = yardNow().dow;
    document.querySelectorAll('.hours-table tr[data-dow]').forEach(function (tr) {
      if (tr.getAttribute('data-dow').split(',').indexOf(String(d)) !== -1) {
        tr.classList.add('is-today');
      }
    });
  } catch (e) { /* no-op */ }

  /* ── Contact form → mailto fallback ─────────────────────────
     No backend is wired up. Rather than a button that silently
     does nothing, compose a prefilled email. Replace this with a
     real endpoint (Formspree / Netlify Forms) when there is one. */
  var form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = new FormData(form);
      var get = function (k) { return (data.get(k) || '').toString().trim(); };
      var body = [
        'Name: ' + get('name'),
        'Phone: ' + get('phone'),
        'Email: ' + get('email'),
        'Enquiry: ' + get('subject'),
        '',
        get('message')
      ].join('\n');
      window.location.href = 'mailto:office@fmrecycling.ca'
        + '?subject=' + encodeURIComponent(get('subject') || 'Website enquiry')
        + '&body=' + encodeURIComponent(body);
      var status = document.getElementById('form-status');
      if (status) {
        status.hidden = false;
        status.textContent = 'Opening your email app with the details filled in. '
          + 'If nothing happens, email office@fmrecycling.ca or call (705) 325-8118.';
      }
    });
  }
})();
