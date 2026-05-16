import client from './client'

export const getTransactions = (filters = {}) =>
  client.get('/transactions/', { params: filters })

export const createTransaction = (data) => client.post('/transactions/', data)

export const updateTransaction = (id, data) =>
  client.put(`/transactions/${id}`, data)

export const deleteTransaction = (id) => client.delete(`/transactions/${id}`)

export const getAnalytics = (date_from, date_to) =>
  client.get('/transactions/analytics', { params: { date_from, date_to } })
