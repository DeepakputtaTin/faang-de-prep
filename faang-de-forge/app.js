/* ============================================================
   FAANG DE Forge — App Logic v15
   Improvements: LC URLs · GitHub/LinkedIn · Countdown ·
                 Week badges · Mobile hamburger
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

    // ── LeetCode Slug Map ─────────────────────────────────────
    // Maps LC number → URL slug for direct problem links
    const LC_SLUGS = {
        175: 'combine-two-tables',
        176: 'second-highest-salary',
        177: 'nth-highest-salary',
        178: 'rank-scores',
        180: 'consecutive-numbers',
        181: 'employees-earning-more-than-their-managers',
        182: 'duplicate-emails',
        183: 'customers-who-never-order',
        184: 'department-highest-salary',
        185: 'department-top-three-salaries',
        196: 'delete-duplicate-emails',
        197: 'rising-temperature',
        262: 'trips-and-users',
        511: 'game-play-analysis-i',
        512: 'game-play-analysis-ii',
        534: 'game-play-analysis-iii',
        550: 'game-play-analysis-iv',
        569: 'median-employee-salary',
        570: 'managers-with-at-least-5-direct-reports',
        571: 'find-median-given-frequency-of-numbers',
        574: 'winning-candidate',
        577: 'employee-bonus',
        578: 'get-highest-answer-rate-question',
        579: 'find-cumulative-salary-of-an-employee',
        580: 'count-student-number-in-departments',
        584: 'find-customer-referee',
        585: 'investments-in-2016',
        586: 'customer-placing-the-largest-number-of-orders',
        595: 'big-countries',
        596: 'classes-more-than-5-students',
        597: 'friend-requests-i-overall-acceptance-rate',
        601: 'human-traffic-of-stadium',
        602: 'friend-requests-ii-who-has-the-most-friends',
        607: 'sales-person',
        608: 'tree-node',
        610: 'triangle-judgement',
        612: 'shortest-distance-in-a-plane',
        613: 'shortest-distance-in-a-line',
        614: 'second-degree-follower',
        615: 'average-salary-departments-vs-company',
        618: 'students-report-by-geography',
        619: 'biggest-single-number',
        620: 'not-boring-movies',
        626: 'exchange-seats',
        627: 'swap-salary',
        1045: 'customers-who-bought-all-products',
        1050: 'actors-and-directors-who-cooperated-at-least-three-times',
        1068: 'product-sales-analysis-i',
        1069: 'product-sales-analysis-ii',
        1070: 'product-sales-analysis-iii',
        1075: 'project-employees-i',
        1076: 'project-employees-ii',
        1077: 'project-employees-iii',
        1082: 'sales-analysis-i',
        1083: 'sales-analysis-ii',
        1084: 'sales-analysis-iii',
        1097: 'game-play-analysis-v',
        1098: 'unpopular-books',
        1107: 'new-users-daily-count',
        1112: 'highest-grade-for-each-student',
        1113: 'reported-posts',
        1126: 'active-businesses',
        1127: 'user-purchase-platform',
        1132: 'reported-posts-ii',
        1141: 'user-activity-for-the-past-30-days-i',
        1142: 'user-activity-for-the-past-30-days-ii',
        1148: 'article-views-i',
        1149: 'article-views-ii',
        1158: 'market-analysis-i',
        1159: 'market-analysis-ii',
        1164: 'product-price-at-a-given-date',
        1173: 'immediate-food-delivery-i',
        1174: 'immediate-food-delivery-ii',
        1179: 'reformat-department-table',
        1193: 'monthly-transactions-i',
        1194: 'tournament-winners',
        1204: 'last-person-to-fit-in-the-elevator',
        1205: 'monthly-transactions-ii',
        1211: 'queries-quality-and-percentage',
        1212: 'team-scores-in-football-tournament',
        1225: 'report-contiguous-dates',
        1241: 'number-of-comments-per-post',
        1251: 'average-selling-price',
        1264: 'page-recommendations',
        1270: 'all-people-report-to-the-given-manager',
        1280: 'students-and-examinations',
        1285: 'find-the-start-and-end-number-of-continuous-ranges',
        1294: 'weather-type-in-each-country',
        1303: 'find-the-team-size',
        1308: 'running-total-for-different-genders',
        1321: 'restaurant-growth',
        1322: 'ads-performance',
        1327: 'list-the-products-ordered-in-a-period',
        1336: 'number-of-transactions-per-visit',
        1341: 'movie-rating',
        1350: 'students-with-invalid-departments',
        1355: 'activity-participants',
        1364: 'number-of-trusted-contacts-of-a-customer',
        1369: 'get-the-second-most-recent-activity',
        1378: 'replace-employee-id-with-the-unique-identifier',
        1384: 'total-sales-amount-by-year',
        1393: 'capital-gainloss',
        1398: 'customers-who-bought-products-a-and-b-but-not-c',
        1407: 'top-travellers',
        1412: 'find-the-quiet-students-in-all-exams',
        1421: 'npv-queries',
        1435: 'create-a-session-bar-chart',
        1440: 'evaluate-boolean-expression',
        1445: 'apples-oranges',
        1454: 'active-users',
        1459: 'rectangles-area',
        1468: 'calculate-salaries',
        1479: 'sales-by-day-of-the-week',
        1484: 'group-sold-products-by-the-date',
        1495: 'friendly-movies-streamed-last-month',
        1501: 'countries-you-can-safely-invest-in',
        1511: 'customer-order-frequency',
        1517: 'find-users-with-valid-e-mails',
        1527: 'patients-with-a-condition',
        1532: 'the-most-recent-three-orders',
        1543: 'fix-product-name-format',
        1549: 'the-most-recent-orders-for-each-product',
        1555: 'bank-account-summary',
        1565: 'unique-orders-and-customers-per-month',
        1571: 'warehouse-manager',
        1581: 'customer-who-visited-but-did-not-make-any-transactions',
        1587: 'bank-account-summary-ii',
        1596: 'the-most-frequently-ordered-products-for-each-customer',
        1607: 'sellers-with-no-sales',
        1613: 'find-the-missing-ids',
        1623: 'all-valid-triplets-that-can-represent-a-country',
        1633: 'percentage-of-users-attended-a-contest',
        1635: 'hopper-company-queries-i',
        1645: 'hopper-company-queries-ii',
        1651: 'hopper-company-queries-iii',
        1661: 'average-time-of-process-per-machine',
        1667: 'fix-names-in-a-table',
        1677: 'products-worth-over-invoices',
        1683: 'invalid-tweets',
        1693: 'daily-leads-and-partners',
        1699: 'number-of-calls-between-two-persons',
        1709: 'biggest-window-between-visits',
        1715: 'count-apples-and-oranges',
        1729: 'find-followers-count',
        1731: 'the-number-of-employees-which-report-to-each-employee',
        1741: 'find-total-time-spent-by-each-employee',
        1747: 'leetflex-banned-accounts',
        1757: 'recyclable-and-low-fat-products',
        1767: 'find-the-subtasks-that-did-not-execute',
        1777: 'products-price-for-each-store',
        1783: 'grand-slam-titles',
        1789: 'primary-department-for-each-employee',
        1795: 'rearrange-products-table',
        1809: 'ad-free-sessions',
        1811: 'find-interview-candidates',
        1821: 'find-customers-with-positive-revenue-this-year',
        1831: 'maximum-transaction-each-day',
        1841: 'league-statistics',
        1843: 'suspicious-bank-accounts',
        1853: 'convert-date-format',
        1873: 'calculate-special-bonus',
        1875: 'group-employees-of-the-same-salary',
        1890: 'the-latest-login-in-2020',
        1892: 'page-recommendations-ii',
        1907: 'count-salary-categories',
        1934: 'confirmation-rate',
        1939: 'users-that-actively-request-confirmation-messages',
        1949: 'strong-friendship',
        1951: 'all-the-pairs-with-the-maximum-number-of-common-followers',
        1965: 'employees-with-missing-information',
        1972: 'first-and-last-call-on-the-same-day',
        1978: 'employees-whose-manager-left-the-company',
        1988: 'find-cutoff-score-for-each-school',
        1990: 'count-the-number-of-experiments',
        2010: 'the-number-of-seniors-and-juniors-to-join-the-company',
        2020: 'number-of-accounts-that-did-not-stream',
        2026: 'low-quality-problems',
        2041: 'accepted-candidates-from-the-interviews',
        2051: 'the-category-of-each-member-in-the-store',
        2066: 'account-balance',
        2072: 'the-winner-university',
        2084: 'drop-type-1-orders-for-customers-with-type-0-orders',
        2112: 'the-airport-with-the-most-traffic',
        2118: 'build-the-equation',
        2142: 'the-number-of-passengers-in-each-bus-i',
        2153: 'the-number-of-passengers-in-each-bus-ii',
        2159: 'order-two-columns-independently',
        2173: 'longest-winning-streak',
        2175: 'the-change-in-global-rankings',
        2198: 'number-of-single-divisor-triplets',
        2228: 'users-with-two-purchases-within-seven-days',
        2230: 'the-users-that-are-eligible-for-discount',
        2238: 'number-of-times-a-driver-was-a-passenger',
        2252: 'dynamic-pivoting-of-a-table',
        2253: 'dynamic-unpivoting-of-a-table',
        2314: 'the-first-day-of-the-maximum-recorded-degree-in-each-city',
        2324: 'product-sales-analysis-iv',
        2329: 'product-sales-analysis-v',
        2339: 'all-the-matches-of-the-league',
        2356: 'number-of-unique-subjects-taught-by-each-teacher',
        2372: 'calculate-the-influence-of-each-salesperson',
        2377: 'sort-the-olympic-table',
        2388: 'change-null-values-in-a-table-to-the-previous-value',
        2394: 'employees-with-deductions',
        2480: 'form-a-chemical-bond',
        2494: 'merge-overlapping-events-in-the-same-hall',
        2504: 'concatenate-the-name-and-the-profession',
        2510: 'check-if-there-is-a-path-with-equal-number-of-0s-and-1s',
        2513: 'minimize-the-maximum-of-two-arrays',
        2978: 'symmetric-coordinates',
        3059: 'find-all-connected-components-of-a-binary-matrix',
        3103: 'find-trending-hashtags-ii',
        3140: 'consecutive-available-seats-ii',
        3156: 'employee-task-duration-and-concurrent-tasks',
        3166: 'calculate-parking-fees-and-duration',
        3172: 'second-day-verification',
        3182: 'find-top-scoring-students',
        3188: 'find-top-scoring-students-ii',
        3198: 'find-cities-in-each-state',
        3204: 'bitwise-user-permissions-analysis',
        3220: 'odd-and-even-transactions',
        3230: 'customer-purchasing-behavior-analysis',
        3236: 'ceo-subordinate-hierarchy',
        // Python/DSA problems
        1: 'two-sum',
        1: 'two-sum',
        3: 'longest-substring-without-repeating-characters',
        49: 'group-anagrams',
        56: 'merge-intervals',
        57: 'insert-interval',
        76: 'minimum-window-substring',
        125: 'valid-palindrome',
        128: 'longest-consecutive-sequence',
        200: 'number-of-islands',
        206: 'reverse-linked-list',
        207: 'course-schedule',
        208: 'implement-trie-prefix-tree',
        210: 'course-schedule-ii',
        238: 'product-of-array-except-self',
        242: 'valid-anagram',
        268: 'missing-number',
        295: 'find-median-from-data-stream',
        347: 'top-k-frequent-elements',
        380: 'insert-delete-getrandom-o1',
        417: 'pacific-atlantic-water-flow',
        424: 'longest-repeating-character-replacement',
        435: 'non-overlapping-intervals',
        438: 'find-all-anagrams-in-a-string',
        567: 'permutation-in-string',
        621: 'task-scheduler',
        647: 'palindromic-substrings',
        739: 'daily-temperatures',
        752: 'open-the-lock',
        787: 'cheapest-flights-within-k-stops',
        853: 'car-fleet',
        875: 'koko-eating-bananas',
        973: 'k-closest-points-to-origin',
        994: 'rotting-oranges',
        1046: 'last-stone-weight',
        1143: 'longest-common-subsequence',
        1584: 'min-cost-to-connect-all-points',
        1851: 'minimum-interval-to-include-each-query',
    };

    /** Build a LeetCode link given the raw field text like "LC 178" or "LeetCode 1321" */
    function buildLcLink(rawText) {
        if (!rawText || rawText === '—') return '';
        // Extract number(s) from text like "LC 178", "LeetCode #178 - Rank Scores", "178"
        const nums = [...rawText.matchAll(/\b(\d{1,4})\b/g)].map(m => parseInt(m[1]));
        if (!nums.length) return `<div class="lc-badge"><i class="fa-solid fa-code"></i> ${rawText}</div>`;

        const links = nums.map(n => {
            const slug = LC_SLUGS[n];
            const url = slug
                ? `https://leetcode.com/problems/${slug}/`
                : `https://leetcode.com/problemset/?search=${n}`;
            return `<a href="${url}" target="_blank" rel="noreferrer" class="lc-link">LC ${n}</a>`;
        }).join(' ');

        return `<div class="lc-badge"><i class="fa-solid fa-code"></i> ${links} <span class="lc-label">${rawText}</span></div>`;
    }

    // ── State ─────────────────────────────────────────────────
    let studyData = [];
    let state = {
        weeks: {},
        activeWeek: null,
        completedDays: new Set(),
        streak: 0,
    };

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

    // ── Sidebar toggle (desktop + mobile) ────────────────────
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        // On mobile, also toggle a visible class
        sidebar.classList.toggle('mobile-open');
    });

    // Close sidebar on mobile when clicking outside
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768
            && sidebar.classList.contains('mobile-open')
            && !sidebar.contains(e.target)
            && !sidebarToggle.contains(e.target)) {
            sidebar.classList.remove('mobile-open');
        }
    });

    // ── GitHub + LinkedIn buttons in topbar ──────────────────
    const topbarRight = document.querySelector('.topbar-right');
    if (topbarRight) {
        const ghBtn = document.createElement('a');
        ghBtn.href = 'https://github.com/DeepakputtaTin/faang-de-prep';
        ghBtn.target = '_blank';
        ghBtn.rel = 'noreferrer';
        ghBtn.className = 'topbar-icon-btn';
        ghBtn.title = 'View source on GitHub';
        ghBtn.innerHTML = '<i class="fa-brands fa-github"></i>';

        const liBtn = document.createElement('a');
        liBtn.href = 'https://www.linkedin.com/in/deepakputta/';
        liBtn.target = '_blank';
        liBtn.rel = 'noreferrer';
        liBtn.className = 'topbar-icon-btn li-btn';
        liBtn.title = 'Connect on LinkedIn';
        liBtn.innerHTML = '<i class="fa-brands fa-linkedin"></i>';

        // Insert before streak pill
        const streakPill = topbarRight.querySelector('.streak-pill');
        topbarRight.insertBefore(liBtn, streakPill);
        topbarRight.insertBefore(ghBtn, liBtn);
    }

    // ── Interview Countdown ───────────────────────────────────
    const INTERVIEW_DATE_KEY = 'faang_interview_date';

    function buildCountdown() {
        const savedDate = localStorage.getItem(INTERVIEW_DATE_KEY);
        const pod = document.createElement('div');
        pod.className = 'interview-countdown-pod';
        pod.id = 'interview-pod';
        pod.innerHTML = buildCountdownHTML(savedDate);
        // Insert into sidebar after progress pod
        const progressPod = document.querySelector('.progress-pod');
        if (progressPod && progressPod.parentNode) {
            progressPod.parentNode.insertBefore(pod, progressPod.nextSibling);
        }
        bindCountdownEvents(pod);
    }

    function buildCountdownHTML(dateStr) {
        if (!dateStr) {
            return `
                <div class="cd-header">🎯 Interview Date</div>
                <div class="cd-not-set">
                    <input type="date" id="cd-date-input" class="cd-date-input" />
                    <button id="cd-save-btn" class="cd-save-btn">Set Date</button>
                </div>`;
        }
        const target = new Date(dateStr);
        const now = new Date();
        const diff = Math.ceil((target - now) / (1000 * 60 * 60 * 24));
        const label = diff > 0
            ? `<span class="cd-days ${diff <= 14 ? 'urgent' : ''}">${diff}</span><span class="cd-unit">days to go</span>`
            : diff === 0
                ? `<span class="cd-days urgent">Today!</span>`
                : `<span class="cd-days done">Done 🏆</span>`;
        const dateLabel = target.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
        return `
            <div class="cd-header">🎯 Interview Countdown</div>
            <div class="cd-display">
                ${label}
            </div>
            <div class="cd-date-label">${dateLabel} <button id="cd-reset-btn" class="cd-reset-btn" title="Change date">✏️</button></div>`;
    }

    function bindCountdownEvents(pod) {
        pod.addEventListener('click', (e) => {
            if (e.target.id === 'cd-save-btn') {
                const input = pod.querySelector('#cd-date-input');
                if (input && input.value) {
                    localStorage.setItem(INTERVIEW_DATE_KEY, input.value);
                    pod.innerHTML = buildCountdownHTML(input.value);
                    bindCountdownEvents(pod);
                }
            }
            if (e.target.id === 'cd-reset-btn') {
                localStorage.removeItem(INTERVIEW_DATE_KEY);
                pod.innerHTML = buildCountdownHTML(null);
                bindCountdownEvents(pod);
                setTimeout(() => pod.querySelector('#cd-date-input')?.focus(), 50);
            }
        });
    }

    // ── Init ──────────────────────────────────────────────────
    function init() {
        try {
            studyData = studyDataFromJS;
        } catch (e) {
            daysContainer.innerHTML = '<div style="color:red;padding:40px">Failed to load data.js</div>';
            return;
        }

        studyData.forEach(day => {
            const w = day.Week;
            if (!state.weeks[w]) state.weeks[w] = [];
            day.id = `w${w}-${day.Day.toLowerCase()}`;
            state.weeks[w].push(day);
        });

        buildWeekNav();
        buildWeekGrid();
        updateProgress();
        buildCountdown();

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
            const allDone = done === days.length;

            const btn = document.createElement('button');
            btn.className = 'week-btn';
            btn.dataset.week = w;
            btn.innerHTML = `
                <div class="week-btn-left">
                    <span class="week-btn-title">Week ${w} ${allDone ? '🏆' : ''}</span>
                    <span class="week-btn-theme">${theme}</span>
                </div>
                <div class="week-btn-right">
                    <span class="week-badge" data-badge-week="${w}">${done}/${days.length}</span>
                    <i class="fa-solid fa-chevron-right week-caret"></i>
                </div>`;
            btn.addEventListener('click', () => toggleWeek(w));

            const list = document.createElement('div');
            list.className = 'day-nav-list';
            list.id = `day-list-w${w}`;

            days.forEach(day => {
                const isDone = state.completedDays.has(day.id);
                const chip = document.createElement('button');
                chip.className = `day-chip ${isDone ? 'done' : ''}`;
                chip.dataset.dayId = day.id;
                chip.dataset.week = w;
                chip.innerHTML = `
                    <span class="day-chip-day">${day.Day}</span>
                    <span class="day-chip-topic">${day.SpecificTopic || day.Theme || ''}</span>`;
                chip.addEventListener('click', () => {
                    selectDay(day.id, w);
                    // On mobile close sidebar after picking a day
                    if (window.innerWidth <= 768) {
                        sidebar.classList.remove('mobile-open');
                    }
                });
                list.appendChild(chip);
            });

            weekNav.appendChild(btn);
            weekNav.appendChild(list);
        });
    }

    // ── Week themes ───────────────────────────────────────────
    const WEEK_THEMES = {
        1: 'SQL Analytics', 2: 'SQL Optimization', 3: 'Data Modeling',
        4: 'Python Logic', 5: 'Python Systems', 6: 'Storage Internals',
        7: 'Spark Internals', 8: 'Advanced Modeling', 9: 'Quality & Contracts',
        10: 'Orchestration', 11: 'Streaming', 12: 'System Design',
        13: 'Behavioral'
    };

    // ── Week completion badge ─────────────────────────────────
    const WEEK_BADGES = {
        1: 'SQL Analytics Master', 2: 'Query Optimizer',
        3: 'Data Modeling Master', 4: 'Python Pro',
        5: 'Systems Engineer', 6: 'Storage Guru',
        7: 'Spark Expert', 8: 'Modeling Architect',
        9: 'Quality Champion', 10: 'Orchestration Wizard',
        11: 'Streaming Specialist', 12: 'System Designer',
        13: 'FAANG Ready 🚀'
    };

    function checkWeekCompletion(weekNum) {
        const days = state.weeks[weekNum];
        const done = days.filter(d => state.completedDays.has(d.id)).length;
        if (done === days.length) {
            showWeekBadge(weekNum);
        }
    }

    function showWeekBadge(weekNum) {
        // Don't show if already shown this session
        if (document.getElementById(`week-badge-toast-${weekNum}`)) return;
        const toast = document.createElement('div');
        toast.id = `week-badge-toast-${weekNum}`;
        toast.className = 'week-badge-toast';
        toast.innerHTML = `
            <div class="badge-trophy">🏆</div>
            <div class="badge-title">Week ${weekNum} Complete!</div>
            <div class="badge-sub">${WEEK_THEMES[weekNum]} — ${WEEK_BADGES[weekNum]}</div>
            <button class="badge-close" onclick="this.closest('.week-badge-toast').remove()">✕</button>`;
        document.body.appendChild(toast);
        // Auto remove after 6 seconds
        setTimeout(() => toast.remove(), 6000);
    }

    // ── Week overview grid ────────────────────────────────────
    function buildWeekGrid() {
        weekGrid.innerHTML = '';
        Object.keys(state.weeks).forEach(w => {
            const days = state.weeks[w];
            const done = days.filter(d => state.completedDays.has(d.id)).length;
            const pct = Math.round(done / days.length * 100);
            const theme = WEEK_THEMES[w] || days[0]?.Theme || '';
            const allDone = done === days.length;

            const card = document.createElement('div');
            card.className = `week-overview-card ${allDone ? 'woc-complete' : ''}`;
            card.innerHTML = `
                <div class="woc-week">Week ${w} ${allDone ? '🏆' : ''}</div>
                <div class="woc-theme">${theme}</div>
                <div class="woc-bar"><div class="woc-fill" style="width:${pct}%"></div></div>
                <div class="woc-stat">${done}/${days.length} days · ${pct}%</div>`;
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
            l.classList.toggle('expanded', l.id === `day-list-w${w}`);
        });
        state.activeWeek = w;
    }

    // ── Select day ────────────────────────────────────────────
    function selectDay(dayId, weekNum) {
        openWeek(weekNum);

        document.querySelectorAll('.day-chip').forEach(c => {
            c.classList.toggle('active', c.dataset.dayId === dayId);
        });

        crumbWeek.textContent = `Week ${weekNum}`;
        crumbSep.style.display = 'inline';
        crumbDay.style.display = 'inline';

        const idx = studyData.findIndex(d => d.id === dayId);
        if (idx === -1) return;
        const day = studyData[idx];
        crumbDay.textContent = `${day.Day} — ${day.SpecificTopic || day.Theme}`;

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
            </li>`).join('');
        const hintsHtml = hints.map(h => `<div class="hint-row">${h}</div>`).join('');

        // ── LeetCode link (FIXED — direct URL) ───────────────
        const lc = buildLcLink(day.LeetCodeProblem);

        const card = document.createElement('div');
        card.className = `day-card ${isDone ? 'is-done' : ''}`;
        card.id = `card-${day.id}`;

        // Warmup & level content blocks
        const warmupBlock = day.Warmup
            ? `<div class="warmup-block"><span class="warmup-label">☀️ Warmup</span><div class="warmup-text">${day.Warmup}</div></div>` : '';

        const buildLevelHtml = (lvl, icon, label) => {
            if (!lvl) return '';
            const items = Array.isArray(lvl) ? lvl : [lvl];
            return `<div class="level-block">
                <div class="level-label">${icon} ${label}</div>
                ${items.map(i => `<div class="level-item">${i}</div>`).join('')}
            </div>`;
        };

        const level1Html = buildLevelHtml(day.Level1_Foundation, '🟢', 'Level 1 — Foundation');
        const level2Html = buildLevelHtml(day.Level2_Application, '🟡', 'Level 2 — Application');
        const level3Html = buildLevelHtml(day.Level3_Synthesis, '🟠', 'Level 3 — Synthesis');
        const level4Html = buildLevelHtml(day.Level4_FAANG_Scale, '🔴', 'Level 4 — FAANG Scale');

        card.innerHTML = `
          <!-- Card Header -->
          <div class="day-header">
            <div class="day-header-left">
              <div class="day-week-badge">Week ${day.Week} · ${WEEK_THEMES[day.Week] || day.Theme}</div>
              <h2 class="day-title">${day.Day}</h2>
              <div class="day-topic">${day.SpecificTopic || day.Theme || ''}</div>
            </div>
            <label class="mark-done-btn ${isDone ? 'is-done' : ''}" for="done-cb-${day.id}">
              <input type="checkbox" class="day-checkbox" id="done-cb-${day.id}" data-id="${day.id}" ${isDone ? 'checked' : ''}>
              <i class="fa-solid ${isDone ? 'fa-circle-check' : 'fa-circle'}"></i>
              ${isDone ? 'Completed' : 'Mark Done'}
            </label>
          </div>

          ${warmupBlock}

          <!-- Hour 1: Foundation -->
          <div class="hour-block hour-bg-1 hb-1 open" data-block="1">
            <div class="hour-header">
              <div class="hour-icon-wrap h1"><i class="fa-solid fa-seedling"></i></div>
              <div class="hour-meta">
                <div class="hour-title">Hour 1: Foundation & Mental Models</div>
                <div class="hour-sub">Core concepts, analogies, and intuition-building</div>
              </div>
              <i class="fa-solid fa-chevron-down hour-toggle-icon"></i>
            </div>
            <div class="hour-body">
              <div class="hour-content">
                ${level1Html || `<ul class="concepts-list">${conceptsHtml}</ul>`}
              </div>
            </div>
          </div>

          <!-- Hour 2: Application -->
          ${level2Html ? `
          <div class="hour-block hour-bg-2 hb-2" data-block="2">
            <div class="hour-header">
              <div class="hour-icon-wrap h2"><i class="fa-solid fa-code"></i></div>
              <div class="hour-meta">
                <div class="hour-title">Hour 2: Hands-On Implementation</div>
                <div class="hour-sub">Write it, run it, own it</div>
              </div>
              <i class="fa-solid fa-chevron-down hour-toggle-icon"></i>
            </div>
            <div class="hour-body">
              <div class="hour-content">${level2Html}</div>
            </div>
          </div>` : (tasksHtml ? `
          <div class="hour-block hour-bg-2 hb-2" data-block="2">
            <div class="hour-header">
              <div class="hour-icon-wrap h2"><i class="fa-solid fa-code"></i></div>
              <div class="hour-meta">
                <div class="hour-title">Hour 2: Tasks</div>
                <div class="hour-sub">Hands-on practice</div>
              </div>
              <i class="fa-solid fa-chevron-down hour-toggle-icon"></i>
            </div>
            <div class="hour-body">
              <div class="hour-content"><ul class="task-list">${tasksHtml}</ul></div>
            </div>
          </div>` : '')}

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
                ${level3Html || `<ul class="concepts-list">${conceptsHtml}</ul>`}
                ${level4Html}
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
                <div class="practice-block">
                  <div class="practice-label"><i class="fa-solid fa-code"></i> Practice Problem</div>
                  <div class="practice-text">${day.PracticeProblem?.problem || day.ActionItem_Deliverable || 'No problem assigned.'}</div>
                  ${hintsHtml ? `
                    <div class="hints-wrap">
                      <button class="hints-toggle-btn toggle-hints">
                        <i class="fa-solid fa-chevron-down"></i> Show Hints
                      </button>
                      <div class="hints-list">${hintsHtml}</div>
                    </div>` : ''}
                </div>
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
        `;

        daysContainer.appendChild(card);
        attachEvents(card, day, index);
    }

    // ── Event wiring ──────────────────────────────────────────
    function attachEvents(card, day, index) {
        card.querySelectorAll('.hour-header').forEach(hdr => {
            hdr.addEventListener('click', () => {
                hdr.closest('.hour-block').classList.toggle('open');
            });
        });

        card.querySelectorAll('.toggle-hints').forEach(btn => {
            btn.addEventListener('click', () => {
                btn.classList.toggle('open');
                btn.nextElementSibling.classList.toggle('visible');
                const isOpen = btn.classList.contains('open');
                btn.innerHTML = `<i class="fa-solid fa-chevron-${isOpen ? 'up' : 'down'}"></i> ${isOpen ? 'Hide Hints' : 'Show Hints'}`;
            });
        });

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
                    lbl.querySelector('.day-checkbox').addEventListener('change', e => { e.target.checked = false; e.target.dispatchEvent(new Event('change')); });
                    // Check for week completion
                    checkWeekCompletion(day.Week);
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

        const prevBtn = card.querySelector('#btn-prev');
        const nextBtn = card.querySelector('#btn-next');
        if (prevBtn && index > 0) {
            prevBtn.addEventListener('click', () => { const p = studyData[index - 1]; selectDay(p.id, p.Week); });
        }
        if (nextBtn && index < studyData.length - 1) {
            nextBtn.addEventListener('click', () => { const n = studyData[index + 1]; selectDay(n.id, n.Week); });
        }
    }

    function updateSidebarChip(id, done) {
        const chip = document.querySelector(`.day-chip[data-day-id="${id}"]`);
        if (chip) chip.classList.toggle('done', done);
        Object.keys(state.weeks).forEach(w => {
            const days = state.weeks[w];
            const cnt = days.filter(d => state.completedDays.has(d.id)).length;
            const allDone = cnt === days.length;
            const badge = document.querySelector(`[data-badge-week="${w}"]`);
            if (badge) badge.textContent = `${cnt}/${days.length}`;
            // Update week title trophy
            const wBtn = document.querySelector(`.week-btn[data-week="${w}"] .week-btn-title`);
            if (wBtn) wBtn.textContent = `Week ${w} ${allDone ? '🏆' : ''}`;
            if (weekGrid) {
                const cards = weekGrid.querySelectorAll('.week-overview-card');
                if (cards[w - 1]) {
                    const fill = cards[w - 1].querySelector('.woc-fill');
                    const stat = cards[w - 1].querySelector('.woc-stat');
                    const weekLbl = cards[w - 1].querySelector('.woc-week');
                    const pct = Math.round(cnt / days.length * 100);
                    if (fill) fill.style.width = pct + '%';
                    if (stat) stat.textContent = `${cnt}/${days.length} days · ${pct}%`;
                    if (weekLbl) weekLbl.textContent = `Week ${w} ${allDone ? '🏆' : ''}`;
                    cards[w - 1].classList.toggle('woc-complete', allDone);
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

        let streak = 0;
        for (let i = done - 1; i >= 0; i--) {
            if (state.completedDays.has(studyData[i]?.id)) streak++;
            else break;
        }
        state.streak = streak;
        if (streakEl) streakEl.textContent = streak;
    }

    function persist() {
        localStorage.setItem('faangPrepCompleted_v2', JSON.stringify([...state.completedDays]));
    }

    // ── SVG gradient ──────────────────────────────────────────
    const svgEl = document.querySelector('.ring-svg');
    if (svgEl) {
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        defs.innerHTML = `
          <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%"   stop-color="#7c6ffc"/>
            <stop offset="100%" stop-color="#06d6db"/>
          </linearGradient>`;
        svgEl.prepend(defs);
    }

    // ── Boot ──────────────────────────────────────────────────
    init();
});
