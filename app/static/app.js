const API = '/api';
let token = localStorage.getItem('token');
let currentUser = null;
let lang = localStorage.getItem('lang') || 'ru';

const i18n = {
  ru: {
    'nav.tasks': 'Задачи',
    'nav.profile': 'Профиль',
    'nav.admin': 'Админ',
    'nav.api': 'API Docs',
    'nav.logout': 'Выйти',
    'nav.lang': 'EN',
    'auth.login': 'Вход',
    'auth.register': 'Регистрация',
    'auth.login_btn': 'Войти',
    'auth.register_btn': 'Зарегистрироваться',
    'auth.login_switch': 'Войти',
    'auth.register_switch': 'Зарегистрироваться',
    'auth.username': 'Логин',
    'auth.email': 'Почта',
    'auth.password': 'Пароль',
    'auth.success': 'Регистрация успешна! Теперь войдите.',
    'auth.error.429': 'Слишком много запросов. Подождите!',
    'auth.error.failed': 'Ошибка запроса',
    'tasks.title': 'Мои задачи',
    'tasks.add': 'Добавить',
    'tasks.title_ph': 'Название задачи',
    'tasks.desc_ph': 'Описание',
    'tasks.done': 'Готово',
    'tasks.empty_title': 'Задач пока нет',
    'tasks.empty_desc': 'Создайте первую задачу прямо сейчас!',
    'tasks.undo': 'Отменить',
    'tasks.delete': 'Удалить',
    'tasks.edit': 'Редактировать',
    'tasks.save': 'Сохранить',
    'tasks.cancel': 'Отмена',
    'profile.title': 'Настройки профиля',
    'profile.email': 'Новая почта (оставьте пустым, если не меняете)',
    'profile.old_pw': 'Текущий пароль',
    'profile.new_pw': 'Новый пароль (оставьте пустым)',
    'profile.save': 'Сохранить',
    'profile.need_old': 'Введите текущий пароль для смены',
    'profile.empty': 'Нечего обновлять',
    'profile.updated': 'Профиль обновлён!',
    'admin.title': 'Панель администратора',
    'admin.id': 'ID',
    'admin.username': 'Логин',
    'admin.email': 'Почта',
    'admin.role': 'Роль',
    'admin.status': 'Статус',
    'admin.actions': 'Действия',
    'admin.active': 'Активен',
    'admin.blocked': 'Заблокирован',
    'admin.offline': 'Не в сети',
    'admin.never': 'Не заходил',
    'admin.block': 'Заблокировать',
    'admin.unblock': 'Разблокировать',
    'admin.delete': 'Удалить',
    'admin.delete_confirm': 'Удалить этого пользователя?',
  },
  en: {
    'nav.tasks': 'Tasks',
    'nav.profile': 'Profile',
    'nav.admin': 'Admin',
    'nav.api': 'API Docs',
    'nav.logout': 'Logout',
    'nav.lang': 'RU',
    'auth.login': 'Login',
    'auth.register': 'Register',
    'auth.login_btn': 'Login',
    'auth.register_btn': 'Register',
    'auth.login_switch': 'Login',
    'auth.register_switch': 'Register',
    'auth.username': 'Username',
    'auth.email': 'Email',
    'auth.password': 'Password',
    'auth.success': 'Registration successful! Please login.',
    'auth.error.429': 'Too many requests. Slow down!',
    'auth.error.failed': 'Request failed',
    'tasks.title': 'My Tasks',
    'tasks.add': 'Add Task',
    'tasks.title_ph': 'Task title',
    'tasks.desc_ph': 'Description',
    'tasks.done': 'Done',
    'tasks.empty_title': 'No tasks yet',
    'tasks.empty_desc': 'Create your first task now!',
    'tasks.undo': 'Undo',
    'tasks.delete': 'Delete',
    'tasks.edit': 'Edit',
    'tasks.save': 'Save',
    'tasks.cancel': 'Cancel',
    'profile.title': 'Profile Settings',
    'profile.email': 'New email (leave blank to keep)',
    'profile.old_pw': 'Current password',
    'profile.new_pw': 'New password (leave blank)',
    'profile.save': 'Save Changes',
    'profile.need_old': 'Enter current password to set a new one',
    'profile.empty': 'Nothing to update',
    'profile.updated': 'Profile updated!',
    'admin.title': 'Admin Panel',
    'admin.id': 'ID',
    'admin.username': 'Username',
    'admin.email': 'Email',
    'admin.role': 'Role',
    'admin.status': 'Status',
    'admin.actions': 'Actions',
    'admin.active': 'Active',
    'admin.blocked': 'Blocked',
    'admin.offline': 'Offline',
    'admin.never': 'Never logged in',
    'admin.block': 'Block',
    'admin.unblock': 'Unblock',
    'admin.delete': 'Delete',
    'admin.delete_confirm': 'Delete this user?',
  },
};

