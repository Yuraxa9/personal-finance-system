const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function validateEmail(email) {
  if (!email?.trim()) return { valid: false, error: 'Email обязателен' }
  if (!EMAIL_RE.test(email)) return { valid: false, error: 'Некорректный email' }
  return { valid: true, error: '' }
}

export function validatePassword(password) {
  if (!password) return { valid: false, error: 'Пароль обязателен' }
  if (password.length < 6) return { valid: false, error: 'Минимум 6 символов' }
  return { valid: true, error: '' }
}

export function validateAmount(amount) {
  if (amount === '' || amount === null || amount === undefined)
    return { valid: false, error: 'Сумма обязательна' }
  const num = Number(amount)
  if (isNaN(num)) return { valid: false, error: 'Введите число' }
  if (num <= 0) return { valid: false, error: 'Сумма должна быть больше нуля' }
  return { valid: true, error: '' }
}

export function validateRequired(value, fieldName) {
  if (!value || !String(value).trim())
    return { valid: false, error: `${fieldName} обязательно` }
  return { valid: true, error: '' }
}
