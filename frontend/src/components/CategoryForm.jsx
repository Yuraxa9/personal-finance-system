import { useState } from 'react'
import Button from './Button'
import Input from './Input'

const CATEGORY_TYPES = [
  { value: 'expense', label: 'Расход' },
  { value: 'income', label: 'Доход' },
]

const PRESET_ICONS = ['🛒', '🍔', '🚗', '🏠', '💊', '🎬', '✈️', '📚', '💪', '🐾', '💡', '🎁']

function getInitialForm(initialData) {
  return {
    name: initialData?.name ?? '',
    category_type: initialData?.category_type ?? 'expense',
    color: initialData?.color ?? '#6366f1',
    icon: initialData?.icon ?? '🛒',
  }
}

export default function CategoryForm({ initialData, onSubmit, onCancel }) {
  const [form, setForm] = useState(() => getInitialForm(initialData))
  const [errors, setErrors] = useState({})
  const [submitError, setSubmitError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  function updateField(field, value) {
    setForm((cur) => ({ ...cur, [field]: value }))
  }

  function validate() {
    const next = {}
    if (!form.name.trim()) next.name = 'Введите название'
    if (!form.icon.trim()) next.icon = 'Введите иконку'
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
      await onSubmit({ name: form.name.trim(), category_type: form.category_type, color: form.color, icon: form.icon.trim() })
    } catch {
      setSubmitError('Не удалось сохранить категорию')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <Input
        label="Название"
        value={form.name}
        onChange={(e) => updateField('name', e.target.value)}
        placeholder="Продукты"
        error={errors.name}
      />

      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">Тип</label>
        <select
          value={form.category_type}
          onChange={(e) => updateField('category_type', e.target.value)}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
        >
          {CATEGORY_TYPES.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
      </div>

      <div className="flex gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Цвет</label>
          <input
            type="color"
            value={form.color}
            onChange={(e) => updateField('color', e.target.value)}
            className="h-10 w-16 cursor-pointer rounded-lg border border-gray-300 p-1"
          />
        </div>
        <div className="flex flex-1 flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Иконка</label>
          <Input
            value={form.icon}
            onChange={(e) => updateField('icon', e.target.value)}
            placeholder="🛒"
            error={errors.icon}
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {PRESET_ICONS.map((ic) => (
          <button
            key={ic}
            type="button"
            onClick={() => updateField('icon', ic)}
            className={`rounded-lg p-1.5 text-xl transition hover:bg-gray-100 ${form.icon === ic ? 'bg-gray-100 ring-2 ring-blue-400' : ''}`}
          >
            {ic}
          </button>
        ))}
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
