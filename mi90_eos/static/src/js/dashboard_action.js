/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onMounted, useRef } from "@odoo/owl";

class Mi90DashboardAction extends Component {
  static template = "mi90_eos.Dashboard";

  setup() {
    this.rootRef = useRef("root");
    
    onMounted(() => {
      setTimeout(() => {
        this.setupNavigation();
        // Fetch live data and render
        this.fetchAll();
      }, 100);
    });
  }

  async fetchAll() {
    try {
      await Promise.all([
        this.fetchAndRenderScorecard(),
        this.fetchAndRenderScorecardTable(),
        this.fetchAndRenderRocks(),
        this.fetchAndRenderIssues(),
        this.fetchAndRenderMeetings(),
      ]);
    } catch (e) {
      // Keep silent; logs can be inspected in browser console
      console.error('mi90_eos: fetchAll error', e);
    }
  }

  async fetchJson(url, options) {
    const res = await fetch(url, Object.assign({credentials: 'same-origin'}, options || {}));
    if (!res.ok) throw new Error(`${url} -> ${res.status}`);
    return res.json();
  }

  async fetchAndRenderRocks() {
    const rootEl = this.rootRef.el || this.el;
    try {
      const data = await this.fetchJson('/mi90_eos/data/rocks');
      const rocks = data.rocks || [];
      this.renderRocks(rootEl, rocks);
      this.renderRocksAnalytics(rootEl, rocks);
    } catch (e) {
      console.warn('Unable to load rocks', e);
    }
  }

  renderRocks(rootEl, rocks) {
    const list = rootEl.querySelector('.rocks--list');
    const progLabel = rootEl.querySelector('.rocks-progress-label') || rootEl.querySelector('.rocks--wrap div[style*="Progreso general"]');
    if (progLabel && rocks.length) {
      try {
        const avg = Math.round((rocks.reduce((s,r) => s + (r.progress || 0), 0) / rocks.length) || 0);
        progLabel.textContent = `Progreso general: ${avg}%`;
      } catch(e){/* ignore */}
    }
    if (!list) return;
    list.innerHTML = rocks.map(r => {
      const owner = (r.owner_id && r.owner_id[1]) ? r.owner_id[1] : (r.owner_id || '—');
      const due = r.due_date || '—';
      const progress = r.progress || 0;
      const status = r.status || 'En progreso';
      const krsHtml = (r.key_result_ids && r.key_result_ids.length) ? `<ul style="margin:6px 0 0 18px;color:var(--muted);font-size:13px">${r.key_result_ids.map(kr => `<li>${kr}</li>`).join('')}</ul>` : '';
      const notes = r.description ? (r.description.substring(0,120)) : '';
      return `
        <li class="rock">
          <div class="rock--header" style="display:flex;justify-content:space-between;align-items:center">
            <div style="display:flex;align-items:center;gap:8px">
              <div class="rock--title">${r.name || ''}</div>
              <div style="font-size:12px;color:var(--muted);padding:2px 8px;border-radius:12px;background:#f1f5f9">${owner}</div>
            </div>
            <div style="font-size:12px;color:var(--muted)">Due: ${due}</div>
          </div>
          <div class="rock--progress" style="margin-top:8px;background:#f3e8ff;border-radius:999px;height:10px;overflow:hidden">
            <div class="rock--progress-bar" style="width:${progress}%;background:linear-gradient(90deg,var(--lav),#d8b4fe);height:100%"></div>
          </div>
          <div class="rock--meta" style="display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin-top:6px">
            <span>${status}</span>
            <span>Progreso: ${progress}%</span>
          </div>
          ${krsHtml}
          <div class="rock--notes" style="margin-top:8px;font-size:12px;color:var(--muted)">${notes}</div>
        </li>`;
    }).join('\n');
  }

  async fetchAndRenderTodos() {
    const rootEl = this.rootRef.el || this.el;
    try {
      const data = await this.fetchJson('/mi90_eos/data/todos');
      const todos = data.todos || [];
      this.renderTodos(rootEl, todos);
    } catch (e) {
      console.warn('Unable to load todos', e);
    }
  }