function t(key) {
  return i18n[lang][key] || key;
}

function toggleLang() {
  lang = lang === 'ru' ? 'en' : 'ru';
  localStorage.setItem('lang', lang);
  applyLang();
}

function applyLang() {
  document.getElementById('nav-lang').textContent = t('nav.lang');
  if (token) {
    document.getElementById('nav-tasks').textContent = t('nav.tasks');
    document.getElementById('nav-profile').textContent = t('nav.profile');
    document.getElementById('nav-admin').textContent = t('nav.admin');
    document.getElementById('nav-api').textContent = t('nav.api');
    document.getElementById('nav-logout').textContent = t('nav.logout');
  }
  updateAuthUI();
  document.querySelector('.tasks-header h2').textContent = t('tasks.title');
  document.getElementById('task-title').placeholder = t('tasks.title_ph');
  document.getElementById('task-desc').placeholder = t('tasks.desc_ph');
  document.querySelector('#task-form button').textContent = t('tasks.add');
  document.getElementById('empty-title').textContent = t('tasks.empty_title');
  document.getElementById('empty-desc').textContent = t('tasks.empty_desc');

  document.querySelector('#page-admin > h2').textContent = t('admin.title');
  updateAdminTableHeaders();
}

function updateAdminTableHeaders() {
  const ths = document.querySelectorAll('#admin-table thead th');
  if (ths.length >= 7) {
    ths[0].textContent = t('admin.id');
    ths[1].textContent = t('admin.username');
    ths[2].textContent = t('admin.email');
    ths[3].textContent = t('admin.role');
    ths[4].textContent = 'Вход';
    ths[5].textContent = t('admin.status');
    ths[6].textContent = t('admin.actions');
  }
}

function updateAuthUI() {
  const mode = document.getElementById('auth-mode');
  const title = document.getElementById('auth-title');
  const submit = document.getElementById('auth-submit');
  const toggle = document.getElementById('auth-toggle');
  document.getElementById('auth-username').placeholder = t('auth.username');
  document.getElementById('auth-email').placeholder = t('auth.email');
  document.getElementById('auth-password').placeholder = t('auth.password');
  if (mode.value === 'login') {
    title.textContent = t('auth.login');
    submit.textContent = t('auth.login_btn');
    toggle.textContent = t('auth.register_switch');
  } else {
    title.textContent = t('auth.register');
    submit.textContent = t('auth.register_btn');
    toggle.textContent = t('auth.login_switch');
  }
}

