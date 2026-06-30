const API = '/api';
let token = localStorage.getItem('token');
let currentUser = null;

async function request(method, path, body) {
    const opts = {
        method,
        headers: { 'Content-Type': 'application/json' },
    };
    if (body) opts.body = JSON.stringify(body);
    if (token) opts.headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API}${path}`, opts);
    if (res.status === 429) throw new Error('Too many requests. Slow down!');
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || 'Request failed');
    }
    if (res.status === 204) return null;
    return res.json();
}

function showPage(name) {
    document.querySelectorAll('main > section').forEach(s => s.style.display = 'none');
    document.getElementById(`page-${name}`).style.display = 'block';
}

function toggleAuth() {
    const mode = document.getElementById('auth-mode');
    const email = document.getElementById('auth-email');
    const title = document.getElementById('auth-title');
    const submit = document.getElementById('auth-submit');
    const toggle = document.getElementById('auth-toggle');

    if (mode.value === 'login') {
        mode.value = 'register';
        email.style.display = 'block';
        title.textContent = 'Register';
        submit.textContent = 'Register';
        toggle.textContent = 'Login instead';
    } else {
        mode.value = 'login';
        email.style.display = 'none';
        title.textContent = 'Login';
        submit.textContent = 'Login';
        toggle.textContent = 'Register instead';
    }
    document.getElementById('auth-error').textContent = '';
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
            errorEl.textContent = 'Registration successful! Please login.';
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
    document.getElementById('nav-logout').style.display = 'inline';

    currentUser = await request('GET', '/users/me');
    if (currentUser.role === 'admin') {
        document.getElementById('nav-admin').style.display = 'inline';
    }
    showPage('tasks');
    loadTasks();
    loadAdmin();
}

async function loadTasks() {
    const tasks = await request('GET', '/tasks');
    const list = document.getElementById('task-list');
    list.innerHTML = tasks.map(t => `
        <li class="${t.completed ? 'completed' : ''}">
            <div class="task-info">
                <strong>${escapeHtml(t.title)}</strong>
                <span>${escapeHtml(t.description)}</span>
            </div>
            <div class="task-actions">
                <button onclick="toggleTask(${t.id}, ${!t.completed})">${t.completed ? 'Undo' : 'Done'}</button>
                <button class="delete" onclick="deleteTask(${t.id})">Delete</button>
            </div>
        </li>
    `).join('');
}

async function handleTaskSubmit(e) {
    e.preventDefault();
    const title = document.getElementById('task-title').value;
    const desc = document.getElementById('task-desc').value;
    await request('POST', '/tasks', { title, description: desc });
    document.getElementById('task-title').value = '';
    document.getElementById('task-desc').value = '';
    loadTasks();
}

async function toggleTask(id, completed) {
    await request('PUT', `/tasks/${id}`, { completed });
    loadTasks();
}

async function deleteTask(id) {
    await request('DELETE', `/tasks/${id}`);
    loadTasks();
}

async function loadAdmin() {
    if (!currentUser || currentUser.role !== 'admin') return;
    try {
        const users = await request('GET', '/users');
        const body = document.getElementById('admin-body');
        body.innerHTML = users.map(u => `
            <tr>
                <td>${u.id}</td>
                <td>${escapeHtml(u.username)}</td>
                <td>${escapeHtml(u.email)}</td>
                <td>${u.role}</td>
                <td><button class="delete" onclick="deleteUser(${u.id})" ${u.id === currentUser.id ? 'disabled' : ''}>Delete</button></td>
            </tr>
        `).join('');
    } catch (e) {
        // not admin
    }
}

async function deleteUser(id) {
    if (!confirm('Delete this user?')) return;
    await request('DELETE', `/users/${id}`);
    loadAdmin();
}

function logout() {
    token = null;
    localStorage.removeItem('token');
    document.getElementById('page-tasks').style.display = 'none';
    document.getElementById('page-admin').style.display = 'none';
    document.getElementById('nav-tasks').style.display = 'none';
    document.getElementById('nav-admin').style.display = 'none';
    document.getElementById('nav-logout').style.display = 'none';
    document.getElementById('page-auth').style.display = 'block';
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Init
if (token) {
    loadApp().catch(() => {
        token = null;
        localStorage.removeItem('token');
    });
}
