import { useEffect, useState } from 'react'
import { createCategory, deleteCategory, getCategories } from '../api/categories'
import Button from '../components/Button'
import CategoryForm from '../components/CategoryForm'
import Modal from '../components/Modal'

const TYPE_LABEL = { income: 'Доход', expense: 'Расход' }

export default function CategoriesPage() {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('expense')
  const [showModal, setShowModal] = useState(false)
  const [deletingId, setDeletingId] = useState(null)

  async function load() {
    try {
      const { data } = await getCategories()
      setCategories(data)
    } catch {
      setError('Не удалось загрузить категории')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  async function handleCreate(data) {
    await createCategory(data)
    setShowModal(false)
    load()
  }

  async function handleDelete(id) {
    if (!window.confirm('Удалить категорию?')) return
    setDeletingId(id)
    try {
      await deleteCategory(id)
      setCategories((prev) => prev.filter((c) => c.id !== id))
    } catch {
      setError('Не удалось удалить категорию')
    } finally {
      setDeletingId(null)
    }
  }

  const filtered = categories.filter((c) => c.category_type === activeTab)

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Категории</h1>
        <Button onClick={() => setShowModal(true)}>+ Добавить категорию</Button>
      </div>

      {error && (
        <div className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-600">{error}</div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 rounded-xl bg-gray-100 p-1 w-fit">
        {['expense', 'income'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`rounded-lg px-5 py-2 text-sm font-medium transition ${
              activeTab === tab ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {TYPE_LABEL[tab]}
          </button>
        ))}
      </div>

      {/* Category cards */}
      {filtered.length === 0 ? (
        <p className="text-sm text-gray-400">
          Нет категорий типа «{TYPE_LABEL[activeTab]}». Создайте первую!
        </p>
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((cat) => (
            <div
              key={cat.id}
              className="flex items-center justify-between rounded-2xl bg-white p-4 shadow-sm"
            >
              <div className="flex items-center gap-3">
                <span
                  className="flex h-11 w-11 items-center justify-center rounded-xl text-xl"
                  style={{ backgroundColor: cat.color + '22', color: cat.color }}
                >
                  {cat.icon}
                </span>
                <div>
                  <p className="font-medium text-gray-800">{cat.name}</p>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">{TYPE_LABEL[cat.category_type]}</span>
                    {cat.is_default && (
                      <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
                        Системная
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {!cat.is_default && (
                <button
                  onClick={() => handleDelete(cat.id)}
                  disabled={deletingId === cat.id}
                  className="rounded-lg p-1.5 text-gray-400 transition hover:bg-red-50 hover:text-red-500 disabled:opacity-40"
                  aria-label="Удалить"
                >
                  {deletingId === cat.id ? (
                    <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-red-400 border-t-transparent" />
                  ) : '🗑'}
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Новая категория">
        <CategoryForm
          initialData={{ category_type: activeTab }}
          onSubmit={handleCreate}
          onCancel={() => setShowModal(false)}
        />
      </Modal>
    </div>
  )
}