async function request(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);
  if (token) opts.headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API}${path}`, opts);
  if (res.status === 429) throw new Error(t('auth.error.429'));
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || t('auth.error.failed'));
  }
  if (res.status === 204) return null;
  return res.json();
}

function showPage(name) {
  document.querySelectorAll('main > section').forEach(s => s.style.display = 'none');
  document.getElementById(`page-${name}`).style.display = 'block';
}

function showTasks() {
  showPage('tasks');
  loadTasks();
}

function showAdmin() {
  showPage('admin');
  loadAdmin();
}

function showProfile() {
  showPage('profile');
  document.querySelector('#page-profile h2').textContent = t('profile.title');
  document.getElementById('profile-email').placeholder = t('profile.email');
  document.getElementById('profile-old-pw').placeholder = t('profile.old_pw');
  document.getElementById('profile-new-pw').placeholder = t('profile.new_pw');
  document.querySelector('#profile-form button').textContent = t('profile.save');
}

function toggleAuth() {
  const mode = document.getElementById('auth-mode');
  const email = document.getElementById('auth-email');

  if (mode.value === 'login') {
    mode.value = 'register';
    email.style.display = 'block';
  } else {
    mode.value = 'login';
    email.style.display = 'none';
  }
  document.getElementById('auth-error').textContent = '';
  updateAuthUI();
}

async function handleAuth(e) {
  e.preventDefault();
  const mode = document.getElementById('auth-mode').value;
  const username = document.getElementById('auth-username').value;
  const password = document.getElementById('auth-password').value;
  const errorEl = document.getElementById('auth-error');
  errorEl.textContent = '';

  try {
    if (mode === 'register') {
      const email = document.getElementById('auth-email').value;
      await request('POST', '/auth/register', { username, email, password });
      errorEl.textContent = t('auth.success');
      errorEl.className = 'success';
      toggleAuth();
      return;
    }
    const data = await request('POST', '/auth/login', { username, password });
    token = data.access_token;
    localStorage.setItem('token', token);
    await loadApp();
  } catch (err) {
    errorEl.textContent = err.message;
    errorEl.className = 'error';
  }
}

async function loadApp() {
  document.getElementById('page-auth').style.display = 'none';
  document.getElementById('nav-tasks').style.display = 'inline';
  document.getElementById('nav-profile').style.display = 'inline';
  document.getElementById('nav-api').style.display = 'inline';
  document.getElementById('nav-logout').style.display = 'inline';
  document.getElementById('online-dot').style.display = 'inline-block';
  applyLang();

  currentUser = await request('GET', '/users/me');
  if (currentUser.role === 'admin') {
    document.getElementById('nav-admin').style.display = 'inline';
  }
  document.getElementById('online-dot').style.background = 'var(--success)';
  document.getElementById('online-dot').style.boxShadow = '0 0 8px var(--success)';
  startHeartbeat();
  showTasks();
  loadAdmin();
}

function loadTasks() {
  const list = document.getElementById('task-list');
  const empty = document.getElementById('empty-state');
  const progressText = document.getElementById('progress-text');
  const progressFill = document.getElementById('progress-fill');
  request('GET', '/tasks').then(tasks => {
    const myTasks = currentUser?.role === 'admin' ? tasks.filter(t => t.owner_id === currentUser.id) : tasks;
    const total = myTasks.length;
    const done = myTasks.filter(t => t.completed).length;
    progressText.textContent = `${done} / ${total}`;
    progressFill.style.width = total > 0 ? `${(done / total) * 100}%` : '0%';
    if (total === 0) {
      list.style.display = 'none';
      empty.style.display = 'block';
      return;
    }
    list.style.display = '';
    empty.style.display = 'none';
    list.innerHTML = tasks.map(task => `
      <li id="task-${task.id}" class="${task.completed ? 'completed' : ''}" data-id="${task.id}">
        <div class="task-info">
          <strong>${escapeHtml(task.title)}</strong>
          <span>${escapeHtml(task.description)}</span>
          ${currentUser && currentUser.role === 'admin' ? `<small class="owner">— ${escapeHtml(task.owner_name)}</small>` : ''}
        </div>
        <div class="task-actions">
          <button data-action="toggle" data-completed="${!task.completed}">${task.completed ? t('tasks.undo') : t('tasks.done')}</button>
          <button data-action="edit">${t('tasks.edit')}</button>
          <button class="delete" data-action="delete">${t('tasks.delete')}</button>
        </div>
      </li>
    `).join('');
  }).catch(err => {
    list.style.display = '';
    empty.style.display = 'none';
    list.innerHTML = `<li class="error" style="text-align:center;padding:1rem">${escapeHtml(err.message)}</li>`;
  });
}

function editTask(id) {
  const li = document.getElementById(`task-${id}`);
  const info = li.querySelector('.task-info');
  const title = info.querySelector('strong').textContent;
  const desc = info.querySelector('span').textContent;
  li.innerHTML = `
    <div class="task-info">
      <input type="text" id="edit-title-${id}" value="${escapeHtml(title)}" placeholder="${t('tasks.title_ph')}">
      <input type="text" id="edit-desc-${id}" value="${escapeHtml(desc)}" placeholder="${t('tasks.desc_ph')}">
    </div>
    <div class="task-actions">
      <button data-action="save" data-id="${id}">${t('tasks.save')}</button>
      <button data-action="cancel">${t('tasks.cancel')}</button>
    </div>
  `;
}

async function saveTask(id) {
  const title = document.getElementById(`edit-title-${id}`).value;
  const desc = document.getElementById(`edit-desc-${id}`).value;
  try {
    await request('PUT', `/tasks/${id}`, { title, description: desc });
    loadTasks();
  } catch (err) {
    const li = document.getElementById(`task-${id}`);
    const actions = li.querySelector('.task-actions');
    const errEl = document.createElement('p');
    errEl.className = 'error';
    errEl.textContent = err.message;
    actions.after(errEl);
  }
}

async function handleTaskSubmit(e) {
  e.preventDefault();
  const btn = document.querySelector('#task-form button');
  const title = document.getElementById('task-title').value;
  const desc = document.getElementById('task-desc').value;
  const errorEl = document.getElementById('task-error');
  errorEl.textContent = '';
  btn.classList.add('loading');
  try {
    await request('POST', '/tasks', { title, description: desc });
    document.getElementById('task-title').value = '';
    document.getElementById('task-desc').value = '';
    loadTasks();
  } catch (err) {
    errorEl.textContent = err.message;
    errorEl.className = 'error';
  } finally {
    btn.classList.remove('loading');
  }
}

async function toggleTask(id, completed) {
  await request('PUT', `/tasks/${id}`, { completed });
  loadTasks();
}

async function deleteTask(id) {
  await request('DELETE', `/tasks/${id}`);
  loadTasks();
}

function loadAdmin() {
  if (!currentUser || currentUser.role !== 'admin') return;
  const body = document.getElementById('admin-body');
  request('GET', '/users').then(users => {
    body.innerHTML = users.map(u => `
      <tr data-id="${u.id}">
        <td>${u.id}</td>
        <td>${escapeHtml(u.username)}</td>
        <td>${escapeHtml(u.email)}</td>
        <td>
          <select data-action="role" ${u.id === currentUser.id ? 'disabled' : ''}>
            <option value="user" ${u.role === 'user' ? 'selected' : ''}>user</option>
            <option value="admin" ${u.role === 'admin' ? 'selected' : ''}>admin</option>
          </select>
        </td>
        <td>${u.last_login ? new Date(u.last_login).toLocaleString() : t('admin.never')}</td>
        <td>${statusBadge(u)}</td>
        <td>
          <button data-action="status" data-active="${!u.is_active}" ${u.id === currentUser.id ? 'disabled' : ''}>
            ${u.is_active ? t('admin.block') : t('admin.unblock')}
          </button>
          <button class="delete" data-action="delete" ${u.id === currentUser.id ? 'disabled' : ''}>${t('admin.delete')}</button>
        </td>
      </tr>
    `).join('');
  }).catch(err => {
    body.innerHTML = `<tr><td colspan="6" class="error" style="text-align:center">${escapeHtml(err.message)}</td></tr>`;
  });
}

async function deleteUser(id) {
  if (!confirm(t('admin.delete_confirm'))) return;
  await request('DELETE', `/users/${id}`);
  loadAdmin();
}

async function toggleUserStatus(id, isActive) {
  await request('PATCH', `/users/${id}/status`, { is_active: isActive });
  loadAdmin();
}

async function changeRole(id, role) {
  await request('PATCH', `/users/${id}/role`, { role });
  loadAdmin();
}

async function handleProfileUpdate(e) {
  e.preventDefault();
  const email = document.getElementById('profile-email').value;
  const oldPassword = document.getElementById('profile-old-pw').value;
  const newPassword = document.getElementById('profile-new-pw').value;
  const errorEl = document.getElementById('profile-error');
  errorEl.textContent = '';

  const body = {};
  if (email) body.email = email;
  if (oldPassword && newPassword) {
    body.old_password = oldPassword;
    body.new_password = newPassword;
  } else if (newPassword && !oldPassword) {
    errorEl.textContent = t('profile.need_old');
    errorEl.className = 'error';
    return;
  }

  if (Object.keys(body).length === 0) {
    errorEl.textContent = t('profile.empty');
    errorEl.className = 'error';
    return;
  }

  try {
    await request('PUT', '/users/me', body);
    currentUser = await request('GET', '/users/me');
    errorEl.textContent = t('profile.updated');
    errorEl.className = 'success';
    document.getElementById('profile-email').value = '';
    document.getElementById('profile-old-pw').value = '';
    document.getElementById('profile-new-pw').value = '';
  } catch (err) {
    errorEl.textContent = err.message;
    errorEl.className = 'error';
  }
}

function logout() {
  token = null;
  localStorage.removeItem('token');
  document.getElementById('page-tasks').style.display = 'none';
  document.getElementById('page-admin').style.display = 'none';
  document.getElementById('nav-tasks').style.display = 'none';
  document.getElementById('nav-profile').style.display = 'none';
  document.getElementById('nav-admin').style.display = 'none';
  document.getElementById('nav-api').style.display = 'none';
  document.getElementById('nav-logout').style.display = 'none';
  document.getElementById('online-dot').style.display = 'none';
  document.getElementById('page-auth').style.display = 'block';
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function isOnline(u) {
  if (!u.last_activity) return false;
  const ts = u.last_activity.includes('T') && !u.last_activity.endsWith('Z') && !u.last_activity.includes('+')
    ? u.last_activity + 'Z' : u.last_activity;
  const diff = Date.now() - new Date(ts).getTime();
  return diff < 5 * 60 * 1000;
}

function statusBadge(u) {
  if (!u.is_active) {
    return `<span class="status-badge status-blocked">${t('admin.blocked')}</span>`;
  }
  if (isOnline(u)) {
    return `<span class="status-badge status-active">${t('admin.active')}</span>`;
  }
  return `<span class="status-badge status-offline">${t('admin.offline')}</span>`;
}

function startHeartbeat() {
  setInterval(() => {
    request('GET', '/users/me').then(u => {
      currentUser = u;
      const dot = document.getElementById('online-dot');
      if (isOnline(u)) {
        dot.style.background = 'var(--success)';
        dot.style.boxShadow = '0 0 8px var(--success)';
      } else {
        dot.style.background = 'var(--text-muted)';
        dot.style.boxShadow = 'none';
      }
    }).catch(() => {});
  }, 2 * 60 * 1000);
}

// Event bindings (вместо inline onclick/onsubmit)
document.getElementById('nav-lang').addEventListener('click', toggleLang);
document.getElementById('nav-tasks').addEventListener('click', showTasks);
document.getElementById('nav-profile').addEventListener('click', showProfile);
document.getElementById('nav-admin').addEventListener('click', showAdmin);
document.getElementById('nav-api').addEventListener('click', () => window.open('/docs', '_blank'));
document.getElementById('nav-logout').addEventListener('click', logout);
document.getElementById('auth-form').addEventListener('submit', handleAuth);
document.getElementById('auth-toggle').addEventListener('click', e => { e.preventDefault(); toggleAuth(); });
document.getElementById('task-form').addEventListener('submit', handleTaskSubmit);
document.getElementById('profile-form').addEventListener('submit', handleProfileUpdate);

// Делегирование для динамических кнопок в списке задач
document.getElementById('task-list').addEventListener('click', e => {
  const btn = e.target.closest('button[data-action]');
  if (!btn) return;
  const li = btn.closest('[data-id]');
  const id = Number(li?.dataset.id);
  if (!id) return;
  const action = btn.dataset.action;
  if (action === 'toggle') toggleTask(id, btn.dataset.completed === 'true');
  else if (action === 'edit') editTask(id);
  else if (action === 'delete') deleteTask(id);
  else if (action === 'save') saveTask(id);
  else if (action === 'cancel') loadTasks();
});

// Делегирование для админки
document.getElementById('admin-body').addEventListener('click', e => {
  const btn = e.target.closest('button[data-action]');
  if (!btn) return;
  const tr = btn.closest('tr[data-id]');
  const id = Number(tr?.dataset.id);
  if (!id) return;
  const action = btn.dataset.action;
  if (action === 'status') toggleUserStatus(id, btn.dataset.active === 'true');
  else if (action === 'delete') deleteUser(id);
});

document.getElementById('admin-body').addEventListener('change', e => {
  const sel = e.target.closest('select[data-action]');
  if (!sel) return;
  const tr = sel.closest('tr[data-id]');
  const id = Number(tr?.dataset.id);
  if (!id) return;
  changeRole(id, sel.value);
});

// Init
applyLang();
if (token) {
  loadApp().catch(() => {
    token = null;
    localStorage.removeItem('token');
    document.getElementById('page-auth').style.display = 'block';
  });
}
