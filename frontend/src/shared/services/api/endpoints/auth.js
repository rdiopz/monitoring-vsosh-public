import api from '../client'

export const authAPI = {
  // Аутентификация
  login: (data) => api.post('/auth/login/', data),
  refreshToken: () => api.post('/auth/refresh/'),

  // Сессии (Пользователь)
  getSessions: () => api.get('/auth/session/'),
  revokeSession: (jti) => api.delete(`/auth/session/${jti}/`),
  logout: () => api.post('/auth/session/logout/'),
  logoutAll: () => api.post('/auth/session/logout-others/'),

  // Сессии (Администратор)
  getAllSessions: (params) => api.get('/auth/session/all', { params }),
  revokeSessionByFingerprint: (data) => api.post('/auth/session/revoke-by-fingerprint/', data),
  revokeAllUserSessions: (data) => api.post('/auth/session/revoke-all-user-sessions/', data),
  adminDestroySession: (jti) => api.delete(`/auth/session/admin/${jti}/`),

  // Профиль
  getProfile: () => api.get('/auth/user/me/'),
  updateProfile: (data) => api.put('/auth/user/me/', data),
  updateProfilePartial: (data) => api.patch('/auth/user/me/', data),
  changePassword: (data) => api.post('/auth/user/me/change-password/', data),

  // Пользователи (Администратор)
  getUsers: (params) => api.get('/auth/user/', { params }),
  getUser: (id) => api.get(`/auth/user/${id}/`),
  updateUser: (id, data) => api.put(`/auth/user/${id}/`, data),
  updateUserPartial: (id, data) => api.patch(`/auth/user/${id}/`, data),
  getReviewers: () => api.get('/auth/user/reviewers/'),

  // Заявки
  checkApplicationStatus: (data) => api.post('/auth/application/check-status/', data),
  registerApplication: (data) => api.post('/auth/application/', data),
  getApplications: (params) => api.get('/auth/application/', { params }),
  getApplication: (id) => api.get(`/auth/application/${id}/`),
  reviewApplication: (id, data) => api.post(`/auth/application/${id}/review/`, data),
  updateApplication: (id, data) => api.put(`/auth/application/${id}/`, data),
  partialUpdateApplication: (id, data) => api.patch(`/auth/application/${id}/`, data),
  deleteApplication: (id) => api.delete(`/auth/application/${id}/`),

  // Настройки
  getSettings: () => api.get('/auth/setting/'),
  updateSetting: (key, data) => api.put(`/auth/setting/${key}/`, data),
  getMonitoringYears: () => api.get('/auth/setting/monitoring-years/'),
  verifyCode: (data) => api.post('/auth/setting/verify-code/', data),

  // Роли
  getRoles: () => api.get('/auth/roles/'),

  // Журнал аудита
  getAuditLogs: (params) => api.get('/auth/audit-log/', { params }),
  getAuditLog: (id) => api.get(`/auth/audit-log/${id}/`),
  getAuditLogFilters: () => api.get('/auth/audit-log/filters/'),
}
