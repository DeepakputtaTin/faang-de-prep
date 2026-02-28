/* ============================================================
   FAANG DE Forge — App Logic v11
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {

    // ── Refs ──────────────────────────────────────────────────
    const weekNav = document.getElementById('week-nav');
    const daysContainer = document.getElementById('days-container');
    const welcomeState = document.getElementById('welcome-state');
    const weekGrid = document.getElementById('week-overview-grid');

    const ringFill = document.getElementById('ring-fill');
    const ringPct = document.getElementById('ring-pct');
    const completedEl = document.getElementById('completed-count');
    const streakEl = document.getElementById('streak-count');

    const crumbWeek = document.getElementById('crumb-week');
    const crumbDay = document.getElementById('crumb-day');
    const crumbSep = document.getElementById('crumb-sep');

    const themeBtn = document.getElementById('theme-toggle');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const startBtn = document.getElementById('start-btn');
    const contentScroll = document.getElementById('content-scroll');

    const RING_C = 201.06; // 2πr where r=32

    // ── State ─────────────────────────────────────────────────
    let studyData = [];
    let state = {
        weeks: {},
        activeWeek: null,
        completedDays: new Set(),
        streak: 0,
    };

    // Persist completed days
    const saved = localStorage.getItem('faangPrepCompleted_v2');
    if (saved) {
        try { state.completedDays = new Set(JSON.parse(saved)); } catch (e) { }
    }

    // ── Theme ─────────────────────────────────────────────────
    const savedTheme = localStorage.getItem('faangTheme') || 'dark';
    document.body.dataset.theme = savedTheme;
    updateThemeIcon();

    themeBtn.addEventListener('click', () => {
        const isLight = document.body.dataset.theme === 'light';
        document.body.dataset.theme = isLight ? 'dark' : 'light';
        localStorage.setItem('faangTheme', document.body.dataset.theme);
        updateThemeIcon();
    });

    function updateThemeIcon() {
        const isLight = document.body.dataset.theme === 'light';
        themeBtn.innerHTML = isLight
            ? '<i class="fa-solid fa-moon"></i>'
            : '<i class="fa-solid fa-sun"></i>';
    }

    // ── Sidebar toggle ────────────────────────────────────────
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });

    // ── Init ──────────────────────────────────────────────────
    function init() {
        try {
            studyData = studyDataFromJS;
        } catch (e) {
            daysContainer.innerHTML = '<div style="color:red;padding:40px">Failed to load data.js</div>';
            return;
        }

        // Group by week
        studyData.forEach(day => {
            const w = day.Week;
            if (!state.weeks[w]) state.weeks[w] = [];
            day.id = `w${w}-${day.Day.toLowerCase()}`;
            state.weeks[w].push(day);
        });

        buildWeekNav();
        buildWeekGrid();
        updateProgress();

        // Auto-open week 1
        const firstWeek = Object.keys(state.weeks)[0];
        if (firstWeek) openWeek(firstWeek);
    }

    // ── Sidebar week nav ──────────────────────────────────────
    function buildWeekNav() {
        weekNav.innerHTML = '';
        Object.keys(state.weeks).forEach(w => {
            const days = state.weeks[w];
            const done = days.filter(d => state.completedDays.has(d.id)).length;
            const theme = WEEK_THEMES[w] || days[0]?.Theme || '';

            // Week button
            const btn = document.createElement('button');
            btn.className = 'week-btn';
            btn.dataset.week = w;
            btn.innerHTML = `
        <div class="week-btn-left">
          <i class="fa-solid fa-chevron-right week-caret"></i>
          <div class="week-btn-label">
            <span class="week-btn-num">Week ${w}</span>
            <span class="week-btn-theme">${theme}</span>
          </div>
        </div>
        <span class="w-badge" data-badge-week="${w}">${done}/${days.length}</span>
      `;
            btn.addEventListener('click', () => toggleWeek(w));

            // Day list
            const list = document.createElement('div');
            list.className = 'day-nav-list';
            list.id = `day-list-w${w}`;

            days.forEach(day => {
                const topic = day.SpecificTopic || '';
                const chip = document.createElement('button');
                chip.className = `day-chip ${state.completedDays.has(day.id) ? 'done' : ''}`;
                chip.dataset.dayId = day.id;
                chip.innerHTML = `
          <div class="chip-content">
            <span class="chip-day">${day.Day}</span>
            ${topic ? `<span class="chip-topic">${topic}</span>` : ''}
          </div>
          <i class="fa-solid fa-check chip-check"></i>
        `;
                chip.addEventListener('click', e => { e.stopPropagation(); selectDay(day.id, w); });
                list.appendChild(chip);
            });

            weekNav.appendChild(btn);
            weekNav.appendChild(list);
        });
    }

    // ── Week overview grid (welcome state) ────────────────────
    const WEEK_THEMES = {
        1: 'SQL Analytics', 2: 'SQL Optimization', 3: 'Data Modeling',
        4: 'Python Logic', 5: 'Python Systems', 6: 'Storage Internals',
        7: 'Spark Internals', 8: 'Advanced Modeling', 9: 'Quality & Contracts',
        10: 'Orchestration', 11: 'Streaming', 12: 'System Design',
        13: 'Behavioral'
    };

    function buildWeekGrid() {
        weekGrid.innerHTML = '';
        Object.keys(state.weeks).forEach(w => {
            const days = state.weeks[w];
            const done = days.filter(d => state.completedDays.has(d.id)).length;
            const pct = Math.round(done / days.length * 100);
            const theme = WEEK_THEMES[w] || days[0]?.Theme || '';

            const card = document.createElement('div');
            card.className = 'week-overview-card';
            card.innerHTML = `
        <div class="woc-week">Week ${w}</div>
        <div class="woc-theme">${theme}</div>
        <div class="woc-bar"><div class="woc-fill" style="width:${pct}%"></div></div>
        <div class="woc-stat">${done}/${days.length} days · ${pct}%</div>
      `;
            card.addEventListener('click', () => {
                welcomeState.style.display = 'none';
                openWeek(w);
                selectDay(days[0].id, w);
            });
            weekGrid.appendChild(card);
        });
    }

    startBtn && startBtn.addEventListener('click', () => {
        welcomeState.style.display = 'none';
        const firstWeek = Object.keys(state.weeks)[0];
        if (firstWeek) selectDay(state.weeks[firstWeek][0].id, firstWeek);
    });

    // ── Toggle/Open week ──────────────────────────────────────
    function toggleWeek(w) {
        const btn = document.querySelector(`.week-btn[data-week="${w}"]`);
        const list = document.getElementById(`day-list-w${w}`);
        const expanding = !btn.classList.contains('expanded');

        // Close all
        document.querySelectorAll('.week-btn').forEach(b => b.classList.remove('expanded'));
        document.querySelectorAll('.day-nav-list').forEach(l => l.classList.remove('expanded'));

        if (expanding) {
            btn.classList.add('expanded');
            list.classList.add('expanded');
            if (state.activeWeek !== w) {
                selectDay(state.weeks[w][0].id, w);
            }
        }
    }

    function openWeek(w) {
        document.querySelectorAll('.week-btn').forEach(b => {
            b.classList.toggle('active', b.dataset.week === String(w));
            b.classList.toggle('expanded', b.dataset.week === String(w));
        });
        document.querySelectorAll('.day-nav-list').forEach(l => {
            const match = l.id === `day-list-w${w}`;
            l.classList.toggle('expanded', match);
        });
        state.activeWeek = w;
    }

    // ── Select day ────────────────────────────────────────────
    function selectDay(dayId, weekNum) {
        openWeek(weekNum);

        // Highlight in sidebar
        document.querySelectorAll('.day-chip').forEach(c => {
            c.classList.toggle('active', c.dataset.dayId === dayId);
        });

        // Update breadcrumb
        crumbWeek.textContent = `Week ${weekNum}`;
        crumbSep.style.display = 'inline';
        crumbDay.style.display = 'inline';

        const idx = studyData.findIndex(d => d.id === dayId);
        if (idx === -1) return;
        const day = studyData[idx];
        crumbDay.textContent = `${day.Day} — ${day.SpecificTopic || day.Theme}`;

        // Update AI chatbot context
        if (typeof window.deforgeSetContext === 'function') {
            window.deforgeSetContext(`${day.SpecificTopic || day.Theme} (Week ${day.Week} — ${day.Day})`);
        }

        renderDay(day, idx);
        contentScroll.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // ── Render day ────────────────────────────────────────────
    function renderDay(day, index) {
        welcomeState.style.display = 'none';
        daysContainer.style.display = 'block';
        daysContainer.innerHTML = '';

        const isDone = state.completedDays.has(day.id);
        const isFirst = index === 0;
        const isLast = index === studyData.length - 1;

        // Safely get arrays
        const concepts = Array.isArray(day.KeyConcepts) ? day.KeyConcepts : [day.KeyConcepts || ''];
        const tasks = Array.isArray(day.Tasks) ? day.Tasks : [];
        const hints = day.PracticeProblem?.hints || [];

        const conceptsHtml = concepts.map(c => `<li>${c}</li>`).join('');

        const tasksHtml = tasks.map(t => `
      <li class="task-item">
        <label>
          <input type="checkbox" class="task-cb">
          <div class="task-text rich">${t}</div>
        </label>
      </li>
    `).join('');

        const hintsHtml = hints.map(h => `<div class="hint-row">${h}</div>`).join('');

        const lc = day.LeetCodeProblem && day.LeetCodeProblem !== '—'
            ? `<div class="lc-badge"><i class="fa-solid fa-code"></i> ${day.LeetCodeProblem}</div>` : '';

        const card = document.createElement('div');
        card.className = `day-card ${isDone ? 'is-done' : ''}`;
        card.id = `card-${day.id}`;

        card.innerHTML = `
      <!-- Card Header -->
      <div class="day-header">
        <div class="day-hd-left">
          <div>
            <div style="display:flex;align-items:center;gap:10px">
              <span class="day-label">${day.Day}</span>
              <span class="day-topic">${day.SpecificTopic || day.Theme || 'Study Day'}</span>
            </div>
            <div class="day-theme-tag">Week ${day.Week} · ${day.Theme || ''}</div>
          </div>
        </div>
        <label class="mark-done-btn ${isDone ? 'is-done' : ''}">
          <input type="checkbox" class="day-checkbox" data-id="${day.id}" ${isDone ? 'checked' : ''}>
          <i class="fa-solid ${isDone ? 'fa-circle-check' : 'fa-circle'}"></i>
          ${isDone ? 'Completed' : 'Mark Done'}
        </label>
      </div>

      <!-- Card Body -->
      <div class="day-body">

        <!-- Warm-up -->
        <div class="warmup-strip">
          <div class="warmup-icon">⚡</div>
          <div>
            <div class="warmup-label">Daily Warm-Up</div>
            <div class="warmup-text">${day.Warmup || 'No warm-up defined.'}</div>
          </div>
        </div>

        <!-- Hour 1: Fundamentals -->
        <div class="hour-block hour-bg-1 hb-1 open" data-block="1">
          <div class="hour-header">
            <div class="hour-icon-wrap h1"><i class="fa-solid fa-book-open"></i></div>
            <div class="hour-meta">
              <div class="hour-title">Hour 1: Basic Fundamentals</div>
              <div class="hour-sub">Theory, diagrams, and core mental models</div>
            </div>
            <i class="fa-solid fa-chevron-down hour-toggle-icon"></i>
          </div>
          <div class="hour-body">
            <div class="hour-content">
              <div class="rich">${day.Basics || '<p>No content defined.</p>'}</div>
            </div>
          </div>
        </div>

        <!-- Hour 2: Implementation -->
        ${tasks.length > 0 ? `
        <div class="hour-block hour-bg-2 hb-2" data-block="2">
          <div class="hour-header">
            <div class="hour-icon-wrap h2"><i class="fa-solid fa-terminal"></i></div>
            <div class="hour-meta">
              <div class="hour-title">Hour 2: Step-by-Step Implementation</div>
              <div class="hour-sub">Hands-on coding with full SQL / Python syntax</div>
            </div>
            <i class="fa-solid fa-chevron-down hour-toggle-icon"></i>
          </div>
          <div class="hour-body">
            <div class="hour-content">
              <ul class="task-list">${tasksHtml}</ul>
            </div>
          </div>
        </div>
        ` : ''}

        <!-- Hour 3: Expert Concepts -->
        <div class="hour-block hour-bg-3 hb-3" data-block="3">
          <div class="hour-header">
            <div class="hour-icon-wrap h3"><i class="fa-solid fa-brain"></i></div>
            <div class="hour-meta">
              <div class="hour-title">Hour 3: Expert-Level Concepts & Edge Cases</div>
              <div class="hour-sub">Performance tradeoffs, gotchas, and FAANG-level depth</div>
            </div>
            <i class="fa-solid fa-chevron-down hour-toggle-icon"></i>
          </div>
          <div class="hour-body">
            <div class="hour-content">
              <ul class="concepts-list">${conceptsHtml}</ul>
            </div>
          </div>
        </div>

        <!-- Hour 4: FAANG Problem Solving -->
        <div class="hour-block hour-bg-4 hb-4" data-block="4">
          <div class="hour-header">
            <div class="hour-icon-wrap h4"><i class="fa-solid fa-trophy"></i></div>
            <div class="hour-meta">
              <div class="hour-title">Hour 4: FAANG Problem Solving</div>
              <div class="hour-sub">Practice problem + Boss-level architecture challenge</div>
            </div>
            <i class="fa-solid fa-chevron-down hour-toggle-icon"></i>
          </div>
          <div class="hour-body">
            <div class="hour-content">
              <!-- Practice problem -->
              <div class="practice-block">
                <div class="practice-label"><i class="fa-solid fa-code"></i> Practice Problem</div>
                <div class="practice-text">${day.PracticeProblem?.problem || day.ActionItem_Deliverable || 'No problem assigned.'}</div>
                ${hintsHtml ? `
                  <div class="hints-wrap">
                    <button class="hints-toggle-btn toggle-hints">
                      <i class="fa-solid fa-chevron-down"></i> Show Hints
                    </button>
                    <div class="hints-list">${hintsHtml}</div>
                  </div>
                ` : ''}
              </div>
              <!-- Boss problem -->
              <div class="boss-block">
                <div class="boss-label"><i class="fa-solid fa-dragon"></i> Boss Challenge</div>
                <div class="boss-text">${day.HardProblem || 'No hard problem assigned.'}</div>
                ${lc}
              </div>
            </div>
          </div>
        </div>

        <!-- Navigation -->
        <div class="day-footer">
          <button class="nav-btn" id="btn-prev" ${isFirst ? 'disabled' : ''}>
            <i class="fa-solid fa-arrow-left"></i> Previous
          </button>
          <span style="font-size:12px;color:var(--txt-3)">Day ${index + 1} of ${studyData.length}</span>
          <button class="nav-btn primary" id="btn-next" ${isLast ? 'disabled' : ''}>
            Next <i class="fa-solid fa-arrow-right"></i>
          </button>
        </div>

      </div>
    `;

        daysContainer.appendChild(card);

        // Wire up events
        attachEvents(card, day, index);
    }

    // ── Event wiring ──────────────────────────────────────────
    function attachEvents(card, day, index) {
        // Collapsible hour blocks
        card.querySelectorAll('.hour-header').forEach(hdr => {
            hdr.addEventListener('click', () => {
                const block = hdr.closest('.hour-block');
                block.classList.toggle('open');
            });
        });

        // Hints toggle
        card.querySelectorAll('.toggle-hints').forEach(btn => {
            btn.addEventListener('click', () => {
                btn.classList.toggle('open');
                const list = btn.nextElementSibling;
                list.classList.toggle('visible');
                const isOpen = btn.classList.contains('open');
                btn.innerHTML = `<i class="fa-solid fa-chevron-${isOpen ? 'up' : 'down'}"></i> ${isOpen ? 'Hide Hints' : 'Show Hints'}`;
            });
        });

        // Mark done checkbox
        card.querySelectorAll('.day-checkbox').forEach(box => {
            box.addEventListener('change', e => {
                const id = e.target.dataset.id;
                const lbl = card.querySelector('.mark-done-btn');
                const cardEl = document.getElementById(`card-${id}`);

                if (e.target.checked) {
                    state.completedDays.add(id);
                    cardEl.classList.add('is-done');
                    lbl.classList.add('is-done');
                    lbl.innerHTML = `<input type="checkbox" class="day-checkbox" data-id="${id}" checked> <i class="fa-solid fa-circle-check"></i> Completed`;
                    // re-wire
                    lbl.querySelector('.day-checkbox').addEventListener('change', e => { e.target.checked = false; e.target.dispatchEvent(new Event('change')); });
                } else {
                    state.completedDays.delete(id);
                    cardEl.classList.remove('is-done');
                    lbl.classList.remove('is-done');
                    lbl.innerHTML = `<input type="checkbox" class="day-checkbox" data-id="${id}"> <i class="fa-solid fa-circle"></i> Mark Done`;
                    lbl.querySelector('.day-checkbox').addEventListener('change', e => { e.target.checked = true; e.target.dispatchEvent(new Event('change')); });
                }

                persist();
                updateProgress();
                updateSidebarChip(id, e.target.checked);
            });
        });

        // Prev / Next
        const prevBtn = card.querySelector('#btn-prev');
        const nextBtn = card.querySelector('#btn-next');
        if (prevBtn && index > 0) {
            prevBtn.addEventListener('click', () => {
                const prev = studyData[index - 1];
                selectDay(prev.id, prev.Week);
            });
        }
        if (nextBtn && index < studyData.length - 1) {
            nextBtn.addEventListener('click', () => {
                const next = studyData[index + 1];
                selectDay(next.id, next.Week);
            });
        }
    }

    function updateSidebarChip(id, done) {
        const chip = document.querySelector(`.day-chip[data-day-id="${id}"]`);
        if (chip) chip.classList.toggle('done', done);
        // Update week badge
        Object.keys(state.weeks).forEach(w => {
            const days = state.weeks[w];
            const cnt = days.filter(d => state.completedDays.has(d.id)).length;
            const badge = document.querySelector(`[data-badge-week="${w}"]`);
            if (badge) badge.textContent = `${cnt}/${days.length}`;
            // Update overview grid too
            if (weekGrid) {
                const cards = weekGrid.querySelectorAll('.week-overview-card');
                if (cards[w - 1]) {
                    const fill = cards[w - 1].querySelector('.woc-fill');
                    const stat = cards[w - 1].querySelector('.woc-stat');
                    const pct = Math.round(cnt / days.length * 100);
                    if (fill) fill.style.width = pct + '%';
                    if (stat) stat.textContent = `${cnt}/${days.length} days · ${pct}%`;
                }
            }
        });
    }

    // ── Progress ring ─────────────────────────────────────────
    function updateProgress() {
        const total = studyData.length;
        const done = state.completedDays.size;
        const pct = total === 0 ? 0 : Math.round(done / total * 100);
        const offset = RING_C - (pct / 100) * RING_C;

        ringFill.style.strokeDashoffset = offset;
        ringPct.textContent = pct + '%';
        if (completedEl) completedEl.textContent = done;

        // Streak calculation (consecutive completed days from index 0)
        let streak = 0;
        for (let i = done - 1; i >= 0; i--) {
            if (state.completedDays.has(studyData[i]?.id)) streak++;
            else break;
        }
        state.streak = streak;
        if (streakEl) streakEl.textContent = streak;
    }

    // ── Persist ───────────────────────────────────────────────
    function persist() {
        localStorage.setItem('faangPrepCompleted_v2', JSON.stringify([...state.completedDays]));
    }

    // ── SVG gradient (inline fallback) ───────────────────────
    // Inject defs into the ring SVG for the gradient
    const svgEl = document.querySelector('.ring-svg');
    if (svgEl) {
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        defs.innerHTML = `
      <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%"   stop-color="#7c6ffc"/>
        <stop offset="100%" stop-color="#06d6db"/>
      </linearGradient>
    `;
        svgEl.prepend(defs);
    }

    // ── Boot ──────────────────────────────────────────────────
    init();
});
