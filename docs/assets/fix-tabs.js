// Fix top-level tab links to absolute paths based on the MkDocs runtime config
function rewriteTopLevelLinks() {
  try {
    let base = null;
    const cfgEl = document.getElementById('__config');
    if (cfgEl) {
      try {
        const cfg = JSON.parse(cfgEl.textContent);
        if (cfg && cfg.base) base = cfg.base;
      } catch (e) {
        // fall through
      }
    }

    // Fallback to canonical link if cfg.base is missing
    if (!base) {
      const canonical = document.querySelector('link[rel="canonical"]');
      if (canonical) base = canonical.href;
    }

    // If we still don't have a base, bail out
    if (!base) return;

    // Resolve base into an absolute URL (works when base is relative like '../../..')
    const baseUrl = new URL(base, location.href);

    const anchors = document.querySelectorAll('.md-tabs__link, .md-nav__link');
    anchors.forEach(a => {
      const href = a.getAttribute('href');
      if (!href) return;
      // skip absolute links, anchors, mailto, or protocol-relative
      if (href.startsWith('#') || href.startsWith('/') || href.match(/^[a-zA-Z]+:\/\//)) return;
      // Only adjust single-segment relative links (e.g. 'Einfuehrung/' or 'Einfuehrung')
      if (/^[^\/]+\/?$/.test(href)) {
        try {
          let newHref;
          if (href.startsWith('/')) {
            // href is root-absolute; join it with baseUrl.pathname to avoid dropping the site prefix
            const basePath = baseUrl.pathname.replace(/\/$/, '');
            const combined = (basePath + '/' + href.replace(/^\/+/, '')).replace(/\/+/g, '/');
            newHref = combined + (new URL(href, location.origin).search || '') + (new URL(href, location.origin).hash || '');
            if (typeof console !== 'undefined') console.info('fix-tabs: root-absolute rewrite', href, '->', newHref);
          } else {
            const resolved = new URL(href, baseUrl);
            // Use pathname + search + hash to keep URL structure but make it root-relative
            newHref = resolved.pathname + (resolved.search || '') + (resolved.hash || '');
            if (typeof console !== 'undefined') console.info('fix-tabs: relative rewrite', href, '->', newHref);
          }
          // Avoid changing if it's the same
          if (a.getAttribute('href') !== newHref) a.setAttribute('href', newHref);
        } catch (e) {
          // ignore invalid URLs
        }
      }
    });
  } catch (e) {
    console.warn('fix-tabs: failed', e);
  }
}

// Run on initial load and also after the Material JS finishes rendering (document$ event)
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', rewriteTopLevelLinks);
} else {
  // already loaded
  rewriteTopLevelLinks();
}

// Material for MkDocs dispatches a global event bus; ensure we re-run when navigation updates
if (window.document$ && typeof window.document$.subscribe === 'function') {
  window.document$.subscribe(rewriteTopLevelLinks);
} else {
  // as a fallback, listen for popstate (client navigation) and hashchange
  window.addEventListener('popstate', rewriteTopLevelLinks);
  window.addEventListener('hashchange', rewriteTopLevelLinks);
}

