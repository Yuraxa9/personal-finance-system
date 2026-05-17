import { useEffect, useState } from 'react'
import { getAccounts } from '../api/accounts'
import { getCategories } from '../api/categories'
import Button from './Button'
import Input from './Input'

const TX_TYPES = [
  { value: 'income', label: 'Доход' },
  { value: 'expense', label: 'Расход' },
  { value: 'transfer', label: 'Перевод' },
]

function toDatetimeLocal(iso) {
  if (!iso) return ''
  return new Date(iso).toISOString().slice(0, 16)
}

function getInitialForm(initialData) {
  return {
    account_id: initialData?.account_id ?? '',
    category_id: initialData?.category_id ?? '',
    transaction_type: initialData?.transaction_type ?? 'expense',
    amount: initialData?.amount ?? '',
    description: initialData?.description ?? '',
    date: toDatetimeLocal(initialData?.date) || toDatetimeLocal(new Date().toISOString()),
  }
}

export default function TransactionForm({ initialData, onSubmit, onCancel }) {
  const [form, setForm] = useState(() => getInitialForm(initialData))
  const [accounts, setAccounts] = useState([])
  const [categories, setCategories] = useState([])
  const [errors, setErrors] = useState({})
  const [submitError, setSubmitError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    Promise.all([getAccounts(), getCategories()])
      .then(([accRes, catRes]) => {
        setAccounts(accRes.data)
        setCategories(catRes.data)
        if (!form.account_id && accRes.data.length > 0) {
          setForm((f) => ({ ...f, account_id: accRes.data[0].id }))
        }
      })
      .catch(() => {})
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  function validate() {
    const next = {}
    if (!form.account_id) next.account_id = 'Выберите счёт'
    if (!form.amount || Number(form.amount) <= 0) next.amount = 'Введите положительную сумму'
    if (!form.date) next.date = 'Укажите дату'
    return next
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const next = validate()
    if (Object.keys(next).length > 0) { setErrors(next); return }
    setErrors({})
    setSubmitError('')
    setIsSubmitting(true)
    try {
      await onSubmit({
        account_id: form.account_id,
        category_id: form.category_id || null,
        transaction_type: form.transaction_type,
        amount: form.amount,
        description: form.description || null,
        date: new Date(form.date).toISOString(),
      })
    } catch {
      setSubmitError('Не удалось сохранить транзакцию')
    } finally {
      setIsSubmitting(false)
    }
  }

  const filteredCategories = categories.filter(
    (c) => c.category_type === form.transaction_type || form.transaction_type === 'transfer',
  )

  const selectCls =
    'w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100'

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      {/* Account */}
      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">Счёт</label>
        <select value={form.account_id} onChange={(e) => update('account_id', e.target.value)} className={selectCls}>
          <option value="">— выберите счёт —</option>
          {accounts.map((a) => (
            <option key={a.id} value={a.id}>{a.name}</option>
          ))}
        </select>
        {errors.account_id && <span className="text-xs text-red-500">{errors.account_id}</span>}
      </div>

      {/* Type */}
      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">Тип</label>
        <select value={form.transaction_type} onChange={(e) => update('transaction_type', e.target.value)} className={selectCls}>
          {TX_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
        </select>
      </div>

      {/* Category */}
      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">Категория <span className="text-gray-400">(необязательно)</span></label>
        <select value={form.category_id} onChange={(e) => update('category_id', e.target.value)} className={selectCls}>
          <option value="">— без категории —</option>
          {filteredCategories.map((c) => (
            <option key={c.id} value={c.id}>{c.icon} {c.name}</option>
          ))}
        </select>
      </div>

      {/* Amount */}
      <Input
        label="Сумма"
        type="number"
        step="0.01"
        min="0.01"
        value={form.amount}
        onChange={(e) => update('amount', e.target.value)}
        placeholder="0.00"
        error={errors.amount}
      />

      {/* Date */}
      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">Дата и время</label>
        <input
          type="datetime-local"
          value={form.date}
          onChange={(e) => update('date', e.target.value)}
          className={selectCls}
        />
        {errors.date && <span className="text-xs text-red-500">{errors.date}</span>}
      </div>

      {/* Description */}
      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">Описание <span className="text-gray-400">(необязательно)</span></label>
        <textarea
          value={form.description}
          onChange={(e) => update('description', e.target.value)}
          placeholder="Комментарий к транзакции…"
          rows={2}
          className="w-full resize-none rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
        />
      </div>

      {submitError && (
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{submitError}</p>
      )}

      <div className="mt-2 grid grid-cols-2 gap-3">
        <Button variant="secondary" onClick={onCancel} disabled={isSubmitting}>Отмена</Button>
        <Button type="submit" loading={isSubmitting}>Сохранить</Button>
      </div>
    </form>
  )
}
