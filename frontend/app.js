const API_BASE = 'http://localhost:8000';

// --- Token Management ---

function getAccessToken() {
  return localStorage.getItem('access_token');
}

function getRefreshToken() {
  return localStorage.getItem('refresh_token');
}

function saveTokens(accessToken, refreshToken) {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
}

function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
}

function saveUser(user) {
  localStorage.setItem('user', JSON.stringify(user));
}

function getUser() {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
}

function isLoggedIn() {
  return !!getAccessToken();
}

function logout() {
  clearTokens();
  window.location.href = '/frontend/index.html';
}

// --- API Calls ---

async function apiCall(endpoint, method = 'GET', body = null) {
  const headers = {
    'Content-Type': 'application/json',
  };

  const token = getAccessToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = { method, headers };
  if (body) {
    config.body = JSON.stringify(body);
  }

  let response = await fetch(`${API_BASE}${endpoint}`, config);

  // token expired — try refresh
  if (response.status === 401) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      headers['Authorization'] = `Bearer ${getAccessToken()}`;
      response = await fetch(`${API_BASE}${endpoint}`, { method, headers, body: body ? JSON.stringify(body) : null });
    } else {
      logout();
      return null;
    }
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Something went wrong');
  }

  if (response.status === 204) return null;
  return response.json();
}

async function tryRefreshToken() {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;

  try {
    const response = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken })
    });

    if (!response.ok) return false;

    const data = await response.json();
    saveTokens(data.access_token, data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

// --- Auth Guard ---

function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = '/frontend/index.html';
    return false;
  }
  return true;
}

function redirectIfLoggedIn() {
  if (isLoggedIn()) {
    window.location.href = '/frontend/dashboard.html';
  }
}

// --- Formatting Helpers ---

function formatCurrency(amount) {
  return '₹' + parseFloat(amount).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

function formatDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  });
}

function formatTime(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit'
  });
}

function getTransactionEmoji(transaction) {
  if (transaction.category === 'allocation') return '💰';
  if (transaction.category === 'penalty') return '⚠️';
  if (transaction.type === 'credit') return '📥';
  const cat = (transaction.category || '').toLowerCase();
  const emojis = {
    food: '🍔', rent: '🏠', shopping: '🛍️',
    medical: '💊', travel: '✈️', entertainment: '🎬',
    utilities: '💡', savings: '🏦', gift: '🎁'
  };
  return emojis[cat] || '💳';
}

function getBalancePercentage(current, allocated) {
  if (!allocated || allocated === 0) return 0;
  return Math.min(100, Math.round((current / allocated) * 100));
}

function showAlert(containerId, message, type = 'danger') {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
  setTimeout(() => { container.innerHTML = ''; }, 4000);
}

function showLoading(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = `
    <div class="loading">
      <div class="spinner"></div>
      Loading...
    </div>`;
}

// --- Store vault data globally for reuse across pages ---
let cachedVaults = [];
let cachedBankAccounts = [];

async function loadVaults() {
  try {
    cachedVaults = await apiCall('/vaults');
    return cachedVaults;
  } catch {
    return [];
  }
}

async function loadBankAccounts() {
  try {
    cachedBankAccounts = await apiCall('/bank-accounts');
    return cachedBankAccounts;
  } catch {
    return [];
  }
}