  renderTodos(rootEl, todos) {
    // Render a 4-column board using todo.status
    const board = rootEl.querySelector('.todos-board');
    if (!board) return;

    const columns = {
      todo: board.querySelector('.todos-column[data-state="todo"] .todos-column-list'),
      in_progress: board.querySelector('.todos-column[data-state="in_progress"] .todos-column-list'),
      in_review: board.querySelector('.todos-column[data-state="in_review"] .todos-column-list'),
      done: board.querySelector('.todos-column[data-state="done"] .todos-column-list'),
    };

    // Clear columns
    Object.values(columns).forEach(el => { if (el) el.innerHTML = ''; });

    // Place todos into columns
    todos.forEach(t => {
      const state = t.status || 'todo';
      const col = columns[state] || columns.todo;
      const name = t.name || '';
      const desc = (t.description && t.description.substring(0,120)) || '';
      const owner = (t.owner_id && t.owner_id[1]) ? t.owner_id[1] : '';
      const card = document.createElement('div');
      card.className = 'todo-card mi90--card';
      card.style.marginBottom = '8px';
      card.dataset.id = t.id;
      card.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center">
          <div style="font-weight:600">${name}</div>
          <div style="font-size:12px;color:var(--muted)">${owner}</div>
        </div>
        <div style="font-size:12px;color:var(--muted);margin-top:6px">${desc}</div>
        <div style="display:flex;gap:6px;justify-content:flex-end;margin-top:8px">
          <button class="mi90-todo-btn mi90-todo-prev" data-id="${t.id}">◀</button>
          <button class="mi90-todo-btn mi90-todo-next" data-id="${t.id}">▶</button>
          <button class="mi90-todo-btn mi90-todo-edit" data-id="${t.id}">✎</button>
          <button class="mi90-todo-btn mi90-todo-delete" data-id="${t.id}" title="Eliminar">🗑</button>
        </div>
      `;
      if (col) col.appendChild(card);
    });

    // Update column counts
    ['todo','in_progress','in_review','done'].forEach(s => {
      const badge = rootEl.querySelector(`.mi90-todos-count-${s}`);
      const count = todos.filter(t => (t.status||'todo') === s).length;
      if (badge) badge.textContent = count;
    });

    // Attach handlers for add button
    const addBtn = rootEl.querySelector('.mi90-todo-add-btn');
    const addInput = rootEl.querySelector('.mi90-todo-new-input');
    if (addBtn && addInput) {
      addBtn.onclick = async (ev) => {
        const name = (addInput.value || '').trim();
        if (!name) return;
        addBtn.disabled = true;
        try {
          await this.fetchJson('/mi90_eos/data/todos/create', {method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name: name, status: 'todo'})});
          addInput.value = '';
          await this.fetchAndRenderTodos();
        } catch(e) {
          console.error('todo create failed', e);
        } finally { addBtn.disabled = false; }
      };
    }

    // Attach handlers for move buttons
    rootEl.querySelectorAll('.mi90-todo-prev').forEach(btn => {
      btn.addEventListener('click', async (ev) => {
        const id = ev.currentTarget.dataset.id;
        await this._changeTodoStateByDelta(id, -1);
      });
    });
    rootEl.querySelectorAll('.mi90-todo-next').forEach(btn => {
      btn.addEventListener('click', async (ev) => {
        const id = ev.currentTarget.dataset.id;
        await this._changeTodoStateByDelta(id, +1);
      });
    });
    // edit button currently refreshes (placeholder)
    rootEl.querySelectorAll('.mi90-todo-edit').forEach(btn => {
      btn.addEventListener('click', async (ev) => {
        const id = ev.currentTarget.dataset.id;
        // simple toggle to done as quick action
        try {
          await this.fetchJson('/mi90_eos/data/todos/update', {method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({id: id, status: 'done'})});
          await this.fetchAndRenderTodos();
        } catch(e) { console.error('todo edit failed', e); }
      });
    });
  }

  // Change todo state by advancing/retreating through the workflow
  async _changeTodoStateByDelta(id, delta) {
    // ordered states
    const order = ['todo','in_progress','in_review','done'];
    try {
      // fetch current record to know state
      const res = await this.fetchJson('/mi90_eos/data/todos');
      const todos = res.todos || [];
      const t = todos.find(x => String(x.id) === String(id));
      if (!t) return;
      const cur = t.status || 'todo';
      let idx = order.indexOf(cur);
      if (idx === -1) idx = 0;
      let newIdx = Math.min(order.length-1, Math.max(0, idx + delta));
      const newState = order[newIdx];
      await this.fetchJson('/mi90_eos/data/todos/update', {method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({id: id, status: newState})});
      await this.fetchAndRenderTodos();
    } catch(e) {
      console.error('change todo state failed', e);
    }
  }

  async fetchAndRenderScorecard() {
    const rootEl = this.rootRef.el || this.el;
    try {
      const data = await this.fetchJson('/mi90_eos/data/scorecard');
      const s = data.scorecard || {};
      this.renderScorecard(rootEl, s);
      this.renderObjectivesChart(rootEl, s);
    } catch(e) {
      console.warn('Unable to load scorecard', e);
    }
  }

  renderScorecard(rootEl, s) {
    const wrapper = rootEl.querySelector('.scorecard--wrap');
    if (!wrapper) return;
    const headerRight = wrapper.querySelector('.scorecard--wrap > div:nth-child(1) > div:nth-child(2)');
    if (headerRight) {
      headerRight.textContent = `Resumen — Total:${s.total||0} · Hechas:${s.done||0} · En Progreso:${s.in_progress||0} · Atrasadas:${s.overdue||0}`;
    }
  }

  renderObjectivesChart(rootEl, s) {
    const chart = rootEl.querySelector('.mi90--chart');
    if (!chart) return;
    const total = Number(s.total || 0);
    const done = Number(s.done || 0);
    const inprog = Number(s.in_progress || 0);
    const overdue = Number(s.overdue || 0);
    const safePct = (n, d) => d > 0 ? Math.round((n * 100) / d) : 0;
    const pDone = safePct(done, total);
    const pInprog = safePct(inprog, total);
    const pOver = Math.max(0, 100 - pDone - pInprog); // ensure full circle

    // Update numbers
    const totalEl = chart.querySelector('.chart--total-num');
    if (totalEl) totalEl.textContent = String(total);
    const cDone = chart.querySelector('.chart--count-done');
    const cInprog = chart.querySelector('.chart--count-inprogress');
    const cOver = chart.querySelector('.chart--count-overdue');
    if (cDone) cDone.textContent = String(done);
    if (cInprog) cInprog.textContent = String(inprog);
    if (cOver) cOver.textContent = String(overdue);
    const pDoneEl = chart.querySelector('.chart--pct-done');
    const pInprogEl = chart.querySelector('.chart--pct-inprogress');
    const pOverEl = chart.querySelector('.chart--pct-overdue');
    if (pDoneEl) pDoneEl.textContent = `${pDone}%`;
    if (pInprogEl) pInprogEl.textContent = `${pInprog}%`;
    if (pOverEl) pOverEl.textContent = `${pOver}%`;

    // Render simple pie via conic-gradient (colors tuned to legend dots)
    const pie = chart.querySelector('.pie');
    if (pie) {
      const g1 = '#22c55e'; // green
      const g2 = '#3b82f6'; // blue
      const g3 = '#ef4444'; // red
      const s1 = pDone;
      const s2 = pDone + pInprog;
      pie.style.width = '160px';
      pie.style.height = '160px';
      pie.style.borderRadius = '50%';
      pie.style.background = `conic-gradient(${g1} 0% ${s1}%, ${g2} ${s1}% ${s2}%, ${g3} ${s2}% 100%)`;
    }
  }

  async fetchAndRenderScorecardTable() {
    const rootEl = this.rootRef.el || this.el;
    try {
      const data = await this.fetchJson('/mi90_eos/data/scorecard_table?weeks=12');
      const table = data.table || {};
      this.renderScorecardTable(rootEl, table);
    } catch(e) {
      console.warn('Unable to load scorecard table', e);
    }
  }

  renderScorecardTable(rootEl, table) {
    const sc = rootEl.querySelector('.scorecard--wrap');
    if (!sc) return;
    const headRow = sc.querySelector('.sc-head');
    const body = sc.querySelector('.scorecard-body');
    const lastUpd = sc.querySelector('.sc-last-update');
    if (!headRow || !body) return;

    const weeks = table.weeks || [];
    const rows = table.rows || [];
    if (lastUpd) lastUpd.textContent = `Actualizado: ${table.last_update || ''}`;

    // Clear and rebuild header week columns
    // Keep first 3 sticky headers (owner, name, goal)
    // Remove any existing dynamic week th's
    while (headRow.children.length > 3) {
      headRow.removeChild(headRow.lastElementChild);
    }
    weeks.forEach(w => {
      const th = document.createElement('th');
      th.textContent = this._fmtWeekLabel(w);
      headRow.appendChild(th);
    });

    // Build body rows
    body.innerHTML = '';
    rows.forEach(r => {
      const tr = document.createElement('tr');
      const tds = [];
      const tdOwner = document.createElement('td');
      tdOwner.textContent = r.owner || '';
      tdOwner.className = 'sc-sticky';
      const tdName = document.createElement('td');
      tdName.textContent = r.name || '';
      tdName.className = 'sc-sticky';
      const tdGoal = document.createElement('td');
      tdGoal.textContent = `${(r.target ?? 0)}${r.unit ? ' ' + r.unit : ''}`;
      tdGoal.className = 'sc-sticky';
      tds.push(tdOwner, tdName, tdGoal);

      weeks.forEach(w => {
        const td = document.createElement('td');
        const v = r.values ? r.values[w] : undefined;
        if (v === undefined || v === null) {
          td.textContent = '—';
          td.style.color = 'var(--muted)';
        } else {
          td.textContent = String(v);
          const ok = this._meetsTarget(v, r.target);
          td.classList.add(ok ? 'sc-ok' : 'sc-bad');
        }
        tds.push(td);
      });

      tds.forEach(td => tr.appendChild(td));
      body.appendChild(tr);
    });
  }

  _fmtWeekLabel(d) {
    try {
      const dt = new Date(d);
      const dd = String(dt.getDate()).padStart(2, '0');
      const mm = String(dt.getMonth() + 1).padStart(2, '0');
      return `${dd}/${mm}`;
    } catch(e){ return String(d); }
  }

  _meetsTarget(value, target) {
    const t = Number(target || 0);
    const v = Number(value || 0);
    // Default rule: higher is better
    return v >= t;
  }

  async fetchAndRenderIssues() {
    const rootEl = this.rootRef.el || this.el;
    try {
      const data = await this.fetchJson('/mi90_eos/data/issues');
      const items = data.issues || [];
      this.renderIssues(rootEl, items);
      this.renderIssuesAnalytics(rootEl, items);
    } catch(e){/* ignore */}
  }

  renderIssues(rootEl, items) {
    const list = rootEl.querySelector('.issues--list');
    if (!list) return;
    list.innerHTML = items.map(i => `<li>${i.name || ''} <small style="color:var(--muted)">${i.priority||''}</small></li>`).join('');
  }

  async fetchAndRenderMeetings() {
    const rootEl = this.rootRef.el || this.el;
    try {
      const data = await this.fetchJson('/mi90_eos/data/meetings');
      const items = data.meetings || [];
      this.renderMeetings(rootEl, items);
    } catch(e){/* ignore */}
  }

  renderMeetings(rootEl, items) {
    const list = rootEl.querySelector('.meetings--list');
    if (!list) return;
    list.innerHTML = items.map(m => `<li>${m.name||''} <small style="color:var(--muted)">${m.date||''}</small></li>`).join('');
  }

  renderRocksAnalytics(rootEl, rocks) {
    const card = rootEl.querySelector('.mi90--analytics');
    if (!card) return;
    const total = rocks.length || 0;
    const done = rocks.filter(r => Number(r.progress||0) >= 100).length;
    const inprog = rocks.filter(r => {
      const p = Number(r.progress||0);
      // consider not overdue and not done as in progress
      const overdue = r.due_date && new Date(r.due_date) < new Date();
      return p > 0 && p < 100 && !overdue;
    }).length;
    const overdue = rocks.filter(r => r.due_date && new Date(r.due_date) < new Date() && Number(r.progress||0) < 100).length;
    const avg = total ? Math.round(rocks.reduce((s,r) => s + Number(r.progress||0), 0) / total) : 0;

    // Update KPIs
    const tEl = card.querySelector('.rocks-total-count');
    const aEl = card.querySelector('.rocks-avg-progress');
    if (tEl) tEl.textContent = String(total);
    if (aEl) aEl.textContent = `${avg}%`;

    // Update legend counts
    const dEl = card.querySelector('.rocks-done-count');
    const iEl = card.querySelector('.rocks-inprogress-count');
    const oEl = card.querySelector('.rocks-overdue-count');
    if (dEl) dEl.textContent = String(done);
    if (iEl) iEl.textContent = String(inprog);
    if (oEl) oEl.textContent = String(overdue);

    // Pie
    const pie = card.querySelector('.pie-rocks-status');
    if (pie) {
      const safeTotal = Math.max(1, done + inprog + overdue);
      const pDone = Math.round(done * 100 / safeTotal);
      const pIn = Math.round(inprog * 100 / safeTotal);
      const pOv = Math.max(0, 100 - pDone - pIn);
      const cDone = '#22c55e';
      const cIn = '#3b82f6';
      const cOv = '#ef4444';
      const s1 = pDone;
      const s2 = pDone + pIn;
      pie.style.width = '140px';
      pie.style.height = '140px';
      pie.style.borderRadius = '50%';
      pie.style.background = `conic-gradient(${cDone} 0% ${s1}%, ${cIn} ${s1}% ${s2}%, ${cOv} ${s2}% 100%)`;
    }
  }

  // ---------------- Analytics (Issues) ----------------
  renderIssuesAnalytics(rootEl, items) {
    const card = rootEl.querySelector('.mi90--analytics');
    if (!card) return;

    // Priority pie (open issues only)
    const open = items.filter(i => !i.resolved);
    const hi = open.filter(i => (i.priority||'').toLowerCase() === 'high').length;
    const md = open.filter(i => (i.priority||'').toLowerCase() === 'medium').length;
    const lo = open.filter(i => (i.priority||'').toLowerCase() === 'low').length;
    const total = Math.max(1, hi + md + lo);
    const pHi = Math.round(hi * 100 / total);
    const pMd = Math.round(md * 100 / total);
    const pLo = Math.max(0, 100 - pHi - pMd);
    const pie = card.querySelector('.pie-issues-priority');
    if (pie) {
      const cHi = '#ef4444'; // red
      const cMd = '#3b82f6'; // blue
      const cLo = '#22c55e'; // green
      const s1 = pHi;
      const s2 = pHi + pMd;
      pie.style.width = '140px';
      pie.style.height = '140px';
      pie.style.borderRadius = '50%';
      pie.style.background = `conic-gradient(${cHi} 0% ${s1}%, ${cMd} ${s1}% ${s2}%, ${cLo} ${s2}% 100%)`;
    }
    const lblHi = card.querySelector('.issues-prio-high');
    const lblMd = card.querySelector('.issues-prio-medium');
    const lblLo = card.querySelector('.issues-prio-low');
    if (lblHi) lblHi.textContent = String(hi);
    if (lblMd) lblMd.textContent = String(md);
    if (lblLo) lblLo.textContent = String(lo);

    // Open vs Closed bars (all issues)
    const openCount = items.filter(i => !i.resolved).length;
    const closedCount = items.filter(i => !!i.resolved).length;
    const sum = Math.max(1, openCount + closedCount);
    const wOpen = Math.round(openCount * 100 / sum);
    const wClosed = Math.max(0, 100 - wOpen);
    const barOpen = card.querySelector('.bar-open');
    const barClosed = card.querySelector('.bar-closed');
    if (barOpen) barOpen.style.width = `${wOpen}%`;
    if (barClosed) barClosed.style.width = `${wClosed}%`;
    const oLbl = card.querySelector('.issues-open-count');
    const cLbl = card.querySelector('.issues-closed-count');
    if (oLbl) oLbl.textContent = String(openCount);
    if (cLbl) cLbl.textContent = String(closedCount);
  }

  setupNavigation() {
    const rootEl = this.rootRef.el || this.el;
    if (!rootEl) return;
    
    const navButtons = rootEl.querySelectorAll('.mi90--nav-btn');
    
    navButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Remover clase active de todos los botones
        navButtons.forEach(btn => btn.classList.remove('active'));
        
        // Agregar clase active al botón clickeado
        button.classList.add('active');
        
        // Obtener la vista seleccionada
        const view = button.dataset.view;
        
        if (view === 'scorecard') {
          // Mostrar solo la card del scorecard expandida
          this.showScorecardView(rootEl);
        } else if (view === 'rocas') {
          // Mostrar solo la card de rocas expandida
          this.showRocasView(rootEl);
        } else {
          // Mostrar vista Mi 90 normal
          this.showMi90View(rootEl);
        }
      });
    });
  }

  showScorecardView(rootEl) {
    const grid = rootEl.querySelector('.mi90--grid');
    if (grid) {
      grid.style.gridTemplateColumns = '1fr';
      
      // Ocultar otras cards
      const row = rootEl.querySelector('.mi90--row');
      if (row) {
        row.style.display = 'none';
      }
      
      // Expandir scorecard
      const scorecardCard = rootEl.querySelector('.mi90--scorecard');
      if (scorecardCard) {
        scorecardCard.style.gridColumn = '1';
      }
    }
  }

  showMi90View(rootEl) {
    const grid = rootEl.querySelector('.mi90--grid');
    if (grid) {
      grid.style.gridTemplateColumns = 'repeat(2,1fr)';
      
      // Restaurar todas las cards
      const scorecardCard = rootEl.querySelector('.mi90--scorecard');
      const todosCard = rootEl.querySelector('.mi90--todos');
      const rocasCard = rootEl.querySelector('.mi90--rocks');
      const chartCard = rootEl.querySelector('.mi90--chart');
      
      if (scorecardCard) {
        scorecardCard.style.display = 'block';
        scorecardCard.style.gridColumn = 'auto';
      }
      if (todosCard) todosCard.style.display = 'block';
      if (rocasCard) rocasCard.style.display = 'block';
      if (chartCard) chartCard.style.display = 'block';
      
      // Restaurar el row
      const row = rootEl.querySelector('.mi90--row');
      if (row) {
        row.style.display = 'grid';
        row.style.gridTemplateColumns = '1fr 1fr 1fr';
      }
    }
  }

  showRocasView(rootEl) {
    const grid = rootEl.querySelector('.mi90--grid');
    if (grid) {
      grid.style.gridTemplateColumns = '1fr';
      
      // Ocultar scorecard
      const scorecardCard = rootEl.querySelector('.mi90--scorecard');
      if (scorecardCard) {
        scorecardCard.style.display = 'none';
      }
      
      // Ocultar otras cards del row
      const todosCard = rootEl.querySelector('.mi90--todos');
      const chartCard = rootEl.querySelector('.mi90--chart');
      if (todosCard) todosCard.style.display = 'none';
      if (chartCard) chartCard.style.display = 'none';
      
      // Expandir solo la card de rocas
      const rocasCard = rootEl.querySelector('.mi90--rocks');
      if (rocasCard) {
        rocasCard.style.display = 'block';
        rocasCard.style.gridColumn = '1';
      }
      
      // Mostrar el row pero solo con rocas
      const row = rootEl.querySelector('.mi90--row');
      if (row) {
        row.style.display = 'block';
        row.style.gridTemplateColumns = '1fr';
      }
    }
  }
}

registry.category("actions").add("mi90_eos.dashboard_action", Mi90DashboardAction);

// NOTE: The legacy Mi90TodosAction (fetch-based) was removed to avoid duplicate
// registrations for the `mi90_eos.todo_board` action. The OWL implementation
// is present in `static/src/js/todo_board.js` and is the one that should be used.
