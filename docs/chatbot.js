/* ============================================================
   DE Forge AI Chatbot — chatbot.js v14
   Multi-provider: Groq (recommended) | Gemini | OpenRouter
   ============================================================ */
(function () {
    'use strict';

    /* ── Providers ───────────────────────────────────────────── */
    const PROVIDERS = {
        groq: {
            id: 'groq',
            name: 'Groq',
            badge: '⚡ Groq — LLaMA 3.3 70B',
            subtitle: 'Groq · LLaMA 3.3 70B · FAANG coach',
            icon: '⚡',
            free: true,
            limit: '30 rpm',
            keyPrefix: 'gsk_',
            keyHint: 'gsk_…',
            getUrl: () => 'https://api.groq.com/openai/v1/chat/completions',
            buildRequest: (messages, systemTxt) => ({
                model: 'llama-3.3-70b-versatile',
                messages: [{ role: 'system', content: systemTxt }, ...messages],
                max_tokens: 1024,
                temperature: 0.7,
                stream: false,
            }),
            parseReply: (data) => data?.choices?.[0]?.message?.content || '',
            authHeader: (key) => ({ 'Authorization': `Bearer ${key}`, 'Content-Type': 'application/json' }),
            setupSteps: [
                'Go to <a href="https://console.groq.com/keys" target="_blank" rel="noreferrer"><strong>console.groq.com/keys</strong></a>',
                'Sign up free (no credit card) and click <strong>"Create API Key"</strong>',
                'Copy the key (starts with <code>gsk_</code>) and paste below',
            ],
            link: 'https://console.groq.com/keys',
        },
        openrouter: {
            id: 'openrouter',
            name: 'OpenRouter',
            badge: '🔓 OpenRouter — Free Models',
            subtitle: 'OpenRouter · Gemma 3 27B · FAANG coach',
            icon: '🔓',
            free: true,
            limit: '20 rpm',
            keyPrefix: 'sk-or-',
            keyHint: 'sk-or-…',
            getUrl: () => 'https://openrouter.ai/api/v1/chat/completions',
            buildRequest: (messages, systemTxt) => ({
                model: 'google/gemma-3-27b-it:free',
                messages: [{ role: 'system', content: systemTxt }, ...messages],
                max_tokens: 1024,
                temperature: 0.7,
            }),
            parseReply: (data) => data?.choices?.[0]?.message?.content || '',
            authHeader: (key) => ({
                'Authorization': `Bearer ${key}`,
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://localhost:8000',
                'X-Title': 'DE Forge FAANG Prep',
            }),
            setupSteps: [
                'Go to <a href="https://openrouter.ai/keys" target="_blank" rel="noreferrer"><strong>openrouter.ai/keys</strong></a>',
                'Click <strong>"Create Key"</strong> — free account, no credit card',
                'Copy the key (starts with <code>sk-or-</code>) and paste below',
            ],
            link: 'https://openrouter.ai/keys',
        },
        gemini: {
            id: 'gemini',
            name: 'Gemini',
            badge: '🔵 Gemini — Flash Lite',
            subtitle: 'Gemini Flash Lite · FAANG coach',
            icon: '🔵',
            free: true,
            limit: '30 rpm',
            keyPrefix: 'AIza',
            keyHint: 'AIzaSy…',
            getUrl: () => 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent',
            buildRequest: (messages, systemTxt) => ({
                system_instruction: { parts: [{ text: systemTxt }] },
                contents: messages.map(m => ({ role: m.role === 'assistant' ? 'model' : 'user', parts: [{ text: m.content }] })),
                generationConfig: { temperature: 0.7, maxOutputTokens: 1024 },
                safetySettings: [
                    { category: 'HARM_CATEGORY_HARASSMENT', threshold: 'BLOCK_NONE' },
                    { category: 'HARM_CATEGORY_HATE_SPEECH', threshold: 'BLOCK_NONE' },
                    { category: 'HARM_CATEGORY_SEXUALLY_EXPLICIT', threshold: 'BLOCK_NONE' },
                    { category: 'HARM_CATEGORY_DANGEROUS_CONTENT', threshold: 'BLOCK_NONE' },
                ],
            }),
            parseReply: (data) => data?.candidates?.[0]?.content?.parts?.[0]?.text || '',
            authHeader: null, // uses ?key= param instead
            buildUrl: (url, key) => `${url}?key=${key}`,
            setupSteps: [
                'Go to <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer"><strong>aistudio.google.com/app/apikey</strong></a>',
                'Click <strong>"Create API Key"</strong> — free, no credit card',
                'Copy the key (starts with <code>AIza</code>) and paste below',
            ],
            link: 'https://aistudio.google.com/app/apikey',
        },
    };

    /* ── State ────────────────────────────────────────────────── */
    const KEY_STORE = 'deforge_api_key_v2';
    const PROV_STORE = 'deforge_provider_v2';
    const HISTORY_KEY = 'deforge_chat_history';

    let apiKey = localStorage.getItem(KEY_STORE) || '';
    let providerId = localStorage.getItem(PROV_STORE) || 'groq';
    let provider = PROVIDERS[providerId] || PROVIDERS.groq;
    let isOpen = false;
    let isLoading = false;
    let currentCtx = 'FAANG Data Engineering';
    let history = []; // [{role:'user'|'assistant', content}]
    let lastSendTime = 0;

    /* ── Quick prompts ────────────────────────────────────────── */
    const QUICK_PROMPTS = [
        'Explain this topic briefly',
        'Give me a FAANG interview question',
        'What are common mistakes here?',
        'Show me a SQL/Python example',
    ];

    /* ── System prompt ────────────────────────────────────────── */
    function systemPrompt() {
        return `You are "DE Forge AI", an expert FAANG Data Engineering interview coach embedded inside a 13-week prep platform.

Current student context: The student is currently studying: **${currentCtx}**

Your personality and rules:
- You are concise, precise, and practical — answer like a senior DE at FAANG would explain it.
- You ALWAYS give code examples in SQL or Python when relevant.
- Format code blocks with backtick fences (\`\`\`sql or \`\`\`python).
- For complex concepts, use numbered steps or bullet points.
- After answering, ask a short follow-up question to check understanding.
- If asked about something unrelated to Data Engineering, gently redirect.
- Keep responses under 400 words unless the student explicitly asks for more detail.
- When relevant, mention FAANG-specific scale (billions of rows, petabyte lakes, etc.).

Topics you know deeply: SQL window functions, CTEs, query optimization, execution plans, indexes, joins, NULL handling, dimensional modeling, SCDs, normalization, Python hash maps, generators, decorators, file I/O, Parquet/Avro/ORC, S3 partitioning, Delta Lake, Spark Catalyst optimizer, shuffle, broadcast joins, data skew, Kafka pub/sub, consumer groups, exactly-once semantics, Airflow DAGs, XComs, orchestration patterns, data quality contracts, dbt tests, observability, system design patterns (batch ETL, streaming, CDC), back-of-envelope math, and behavioral interview (STAR method, Amazon Leadership Principles).`.trim();
    }

    /* ── Build DOM ────────────────────────────────────────────── */
    function buildUI() {
        const fab = document.createElement('button');
        fab.id = 'chat-fab';
        fab.setAttribute('aria-label', 'Open AI assistant');
        fab.innerHTML = `
      <i class="fa-solid fa-robot fab-icon"></i>
      <i class="fa-solid fa-xmark fab-icon-close"></i>
      <span id="chat-badge"></span>
    `;
        document.body.appendChild(fab);

        const panel = document.createElement('div');
        panel.id = 'chat-panel';
        panel.setAttribute('role', 'dialog');
        panel.setAttribute('aria-label', 'DE Forge AI Chatbot');
        panel.innerHTML = buildPanelHTML();
        document.body.appendChild(panel);

        bindEvents(fab, panel);
        if (apiKey) showChat(panel);
        else showSetup(panel);
    }

    function buildPanelHTML() {
        const provOpts = Object.values(PROVIDERS).map(p => `
          <button class="provider-btn ${p.id === providerId ? 'active' : ''}" data-provider="${p.id}">
            <span class="provider-icon">${p.icon}</span>
            <span class="provider-name">${p.name}</span>
            <span class="provider-limit">${p.limit} free</span>
          </button>
        `).join('');

        return `
      <!-- Header -->
      <div class="chat-header">
        <div class="chat-header-icon"><i class="fa-solid fa-robot"></i></div>
        <div class="chat-header-text">
          <div class="chat-header-title">
            DE Forge AI
            <span class="chat-online-dot"></span>
          </div>
          <div class="chat-header-sub" id="chat-header-sub">${provider.subtitle}</div>
        </div>
        <span class="chat-context-tag" id="chat-ctx-tag">General</span>
        <button class="chat-clear-btn" id="chat-change-key-btn" title="Change provider / API key" style="display:none">
          <i class="fa-solid fa-key"></i>
        </button>
        <button class="chat-clear-btn" id="chat-clear-btn" title="New conversation">
          <i class="fa-solid fa-rotate-right"></i>
        </button>
      </div>

      <!-- Setup screen -->
      <div class="chat-setup" id="chat-setup">
        <div class="chat-setup-icon">🤖</div>
        <h3>Choose your AI Provider</h3>
        <p>All providers are <strong>free</strong> — no credit card needed. Groq is recommended (fastest).</p>

        <div class="provider-picker" id="provider-picker">
          ${provOpts}
        </div>

        <div class="chat-setup-steps" id="provider-steps"></div>

        <input
          type="password"
          id="chat-key-input"
          class="chat-key-input"
          placeholder="${provider.keyHint}"
          autocomplete="off"
          spellcheck="false"
        />
        <div id="chat-key-error" class="chat-error" style="display:none"></div>
        <button class="chat-setup-btn" id="chat-save-key-btn">✓ Save Key &amp; Start Chatting</button>
      </div>

      <!-- Chat area -->
      <div id="chat-body" style="display:none;flex:1;overflow:hidden;display:none;flex-direction:column;">
        <div class="chat-messages" id="chat-messages">
          <div class="chat-empty" id="chat-empty">
            <div class="chat-empty-icon">🤖</div>
            <div class="chat-empty-title">Ask me anything!</div>
            <div class="chat-empty-sub">I'm context-aware — I know what you're studying right now.</div>
          </div>
        </div>
        <div class="chat-input-wrap">
          <div class="chat-quick-btns" id="chat-quick-btns">
            ${QUICK_PROMPTS.map(q => `<button class="quick-btn">${q}</button>`).join('')}
          </div>
          <div class="chat-input-row">
            <textarea
              id="chat-input"
              placeholder="Ask about ${currentCtx}…"
              rows="1"
              maxlength="2000"
            ></textarea>
            <button id="chat-send-btn" aria-label="Send message">
              <i class="fa-solid fa-paper-plane"></i>
            </button>
          </div>
        </div>
      </div>
    `;
    }

    /* ── Show/hide setup vs chat ─────────────────────────────── */
    function showSetup(panel) {
        panel.querySelector('#chat-setup').style.display = 'flex';
        panel.querySelector('#chat-body').style.display = 'none';
        renderProviderSteps(panel);
    }

    function showChat(panel) {
        panel.querySelector('#chat-setup').style.display = 'none';
        const body = panel.querySelector('#chat-body');
        body.style.display = 'flex';
        body.style.flexDirection = 'column';
        body.style.flex = '1';
        body.style.overflow = 'hidden';
        const ckb = panel.querySelector('#chat-change-key-btn');
        if (ckb) ckb.style.display = 'inline-flex';
        updateHeaderSub();
        updateContextTag();
        const saved = localStorage.getItem(HISTORY_KEY);
        if (saved) {
            try { history = JSON.parse(saved); replayHistory(panel); } catch (e) { history = []; }
        }
    }

    function renderProviderSteps(panel) {
        const stepsEl = panel.querySelector('#provider-steps');
        if (!stepsEl) return;
        stepsEl.innerHTML = provider.setupSteps.map((s, i) =>
            `<div class="setup-step"><span class="setup-step-num">${i + 1}</span>${s}</div>`
        ).join('');
        const input = panel.querySelector('#chat-key-input');
        if (input) input.placeholder = provider.keyHint;
    }

    function updateHeaderSub() {
        const el = document.querySelector('#chat-header-sub');
        if (el) el.textContent = provider.subtitle;
    }

    /* ── Bind events ─────────────────────────────────────────── */
    function bindEvents(fab, panel) {
        // FAB toggle
        fab.addEventListener('click', () => {
            isOpen = !isOpen;
            fab.classList.toggle('open', isOpen);
            panel.classList.toggle('open', isOpen);
            if (isOpen) {
                clearBadge();
                setTimeout(() => panel.querySelector('#chat-input')?.focus(), 350);
            }
        });

        // Provider picker
        const picker = panel.querySelector('#provider-picker');
        if (picker) {
            picker.addEventListener('click', e => {
                const btn = e.target.closest('.provider-btn');
                if (!btn) return;
                providerId = btn.dataset.provider;
                provider = PROVIDERS[providerId];
                picker.querySelectorAll('.provider-btn').forEach(b => b.classList.toggle('active', b.dataset.provider === providerId));
                renderProviderSteps(panel);
                const errEl = panel.querySelector('#chat-key-error');
                if (errEl) errEl.style.display = 'none';
                panel.querySelector('#chat-key-input')?.focus();
            });
        }

        // Save key
        panel.querySelector('#chat-save-key-btn')?.addEventListener('click', () => saveKey(panel));
        panel.querySelector('#chat-key-input')?.addEventListener('keydown', e => { if (e.key === 'Enter') saveKey(panel); });

        // Send
        panel.querySelector('#chat-send-btn')?.addEventListener('click', () => sendMessage(panel));
        const textarea = panel.querySelector('#chat-input');
        if (textarea) {
            textarea.addEventListener('keydown', e => {
                if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(panel); }
            });
            textarea.addEventListener('input', () => {
                textarea.style.height = 'auto';
                textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
            });
        }

        // Quick prompts
        panel.querySelector('#chat-quick-btns')?.querySelectorAll('.quick-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const inp = panel.querySelector('#chat-input');
                if (inp) { inp.value = btn.textContent; sendMessage(panel); }
            });
        });

        // Change provider/key button
        panel.querySelector('#chat-change-key-btn')?.addEventListener('click', () => {
            apiKey = '';
            localStorage.removeItem(KEY_STORE);
            history = [];
            localStorage.removeItem(HISTORY_KEY);
            const ckb = panel.querySelector('#chat-change-key-btn');
            if (ckb) ckb.style.display = 'none';
            showSetup(panel);
            setTimeout(() => panel.querySelector('#chat-key-input')?.focus(), 100);
        });

        // Clear chat
        panel.querySelector('#chat-clear-btn')?.addEventListener('click', () => clearChat(panel));

        // Keyboard shortcut
        document.addEventListener('keydown', e => {
            if ((e.ctrlKey || e.metaKey) && e.key === '/') { e.preventDefault(); fab.click(); }
        });
    }

    /* ── Save API key ─────────────────────────────────────────── */
    async function saveKey(panel) {
        const input = panel.querySelector('#chat-key-input');
        const errEl = panel.querySelector('#chat-key-error');
        const key = input?.value?.trim() || '';

        if (!key) { showKeyError(errEl, `⚠️ Please paste your ${provider.name} API key`); return; }
        if (!key.startsWith(provider.keyPrefix)) {
            showKeyError(errEl, `⚠️ ${provider.name} keys start with "${provider.keyPrefix}…" — check you copied the full key`);
            return;
        }

        const btn = panel.querySelector('#chat-save-key-btn');
        if (btn) { btn.textContent = '⏳ Validating…'; btn.disabled = true; }
        if (errEl) errEl.style.display = 'none';

        try {
            const testMsg = [{ role: 'user', content: 'Reply OK in 2 words.' }];
            const res = await callProvider(provider, key, testMsg, 'Reply OK in 2 words.');

            if (!res.ok) {
                const errBody = await res.json().catch(() => ({}));
                const status = res.status;
                const msg = errBody?.error?.message || errBody?.message || '';
                if (status === 401) throw new Error(`❌ Invalid API key. Check you copied the full key from ${provider.name}.`);
                if (status === 403) throw new Error(`❌ Access denied. Make sure your ${provider.name} key has the right permissions.`);
                if (status === 429) {
                    // Key IS valid, just rate limited — accept it
                    apiKey = key;
                    localStorage.setItem(KEY_STORE, apiKey);
                    localStorage.setItem(PROV_STORE, providerId);
                    showChat(panel);
                    setTimeout(() => appendAiMsg(panel, `👋 Key saved! The ${provider.name} API is briefly rate-limited right now — try asking in a moment.`), 200);
                    return;
                }
                throw new Error(`❌ ${provider.name} error ${status}: ${msg || 'Try again.'}`);
            }

            apiKey = key;
            localStorage.setItem(KEY_STORE, apiKey);
            localStorage.setItem(PROV_STORE, providerId);
            showChat(panel);
            setTimeout(() => appendAiMsg(panel, `👋 Hey! I'm **DE Forge AI** powered by **${provider.name}**.\n\nI can see you're studying **${currentCtx}** right now. Ask me anything — definitions, code examples, or a mock interview question. Let's go! 🚀`), 200);
        } catch (e) {
            const msg = e.message?.includes('Failed to fetch')
                ? '❌ Network error — check your internet connection.'
                : (e.message || '❌ Could not validate key. Try again.');
            showKeyError(errEl, msg);
        } finally {
            if (btn) { btn.textContent = '✓ Save Key & Start Chatting'; btn.disabled = false; }
        }
    }

    function showKeyError(errEl, msg) {
        if (!errEl) return;
        errEl.innerHTML = msg;
        errEl.style.display = 'block';
        errEl.style.color = '#ff6b6b';
    }

    /* ── Unified provider call ─────────────────────────────────── */
    async function callProvider(prov, key, messages, sysText) {
        const url = prov.buildUrl ? prov.buildUrl(prov.getUrl(), key) : prov.getUrl();
        const headers = prov.authHeader ? prov.authHeader(key) : { 'Content-Type': 'application/json' };
        const body = prov.buildRequest(messages, sysText);
        return fetch(url, { method: 'POST', headers, body: JSON.stringify(body) });
    }

    /* ── Send message ─────────────────────────────────────────── */
    async function sendMessage(panel) {
        const input = panel.querySelector('#chat-input');
        const text = input?.value?.trim();
        if (!text || isLoading) return;

        const now = Date.now();
        if (now - lastSendTime < 500) return;
        lastSendTime = now;

        input.value = '';
        input.style.height = 'auto';
        hideEmpty(panel);
        appendUserMsg(panel, text);
        showTyping(panel);

        // Build OpenAI-compat message history
        const msgs = history.map(h => ({ role: h.role, content: h.content }));
        msgs.push({ role: 'user', content: text });
        history.push({ role: 'user', content: text });
        isLoading = true;

        const sendBtn = panel.querySelector('#chat-send-btn');
        if (sendBtn) sendBtn.disabled = true;

        let reply = null;
        let errorMsg = null;

        try {
            const res = await callProvider(provider, apiKey, msgs, systemPrompt());

            if (!res.ok) {
                const errBody = await res.json().catch(() => ({}));
                const status = res.status;
                const rawMsg = errBody?.error?.message || errBody?.message || '';

                if (status === 429) {
                    // Rate limited — try once more after 15s countdown
                    updateTyping(panel, '⏳ Rate limit hit — waiting 15s then retrying…');
                    await countdown(panel, 15);
                    const res2 = await callProvider(provider, apiKey, msgs, systemPrompt());
                    if (!res2.ok) {
                        const e2 = await res2.json().catch(() => ({}));
                        errorMsg = `⏳ Still rate limited. Wait a minute then try again. (${provider.name} free tier: ${provider.limit})`;
                    } else {
                        const data2 = await res2.json();
                        reply = provider.parseReply(data2);
                    }
                } else if (status === 401 || status === 403) {
                    errorMsg = `❌ API key rejected. Click the 🔑 icon to enter a new key.`;
                } else {
                    errorMsg = `⚠️ ${provider.name} error ${status}: ${rawMsg || 'Try again.'}`;
                }
            } else {
                const data = await res.json();
                reply = provider.parseReply(data);
            }
        } catch (fetchErr) {
            errorMsg = '❌ Network error — check your internet connection.';
        }

        removeTyping(panel);

        if (reply) {
            appendAiMsg(panel, reply);
            history.push({ role: 'assistant', content: reply });
            if (history.length > 40) history = history.slice(-40);
            localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
            if (!isOpen) showBadge();
        } else if (errorMsg) {
            // Remove the user message from history since it wasn't answered
            history.pop();
            appendErrorMessage(panel, errorMsg);
        }

        isLoading = false;
        if (sendBtn) sendBtn.disabled = false;
        panel.querySelector('#chat-input')?.focus();
    }

    /* ── Countdown helper ─────────────────────────────────────── */
    function updateTyping(panel, text) {
        const dots = panel.querySelector('#typing-row .typing-dots');
        if (!dots) return;
        dots.textContent = text;
        Object.assign(dots.style, { fontFamily: 'Inter, sans-serif', fontSize: '12px', color: '#9898b8', padding: '6px 12px', background: 'none', gap: '0' });
    }

    async function countdown(panel, seconds) {
        for (let s = seconds; s > 0; s--) {
            updateTyping(panel, `⏳ Retrying in ${s}s…`);
            await new Promise(r => setTimeout(r, 1000));
        }
        // Restore dots
        const dots = panel.querySelector('#typing-row .typing-dots');
        if (dots) { dots.textContent = ''; dots.removeAttribute('style'); dots.innerHTML = '<span></span><span></span><span></span>'; }
    }

    /* ── Message renderers ────────────────────────────────────── */
    function appendUserMsg(panel, text) {
        const msgs = panel.querySelector('#chat-messages');
        msgs.appendChild(createMsg('user', escapeHtml(text)));
        scrollBottom(msgs);
    }

    function appendAiMsg(panel, text) {
        const msgs = panel.querySelector('#chat-messages');
        msgs.appendChild(createMsg('ai', mdToHtml(text)));
        scrollBottom(msgs);
    }

    function appendErrorMessage(panel, text) {
        const msgs = panel.querySelector('#chat-messages');
        const el = document.createElement('div');
        el.className = 'chat-error';
        el.style.margin = '0 0 4px';
        el.innerHTML = text;
        msgs.appendChild(el);
        scrollBottom(msgs);
    }

    function createMsg(role, html) {
        const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const div = document.createElement('div');
        div.className = `msg ${role}`;
        div.innerHTML = `
      <div class="msg-avatar"><i class="fa-solid ${role === 'ai' ? 'fa-robot' : 'fa-user'}"></i></div>
      <div>
        <div class="msg-bubble">${html}</div>
        <div class="msg-time">${now}</div>
      </div>
    `;
        return div;
    }

    function showTyping(panel) {
        const msgs = panel.querySelector('#chat-messages');
        const div = document.createElement('div');
        div.className = 'msg ai typing-indicator';
        div.id = 'typing-row';
        div.innerHTML = `
      <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
      <div class="typing-dots"><span></span><span></span><span></span></div>
    `;
        msgs.appendChild(div);
        scrollBottom(msgs);
    }
    function removeTyping(panel) { panel.querySelector('#typing-row')?.remove(); }
    function hideEmpty(panel) { panel.querySelector('#chat-empty')?.style && (panel.querySelector('#chat-empty').style.display = 'none'); }

    function clearChat(panel) {
        history = [];
        localStorage.removeItem(HISTORY_KEY);
        panel.querySelector('#chat-messages').innerHTML = `
      <div class="chat-empty" id="chat-empty">
        <div class="chat-empty-icon">🤖</div>
        <div class="chat-empty-title">Fresh start!</div>
        <div class="chat-empty-sub">Ask me anything about ${currentCtx}.</div>
      </div>
    `;
    }

    function replayHistory(panel) {
        if (!history.length) return;
        hideEmpty(panel);
        const msgs = panel.querySelector('#chat-messages');
        history.slice(-12).forEach(h => {
            msgs.appendChild(createMsg(h.role === 'user' ? 'user' : 'ai',
                h.role === 'user' ? escapeHtml(h.content) : mdToHtml(h.content)));
        });
        scrollBottom(msgs);
    }

    /* ── Context (called by app.js) ───────────────────────────── */
    window.deforgeSetContext = function (ctx) {
        currentCtx = ctx || 'FAANG Data Engineering';
        updateContextTag();
        const input = document.querySelector('#chat-input');
        if (input) input.placeholder = `Ask about ${currentCtx}…`;
    };

    function updateContextTag() {
        const tag = document.querySelector('#chat-ctx-tag');
        if (!tag) return;
        const short = currentCtx.length > 20 ? currentCtx.slice(0, 18) + '…' : currentCtx;
        tag.textContent = short;
        tag.title = currentCtx;
    }

    /* ── Badge ────────────────────────────────────────────────── */
    function showBadge() { document.querySelector('#chat-badge')?.classList.add('show'); }
    function clearBadge() { document.querySelector('#chat-badge')?.classList.remove('show'); }

    /* ── Helpers ──────────────────────────────────────────────── */
    function scrollBottom(el) { requestAnimationFrame(() => { el.scrollTop = el.scrollHeight; }); }

    function escapeHtml(str) {
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
    }

    function mdToHtml(text) {
        let html = text
            .replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang, code) =>
                `<pre><code class="lang-${lang || 'text'}">${escCode(code.trim())}</code></pre>`)
            .replace(/```([\s\S]*?)```/g, (_, code) => `<pre><code>${escCode(code.trim())}</code></pre>`)
            .replace(/`([^`\n]+)`/g, (_, c) => `<code>${escCode(c)}</code>`)
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>')
            .replace(/^[-*]\s+(.+)$/gm, '<li>$1</li>')
            .replace(/^#{1,3}\s+(.+)$/gm, '<strong>$1</strong>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
        html = html.replace(/(<li>.*?<\/li>(\s*<br\s*\/?>)*)+/gs, m => '<ul>' + m.replace(/<br\s*\/?>/g, '') + '</ul>');
        return `<p>${html}</p>`;
    }

    function escCode(code) {
        return code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    /* ── Init ─────────────────────────────────────────────────── */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', buildUI);
    } else {
        buildUI();
    }

})();
