import api from '../client'
import { serializeParams } from '@utils/params'

export const vsoshAPI = {
  // Муниципалитеты
  getMunicipalities: (params) => api.get('/vsosh/municipality/', { params }),
  getMunicipality: (id) => api.get(`/vsosh/municipality/${id}/`),
  createMunicipality: (data) => api.post('/vsosh/municipality/', data),
  updateMunicipality: (id, data) => api.put(`/vsosh/municipality/${id}/`, data),
  partialUpdateMunicipality: (id, data) => api.patch(`/vsosh/municipality/${id}/`, data),
  deleteMunicipality: (id) => api.delete(`/vsosh/municipality/${id}/`),
  exportMunicipalities: (params) =>
    api.get('/vsosh/municipality/export/', {
      params,
      paramsSerializer: serializeParams,
      responseType: 'blob',
    }),
  importMunicipalities: (formData) =>
    api.post('/vsosh/municipality/import_data/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  // Предметы
  getSubjects: (params) => api.get('/vsosh/subject/', { params }),
  getSubject: (id) => api.get(`/vsosh/subject/${id}/`),
  createSubject: (data) => api.post('/vsosh/subject/', data),
  updateSubject: (id, data) => api.put(`/vsosh/subject/${id}/`, data),
  partialUpdateSubject: (id, data) => api.patch(`/vsosh/subject/${id}/`, data),
  deleteSubject: (id) => api.delete(`/vsosh/subject/${id}/`),
  exportSubjects: (params) =>
    api.get('/vsosh/subject/export/', {
      params,
      paramsSerializer: serializeParams,
      responseType: 'blob',
    }),
  importSubjects: (formData) =>
    api.post('/vsosh/subject/import_data/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  // Участники
  getParticipants: (params) => api.get('/vsosh/participant/', { params }),
  getParticipant: (id) => api.get(`/vsosh/participant/${id}/`),
  createParticipant: (data) => api.post('/vsosh/participant/', data),
  updateParticipant: (id, data) => api.put(`/vsosh/participant/${id}/`, data),
  partialUpdateParticipant: (id, data) => api.patch(`/vsosh/participant/${id}/`, data),
  deleteParticipant: (id) => api.delete(`/vsosh/participant/${id}/`),
  exportParticipants: (params) =>
    api.get('/vsosh/participant/export/', {
      params,
      paramsSerializer: serializeParams,
      responseType: 'blob',
    }),
  importParticipants: (formData) =>
    api.post('/vsosh/participant/import_data/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  searchParticipants: (params) =>
    api.get('/vsosh/participant/search/', {
      params,
      paramsSerializer: serializeParams,
    }),

  // Школы
  getSchools: (params) => api.get('/vsosh/education-institution/', { params }),
  getSchool: (id) => api.get(`/vsosh/education-institution/${id}/`),
  createSchool: (data) => api.post('/vsosh/education-institution/', data),
  updateSchool: (id, data) => api.put(`/vsosh/education-institution/${id}/`, data),
  partialUpdateSchool: (id, data) => api.patch(`/vsosh/education-institution/${id}/`, data),
  deleteSchool: (id) => api.delete(`/vsosh/education-institution/${id}/`),
  exportSchools: (params) =>
    api.get('/vsosh/education-institution/export/', {
      params,
      paramsSerializer: serializeParams,
      responseType: 'blob',
    }),
  importSchools: (formData) =>
    api.post('/vsosh/education-institution/import_data/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getSchoolFilters: () => api.get('/vsosh/education-institution/filters/'),

  // Олимпиады
  getOlympiadParticipations: (params) => api.get('/vsosh/olympiad-participation/', { params }),
  getOlympiadParticipation: (id) => api.get(`/vsosh/olympiad-participation/${id}/`),
  createOlympiadParticipation: (data) => api.post('/vsosh/olympiad-participation/', data),
  updateOlympiadParticipation: (id, data) => api.put(`/vsosh/olympiad-participation/${id}/`, data),
  partialUpdateOlympiadParticipation: (id, data) =>
    api.patch(`/vsosh/olympiad-participation/${id}/`, data),
  deleteOlympiadParticipation: (id) => api.delete(`/vsosh/olympiad-participation/${id}/`),
  exportOlympiadParticipations: (params) =>
    api.get('/vsosh/olympiad-participation/export/', {
      params,
      paramsSerializer: serializeParams,
      responseType: 'blob',
    }),
  importOlympiadParticipations: (formData) =>
    api.post('/vsosh/olympiad-participation/import_data/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getOlympiadFilters: () => api.get('/vsosh/olympiad-participation/filters/'),

  // Дашборд
  getDashboard: (params) =>
    api.get('/vsosh/dashboard/', {
      params,
      paramsSerializer: serializeParams,
    }),
  getParticipantDashboard: (participantId, params) =>
    api.get(`/vsosh/dashboard/participants/${participantId}/`, {
      params,
      paramsSerializer: serializeParams,
    }),

  // Отчёты
  getReportsList: () => api.get('/vsosh/reports/'),
  generateReport: (reportKey, params = {}) =>
    api.get(`/vsosh/reports/${reportKey}/`, {
      params,
      paramsSerializer: serializeParams,
      responseType: 'blob',
    }),
}
