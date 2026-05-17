export function formatCurrency(amount, currency = 'RUB') {
  return Number(amount).toLocaleString('ru-RU', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

export function formatDate(date) {
  return new Date(date).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

export function formatDateShort(date) {
  return new Date(date).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

export function formatDateTime(date) {
  return new Date(date).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const TX_TYPE_LABELS = { income: 'Доход', expense: 'Расход', transfer: 'Перевод' }
export function formatTransactionType(type) {
  return TX_TYPE_LABELS[type] ?? type
}

const ACCOUNT_TYPE_LABELS = { cash: 'Наличные', card: 'Карта', savings: 'Накопления' }
export function formatAccountType(type) {
  return ACCOUNT_TYPE_LABELS[type] ?? type
}
