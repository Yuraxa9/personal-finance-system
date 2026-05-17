import client from './client'

export const updateProfile = (full_name) => client.patch('/auth/me', { full_name })

export const changePassword = (current_password, new_password) =>
  client.post('/auth/change-password', { current_password, new_password })
