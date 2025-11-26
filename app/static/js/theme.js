'use strict';
(function () {
  const doc = document.documentElement;
  const STORAGE_KEY = 'theme';
  const DARK_CLASS = 'dark';

  const readStoredTheme = () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored === 'dark' || stored === 'light' ? stored : null;
    } catch (_) {
      return null;
    }
  };

  const prefersDark = () => {
    try {
      return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    } catch (_) {
      return false;
    }
  };

  const applyTheme = (mode, { persist = true, syncIcon = true } = {}) => {
    const isDark = mode === 'dark';
    doc.classList.toggle(DARK_CLASS, isDark);
    if (persist) {
      try {
        localStorage.setItem(STORAGE_KEY, isDark ? 'dark' : 'light');
      } catch (_) {}
    }
    if (syncIcon) updateToggleIcon(isDark);
    return isDark;
  };

  const ensureInitialTheme = () => {
    const stored = readStoredTheme();
    const mode = stored ?? (prefersDark() ? 'dark' : 'light');
    return applyTheme(mode, { persist: false, syncIcon: false });
  };

  const updateToggleIcon = (isDark) => {
    const toggle = document.getElementById('themeToggle');
    if (!toggle) return;
    const moon = toggle.querySelector('[data-icon="moon"]');
    const sun = toggle.querySelector('[data-icon="sun"]');
    if (!moon || !sun) return;
    moon.toggleAttribute('hidden', isDark);
    sun.toggleAttribute('hidden', !isDark);
  };

  const toggleTheme = () => {
    const isDark = !doc.classList.contains(DARK_CLASS);
    applyTheme(isDark ? 'dark' : 'light');
  };

  function showLoader() { document.getElementById('globalLoader')?.classList.add('show'); }
  function hideLoader() { document.getElementById('globalLoader')?.classList.remove('show'); }

  function hookLinksForLoader() {
    document.addEventListener('click', (e) => {
      const a = e.target.closest('a');
      if (!a || a.href === undefined) return;
      const url = new URL(a.href, window.location.href);
      if (url.origin === window.location.origin && !a.hasAttribute('data-no-loader') && a.target !== '_blank') {
        showLoader();
      }
    }, true);
    window.addEventListener('pageshow', hideLoader);
  }

  function initAOS() {
    if (window.AOS) {
      window.AOS.init({ duration: 600, once: true, offset: 24, easing: 'ease-out-cubic' });
    }
  }

  ensureInitialTheme();

  if (window.matchMedia) {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', (event) => {
      if (readStoredTheme()) return;
      applyTheme(event.matches ? 'dark' : 'light');
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    updateToggleIcon(doc.classList.contains(DARK_CLASS));
    const btn = document.getElementById('themeToggle');
    if (btn) btn.addEventListener('click', toggleTheme);
    hookLinksForLoader();
    initAOS();
  });
})();
