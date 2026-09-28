/**
 * MÃ SỐ KARAOKE VIETNAM - CORE APPLICATION JAVASCRIPT
 * Bản quyền Web & App thuộc về: Trần Hoàng Thứ - HoangThuIT
 * Kho dữ liệu 88,130+ bài hát: Arirang, MusicCore Vol 102, Paramax Vol 52, California, Việt KTV, Vitek VTB
 * Hỗ trợ Giao diện Sáng/Tối, 3 Kiểu hiển thị (Card, List, Grid), Màn hình riêng (Activity) & Offline 100%
 */

(function () {
  'use strict';

  // 7 Karaoke Systems with Official Brand Logos
  const COMPANIES = {
    a: { key: 'a', name: 'Arirang 5 số (Vol 66)', short: 'Arirang', varName: 'KARAOKE_DATA_A', file: 'arirang', logo: 'icons/arirang5.png' },
    acnos: { key: 'acnos', name: 'Acnos Soncamedia (Vol 62)', short: 'Acnos', varName: 'KARAOKE_DATA_ACNOS', file: 'acnos', logo: 'icons/sonca6.png' },
    m: { key: 'm', name: 'MusicCore 5 số (Vol 102)', short: 'MusicCore', varName: 'KARAOKE_DATA_M', file: 'musiccore', logo: 'icons/musiccore5.png' },
    p: { key: 'p', name: 'Paramax 5 số (Vol 52)', short: 'Paramax', varName: 'KARAOKE_DATA_P', file: 'paramax', logo: 'icons/paramax5.png' },
    c: { key: 'c', name: 'California 6 số', short: 'California', varName: 'KARAOKE_DATA_C', file: 'california', logo: 'icons/california6.png' },
    v: { key: 'v', name: 'Việt KTV 6 số', short: 'Việt KTV', varName: 'KARAOKE_DATA_V', file: 'vietktv', logo: 'icons/vietktv6.png' },
    t: { key: 't', name: 'Vitek VTB', short: 'Vitek VTB', varName: 'KARAOKE_DATA_T', file: 'vitek', logo: 'icons/vitekvtb6.png' },
    dh: { key: 'dh', name: 'Đông Hải KTV (Vol 83B)', short: 'Đông Hải', varName: 'KARAOKE_DATA_DH', file: 'donghai', logo: 'icons/DONGHAI.jpg' }
  };

  const CURRENT_APP_VERSION = '2.4.0';

  const GENRE_NAMES = {
    0: 'Khác',
    1: 'Nhạc Trẻ',
    2: 'Trữ Tình - Bolero',
    3: 'Quê Hương - Cổ Nhạc',
    4: 'Tiền Chiến - Trịnh',
    5: 'Thiếu Nhi'
  };

  // Popular Artists for Quick Author/Singer Filter
  const POPULAR_ARTISTS = [
    'Trịnh Công Sơn', 'Lam Phương', 'Vũ Thành An', 'Trần Thiện Thanh', 
    'Anh Bằng', 'Phạm Duy', 'Ngô Thụy Miên', 'Nguyễn Văn Chung', 
    'Khắc Việt', 'Thái Thịnh', 'Đức Huy', 'Quốc Dũng', 
    'Sơn Tùng M-TP', 'Đan Trường', 'Cẩm Ly', 'Như Quỳnh', 
    'Quang Lê', 'Tuấn Hưng', 'Phi Nhung', 'Lệ Quyên', 'Mỹ Tâm'
  ];

  // State
  const state = {
    company: 'a',
    theme: localStorage.getItem('karaoke_theme_v1') || 'dark',
    viewMode: localStorage.getItem('karaoke_view_mode_v1') || 'card', // 'card', 'list', 'grid'
    activeActivity: 'search', // 'search', 'fav', 'history', 'utilities'
    dataCache: {},
    indexCache: {},
    lyricsCache: {},
    filteredList: [],
    renderedCount: 0,
    batchSize: 60,
    currentFilter: 'all',
    currentVol: '',
    selectedAuthor: '',
    currentSort: 'maso_asc',
    searchQuery: '',
    favSearchQuery: '',
    favCompanyFilter: 'all',
    currentSong: null,
    favorites: loadFavorites(),
    history: loadHistory(),
    pwaPrompt: null,
    fontSizeLevel: 1,
    // Update State
    installedVersion: localStorage.getItem('karaoke_installed_version') || '2.1.0'
  };

  const FONT_SIZES = ['0.88rem', '1rem', '1.18rem', '1.38rem'];

  // DOM Elements
  const el = {
    html: document.documentElement,
    body: document.body,
    brandHomeBtn: document.getElementById('brandHomeBtn'),
    btnThemeToggle: document.getElementById('btnThemeToggle'),
    btnMoreMenu: document.getElementById('btnMoreMenu'),

    // Desktop Nav
    pcNavSearch: document.getElementById('pcNavSearch'),
    pcNavFav: document.getElementById('pcNavFav'),
    pcNavHistory: document.getElementById('pcNavHistory'),
    pcNavUtilities: document.getElementById('pcNavUtilities'),
    pcFavBadge: document.getElementById('pcFavBadge'),

    // Mobile Bottom Nav
    navHome: document.getElementById('navHome'),
    navFav: document.getElementById('navFav'),
    navHistory: document.getElementById('navHistory'),
    navMenu: document.getElementById('navMenu'),
    bottomFavBadge: document.getElementById('bottomFavBadge'),

    // Activities
    activitySearch: document.getElementById('activitySearch'),
    activityFavorites: document.getElementById('activityFavorites'),
    activityHistory: document.getElementById('activityHistory'),
    activityUtilities: document.getElementById('activityUtilities'),

    // Search Activity Elements
    searchInput: document.getElementById('searchInput'),
    btnClearSearch: document.getElementById('btnClearSearch'),
    btnVoiceSearch: document.getElementById('btnVoiceSearch'),
    volSelect: document.getElementById('volSelect'),
    btnOpenAuthorModal: document.getElementById('btnOpenAuthorModal'),
    selectedAuthorText: document.getElementById('selectedAuthorText'),
    btnClearAuthorFilter: document.getElementById('btnClearAuthorFilter'),
    btnViewCard: document.getElementById('btnViewCard'),
    btnViewList: document.getElementById('btnViewList'),
    btnViewGrid: document.getElementById('btnViewGrid'),
    filterChips: document.getElementById('filterChips'),
    chipVocal: document.getElementById('chipVocal'),
    chipChorus: document.getElementById('chipChorus'),
    sortSelect: document.getElementById('sortSelect'),
    resultsCount: document.getElementById('resultsCount'),
    songListContainer: document.getElementById('songListContainer'),
    loadingState: document.getElementById('loadingState'),
    emptyState: document.getElementById('emptyState'),
    loadMoreContainer: document.getElementById('loadMoreContainer'),
    btnLoadMore: document.getElementById('btnLoadMore'),
    btnResetFilters: document.getElementById('btnResetFilters'),

    // Favorites Activity Elements
    favScreenCount: document.getElementById('favScreenCount'),
    btnFavExport: document.getElementById('btnFavExport'),
    btnFavCopyCode: document.getElementById('btnFavCopyCode'),
    btnFavOpenImport: document.getElementById('btnFavOpenImport'),
    btnFavClearAll: document.getElementById('btnFavClearAll'),
    favSearchInput: document.getElementById('favSearchInput'),
    btnFavSearchClear: document.getElementById('btnFavSearchClear'),
    favCompanyChips: document.getElementById('favCompanyChips'),
    favListContainer: document.getElementById('favListContainer'),
    favEmptyState: document.getElementById('favEmptyState'),
    btnFavGoSearch: document.getElementById('btnFavGoSearch'),

    // History Activity Elements
    btnHistClearAll: document.getElementById('btnHistClearAll'),
    historyListContainer: document.getElementById('historyListContainer'),
    historyEmptyState: document.getElementById('historyEmptyState'),
    btnHistGoSearch: document.getElementById('btnHistGoSearch'),

    // Utilities Activity Elements
    btnCheckAppUpdate: document.getElementById('btnCheckAppUpdate'),
    btnOpenChangelog: document.getElementById('btnOpenChangelog'),
    appVersionDisplay: document.getElementById('appVersionDisplay'),
    badgeUpdateStatus: document.getElementById('badgeUpdateStatus'),
    btnUtilExport: document.getElementById('btnUtilExport'),
    btnUtilCopy: document.getElementById('btnUtilCopy'),
    btnUtilSelectFile: document.getElementById('btnUtilSelectFile'),
    btnUtilFileInput: document.getElementById('utilFileInput'),
    btnUtilTextInput: document.getElementById('utilTextInput'),
    btnUtilApplyText: document.getElementById('btnUtilApplyText'),
    btnUtilInstallPwa: document.getElementById('btnUtilInstallPwa'),

    // Author Modal Elements
    authorModal: document.getElementById('authorModal'),
    btnCloseAuthorModal: document.getElementById('btnCloseAuthorModal'),
    authorSearchInput: document.getElementById('authorSearchInput'),
    popularAuthorsContainer: document.getElementById('popularAuthorsContainer'),
    authorListContainer: document.getElementById('authorListContainer'),

    // Song Detail Modal
    songDetailModal: document.getElementById('songDetailModal'),
    btnCloseDetailModal: document.getElementById('btnCloseDetailModal'),
    modalCompanyTag: document.getElementById('modalCompanyTag'),
    modalCompanyLogo: document.getElementById('modalCompanyLogo'),
    modalCompanyName: document.getElementById('modalCompanyName'),
    modalSongCode: document.getElementById('modalSongCode'),
    btnCopyModalCode: document.getElementById('btnCopyModalCode'),
    btnCopyModalCodeText: document.getElementById('btnCopyModalCodeText'),
    modalSongTitle: document.getElementById('modalSongTitle'),
    modalSongAuthor: document.getElementById('modalSongAuthor'),
    btnFilterByAuthor: document.getElementById('btnFilterByAuthor'),
    modalVolBadge: document.getElementById('modalVolBadge'),
    modalGenreBadge: document.getElementById('modalGenreBadge'),
    modalLangBadge: document.getElementById('modalLangBadge'),
    btnSingYoutubeModal: document.getElementById('btnSingYoutubeModal'),
    btnToggleFavModal: document.getElementById('btnToggleFavModal'),
    modalFavIcon: document.getElementById('modalFavIcon'),
    modalFavText: document.getElementById('modalFavText'),
    btnGoogleLyricsModal: document.getElementById('btnGoogleLyricsModal'),
    modalIntroText: document.getElementById('modalIntroText'),
    lyricsFontResizer: document.getElementById('lyricsFontResizer'),
    btnFontDec: document.getElementById('btnFontDec'),
    btnFontInc: document.getElementById('btnFontInc'),
    modalFullLyricsContainer: document.getElementById('modalFullLyricsContainer'),
    btnLoadFullLyrics: document.getElementById('btnLoadFullLyrics')
  };

  // ========================================================================
  // 1. SWEETALERT2 NOTIFICATION TOASTS
  // ========================================================================

  function showAppToast(message, icon = 'success') {
    if (typeof Swal !== 'undefined') {
      const isDark = state.theme === 'dark';
      Swal.mixin({
        toast: true,
        position: window.innerWidth >= 900 ? 'top-end' : 'bottom',
        showConfirmButton: false,
        timer: 2000,
        timerProgressBar: false,
        background: isDark ? '#1e293b' : '#ffffff',
        color: isDark ? '#f8fafc' : '#0f172a',
        customClass: {
          popup: 'swal-toast-custom'
        }
      }).fire({
        icon,
        title: message
      });
    }
  }

  // ========================================================================
  // 2. THEME & VIEW MODE TOGGLE
  // ========================================================================

  function applyTheme(theme) {
    state.theme = theme;
    el.html.dataset.theme = theme;
    localStorage.setItem('karaoke_theme_v1', theme);
  }

  function toggleTheme() {
    const nextTheme = state.theme === 'dark' ? 'light' : 'dark';
    applyTheme(nextTheme);
    showAppToast(`Đã chuyển sang giao diện ${nextTheme === 'dark' ? 'Tối 🌙' : 'Sáng ☀️'}`, 'info');
  }

  function applyViewMode(mode) {
    state.viewMode = mode;
    localStorage.setItem('karaoke_view_mode_v1', mode);

    [el.songListContainer, el.favListContainer, el.historyListContainer].forEach(container => {
      if (container) {
        container.classList.remove('view-card', 'view-list', 'view-grid');
        container.classList.add(`view-${mode}`);
      }
    });

    [el.btnViewCard, el.btnViewList, el.btnViewGrid].forEach(btn => {
      if (btn) btn.classList.toggle('active', btn.dataset.view === mode);
    });

    if (state.activeActivity === 'search') renderResultsBatch(true);
    if (state.activeActivity === 'fav') renderFavoritesActivity();
    if (state.activeActivity === 'history') renderHistoryActivity();
  }

  // ========================================================================
  // 3. ANDROID ACTIVITY SCREEN SWITCHER
  // ========================================================================

  function switchActivity(activityId) {
    state.activeActivity = activityId;

    // 1. Hide all activity sections and activate the target
    const activities = {
      search: el.activitySearch,
      fav: el.activityFavorites,
      history: el.activityHistory,
      utilities: el.activityUtilities
    };

    Object.entries(activities).forEach(([key, section]) => {
      if (!section) return;
      if (key === activityId) {
        section.style.display = 'block';
        section.classList.add('active');
      } else {
        section.style.display = 'none';
        section.classList.remove('active');
      }
    });

    // 2. Update Mobile Bottom Nav items
    if (el.navHome) el.navHome.classList.toggle('active', activityId === 'search');
    if (el.navFav) el.navFav.classList.toggle('active', activityId === 'fav');
    if (el.navHistory) el.navHistory.classList.toggle('active', activityId === 'history');
    if (el.navMenu) el.navMenu.classList.toggle('active', activityId === 'utilities');

    // 3. Update Desktop PC Nav items
    if (el.pcNavSearch) el.pcNavSearch.classList.toggle('active', activityId === 'search');
    if (el.pcNavFav) el.pcNavFav.classList.toggle('active', activityId === 'fav');
    if (el.pcNavHistory) el.pcNavHistory.classList.toggle('active', activityId === 'history');
    if (el.pcNavUtilities) el.pcNavUtilities.classList.toggle('active', activityId === 'utilities');

    // 4. Render specific activity data
    if (activityId === 'fav') {
      renderFavoritesActivity();
    } else if (activityId === 'history') {
      renderHistoryActivity();
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // ========================================================================
  // 4. VIETNAMESE UTILITIES & SEARCH INDEXING
  // ========================================================================

  function removeVietnameseTones(str) {
    if (!str) return '';
    str = str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    str = str.replace(/[đĐ]/g, 'd');
    return str;
  }

  function getAcronym(str) {
    if (!str) return '';
    const norm = removeVietnameseTones(str).toLowerCase();
    const words = norm.split(/[^a-z0-9]+/i).filter(Boolean);
    return words.map(w => w[0]).join('');
  }

  function buildIndex(rows) {
    const vols = new Set();
    const authorsMap = new Map(); // author name -> count
    const list = new Array(rows.length);

    for (let i = 0; i < rows.length; i++) {
      const row = rows[i];
      const id = row[0];
      const maso = row[1];
      const title = row[2] || '';
      const intro = row[3] || '';
      const author = row[4] || '';
      const lan = row[5];
      const g = row[6];
      const v = row[7];

      if (v) vols.add(v);

      if (author && author.trim()) {
        const cleanAuthor = author.trim();
        authorsMap.set(cleanAuthor, (authorsMap.get(cleanAuthor) || 0) + 1);
      }

      const titleNorm = removeVietnameseTones(title).toLowerCase();
      const authorNorm = removeVietnameseTones(author).toLowerCase();
      const introNorm = removeVietnameseTones(intro).toLowerCase();
      const acr = getAcronym(title);

      const isVocal = (row[8] === 1) || (window.ARIRANG_VOCAL_CODES && window.ARIRANG_VOCAL_CODES.has(maso)) || intro.includes('Có lời ca');
      const isChorus = (row[9] === 1) || (window.ARIRANG_CHORUS_CODES && window.ARIRANG_CHORUS_CODES.has(maso)) || intro.includes('Có tiếng bè') || intro.includes('Có bè');
      const maso6Match = intro.match(/\[Mã HDMI:\s*([0-9a-zA-Z]+)\]/);
      const maso6 = maso6Match ? maso6Match[1] : (row[8] && typeof row[8] === 'string' ? row[8] : null);

      list[i] = {
        row,
        id,
        maso,
        masoStr: maso.toString(),
        title,
        intro,
        author,
        lan,
        g,
        v,
        titleNorm,
        authorNorm,
        introNorm,
        acr,
        isRemix: titleNorm.includes('remix'),
        isForeignVi: author.startsWith('Nhạc') || author.startsWith('NHẠC'),
        isVocal,
        isChorus,
        maso6
      };
    }

    const sortedVols = Array.from(vols).sort((a, b) => b - a);
    const sortedAuthors = Array.from(authorsMap.entries())
      .sort((a, b) => b[1] - a[1])
      .map(entry => entry[0]);

    return { list, vols: sortedVols, authors: sortedAuthors };
  }

  // ========================================================================
  // 5. ZERO-CORS DATA & LYRICS LOADER
  // ========================================================================

  function loadCompanyData(compKey) {
    return new Promise((resolve, reject) => {
      if (state.dataCache[compKey]) {
        resolve(state.dataCache[compKey]);
        return;
      }

      const comp = COMPANIES[compKey];

      if (window[comp.varName] && Array.isArray(window[comp.varName])) {
        state.dataCache[compKey] = window[comp.varName];
        resolve(state.dataCache[compKey]);
        return;
      }

      const script = document.createElement('script');
      script.src = `data/${comp.file}.js`;
      script.async = true;

      script.onload = () => {
        if (window[comp.varName] && Array.isArray(window[comp.varName])) {
          state.dataCache[compKey] = window[comp.varName];
          resolve(state.dataCache[compKey]);
        } else {
          fetchFallback();
        }
      };

      script.onerror = () => fetchFallback();

      function fetchFallback() {
        fetch(`data/${comp.file}.json`)
          .then(res => {
            if (!res.ok) throw new Error('Network error');
            return res.json();
          })
          .then(data => {
            state.dataCache[compKey] = data;
            resolve(data);
          })
          .catch(err => reject(err));
      }

      document.head.appendChild(script);
    });
  }

  function loadLyricChunk(songId) {
    const chunkIdx = Math.floor(songId / 1000);
    return new Promise((resolve) => {
      if (state.lyricsCache[chunkIdx]) {
        resolve(state.lyricsCache[chunkIdx][String(songId)] || null);
        return;
      }

      const varName = `KARAOKE_LYRICS_${chunkIdx}`;
      if (window[varName]) {
        state.lyricsCache[chunkIdx] = window[varName];
        resolve(state.lyricsCache[chunkIdx][String(songId)] || null);
        return;
      }

      const script = document.createElement('script');
      script.src = `data/lyrics/lyrics_${chunkIdx}.js`;
      script.async = true;

      script.onload = () => {
        if (window[varName]) {
          state.lyricsCache[chunkIdx] = window[varName];
          resolve(state.lyricsCache[chunkIdx][String(songId)] || null);
        } else {
          tryFetch();
        }
      };

      script.onerror = () => tryFetch();

      function tryFetch() {
        fetch(`data/lyrics/lyrics_${chunkIdx}.json`)
          .then(res => res.json())
          .then(data => {
            state.lyricsCache[chunkIdx] = data;
            resolve(data[String(songId)] || null);
          })
          .catch(() => resolve(null));
      }

      document.head.appendChild(script);
    });
  }

  // ========================================================================
  // 6. FILTERING & SMART REAL-TIME SEARCH
  // ========================================================================

  function applyFiltersAndSearch() {
    const indexed = state.indexCache[state.company];
    if (!indexed) return;

    const query = state.searchQuery.trim();
    const queryNorm = removeVietnameseTones(query).toLowerCase();
    const isNumberQuery = /^\d+$/.test(query);
    const filter = state.currentFilter;
    const vol = state.currentVol ? parseInt(state.currentVol, 10) : null;
    const authorFilter = state.selectedAuthor.trim().toLowerCase();

    let results = indexed.list;

    // Filter by Category
    if (filter !== 'all') {
      results = results.filter(item => {
        if (filter === 'vocal') return item.isVocal;
        if (filter === 'chorus') return item.isChorus;
        if (filter === 'vi') return item.lan === 0;
        if (filter === 'en') return item.lan === 1;
        if (filter === 'remix') return item.isRemix;
        if (filter === 'foreign_vi') return item.isForeignVi;
        if (filter === 'g1') return item.g === 1;
        if (filter === 'g2') return item.g === 2;
        if (filter === 'g3') return item.g === 3;
        if (filter === 'g4') return item.g === 4;
        if (filter === 'g5') return item.g === 5;
        return true;
      });
    }

    // Filter by Vol
    if (vol !== null) {
      results = results.filter(item => item.v === vol);
    }

    // Filter by Author/Singer
    if (authorFilter) {
      results = results.filter(item => item.authorNorm.includes(authorFilter));
    }

    // Filter by Search Query
    if (queryNorm) {
      if (isNumberQuery) {
        results = results.filter(item => {
          return item.masoStr.startsWith(query) || item.masoStr.includes(query);
        });
      } else {
        results = results.filter(item => {
          if (item.acr.includes(queryNorm)) return true;
          if (item.titleNorm.includes(queryNorm)) return true;
          if (item.authorNorm.includes(queryNorm)) return true;
          if (item.introNorm.includes(queryNorm)) return true;
          return false;
        });

        // Relevance sort
        results.sort((a, b) => {
          const aCode = a.masoStr.startsWith(query) ? 1 : 0;
          const bCode = b.masoStr.startsWith(query) ? 1 : 0;
          if (aCode !== bCode) return bCode - aCode;

          const aAcrExact = a.acr === queryNorm ? 1 : 0;
          const bAcrExact = b.acr === queryNorm ? 1 : 0;
          if (aAcrExact !== bAcrExact) return bAcrExact - aAcrExact;

          const aStart = a.titleNorm.startsWith(queryNorm) ? 1 : 0;
          const bStart = b.titleNorm.startsWith(queryNorm) ? 1 : 0;
          if (aStart !== bStart) return bStart - aStart;

          return 0;
        });
      }
    }

    // Apply Sorting
    if (!queryNorm || isNumberQuery) {
      if (state.currentSort === 'maso_asc') {
        results.sort((a, b) => a.maso - b.maso);
      } else if (state.currentSort === 'maso_desc') {
        results.sort((a, b) => b.maso - a.maso);
      } else if (state.currentSort === 'title_asc') {
        results.sort((a, b) => a.title.localeCompare(b.title, 'vi'));
      } else if (state.currentSort === 'vol_desc') {
        results.sort((a, b) => (b.v || 0) - (a.v || 0));
      }
    }

    state.filteredList = results;
    state.renderedCount = 0;
    renderResultsBatch(true);
  }

  // ========================================================================
  // 7. CARD / LIST / GRID RENDERING
  // ========================================================================

  function highlightMatch(text, query) {
    if (!query || !text) return escapeHtml(text);
    const escaped = escapeHtml(text);
    const queryNorm = removeVietnameseTones(query).toLowerCase();
    const textNorm = removeVietnameseTones(text).toLowerCase();

    const idx = textNorm.indexOf(queryNorm);
    if (idx === -1) return escaped;

    const before = escapeHtml(text.slice(0, idx));
    const match = escapeHtml(text.slice(idx, idx + query.length));
    const after = escapeHtml(text.slice(idx + query.length));
    return `${before}<mark>${match}</mark>${after}`;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function renderSongCardHtml(item, compKey, isFav, query, mode) {
    const titleHtml = highlightMatch(item.title, query);
    const introHtml = highlightMatch(item.intro, query);
    const genreLabel = GENRE_NAMES[item.g] || 'Khác';
    const comp = COMPANIES[compKey];
    const brandBadgeHtml = comp && (state.activeActivity === 'fav' || state.activeActivity === 'history')
      ? `<span class="badge badge-brand"><img src="${comp.logo}" class="badge-brand-img" alt=""> ${comp.short}</span>`
      : '';

    if (mode === 'list') {
      return `
        <div class="card-header-row">
          <div class="card-code-wrap">
            <span class="song-code">${item.maso}</span>
            <button type="button" class="btn-card-copy" data-action="copy" data-code="${item.maso}" title="Sao chép">
              <svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
            </button>
          </div>
        </div>

        <div class="card-body-row">
          <h2 class="song-title">${titleHtml}</h2>
          <div class="song-author">${escapeHtml(item.author || '')}</div>
        </div>

        <div class="card-footer-row">
          <div class="card-badges">
            ${brandBadgeHtml}
            ${item.v ? `<span class="badge badge-vol">V${item.v}</span>` : ''}
            ${item.isVocal ? '<span class="badge badge-vocal">🎤 Vocal</span>' : ''}
            ${item.isChorus ? '<span class="badge badge-chorus">💋 Chorus</span>' : ''}
            ${item.maso6 ? `<span class="badge badge-hdmi">HDMI: ${item.maso6}</span>` : ''}
          </div>
          <button type="button" class="btn-card-yt" data-action="youtube" title="Hát Karaoke ngay trên YouTube">
            ▶️ YouTube
          </button>
          <button type="button" class="btn-fav-toggle ${isFav ? 'is-fav' : ''}" data-action="fav" title="${isFav ? 'Bỏ thích' : 'Yêu thích'}">
            ${isFav ? '❤️' : '🤍'}
          </button>
        </div>
      `;
    } else if (mode === 'grid') {
      return `
        <div class="card-header-row">
          <span class="song-code">${item.maso}</span>
          <div class="card-actions-quick">
            <button type="button" class="btn-fav-toggle ${isFav ? 'is-fav' : ''}" data-action="fav" title="${isFav ? 'Bỏ thích' : 'Yêu thích'}">
              ${isFav ? '❤️' : '🤍'}
            </button>
          </div>
        </div>

        <div class="card-body-row">
          <h2 class="song-title">${titleHtml}</h2>
          <div class="song-author">${escapeHtml(item.author || 'Chưa rõ')}</div>
        </div>

        <div class="card-footer-row" style="justify-content: center; gap: 6px;">
          ${brandBadgeHtml}
          <button type="button" class="btn-card-yt" data-action="youtube" style="padding: 2px 8px; font-size: 0.72rem;">
            ▶️ YouTube
          </button>
          <button type="button" class="btn-card-copy" data-action="copy" data-code="${item.maso}" title="Sao chép">
            📋
          </button>
        </div>
      `;
    } else {
      // FULL CARD VIEW
      return `
        <div class="card-header-row">
          <div class="card-code-wrap">
            <span class="song-code">${item.maso}</span>
            <button type="button" class="btn-card-copy" data-action="copy" data-code="${item.maso}" title="Sao chép mã bài hát">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
            </button>
          </div>
          <div class="card-actions-quick">
            <button type="button" class="btn-fav-toggle ${isFav ? 'is-fav' : ''}" data-action="fav" title="${isFav ? 'Bỏ thích' : 'Yêu thích'}">
              ${isFav ? '❤️' : '🤍'}
            </button>
          </div>
        </div>

        <div class="card-body-row">
          <h2 class="song-title">${titleHtml}</h2>
          <div class="song-author">${escapeHtml(item.author || 'Đang cập nhật')}</div>
          ${item.intro ? `<p class="song-intro">${introHtml}</p>` : ''}
        </div>

        <div class="card-footer-row">
          <div class="card-badges">
            ${brandBadgeHtml}
            ${item.v ? `<span class="badge badge-vol">Vol ${item.v}</span>` : ''}
            ${item.isVocal ? '<span class="badge badge-vocal">🎤 Có lời (Vocal)</span>' : ''}
            ${item.isChorus ? '<span class="badge badge-chorus">💋 Có bè (Chorus)</span>' : ''}
            ${item.maso6 ? `<span class="badge badge-hdmi">HDMI: ${item.maso6}</span>` : ''}
            <span class="badge badge-genre">${genreLabel}</span>
            ${item.lan === 1 ? `<span class="badge badge-lang">Ngoại ngữ</span>` : ''}
          </div>
          <button type="button" class="btn-card-yt" data-action="youtube" title="Hát Karaoke ngay trên YouTube">
            ▶️ Hát YouTube
          </button>
        </div>
      `;
    }
  }

  function renderResultsBatch(reset = false) {
    const total = state.filteredList.length;

    if (total === 0) {
      el.resultsCount.textContent = '0 bài hát';
      el.songListContainer.innerHTML = '';
      el.emptyState.style.display = 'block';
      el.loadMoreContainer.style.display = 'none';
      return;
    }

    el.emptyState.style.display = 'none';
    el.resultsCount.textContent = `Tìm thấy ${total.toLocaleString('vi-VN')} bài hát`;

    if (reset) {
      el.songListContainer.innerHTML = '';
      state.renderedCount = 0;
    }

    const startIndex = state.renderedCount;
    const nextBatch = Math.min(startIndex + state.batchSize, total);
    const fragment = document.createDocumentFragment();

    const compKey = state.company;
    const query = state.searchQuery.trim();
    const mode = state.viewMode;

    for (let i = startIndex; i < nextBatch; i++) {
      const item = state.filteredList[i];
      const isFav = isFavorite(compKey, item.maso);

      const card = document.createElement('article');
      card.className = 'song-card';
      card.dataset.index = i;
      card.setAttribute('role', 'button');
      card.setAttribute('tabindex', '0');

      card.innerHTML = renderSongCardHtml(item, compKey, isFav, query, mode);
      fragment.appendChild(card);
    }

    el.songListContainer.appendChild(fragment);
    state.renderedCount = nextBatch;

    if (state.renderedCount < total) {
      el.loadMoreContainer.style.display = 'block';
      el.btnLoadMore.textContent = `Xem thêm (${state.renderedCount} / ${total.toLocaleString('vi-VN')})`;
    } else {
      el.loadMoreContainer.style.display = 'none';
    }
  }

  // ========================================================================
  // 8. FAVORITES ACTIVITY RENDERING
  // ========================================================================

  function renderFavoritesActivity() {
    const favArray = Object.values(state.favorites).sort((a, b) => b.addedAt - a.addedAt);
    const totalCount = favArray.length;

    if (el.favScreenCount) el.favScreenCount.textContent = `${totalCount} bài`;

    // Filter by query and company
    const query = state.favSearchQuery.trim().toLowerCase();
    const compFilter = state.favCompanyFilter;

    let filtered = favArray;
    if (compFilter !== 'all') {
      filtered = filtered.filter(x => x.company === compFilter);
    }

    if (query) {
      filtered = filtered.filter(x => {
        const titleNorm = removeVietnameseTones(x.title || '').toLowerCase();
        const authorNorm = removeVietnameseTones(x.author || '').toLowerCase();
        const masoStr = (x.maso || '').toString();
        const acr = getAcronym(x.title || '');
        return masoStr.includes(query) || titleNorm.includes(query) || authorNorm.includes(query) || acr.includes(query);
      });
    }

    const container = el.favListContainer;
    container.innerHTML = '';

    if (filtered.length === 0) {
      el.favEmptyState.style.display = 'block';
      return;
    }

    el.favEmptyState.style.display = 'none';
    const fragment = document.createDocumentFragment();
    const mode = state.viewMode;

    filtered.forEach((item, idx) => {
      const card = document.createElement('article');
      card.className = 'song-card';
      card.dataset.favIndex = idx;
      card.setAttribute('role', 'button');
      card.setAttribute('tabindex', '0');

      card.innerHTML = renderSongCardHtml(item, item.company, true, query, mode);

      // Card clicks
      card.addEventListener('click', (e) => {
        const copyBtn = e.target.closest('[data-action="copy"]');
        if (copyBtn) {
          e.stopPropagation();
          copyToClipboard(item.maso, `Đã chép mã số: ${item.maso}`);
          return;
        }

        const ytBtn = e.target.closest('[data-action="youtube"]');
        if (ytBtn) {
          e.stopPropagation();
          openYoutubeDirect(item);
          return;
        }

        const favBtn = e.target.closest('[data-action="fav"]');
        if (favBtn) {
          e.stopPropagation();
          toggleFavorite(item.company, item);
          renderFavoritesActivity();
          return;
        }

        openSongDetail(item, item.company);
      });

      fragment.appendChild(card);
    });

    container.appendChild(fragment);
  }

  // ========================================================================
  // 9. HISTORY ACTIVITY RENDERING
  // ========================================================================

  function renderHistoryActivity() {
    const list = state.history;
    const container = el.historyListContainer;
    container.innerHTML = '';

    if (!list || list.length === 0) {
      el.historyEmptyState.style.display = 'block';
      return;
    }

    el.historyEmptyState.style.display = 'none';
    const fragment = document.createDocumentFragment();
    const mode = state.viewMode;

    list.forEach((item, idx) => {
      const isFav = isFavorite(item.company, item.maso);
      const card = document.createElement('article');
      card.className = 'song-card';
      card.dataset.histIndex = idx;
      card.setAttribute('role', 'button');
      card.setAttribute('tabindex', '0');

      card.innerHTML = renderSongCardHtml(item, item.company, isFav, '', mode);

      card.addEventListener('click', (e) => {
        const copyBtn = e.target.closest('[data-action="copy"]');
        if (copyBtn) {
          e.stopPropagation();
          copyToClipboard(item.maso, `Đã chép mã số: ${item.maso}`);
          return;
        }

        const ytBtn = e.target.closest('[data-action="youtube"]');
        if (ytBtn) {
          e.stopPropagation();
          openYoutubeDirect(item);
          return;
        }

        const favBtn = e.target.closest('[data-action="fav"]');
        if (favBtn) {
          e.stopPropagation();
          const nowFav = toggleFavorite(item.company, item);
          favBtn.classList.toggle('is-fav', nowFav);
          favBtn.textContent = nowFav ? '❤️' : '🤍';
          return;
        }

        openSongDetail(item, item.company);
      });

      fragment.appendChild(card);
    });

    container.appendChild(fragment);
  }

  // ========================================================================
  // 10. SWITCH COMPANY TAB
  // ========================================================================

  async function switchCompany(compKey) {
    if (!COMPANIES[compKey]) return;

    state.company = compKey;
    el.body.dataset.company = compKey;

    document.querySelectorAll('.company-tabs .tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === compKey);
    });

    // Toggle Arirang vocal & chorus chips
    const isArirang = compKey === 'a';
    if (el.chipVocal) el.chipVocal.style.display = isArirang ? 'inline-flex' : 'none';
    if (el.chipChorus) el.chipChorus.style.display = isArirang ? 'inline-flex' : 'none';

    if (!isArirang && (state.currentFilter === 'vocal' || state.currentFilter === 'chorus')) {
      state.currentFilter = 'all';
      document.querySelectorAll('#filterChips .filter-chip').forEach(c => {
        c.classList.toggle('active', c.dataset.filter === 'all');
      });
    }

    // Reset filters
    state.currentVol = '';
    state.selectedAuthor = '';
    updateAuthorFilterDisplay();

    el.loadingState.style.display = 'block';
    el.emptyState.style.display = 'none';
    el.songListContainer.innerHTML = '';
    el.songListContainer.appendChild(el.loadingState);

    try {
      if (!state.indexCache[compKey]) {
        const rawRows = await loadCompanyData(compKey);
        state.indexCache[compKey] = buildIndex(rawRows);
      }

      populateVolSelect(state.indexCache[compKey].vols);
      applyFiltersAndSearch();
    } catch (err) {
      console.error('Failed to load company data:', err);
      showAppToast('Lỗi tải dữ liệu bài hát. Vui lòng thử lại!', 'error');
    } finally {
      el.loadingState.style.display = 'none';
    }
  }

  function populateVolSelect(vols) {
    el.volSelect.innerHTML = '<option value="">Vol: Tất cả</option>';
    vols.forEach(v => {
      const opt = document.createElement('option');
      opt.value = v;
      opt.textContent = `Vol ${v}`;
      el.volSelect.appendChild(opt);
    });
  }

  // ========================================================================
  // 11. AUTHOR & SINGER FILTER MODAL
  // ========================================================================

  function openAuthorModal() {
    const indexed = state.indexCache[state.company];
    const authors = indexed ? indexed.authors : [];

    // Populate popular authors
    el.popularAuthorsContainer.innerHTML = '';
    POPULAR_ARTISTS.forEach(artist => {
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'author-chip';
      chip.textContent = artist;
      chip.onclick = () => selectAuthor(artist);
      el.popularAuthorsContainer.appendChild(chip);
    });

    // Populate author list in this system
    renderAuthorList(authors, '');

    el.authorSearchInput.value = '';
    el.authorModal.classList.add('active');
    el.authorModal.setAttribute('aria-hidden', 'false');
    setTimeout(() => el.authorSearchInput.focus(), 150);
  }

  function closeAuthorModal() {
    el.authorModal.classList.remove('active');
    el.authorModal.setAttribute('aria-hidden', 'true');
  }

  function renderAuthorList(authors, filterText) {
    const container = el.authorListContainer;
    container.innerHTML = '';

    const norm = removeVietnameseTones(filterText).toLowerCase();
    const filtered = norm 
      ? authors.filter(a => removeVietnameseTones(a).toLowerCase().includes(norm))
      : authors.slice(0, 100);

    if (filtered.length === 0) {
      container.innerHTML = `<div style="padding: 14px; text-align: center; color: var(--text-muted); font-size: 0.85rem;">Không tìm thấy tác giả "${escapeHtml(filterText)}"</div>`;
      return;
    }

    filtered.forEach(author => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'author-row-btn';
      btn.innerHTML = `<span>${escapeHtml(author)}</span> <span style="font-size: 0.75rem; color: var(--brand-primary);">Chọn ➔</span>`;
      btn.onclick = () => selectAuthor(author);
      container.appendChild(btn);
    });
  }

  function selectAuthor(authorName) {
    state.selectedAuthor = authorName;
    updateAuthorFilterDisplay();
    closeAuthorModal();
    applyFiltersAndSearch();
    showAppToast(`Lọc theo: "${authorName}"`, 'info');
  }

  function clearAuthorFilter() {
    state.selectedAuthor = '';
    updateAuthorFilterDisplay();
    applyFiltersAndSearch();
  }

  function updateAuthorFilterDisplay() {
    if (state.selectedAuthor) {
      el.selectedAuthorText.textContent = state.selectedAuthor;
      el.btnOpenAuthorModal.classList.add('has-filter');
      el.btnClearAuthorFilter.style.display = 'inline-flex';
    } else {
      el.selectedAuthorText.textContent = 'Tác giả / Ca sĩ';
      el.btnOpenAuthorModal.classList.remove('has-filter');
      el.btnClearAuthorFilter.style.display = 'none';
    }
  }

  // ========================================================================
  // 12. DIRECT YOUTUBE KARAOKE LINK
  // ========================================================================

  function openYoutubeDirect(item) {
    const query = `karaoke ${item.title} ${item.author || ''}`.trim();
    const url = `https://www.youtube.com/results?search_query=${encodeURIComponent(query)}`;
    window.open(url, '_blank', 'noopener,noreferrer');
  }

  // ========================================================================
  // 13. SONG DETAIL MODAL & FULL LYRICS
  // ========================================================================

  function openSongDetail(item, compKey = state.company) {
    state.currentSong = item;
    addToHistory(compKey, item);

    const comp = COMPANIES[compKey] || COMPANIES.a;
    const isFav = isFavorite(compKey, item.maso);

    if (el.modalCompanyLogo) {
      el.modalCompanyLogo.src = comp.logo || 'icons/arirang5.png';
      el.modalCompanyLogo.alt = comp.short;
    }
    if (el.modalCompanyName) {
      el.modalCompanyName.textContent = comp.name;
    } else if (el.modalCompanyTag) {
      el.modalCompanyTag.innerHTML = `
        <img src="${comp.logo}" alt="${comp.short}" class="modal-company-logo">
        <span>${comp.name}</span>
      `;
    }

    el.modalSongCode.textContent = item.maso;
    el.modalSongTitle.textContent = item.title;
    el.modalSongAuthor.textContent = item.author || 'Chưa rõ';

    el.modalVolBadge.textContent = item.v ? `Vol ${item.v}` : 'Vol --';
    el.modalGenreBadge.textContent = GENRE_NAMES[item.g] || 'Khác';
    el.modalLangBadge.textContent = item.lan === 1 ? 'Ngoại ngữ' : 'Tiếng Việt';

    updateModalFavButton(isFav);
    el.modalIntroText.textContent = item.intro || 'Đang cập nhật câu mở đầu bài hát...';

    // Reset lyrics section
    el.lyricsFontResizer.style.display = 'none';
    el.modalFullLyricsContainer.innerHTML = `
      <button type="button" class="btn-full-lyrics" id="btnLoadFullLyrics">
        <img src="icons/menu_lyric.png" style="width: 18px; height: 18px; vertical-align: middle; margin-right: 6px;" alt="">
        <span>Xem toàn bộ lời bài hát (Đầy đủ)</span>
      </button>
    `;

    document.getElementById('btnLoadFullLyrics').onclick = () => handleFullLyricsClick(item, compKey);

    el.songDetailModal.classList.add('active');
    el.songDetailModal.setAttribute('aria-hidden', 'false');
  }

  async function handleFullLyricsClick(item, compKey) {
    // 1. If Arirang offline full lyrics available
    if (compKey === 'a' && item.id <= 12412) {
      el.modalFullLyricsContainer.innerHTML = `
        <div style="text-align: center; padding: 14px; color: var(--text-muted);">
          <div class="spinner" style="width: 24px; height: 24px;"></div>
          <p style="font-size: 0.84rem;">Đang tải lời bài hát đầy đủ...</p>
        </div>
      `;

      try {
        const lyrics = await loadLyricChunk(item.id);
        if (lyrics && lyrics.trim()) {
          el.lyricsFontResizer.style.display = 'inline-flex';
          el.modalFullLyricsContainer.innerHTML = `
            <div class="full-lyrics-text" id="fullLyricsText" style="font-size: ${FONT_SIZES[state.fontSizeLevel]};">
${escapeHtml(lyrics)}
            </div>
            <div class="lyrics-actions-bar">
              <button type="button" class="btn-sheet-secondary" id="btnCopyFullLyrics">📋 Sao chép toàn bộ lời</button>
              <button type="button" class="btn-sheet-secondary" id="btnGoogleLyricsAlt">🌐 Tìm trên Google</button>
            </div>
          `;

          document.getElementById('btnCopyFullLyrics').onclick = () => {
            copyToClipboard(lyrics, 'Đã sao chép lời bài hát!');
          };

          document.getElementById('btnGoogleLyricsAlt').onclick = () => {
            const q = encodeURIComponent(`lời bài hát ${item.title} ${item.author || ''}`.trim());
            window.open(`https://www.google.com/search?q=${q}`, '_blank', 'noopener,noreferrer');
          };
          return;
        }
      } catch (err) {
        console.warn('Lyrics load error:', err);
      }
    }

    // 2. Fallback for other systems or songs without offline lyrics
    const q = encodeURIComponent(`lời bài hát ${item.title} ${item.author || ''}`.trim());
    el.modalFullLyricsContainer.innerHTML = `
      <div style="background: rgba(128,128,128,0.06); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 14px; text-align: center; margin-top: 8px;">
        <p style="font-size: 0.88rem; font-weight: 700; margin-bottom: 4px;">Lời mở đầu:</p>
        <p style="font-style: italic; color: var(--text-secondary); font-size: 0.92rem; margin-bottom: 12px;">"${escapeHtml(item.intro || item.title)}"</p>
        <a href="https://www.google.com/search?q=${q}" target="_blank" rel="noopener noreferrer" class="btn-sheet-primary" style="display: inline-flex; align-items: center; gap: 6px; text-decoration: none;">
          🌐 Tra cứu lời đầy đủ trên Google (1 chạm) ↗
        </a>
      </div>
    `;
  }

  function updateModalFavButton(isFav) {
    if (el.modalFavIcon) el.modalFavIcon.textContent = isFav ? '❤️' : '🤍';
    if (el.modalFavText) el.modalFavText.textContent = isFav ? 'Đã thích' : 'Yêu thích';
    if (el.btnToggleFavModal) {
      el.btnToggleFavModal.style.borderColor = isFav ? '#ef4444' : '';
      el.btnToggleFavModal.style.color = isFav ? '#ef4444' : '';
    }
  }

  function closeDetailModal() {
    el.songDetailModal.classList.remove('active');
    el.songDetailModal.setAttribute('aria-hidden', 'true');
    state.currentSong = null;
  }

  // ========================================================================
  // 14. FAVORITES & HISTORY STORAGE
  // ========================================================================

  function getFavKey(company, maso) {
    return `${company}_${maso}`;
  }

  function loadFavorites() {
    try {
      const raw = localStorage.getItem('karaoke_favorites_v1');
      return raw ? JSON.parse(raw) : {};
    } catch {
      return {};
    }
  }

  function saveFavorites() {
    try {
      localStorage.setItem('karaoke_favorites_v1', JSON.stringify(state.favorites));
      updateFavBadge();
    } catch (e) {
      console.warn('Storage error:', e);
    }
  }

  function isFavorite(company, maso) {
    return Boolean(state.favorites[getFavKey(company, maso)]);
  }

  function toggleFavorite(company, item) {
    const key = getFavKey(company, item.maso);
    if (state.favorites[key]) {
      delete state.favorites[key];
      saveFavorites();
      showAppToast(`Đã bỏ lưu "${item.title}" khỏi yêu thích`, 'info');
      return false;
    } else {
      state.favorites[key] = {
        company,
        id: item.id,
        maso: item.maso,
        title: item.title,
        author: item.author,
        intro: item.intro,
        v: item.v,
        g: item.g,
        lan: item.lan,
        addedAt: Date.now()
      };
      saveFavorites();
      showAppToast(`Đã lưu "${item.title}" vào yêu thích ❤️`, 'success');
      return true;
    }
  }

  function updateFavBadge() {
    const count = Object.keys(state.favorites).length;
    if (el.bottomFavBadge) {
      el.bottomFavBadge.textContent = count;
      el.bottomFavBadge.style.display = count > 0 ? 'inline-block' : 'none';
    }
    if (el.pcFavBadge) {
      el.pcFavBadge.textContent = count;
      el.pcFavBadge.style.display = count > 0 ? 'inline-block' : 'none';
    }
  }

  function loadHistory() {
    try {
      const raw = localStorage.getItem('karaoke_history_v1');
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  function saveHistory() {
    try {
      localStorage.setItem('karaoke_history_v1', JSON.stringify(state.history));
    } catch (e) {
      console.warn('Storage error:', e);
    }
  }

  function addToHistory(company, item) {
    const existingIdx = state.history.findIndex(x => x.company === company && x.maso === item.maso);
    if (existingIdx !== -1) {
      state.history.splice(existingIdx, 1);
    }
    state.history.unshift({
      company,
      id: item.id,
      maso: item.maso,
      title: item.title,
      author: item.author,
      intro: item.intro,
      v: item.v,
      g: item.g,
      lan: item.lan,
      viewedAt: Date.now()
    });
    if (state.history.length > 80) state.history.pop();
    saveHistory();
  }

  // ========================================================================
  // 15. BACKUP & RESTORE ACTIONS
  // ========================================================================

  function exportFavoritesJson() {
    const keys = Object.keys(state.favorites);
    if (keys.length === 0) {
      Swal.fire({
        icon: 'info',
        title: 'Chưa có bài hát',
        text: 'Danh sách yêu thích của bạn đang trống. Hãy thêm một vài bài hát trước khi sao lưu!',
        confirmButtonText: 'Đã hiểu'
      });
      return;
    }

    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(state.favorites, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute('href', dataStr);
    dlAnchor.setAttribute('download', `karaoke_favorites_${new Date().toISOString().slice(0, 10)}.json`);
    dlAnchor.click();

    showAppToast(`Đã xuất file lưu ${keys.length} bài hát!`, 'success');
  }

  function copyBackupText() {
    const keys = Object.keys(state.favorites);
    if (keys.length === 0) {
      Swal.fire({
        icon: 'info',
        title: 'Chưa có bài hát',
        text: 'Danh sách yêu thích đang trống!',
        confirmButtonText: 'Đã hiểu'
      });
      return;
    }

    const json = JSON.stringify(state.favorites);
    copyToClipboard(json, `Đã sao chép mã sao lưu (${keys.length} bài) vào clipboard!`);
  }

  function applyImportJson(jsonStr) {
    try {
      const parsed = JSON.parse(jsonStr);
      if (typeof parsed !== 'object' || parsed === null) throw new Error('Invalid');

      let importedCount = 0;
      Object.entries(parsed).forEach(([k, v]) => {
        if (v && v.company && v.maso) {
          state.favorites[k] = v;
          importedCount++;
        }
      });

      if (importedCount === 0) {
        Swal.fire({
          icon: 'warning',
          title: 'Không tìm thấy bài hát',
          text: 'Dữ liệu không chứa bài hát hợp lệ nào.',
          confirmButtonText: 'Thử lại'
        });
        return;
      }

      saveFavorites();
      renderFavoritesActivity();
      renderResultsBatch(true);

      Swal.fire({
        icon: 'success',
        title: 'Phục hồi thành công!',
        html: `Đã nạp thành công <strong>${importedCount}</strong> bài hát vào danh sách yêu thích!`,
        confirmButtonText: 'Tuyệt vời'
      });
    } catch {
      Swal.fire({
        icon: 'error',
        title: 'Lỗi định dạng!',
        text: 'Mã hoặc file sao lưu không đúng chuẩn JSON. Vui lòng kiểm tra lại!',
        confirmButtonText: 'Đã hiểu'
      });
    }
  }

  async function clearAllFavorites() {
    const count = Object.keys(state.favorites).length;
    if (count === 0) {
      showAppToast('Danh sách yêu thích đang trống!', 'info');
      return;
    }

    const result = await Swal.fire({
      icon: 'warning',
      title: 'Xóa toàn bộ yêu thích?',
      html: `Bạn có chắc muốn xóa tất cả <strong>${count}</strong> bài hát yêu thích? Hành động này không thể hoàn tác.`,
      showCancelButton: true,
      confirmButtonColor: '#ef4444',
      cancelButtonColor: '#64748b',
      confirmButtonText: 'Xóa tất cả',
      cancelButtonText: 'Giữ lại',
      reverseButtons: true
    });

    if (result.isConfirmed) {
      state.favorites = {};
      saveFavorites();
      renderFavoritesActivity();
      renderResultsBatch(true);
      showAppToast('Đã làm trống danh sách yêu thích!', 'success');
    }
  }

  async function clearAllHistory() {
    if (state.history.length === 0) {
      showAppToast('Lịch sử tra cứu đang trống!', 'info');
      return;
    }

    const result = await Swal.fire({
      icon: 'question',
      title: 'Xóa lịch sử tra cứu?',
      text: 'Bạn có muốn làm trống toàn bộ danh sách các bài hát đã mở xem?',
      showCancelButton: true,
      confirmButtonColor: '#ef4444',
      cancelButtonColor: '#64748b',
      confirmButtonText: 'Xóa lịch sử',
      cancelButtonText: 'Hủy',
      reverseButtons: true
    });

    if (result.isConfirmed) {
      state.history = [];
      saveHistory();
      renderHistoryActivity();
      showAppToast('Đã xóa sạch lịch sử tra cứu!', 'success');
    }
  }

  // ========================================================================
  // 16. CLIPBOARD HELPER
  // ========================================================================

  function copyToClipboard(text, successMsg = 'Đã sao chép!') {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(() => {
        showAppToast(successMsg, 'success');
      }).catch(() => fallbackCopy(text, successMsg));
    } else {
      fallbackCopy(text, successMsg);
    }
  }

  function fallbackCopy(text, successMsg) {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      showAppToast(successMsg, 'success');
    } catch {
      showAppToast('Không thể sao chép!', 'error');
    }
    ta.remove();
  }

  // ========================================================================
  // 17. EVENT LISTENERS
  // ========================================================================

  function setupEventListeners() {
    // 1. Brand Home click
    if (el.brandHomeBtn) {
      el.brandHomeBtn.addEventListener('click', () => switchActivity('search'));
    }

    // 2. Theme Toggle
    if (el.btnThemeToggle) {
      el.btnThemeToggle.addEventListener('click', toggleTheme);
    }

    // 3. More Menu (3 dots on Mobile Header)
    if (el.btnMoreMenu) {
      el.btnMoreMenu.addEventListener('click', () => switchActivity('utilities'));
    }

    // 4. View Mode Switcher
    if (el.btnViewCard) el.btnViewCard.addEventListener('click', () => applyViewMode('card'));
    if (el.btnViewList) el.btnViewList.addEventListener('click', () => applyViewMode('list'));
    if (el.btnViewGrid) el.btnViewGrid.addEventListener('click', () => applyViewMode('grid'));

    // 5. Desktop Navigation Tabs (PC Header)
    if (el.pcNavSearch) el.pcNavSearch.addEventListener('click', () => switchActivity('search'));
    if (el.pcNavFav) el.pcNavFav.addEventListener('click', () => switchActivity('fav'));
    if (el.pcNavHistory) el.pcNavHistory.addEventListener('click', () => switchActivity('history'));
    if (el.pcNavUtilities) el.pcNavUtilities.addEventListener('click', () => switchActivity('utilities'));

    // 6. Mobile Bottom Navigation Bar
    if (el.navHome) el.navHome.addEventListener('click', () => switchActivity('search'));
    if (el.navFav) el.navFav.addEventListener('click', () => switchActivity('fav'));
    if (el.navHistory) el.navHistory.addEventListener('click', () => switchActivity('history'));
    if (el.navMenu) el.navMenu.addEventListener('click', () => switchActivity('utilities'));

    // 7. Karaoke Company Tabs (6 Systems)
    document.querySelectorAll('.company-tabs .tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const comp = btn.dataset.tab;
        if (comp && comp !== state.company) {
          switchCompany(comp);
          if (state.activeActivity !== 'search') switchActivity('search');
        }
      });
    });

    // 8. Search Input (Tra cứu chính)
    let searchDebounce = null;
    if (el.searchInput) {
      el.searchInput.addEventListener('input', (e) => {
        const val = e.target.value;
        if (el.btnClearSearch) el.btnClearSearch.style.display = val ? 'flex' : 'none';

        clearTimeout(searchDebounce);
        searchDebounce = setTimeout(() => {
          state.searchQuery = val;
          applyFiltersAndSearch();
        }, 120);
      });
    }

    if (el.btnClearSearch) {
      el.btnClearSearch.addEventListener('click', () => {
        if (el.searchInput) {
          el.searchInput.value = '';
          el.searchInput.focus();
        }
        el.btnClearSearch.style.display = 'none';
        state.searchQuery = '';
        applyFiltersAndSearch();
      });
    }

    // 9. Voice Search
    if (el.btnVoiceSearch) {
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognizer = new SpeechRecognition();
        recognizer.lang = 'vi-VN';
        recognizer.continuous = false;
        recognizer.interimResults = false;

        recognizer.onstart = () => {
          el.btnVoiceSearch.classList.add('listening');
          showAppToast('Đang lắng nghe... Nói tên bài hát!', 'info');
        };

        recognizer.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          if (el.searchInput) el.searchInput.value = transcript;
          if (el.btnClearSearch) el.btnClearSearch.style.display = 'flex';
          state.searchQuery = transcript;
          applyFiltersAndSearch();
          showAppToast(`Đã nhận: "${transcript}"`, 'success');
        };

        recognizer.onerror = () => el.btnVoiceSearch.classList.remove('listening');
        recognizer.onend = () => el.btnVoiceSearch.classList.remove('listening');

        el.btnVoiceSearch.addEventListener('click', () => {
          try { recognizer.start(); } catch { recognizer.stop(); }
        });
      } else {
        el.btnVoiceSearch.addEventListener('click', () => {
          Swal.fire({
            icon: 'info',
            title: 'Tìm giọng nói',
            text: 'Trình duyệt hiện tại chưa hỗ trợ Web Speech API. Bạn vui lòng dùng Google Chrome trên điện thoại để trải nghiệm.',
            confirmButtonText: 'Đã hiểu'
          });
        });
      }
    }

    // 10. Vol and Sort Selectors
    if (el.volSelect) {
      el.volSelect.addEventListener('change', (e) => {
        state.currentVol = e.target.value;
        applyFiltersAndSearch();
      });
    }

    if (el.sortSelect) {
      el.sortSelect.addEventListener('change', (e) => {
        state.currentSort = e.target.value;
        applyFiltersAndSearch();
      });
    }

    // 11. Author Filter Button & Modal
    if (el.btnOpenAuthorModal) {
      el.btnOpenAuthorModal.addEventListener('click', (e) => {
        if (e.target.closest('#btnClearAuthorFilter')) return;
        openAuthorModal();
      });
    }

    if (el.btnClearAuthorFilter) {
      el.btnClearAuthorFilter.addEventListener('click', (e) => {
        e.stopPropagation();
        clearAuthorFilter();
      });
    }

    if (el.btnCloseAuthorModal) {
      el.btnCloseAuthorModal.addEventListener('click', closeAuthorModal);
    }

    if (el.authorModal) {
      el.authorModal.addEventListener('click', (e) => {
        if (e.target === el.authorModal) closeAuthorModal();
      });
    }

    if (el.authorSearchInput) {
      el.authorSearchInput.addEventListener('input', (e) => {
        const indexed = state.indexCache[state.company];
        if (indexed) renderAuthorList(indexed.authors, e.target.value);
      });
    }

    // 12. Genre Filter Chips
    if (el.filterChips) {
      el.filterChips.addEventListener('click', (e) => {
        const chip = e.target.closest('.filter-chip');
        if (!chip) return;

        document.querySelectorAll('#filterChips .filter-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');

        state.currentFilter = chip.dataset.filter;
        applyFiltersAndSearch();
      });
    }

    // 13. Reset Filters
    if (el.btnResetFilters) {
      el.btnResetFilters.addEventListener('click', () => {
        if (el.searchInput) el.searchInput.value = '';
        if (el.btnClearSearch) el.btnClearSearch.style.display = 'none';
        state.searchQuery = '';
        state.currentFilter = 'all';
        state.currentVol = '';
        state.selectedAuthor = '';
        if (el.volSelect) el.volSelect.value = '';
        updateAuthorFilterDisplay();

        document.querySelectorAll('#filterChips .filter-chip').forEach(c => {
          c.classList.toggle('active', c.dataset.filter === 'all');
        });

        applyFiltersAndSearch();
      });
    }

    // 14. Infinite Scroll & Load More
    if (el.btnLoadMore) el.btnLoadMore.addEventListener('click', () => renderResultsBatch(false));

    window.addEventListener('scroll', () => {
      if (state.activeActivity !== 'search') return;
      if (state.renderedCount >= state.filteredList.length) return;
      const scrollPos = window.innerHeight + window.scrollY;
      const threshold = document.documentElement.scrollHeight - 700;
      if (scrollPos >= threshold) {
        renderResultsBatch(false);
      }
    }, { passive: true });

    // 15. Search Song Card Delegated clicks
    if (el.songListContainer) {
      el.songListContainer.addEventListener('click', (e) => {
        const card = e.target.closest('.song-card');
        if (!card) return;

        const idx = parseInt(card.dataset.index, 10);
        const item = state.filteredList[idx];
        if (!item) return;

        const copyBtn = e.target.closest('[data-action="copy"]');
        if (copyBtn) {
          e.stopPropagation();
          copyToClipboard(item.maso, `Đã chép mã số: ${item.maso}`);
          return;
        }

        const ytBtn = e.target.closest('[data-action="youtube"]');
        if (ytBtn) {
          e.stopPropagation();
          openYoutubeDirect(item);
          return;
        }

        const favBtn = e.target.closest('[data-action="fav"]');
        if (favBtn) {
          e.stopPropagation();
          const nowFav = toggleFavorite(state.company, item);
          favBtn.classList.toggle('is-fav', nowFav);
          favBtn.textContent = nowFav ? '❤️' : '🤍';
          return;
        }

        openSongDetail(item, state.company);
      });
    }

    // 16. Song Detail Modal Events
    if (el.btnCloseDetailModal) el.btnCloseDetailModal.addEventListener('click', closeDetailModal);
    if (el.songDetailModal) {
      el.songDetailModal.addEventListener('click', (e) => {
        if (e.target === el.songDetailModal) closeDetailModal();
      });
    }

    if (el.btnCopyModalCode) {
      el.btnCopyModalCode.addEventListener('click', () => {
        if (!state.currentSong) return;
        copyToClipboard(state.currentSong.maso, `Đã sao chép mã số: ${state.currentSong.maso}`);
        if (el.btnCopyModalCodeText) el.btnCopyModalCodeText.textContent = 'Đã sao chép!';
        setTimeout(() => {
          if (el.btnCopyModalCodeText) el.btnCopyModalCodeText.textContent = 'Sao chép mã';
        }, 1500);
      });
    }

    if (el.btnToggleFavModal) {
      el.btnToggleFavModal.addEventListener('click', () => {
        if (!state.currentSong) return;
        const nowFav = toggleFavorite(state.company, state.currentSong);
        updateModalFavButton(nowFav);
        renderResultsBatch(true);
      });
    }

    if (el.btnSingYoutubeModal) {
      el.btnSingYoutubeModal.addEventListener('click', () => {
        if (!state.currentSong) return;
        openYoutubeDirect(state.currentSong);
      });
    }

    if (el.btnGoogleLyricsModal) {
      el.btnGoogleLyricsModal.addEventListener('click', () => {
        if (!state.currentSong) return;
        const q = encodeURIComponent(`lời bài hát ${state.currentSong.title} ${state.currentSong.author || ''}`.trim());
        window.open(`https://www.google.com/search?q=${q}`, '_blank', 'noopener,noreferrer');
      });
    }

    if (el.btnFilterByAuthor) {
      el.btnFilterByAuthor.addEventListener('click', () => {
        if (!state.currentSong || !state.currentSong.author) return;
        closeDetailModal();
        selectAuthor(state.currentSong.author);
      });
    }

    // Font size controls
    if (el.btnFontDec) {
      el.btnFontDec.addEventListener('click', () => {
        if (state.fontSizeLevel > 0) {
          state.fontSizeLevel--;
          const lyricsEl = document.getElementById('fullLyricsText');
          if (lyricsEl) lyricsEl.style.fontSize = FONT_SIZES[state.fontSizeLevel];
        }
      });
    }

    if (el.btnFontInc) {
      el.btnFontInc.addEventListener('click', () => {
        if (state.fontSizeLevel < FONT_SIZES.length - 1) {
          state.fontSizeLevel++;
          const lyricsEl = document.getElementById('fullLyricsText');
          if (lyricsEl) lyricsEl.style.fontSize = FONT_SIZES[state.fontSizeLevel];
        }
      });
    }

    // 17. Favorites Activity Controls
    if (el.btnFavExport) el.btnFavExport.addEventListener('click', exportFavoritesJson);
    if (el.btnFavCopyCode) el.btnFavCopyCode.addEventListener('click', copyBackupText);
    if (el.btnFavClearAll) el.btnFavClearAll.addEventListener('click', clearAllFavorites);
    if (el.btnFavGoSearch) el.btnFavGoSearch.addEventListener('click', () => switchActivity('search'));

    if (el.btnFavOpenImport) {
      el.btnFavOpenImport.addEventListener('click', () => {
        Swal.fire({
          title: 'Phục hồi danh sách bài hát',
          html: `
            <div style="text-align: left; font-size: 0.88rem;">
              <p style="margin-bottom: 8px;">Dán mã JSON sao lưu của bạn vào ô dưới đây:</p>
              <textarea id="swalImportArea" class="import-area" style="height: 100px; width: 100%;" placeholder="Dán mã JSON..."></textarea>
            </div>
          `,
          showCancelButton: true,
          confirmButtonText: 'Phục hồi ngay',
          cancelButtonText: 'Hủy',
          preConfirm: () => {
            const area = document.getElementById('swalImportArea');
            return area ? area.value.trim() : '';
          }
        }).then(res => {
          if (res.isConfirmed && res.value) {
            applyImportJson(res.value);
          }
        });
      });
    }

    if (el.favSearchInput) {
      el.favSearchInput.addEventListener('input', (e) => {
        state.favSearchQuery = e.target.value;
        if (el.btnFavSearchClear) el.btnFavSearchClear.style.display = e.target.value ? 'inline-flex' : 'none';
        renderFavoritesActivity();
      });
    }

    if (el.btnFavSearchClear) {
      el.btnFavSearchClear.addEventListener('click', () => {
        if (el.favSearchInput) el.favSearchInput.value = '';
        el.btnFavSearchClear.style.display = 'none';
        state.favSearchQuery = '';
        renderFavoritesActivity();
      });
    }

    if (el.favCompanyChips) {
      el.favCompanyChips.addEventListener('click', (e) => {
        const chip = e.target.closest('.filter-chip');
        if (!chip) return;
        document.querySelectorAll('#favCompanyChips .filter-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        state.favCompanyFilter = chip.dataset.favComp || 'all';
        renderFavoritesActivity();
      });
    }

    // 18. History Activity Controls
    if (el.btnHistClearAll) el.btnHistClearAll.addEventListener('click', clearAllHistory);
    if (el.btnHistGoSearch) el.btnHistGoSearch.addEventListener('click', () => switchActivity('search'));

    // 19. Utilities Activity Controls
    if (el.btnUtilExport) el.btnUtilExport.addEventListener('click', exportFavoritesJson);
    if (el.btnUtilCopy) el.btnUtilCopy.addEventListener('click', copyBackupText);

    if (el.btnUtilSelectFile && el.btnUtilFileInput) {
      el.btnUtilSelectFile.addEventListener('click', () => el.btnUtilFileInput.click());
    }

    if (el.btnUtilFileInput) {
      el.btnUtilFileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (evt) => applyImportJson(evt.target.result);
        reader.readAsText(file);
      });
    }

    if (el.btnUtilApplyText && el.btnUtilTextInput) {
      el.btnUtilApplyText.addEventListener('click', () => {
        const text = el.btnUtilTextInput.value.trim();
        if (!text) {
          showAppToast('Vui lòng dán mã JSON vào ô!', 'warning');
          return;
        }
        applyImportJson(text);
      });
    }

    if (el.btnUtilInstallPwa) {
      el.btnUtilInstallPwa.addEventListener('click', () => {
        if (state.pwaPrompt) {
          state.pwaPrompt.prompt();
          state.pwaPrompt.userChoice.then(() => {
            state.pwaPrompt = null;
          });
        } else {
          Swal.fire({
            title: '📱 Cài đặt vào điện thoại / PC',
            html: `
              <div style="text-align: left; font-size: 0.88rem; line-height: 1.6;">
                <p><strong>1. Trên Android (Chrome / Cốc Cốc):</strong> Bấm menu <strong>⋮</strong> ➔ Chọn <strong>"Cài đặt ứng dụng"</strong>.</p>
                <p style="margin-top: 6px;"><strong>2. Trên iOS (Safari):</strong> Bấm nút <strong>Chia sẻ</strong> ➔ Chọn <strong>"Thêm vào Màn hình chính"</strong>.</p>
                <p style="margin-top: 6px;"><strong>3. Trên Máy tính (PC / Chrome):</strong> Bấm vào biểu tượng cài đặt 💻 ở thanh địa chỉ URL.</p>
              </div>
            `,
            confirmButtonText: 'Đã hiểu'
          });
        }
      });
    }

    // 20. App Update Controls
    if (el.btnCheckAppUpdate) {
      el.btnCheckAppUpdate.addEventListener('click', () => checkAppUpdates(true));
    }

    if (el.btnOpenChangelog) {
      el.btnOpenChangelog.addEventListener('click', showChangelogModal);
    }

    // 21. PWA Prompt
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      state.pwaPrompt = e;
    });

    // 22. Keyboard Shortcuts (PC Desktop support)
    window.addEventListener('keydown', (e) => {
      // Escape closes modals
      if (e.key === 'Escape') {
        closeDetailModal();
        closeAuthorModal();
        if (typeof Swal !== 'undefined' && Swal.isVisible()) Swal.close();
        return;
      }

      // If active typing in input, don't trigger global shortcuts
      if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;

      // '/' focuses search
      if (e.key === '/') {
        e.preventDefault();
        if (state.activeActivity !== 'search') switchActivity('search');
        if (el.searchInput) el.searchInput.focus();
        return;
      }

      // 1-8 switches company
      const compKeys = ['a', 'acnos', 'm', 'p', 'c', 'v', 't', 'dh'];
      const num = parseInt(e.key, 10);
      if (num >= 1 && num <= 8) {
        switchCompany(compKeys[num - 1]);
      }
    });
  }

  // ========================================================================
  // 18. IN-APP AUTO-UPDATE NOTIFICATION ENGINE (SYNC VIA SERVER)
  // ========================================================================

  async function checkAppUpdates(isManual = false) {
    if (isManual) {
      Swal.fire({
        title: '🔄 Đang kiểm tra cập nhật...',
        text: 'Đang kết nối tới máy chủ dữ liệu...',
        allowOutsideClick: false,
        didOpen: () => Swal.showLoading()
      });
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 4500);

      // Cache buster ?t=
      const res = await fetch(`version.json?t=${Date.now()}`, {
        cache: 'no-cache',
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (!res.ok) throw new Error('Cannot fetch version.json');
      const data = await res.json();

      const remoteVer = data.version;
      const localVer = localStorage.getItem('karaoke_installed_version') || '2.1.0';

      if (isNewerVersion(remoteVer, localVer)) {
        if (el.badgeUpdateStatus) {
          el.badgeUpdateStatus.textContent = `Có bản mới v${remoteVer}`;
          el.badgeUpdateStatus.classList.add('has-update');
        }
        showUpdateAvailableDialog(data);
      } else {
        if (el.badgeUpdateStatus) {
          el.badgeUpdateStatus.textContent = 'Bản mới nhất';
          el.badgeUpdateStatus.classList.remove('has-update');
        }
        if (isManual) {
          Swal.fire({
            icon: 'success',
            title: 'Bạn đang dùng bản mới nhất!',
            html: `
              <div style="font-size: 0.9rem; line-height: 1.6; text-align: left;">
                <p>✅ Phiên bản: <strong>v${CURRENT_APP_VERSION}</strong></p>
                <p>✅ Kho dữ liệu: <strong>98,000+ bài hát</strong> (7 hệ thống karaoke)</p>
                <p>✅ Đã tích hợp đầy đủ Acnos Vol 62, Arirang Vol 66 (có lời & tiếng bè), MusicCore Vol 102, Paramax Vol 52.</p>
              </div>
            `,
            confirmButtonText: 'Tuyệt vời'
          });
        }
      }
    } catch (err) {
      console.warn('Update check failed (likely offline):', err);
      if (isManual) {
        Swal.fire({
          icon: 'info',
          title: 'Chế độ Ngoại tuyến (Offline)',
          text: 'Không thể kết nối Internet để kiểm tra bản mới. Ứng dụng vẫn hoạt động 100% bình thường với dữ liệu bài hát đã lưu trên thiết bị của bạn!',
          confirmButtonText: 'Đã hiểu'
        });
      }
    }
  }

  function isNewerVersion(remote, local) {
    if (!remote || !local) return false;
    const r = remote.split('.').map(Number);
    const l = local.split('.').map(Number);
    for (let i = 0; i < Math.max(r.length, l.length); i++) {
      const rv = r[i] || 0;
      const lv = l[i] || 0;
      if (rv > lv) return true;
      if (rv < lv) return false;
    }
    return false;
  }

  function showUpdateAvailableDialog(versionData) {
    const changelogHtml = (versionData.changelog || [])
      .map(item => `<li style="margin-bottom: 6px;">${item}</li>`)
      .join('');

    Swal.fire({
      title: '🚀 Đã có Danh mục Bài hát Mới!',
      html: `
        <div style="text-align: left; font-size: 0.88rem; line-height: 1.6;">
          <div style="background: rgba(139, 92, 246, 0.15); border: 1px solid rgba(139, 92, 246, 0.4); padding: 10px 14px; border-radius: 10px; margin-bottom: 12px;">
            <strong style="color: #a78bfa; font-size: 1rem;">Phiên bản v${versionData.version}</strong>
            <div style="font-size: 0.78rem; color: var(--text-secondary);">${versionData.subtitle || ''} (${versionData.buildDate || ''})</div>
          </div>
          <p style="font-weight: 700; margin-bottom: 6px;">Nội dung cập nhật mới:</p>
          <ul style="padding-left: 20px; color: var(--text-secondary);">
            ${changelogHtml}
          </ul>
        </div>
      `,
      showCancelButton: true,
      confirmButtonText: '⚡ Cập nhật ngay',
      cancelButtonText: 'Để sau',
      confirmButtonColor: '#8b5cf6',
      cancelButtonColor: '#64748b',
      reverseButtons: true
    }).then(async (result) => {
      if (result.isConfirmed) {
        performAppUpdate(versionData.version);
      }
    });
  }

  async function performAppUpdate(newVersion) {
    Swal.fire({
      title: '⚡ Đang cập nhật danh mục bài hát...',
      html: `
        <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 14px;">
          Đang làm mới bộ nhớ cache offline và tải dữ liệu bài hát mới nhất...
        </p>
        <div style="height: 6px; width: 100%; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden;">
          <div style="height: 100%; width: 100%; background: linear-gradient(90deg, #ec4899, #8b5cf6); animation: pulseDot 1s infinite;"></div>
        </div>
      `,
      allowOutsideClick: false,
      showConfirmButton: false
    });

    try {
      if ('caches' in window) {
        const cacheKeys = await caches.keys();
        await Promise.all(cacheKeys.map(key => caches.delete(key)));
      }

      localStorage.setItem('karaoke_installed_version', newVersion);

      setTimeout(() => {
        window.location.reload(true);
      }, 1200);
    } catch (e) {
      localStorage.setItem('karaoke_installed_version', newVersion);
      window.location.reload(true);
    }
  }

  function showChangelogModal() {
    Swal.fire({
      title: '📜 Nhật ký Phiên bản v2.4.0',
      html: `
        <div style="text-align: left; font-size: 0.88rem; line-height: 1.6;">
          <div style="background: rgba(6, 182, 212, 0.15); border: 1px solid rgba(6, 182, 212, 0.4); padding: 8px 12px; border-radius: 8px; margin-bottom: 10px;">
            <strong style="color: #06b6d4;">Bản phát hành v2.4.0 - 27/09/2026</strong>
          </div>
          <ul style="padding-left: 20px; color: var(--text-secondary); margin-bottom: 12px;">
            <li><strong>Tích hợp Đông Hải KTV:</strong> Bổ sung trọn bộ 10,976 bài hát từ Vol 82B và Vol 83B mới nhất với mã 6 số chuẩn xác 100%.</li>
            <li><strong>Bài mới Vol 83B:</strong> Cập nhật 151 bài hát mới phát hành (Anh Cứ Đi Đi, Bánh Trôi Nước, Bố Trẻ Con, Bến Sông Chờ Remix,...).</li>
            <li><strong>Phân loại Ca sĩ & Vocal:</strong> Tách biệt 1,659 bài hát có lời ca sĩ (Vocal 🎤), bộ lọc ca sĩ và bài hát theo ngôn ngữ.</li>
            <li><strong>Tự động Đồng bộ (Auto-Update):</strong> Khi có file mới hoặc cấu hình thay đổi trong thư mục, hệ thống tự động phát hiện và nhắc người dùng cập nhật ngay tức thì.</li>
            <li><strong>Xuất Excel hoàn chỉnh:</strong> Đầy đủ 6 sheet phân loại chuyên nghiệp, không trùng lặp và không lệch tên bài hát.</li>
          </ul>
          <div style="font-size: 0.78rem; color: var(--text-muted); text-align: center; border-top: 1px solid var(--border-subtle); padding-top: 8px;">
            Bản quyền thuộc Trần Hoàng Thứ - HoangThuIT
          </div>
        </div>
      `,
      confirmButtonText: 'Đóng'
    });
  }

  // ========================================================================
  // 19. SERVICE WORKER REGISTRATION
  // ========================================================================

  function registerServiceWorker() {
    if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1')) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('sw.js')
          .then((reg) => console.log('ServiceWorker registered:', reg.scope))
          .catch((err) => console.warn('ServiceWorker registration error:', err));
      });
    }
  }

  // ========================================================================
  // 20. BOOTSTRAP APPLICATION
  // ========================================================================

  function init() {
    applyTheme(state.theme);
    applyViewMode(state.viewMode);
    setupEventListeners();
    updateFavBadge();
    registerServiceWorker();

    // Check Auto-Update from Server
    checkAppUpdates(false);

    // Start with Arirang
    switchCompany('a');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
