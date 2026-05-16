import client from './client'

export function login(email, password) {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  return client.post('/auth/token', form)
}

export function register(full_name, email, password) {
  return client.post('/auth/register', { full_name, email, password })
}

export function getMe() {
  return client.get('/auth/me')
}
