/* 登录页逻辑：调用 /api/login，成功后保存 token 跳转到管理界面 */
(function () {
  const BASE = window.APP_BASE || '';
  const form = document.getElementById('loginForm');
  const err = document.getElementById('loginError');
  const btn = document.getElementById('loginBtn');
  const pwd = document.getElementById('password');
  const pwdToggle = document.getElementById('pwdToggle');

  // 已登录则直接跳转
  if (localStorage.getItem('crm_token')) {
    location.href = BASE + '/admin.html';
    return;
  }

  // 显示/隐藏密码
  pwdToggle.addEventListener('click', function () {
    const show = pwd.type === 'password';
    pwd.type = show ? 'text' : 'password';
    pwdToggle.classList.toggle('active', show);
  });

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    err.textContent = '';
    const username = document.getElementById('username').value.trim();
    const password = pwd.value;
    if (!username || !password) {
      err.textContent = '请输入账号和密码';
      return;
    }
    btn.disabled = true;
    btn.classList.add('loading');
    btn.querySelector('span').textContent = '登录中…';
    try {
      const res = await fetch(BASE + '/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || '登录失败');
      localStorage.setItem('crm_token', data.token);
      localStorage.setItem('crm_user', data.username);
      // 用完整地址跳转，并通过 URL 带上 token，兼容 file:// 与 http:// 之间 localStorage 不共享
      location.href = BASE + '/admin.html?token=' + encodeURIComponent(data.token)
        + '&user=' + encodeURIComponent(data.username);
    } catch (e2) {
      err.textContent = e2.message || '网络错误，请确认服务已启动';
      btn.disabled = false;
      btn.classList.remove('loading');
      btn.querySelector('span').textContent = '登 录';
    }
  });
})();
