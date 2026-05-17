import { useCallback, useEffect, useState } from 'react'
import { getAccounts } from '../api/accounts'
import { getCategories } from '../api/categories'
import {
  createTransaction,
  deleteTransaction,
  getTransactions,
  updateTransaction,
} from '../api/transactions'
import Button from '../components/Button'
import ConfirmDialog from '../components/ConfirmDialog'
import EmptyState from '../components/EmptyState'
import Modal from '../components/Modal'
import TransactionForm from '../components/TransactionForm'
import { formatCurrency, formatDateTime, formatTransactionType } from '../utils/formatters'

const PAGE_SIZE = 20

const TX_TYPE_COLOR = {
  income: 'text-green-600',
  expense: 'text-red-500',
  transfer: 'text-blue-500',
}
const TX_TYPE_SIGN = { income: '+', expense: '−', transfer: '↔' }

const EMPTY_FILTERS = { account_id: '', transaction_type: '', date_from: '', date_to: '' }

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState([])
  const [accounts, setAccounts] = useState([])
  const [categories, setCategories] = useState([])
  const [filters, setFilters] = useState(EMPTY_FILTERS)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingTx, setEditingTx] = useState(null)
  const [deletingId, setDeletingId] = useState(null)
  const [confirmTx, setConfirmTx] = useState(null)

  // load reference data once
  useEffect(() => {
    Promise.all([getAccounts(), getCategories()])
      .then(([accRes, catRes]) => {
        setAccounts(accRes.data)
        setCategories(catRes.data)
      })
      .catch(() => {})
  }, [])

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const params = {}
      if (filters.account_id) params.account_id = filters.account_id
      if (filters.transaction_type) params.transaction_type = filters.transaction_type
      if (filters.date_from) params.date_from = new Date(filters.date_from).toISOString()
      if (filters.date_to) params.date_to = new Date(filters.date_to + 'T23:59:59').toISOString()
      const { data } = await getTransactions(params)
      setTransactions(data)
    } catch {
      setError('Не удалось загрузить транзакции')
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => { setPage(1); load() }, [load])

  function updateFilter(field, value) {
    setFilters((f) => ({ ...f, [field]: value }))
  }

  function resetFilters() {
    setFilters(EMPTY_FILTERS)
  }

  function openCreate() { setEditingTx(null); setIsModalOpen(true) }
  function openEdit(tx) { setEditingTx(tx); setIsModalOpen(true) }
  function closeModal() { setIsModalOpen(false); setEditingTx(null) }

  async function handleSubmit(data) {
    if (editingTx) {
      await updateTransaction(editingTx.id, data)
    } else {
      await createTransaction(data)
    }
    closeModal()
    load()
  }

  function handleDelete(tx) {
    setConfirmTx(tx)
  }

  async function confirmDelete() {
    if (!confirmTx) return
    const txId = confirmTx.id
    setDeletingId(txId)
    setConfirmTx(null)
    try {
      await deleteTransaction(txId)
      load()
    } catch {
      setError('Не удалось удалить транзакцию')
    } finally {
      setDeletingId(null)
    }
  }

  const categoryMap = Object.fromEntries(categories.map((c) => [c.id, c]))
  const accountMap = Object.fromEntries(accounts.map((a) => [a.id, a]))

  const paged = transactions.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)
  const totalPages = Math.ceil(transactions.length / PAGE_SIZE)

  const selectCls = 'rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100'

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Транзакции</h1>
        <Button onClick={openCreate}>+ Добавить транзакцию</Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-end gap-3 rounded-2xl bg-white p-4 shadow-sm">
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-gray-500">Счёт</label>
          <select value={filters.account_id} onChange={(e) => updateFilter('account_id', e.target.value)} className={selectCls}>
            <option value="">Все счета</option>
            {accounts.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-gray-500">Тип</label>
          <select value={filters.transaction_type} onChange={(e) => updateFilter('transaction_type', e.target.value)} className={selectCls}>
            <option value="">Все типы</option>
            <option value="income">Доход</option>
            <option value="expense">Расход</option>
            <option value="transfer">Перевод</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-gray-500">Дата от</label>
          <input type="date" value={filters.date_from} onChange={(e) => updateFilter('date_from', e.target.value)} className={selectCls} />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-gray-500">Дата до</label>
          <input type="date" value={filters.date_to} onChange={(e) => updateFilter('date_to', e.target.value)} className={selectCls} />
        </div>

        <button
          onClick={resetFilters}
          className="rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-500 transition hover:bg-gray-50"
        >
          Сбросить
        </button>
      </div>

      {error && <div className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-600">{error}</div>}

      {/* Table */}
      <div className="overflow-hidden rounded-2xl bg-white shadow-sm">
        {loading ? (
          <div className="flex h-48 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          </div>
        ) : transactions.length === 0 ? (
          <EmptyState
            icon="💸"
            title="Транзакций не найдено"
            message="Измените фильтры или добавьте первую транзакцию!"
            actionText="Добавить транзакцию"
            onAction={openCreate}
          />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-gray-50 text-left text-xs font-medium text-gray-500">
                    <th className="px-4 py-3">Дата</th>
                    <th className="px-4 py-3">Описание</th>
                    <th className="px-4 py-3">Категория</th>
                    <th className="px-4 py-3">Счёт</th>
                    <th className="px-4 py-3 text-right">Сумма</th>
                    <th className="px-4 py-3" />
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {paged.map((tx) => {
                    const cat = categoryMap[tx.category_id]
                    const acc = accountMap[tx.account_id]
                    return (
                      <tr key={tx.id} className="transition hover:bg-gray-50">
                        <td className="whitespace-nowrap px-4 py-3 text-gray-500">{formatDateTime(tx.date)}</td>
                        <td className="px-4 py-3">
                          <span className="font-medium text-gray-800">
                            {tx.description || formatTransactionType(tx.transaction_type)}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          {cat ? (
                            <span className="inline-flex items-center gap-1.5">
                              <span
                                className="flex h-5 w-5 items-center justify-center rounded-full text-xs"
                                style={{ backgroundColor: cat.color + '33', color: cat.color }}
                              >
                                {cat.icon}
                              </span>
                              <span className="text-gray-600">{cat.name}</span>
                            </span>
                          ) : (
                            <span className="text-gray-400">—</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-gray-600">{acc?.name ?? '—'}</td>
                        <td className={`whitespace-nowrap px-4 py-3 text-right font-semibold ${TX_TYPE_COLOR[tx.transaction_type]}`}>
                          {TX_TYPE_SIGN[tx.transaction_type]}{formatCurrency(tx.amount)}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center justify-end gap-1">
                            <button
                              onClick={() => openEdit(tx)}
                              className="rounded-lg p-1.5 text-gray-400 transition hover:bg-gray-100 hover:text-gray-700"
                              aria-label="Редактировать"
                            >✏️</button>
                            <button
                              onClick={() => handleDelete(tx)}
                              disabled={deletingId === tx.id}
                              className="rounded-lg p-1.5 text-gray-400 transition hover:bg-red-50 hover:text-red-500 disabled:opacity-40"
                              aria-label="Удалить"
                            >
                              {deletingId === tx.id
                                ? <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-red-400 border-t-transparent" />
                                : '🗑'}
                            </button>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between border-t px-4 py-3">
                <span className="text-xs text-gray-500">
                  {transactions.length} транзакций · страница {page} из {totalPages}
                </span>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="rounded-lg border px-3 py-1.5 text-xs disabled:opacity-40 hover:bg-gray-50"
                  >← Назад</button>
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="rounded-lg border px-3 py-1.5 text-xs disabled:opacity-40 hover:bg-gray-50"
                  >Вперёд →</button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title={editingTx ? 'Редактировать транзакцию' : 'Новая транзакция'}
      >
        <TransactionForm
          key={editingTx?.id ?? 'new-tx'}
          initialData={editingTx}
          onSubmit={handleSubmit}
          onCancel={closeModal}
        />
      </Modal>

      <ConfirmDialog
        isOpen={!!confirmTx}
        title="Удалить транзакцию?"
        message={confirmTx?.description ? `«${confirmTx.description}»` : 'Это действие нельзя отменить.'}
        confirmText="Удалить"
        cancelText="Отмена"
        onConfirm={confirmDelete}
        onCancel={() => setConfirmTx(null)}
      />
    </div>
  )
}
