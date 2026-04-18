(function () {
  'use strict';

  /* ── Nav hamburger ─────────────────────────────────────────────── */
  function initNav() {
    var btn = document.querySelector('.nav__hamburger');
    var links = document.querySelector('.nav__links');
    if (!btn || !links) return;

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = links.hasAttribute('hidden');
      if (open) {
        links.removeAttribute('hidden');
        btn.setAttribute('aria-expanded', 'true');
      } else {
        links.setAttribute('hidden', '');
        btn.setAttribute('aria-expanded', 'false');
      }
    });

    document.addEventListener('click', function (e) {
      if (!btn.contains(e.target) && !links.contains(e.target)) {
        links.setAttribute('hidden', '');
        btn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* ── Character gallery ─────────────────────────────────────────── */
  function initCharacterFilters() {
    var searchInput  = document.getElementById('char-search');
    var speciesSelect= document.getElementById('filter-species');
    var clearBtn     = document.getElementById('filter-clear');
    var countEl      = document.getElementById('char-count');
    var noResults    = document.getElementById('no-results');
    var cards        = Array.from(document.querySelectorAll('.char-card'));

    if (!searchInput || cards.length === 0) return;

    function applyFilters() {
      var search  = searchInput.value.toLowerCase().trim();
      var species = speciesSelect ? speciesSelect.value : '';
      var visible = 0;

      cards.forEach(function (card) {
        var nameMatch    = !search  || card.dataset.name.includes(search)
                                    || (card.dataset.bio || '').includes(search);
        var speciesMatch = !species || card.dataset.species === species;

        if (nameMatch && speciesMatch) {
          card.classList.remove('hidden');
          visible++;
        } else {
          card.classList.add('hidden');
        }
      });

      if (countEl)   countEl.textContent = visible;
      if (noResults) noResults.classList.toggle('hidden', visible > 0);
      writeHash({ search: searchInput.value, species: species || '' });
    }

    function writeHash(state) {
      var p = new URLSearchParams();
      if (state.search)  p.set('search',  state.search);
      if (state.species) p.set('species', state.species);
      var s = p.toString();
      history.replaceState(null, '', s ? '#' + s : location.pathname + location.search);
    }

    function readHash() {
      var hash = location.hash.replace('#', '');
      if (!hash) return;
      var p = new URLSearchParams(hash);
      if (p.get('search')  && searchInput)   searchInput.value   = p.get('search');
      if (p.get('species') && speciesSelect)  speciesSelect.value = p.get('species');
    }

    searchInput.addEventListener('input', applyFilters);
    if (speciesSelect) speciesSelect.addEventListener('change', applyFilters);
    if (clearBtn) clearBtn.addEventListener('click', function () {
      searchInput.value = '';
      if (speciesSelect) speciesSelect.value = '';
      applyFilters();
    });

    readHash();
    applyFilters();
  }

  /* ── Lore archive ──────────────────────────────────────────────── */
  function initLoreFilters() {
    var searchInput = document.getElementById('lore-search');
    var pills       = Array.from(document.querySelectorAll('.tag-pill[data-tag]'));
    var showAll     = document.querySelector('.tag-pill--showall');
    var entries     = Array.from(document.querySelectorAll('.lore-entry'));
    var countEl     = document.getElementById('lore-count');

    if (entries.length === 0) return;

    function activeTags() {
      return pills
        .filter(function (p) { return p.classList.contains('active'); })
        .map(function (p) { return p.dataset.tag; });
    }

    function applyFilters() {
      var search  = searchInput ? searchInput.value.toLowerCase().trim() : '';
      var tags    = activeTags();
      var visible = 0;

      entries.forEach(function (entry) {
        var entryTags = (entry.dataset.tags || '').split(' ').filter(Boolean);
        var tagMatch  = tags.length === 0
                        || tags.some(function (t) { return entryTags.includes(t); });
        var textMatch = !search
                        || (entry.dataset.title   || '').includes(search)
                        || (entry.dataset.content || '').includes(search);

        if (tagMatch && textMatch) {
          entry.classList.remove('hidden');
          visible++;
        } else {
          entry.classList.add('hidden');
        }
      });

      if (countEl) countEl.textContent = visible;
    }

    pills.forEach(function (pill) {
      pill.addEventListener('click', function () {
        pill.classList.toggle('active');
        if (showAll) showAll.classList.remove('active');
        applyFilters();
      });
    });

    if (showAll) {
      showAll.addEventListener('click', function () {
        pills.forEach(function (p) { p.classList.remove('active'); });
        showAll.classList.add('active');
        applyFilters();
      });
      showAll.classList.add('active');
    }

    if (searchInput) searchInput.addEventListener('input', applyFilters);

    applyFilters();
  }

  /* ── Boot ──────────────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    initNav();
    initCharacterFilters();
    initLoreFilters();
  });
}());
