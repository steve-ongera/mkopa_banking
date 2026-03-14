import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";


// ─── Axios instance ───────────────────────────────────────────────────────────
const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Attach token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Handle token refresh on 401
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const refresh = localStorage.getItem('refresh_token');
        const { data } = await axios.post(`${BASE_URL}/auth/token/refresh/`, { refresh });
        localStorage.setItem('access_token', data.access);
        original.headers.Authorization = `Bearer ${data.access}`;
        return api(original);
      } catch {
        localStorage.clear();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ─── Auth ─────────────────────────────────────────────────────────────────────
export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  logout: (refresh) => api.post('/auth/logout/', { refresh }),
  refreshToken: (refresh) => api.post('/auth/token/refresh/', { refresh }),
};

// ─── Profile ──────────────────────────────────────────────────────────────────
export const profileAPI = {
  get: () => api.get('/profile/'),
  update: (data) => api.patch('/profile/', data),
  changePassword: (data) => api.post('/profile/change-password/', data),
};

// ─── Dashboard ────────────────────────────────────────────────────────────────
export const dashboardAPI = {
  get: () => api.get('/dashboard/'),
};

// ─── Accounts ─────────────────────────────────────────────────────────────────
export const accountsAPI = {
  list: () => api.get('/accounts/'),
  get: (id) => api.get(`/accounts/${id}/`),
  create: (data) => api.post('/accounts/', data),
  update: (id, data) => api.patch(`/accounts/${id}/`, data),
};

// ─── Transactions ─────────────────────────────────────────────────────────────
export const transactionsAPI = {
  list: (params) => api.get('/transactions/', { params }),
  get: (id) => api.get(`/transactions/${id}/`),
  deposit: (data) => api.post('/transactions/deposit/', data),
  withdraw: (data) => api.post('/transactions/withdraw/', data),
  transfer: (data) => api.post('/transactions/transfer/', data),
};

// ─── Cards ────────────────────────────────────────────────────────────────────
export const cardsAPI = {
  list: () => api.get('/cards/'),
  get: (id) => api.get(`/cards/${id}/`),
  update: (id, data) => api.patch(`/cards/${id}/`, data),
  toggle: (id) => api.post(`/cards/${id}/toggle/`),
};

// ─── Loans ────────────────────────────────────────────────────────────────────
export const loansAPI = {
  list: () => api.get('/loans/'),
  apply: (data) => api.post('/loans/apply/', data),
};

// ─── Beneficiaries ────────────────────────────────────────────────────────────
export const beneficiariesAPI = {
  list: () => api.get('/beneficiaries/'),
  get: (id) => api.get(`/beneficiaries/${id}/`),
  create: (data) => api.post('/beneficiaries/', data),
  update: (id, data) => api.patch(`/beneficiaries/${id}/`, data),
  delete: (id) => api.delete(`/beneficiaries/${id}/`),
};

// ─── Notifications ────────────────────────────────────────────────────────────
export const notificationsAPI = {
  list: () => api.get('/notifications/'),
  markRead: (id) => api.post(`/notifications/${id}/read/`),
  markAllRead: () => api.post('/notifications/mark-all-read/'),
};

export default api;

// ─── Analytics ────────────────────────────────────────────────────────────────
export const analyticsAPI = {
  spending: () => api.get('/analytics/spending/'),
  statement: (accountId, params) => api.get(`/analytics/statement/${accountId}/`, { params }),
  balanceHistory: () => api.get('/analytics/balance-history/'),
};