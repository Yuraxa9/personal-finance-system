import { useState } from 'react'
import Button from './Button'
import Input from './Input'

const ACCOUNT_TYPES = [
  { value: 'cash', label: 'Наличные' },
  { value: 'card', label: 'Карта' },
  { value: 'savings', label: 'Накопления' },
]

const CURRENCIES = ['RUB', 'USD', 'EUR']

function getInitialForm(initialData) {
  return {
    name: initialData?.name ?? '',
    account_type: initialData?.account_type ?? 'cash',
    balance: initialData?.balance ?? '',
    currency: initialData?.currency ?? 'RUB',
  }
}

export default function AccountForm({ initialData, onSubmit, onCancel }) {
  const [form, setForm] = useState(() => getInitialForm(initialData))
  const [errors, setErrors] = useState({})
  const [submitError, setSubmitError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }))
  }

  function validate() {
    const nextErrors = {}

    if (!form.name.trim()) nextErrors.name = 'Введите название счёта'
    if (form.balance === '') nextErrors.balance = 'Введите баланс'
    if (Number.isNaN(Number(form.balance))) nextErrors.balance = 'Введите число'

    return nextErrors
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const nextErrors = validate()

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors)
      return
    }

    setErrors({})
    setSubmitError('')
    setIsSubmitting(true)

    try {
      await onSubmit({
        name: form.name.trim(),
        account_type: form.account_type,
        balance: form.balance,
        currency: form.currency,
      })
    } catch {
      setSubmitError('Не удалось сохранить счёт')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <Input
        label="Название"
        value={form.name}
        onChange={(event) => updateField('name', event.target.value)}
        placeholder="Основная карта"
        error={errors.name}
      />

      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">Тип счёта</label>
        <select
          value={form.account_type}
          onChange={(event) => updateField('account_type', event.target.value)}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
        >
          {ACCOUNT_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
      </div>

      <Input
        label="Баланс"
        type="number"
        step="0.01"
        value={form.balance}
        onChange={(event) => updateField('balance', event.target.value)}
        placeholder="0.00"
        error={errors.balance}
      />

      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">Валюта</label>
        <select
          value={form.currency}
          onChange={(event) => updateField('currency', event.target.value)}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
        >
          {CURRENCIES.map((currency) => (
            <option key={currency} value={currency}>
              {currency}
            </option>
          ))}
        </select>
      </div>

      {submitError && (
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
          {submitError}
        </p>
      )}

      <div className="mt-2 grid grid-cols-2 gap-3">
        <Button variant="secondary" onClick={onCancel} disabled={isSubmitting}>
          Отмена
        </Button>
        <Button type="submit" loading={isSubmitting}>
          Сохранить
        </Button>
      </div>
    </form>
  )
}
