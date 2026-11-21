/* 管理界面逻辑：用户管理 CRUD */
(function () {
  const BASE = window.APP_BASE || '';

  // 兼容 file:// 跳转过来时通过 URL 传递的 token（localStorage 跨协议不共享）
  const params = new URLSearchParams(location.search);
  const urlToken = params.get('token');
  const urlUser = params.get('user');
  if (urlToken) localStorage.setItem('crm_token', urlToken);
  if (urlUser) localStorage.setItem('crm_user', urlUser);
  if (urlToken) {
    // 移除 URL 上的敏感参数（file:// 下可能受限，忽略即可）
    try { history.replaceState(null, '', location.pathname); } catch (e) {}
  }

  const TOKEN = localStorage.getItem('crm_token');
  if (!TOKEN) { location.href = BASE + '/'; return; }

  const state = { page: 1, pageSize: 8, keyword: '', status: '', total: 0 };
  const $ = id => document.getElementById(id);
  const headers = () => ({
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + TOKEN
  });

  async function api(url, options = {}) {
    const res = await fetch(BASE + url, Object.assign({ headers: headers() }, options));
    if (res.status === 401) {
      localStorage.removeItem('crm_token');
      localStorage.removeItem('crm_user');
      location.href = BASE + '/';
      throw new Error('登录已过期');
    }
    if (options.method === 'DELETE' && res.ok) return null;
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || '请求失败');
    return data;
  }

  function toast(msg, type) {
    const t = $('toast');
    t.textContent = msg;
    t.className = 'toast show ' + (type || '');
    setTimeout(() => { t.className = 'toast'; }, 2400);
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, c =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  /* ---------- 统计卡片 ---------- */
  async function loadStats() {
    const s = await api('/api/stats');
    const items = [
      { label: '客户总数', value: s.total, color: 'indigo', icon: 'users', tip: '系统全部客户' },
      { label: '潜在客户', value: s.byStatus['潜在客户'] || 0, color: 'slate', icon: 'target', tip: '待开发线索' },
      { label: '跟进中', value: s.byStatus['跟进中'] || 0, color: 'amber', icon: 'clock', tip: '正在跟进' },
      { label: '已成交', value: s.byStatus['已成交'] || 0, color: 'green', icon: 'check', tip: '成交客户' }
    ];
    const icons = {
      users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/>',
      target: '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
      clock: '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
      check: '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/>'
    };
    $('stats').innerHTML = items.map(i => `
      <div class="stat stat-${i.color}">
        <div class="stat-icon"><svg viewBox="0 0 24 24">${icons[i.icon]}</svg></div>
        <div class="stat-body">
          <div class="stat-label">${i.label}</div>
          <div class="stat-value">${i.value}</div>
        </div>
        <div class="stat-sub">${i.tip}</div>
      </div>`).join('');
    $('navCount').textContent = s.total;
    $('countPill').textContent = s.total + ' 位客户';
  }

  /* ---------- 列表 ---------- */
  async function loadList() {
    const q = new URLSearchParams({
      keyword: state.keyword, status: state.status,
      page: state.page, page_size: state.pageSize
    });
    const data = await api('/api/customers?' + q);
    state.total = data.total;
    const tbody = $('tableBody');
    if (!data.items.length) {
      tbody.innerHTML = '';
      $('empty').style.display = 'block';
    } else {
      $('empty').style.display = 'none';
      tbody.innerHTML = data.items.map(c => `
        <tr>
          <td>
            <div class="cell-person">
              <span class="person-avatar">${esc(c.name.charAt(0))}</span>
              <div><div class="cell-name">${esc(c.name)}</div><div class="cell-sub">#${c.id}</div></div>
            </div>
          </td>
          <td>${esc(c.company || '-')}</td>
          <td>${esc(c.phone || '-')}</td>
          <td>${esc(c.industry || '-')}</td>
          <td><span class="tag ${c.level === 'VIP' ? 'tag-vip' : 'tag-normal'}">${esc(c.level)}</span></td>
          <td><span class="st st-${esc(c.status)}">${esc(c.status)}</span></td>
          <td class="cell-date">${esc(c.created_at)}</td>
          <td class="right">
            <button class="op-btn" title="编辑" onclick="window.__edit(${c.id})">
              <svg viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.12 2.12 0 0 1 3 3L12 15l-4 1 1-4z"/></svg>
            </button>
            <button class="op-btn del" title="删除" onclick="window.__del(${c.id})">
              <svg viewBox="0 0 24 24"><path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
            </button>
          </td>
        </tr>`).join('');
    }
    const pages = Math.max(1, Math.ceil(state.total / state.pageSize));
    $('pageInfo').textContent = `共 ${state.total} 条记录`;
    $('pageNum').textContent = `${state.page} / ${pages}`;
    $('prevBtn').disabled = state.page <= 1;
    $('nextBtn').disabled = state.page >= pages;
  }

  async function refresh() { await Promise.all([loadStats(), loadList()]); }

  /* ---------- 弹窗 ---------- */
  function openModal(c) {
    $('formError').textContent = '';
    $('uid').value = c ? c.id : '';
    $('modalTitle').textContent = c ? '编辑用户' : '新增用户';
    ['name', 'company', 'phone', 'email', 'industry', 'level', 'status', 'remark'].forEach(k => {
      $('f_' + k).value = c ? (c[k] || '') : (k === 'level' ? '普通' : k === 'status' ? '跟进中' : '');
    });
    $('modalMask').classList.add('show');
    setTimeout(() => $('f_name').focus(), 80);
  }
  function closeModal() { $('modalMask').classList.remove('show'); }

  $('addBtn').onclick = () => openModal(null);
  $('closeModal').onclick = closeModal;
  $('cancelBtn').onclick = closeModal;
  $('modalMask').onclick = e => { if (e.target === $('modalMask')) closeModal(); };

  window.__edit = async function (id) {
    try { openModal(await api('/api/customers/' + id)); }
    catch (e) { toast(e.message, 'err'); }
  };

  /* ---------- 删除确认 ---------- */
  let pendingDeleteId = null;
  window.__del = function (id) {
    pendingDeleteId = id;
    $('confirmMask').classList.add('show');
  };
  function closeConfirm() { $('confirmMask').classList.remove('show'); pendingDeleteId = null; }
  $('confirmCancel').onclick = closeConfirm;
  $('confirmMask').onclick = e => { if (e.target === $('confirmMask')) closeConfirm(); };
  $('confirmOk').onclick = async function () {
    if (pendingDeleteId == null) return;
    const btn = this;
    btn.disabled = true;
    btn.textContent = '删除中…';
    try {
      await api('/api/customers/' + pendingDeleteId, { method: 'DELETE' });
      toast('删除成功', 'ok');
      closeConfirm();
      refresh();
    } catch (e) { toast(e.message, 'err'); }
    btn.disabled = false;
    btn.textContent = '确认删除';
  };

  $('userForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const body = {};
    ['name', 'company', 'phone', 'email', 'industry', 'level', 'status', 'remark'].forEach(k => {
      body[k] = $('f_' + k).value.trim();
    });
    if (!body.name) { $('formError').textContent = '姓名不能为空'; return; }
    const id = $('uid').value;
    const saveBtn = $('saveBtn');
    saveBtn.disabled = true;
    saveBtn.textContent = '保存中…';
    try {
      if (id) {
        await api('/api/customers/' + id, { method: 'PUT', body: JSON.stringify(body) });
        toast('更新成功', 'ok');
      } else {
        await api('/api/customers', { method: 'POST', body: JSON.stringify(body) });
        toast('新增成功', 'ok');
      }
      closeModal();
      refresh();
    } catch (e2) { $('formError').textContent = e2.message; }
    saveBtn.disabled = false;
    saveBtn.textContent = '保存';
  });

  /* ---------- 搜索 / 分页 ---------- */
  let timer;
  $('searchInput').addEventListener('input', e => {
    clearTimeout(timer);
    timer = setTimeout(() => { state.keyword = e.target.value.trim(); state.page = 1; loadList(); }, 300);
  });
  $('statusFilter').addEventListener('change', e => {
    state.status = e.target.value; state.page = 1; loadList();
  });
  $('resetBtn').onclick = () => {
    $('searchInput').value = ''; $('statusFilter').value = '';
    state.keyword = ''; state.status = ''; state.page = 1; loadList();
  };
  $('prevBtn').onclick = () => { if (state.page > 1) { state.page--; loadList(); } };
  $('nextBtn').onclick = () => { state.page++; loadList(); };

  /* ---------- 侧边栏折叠 ---------- */
  $('menuToggle').onclick = () => {
    $('sidebar').classList.toggle('collapsed');
    document.querySelector('.main').classList.toggle('expanded');
  };
  $('overlay').onclick = () => {
    $('sidebar').classList.remove('mobile-open');
    $('overlay').classList.remove('show');
  };
  // 移动端：小屏时点击菜单按钮弹出侧栏
  if (window.innerWidth <= 768) {
    $('menuToggle').onclick = () => {
      $('sidebar').classList.add('mobile-open');
      $('overlay').classList.add('show');
    };
  }
  // 其他菜单项占位提示
  document.querySelectorAll('.nav-item:not(.active)').forEach(el => {
    el.addEventListener('click', e => {
      e.preventDefault();
      const name = el.querySelector('span').textContent;
      toast('「' + name + '」模块即将上线', '');
    });
  });

  /* ---------- 退出 ---------- */
  $('logoutBtn').onclick = () => {
    localStorage.removeItem('crm_token');
    localStorage.removeItem('crm_user');
    location.href = BASE + '/';
  };

  /* ---------- 初始化 ---------- */
  const user = localStorage.getItem('crm_user') || 'admin';
  $('sideUsername').textContent = user;
  $('sideAvatar').textContent = user.charAt(0).toUpperCase();
  $('topAvatar').textContent = user.charAt(0).toUpperCase();
  refresh().catch(e => toast(e.message, 'err'));
})();
