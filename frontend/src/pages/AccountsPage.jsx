import { useEffect, useState } from 'react'
import {
  createAccount,
  deleteAccount,
  getAccounts,
  updateAccount,
} from '../api/accounts'
import AccountForm from '../components/AccountForm'
import ConfirmDialog from '../components/ConfirmDialog'
import EmptyState from '../components/EmptyState'
import Modal from '../components/Modal'
import { formatAccountType, formatCurrency } from '../utils/formatters'

const ACCOUNT_ICON = { cash: '💵', card: '💳', savings: '🏦' }

export default function AccountsPage() {
  const [accounts, setAccounts] = useState([])
  const [confirmTarget, setConfirmTarget] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingAccount, setEditingAccount] = useState(null)

  async function loadAccounts() {
    setLoading(true)
    setError('')

    try {
      const response = await getAccounts()
      setAccounts(response.data)
    } catch {
      setError('Не удалось загрузить счета')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let isMounted = true

    async function loadInitialAccounts() {
      try {
        const response = await getAccounts()
        if (isMounted) setAccounts(response.data)
      } catch {
        if (isMounted) setError('Не удалось загрузить счета')
      } finally {
        if (isMounted) setLoading(false)
      }
    }

    loadInitialAccounts()

    return () => {
      isMounted = false
    }
  }, [])

  function openCreateModal() {
    setEditingAccount(null)
    setIsModalOpen(true)
  }

  function openEditModal(account) {
    setEditingAccount(account)
    setIsModalOpen(true)
  }

  function closeModal() {
    setIsModalOpen(false)
    setEditingAccount(null)
  }

  async function handleSubmit(data) {
    if (editingAccount) {
      await updateAccount(editingAccount.id, data)
    } else {
      await createAccount(data)
    }

    closeModal()
    await loadAccounts()
  }

  async function handleDelete(account) {
    setConfirmTarget(account)
  }

  async function confirmDelete() {
    if (!confirmTarget) return
    try {
      await deleteAccount(confirmTarget.id)
      await loadAccounts()
    } catch {
      setError('Не удалось удалить счёт')
    } finally {
      setConfirmTarget(null)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Мои счета</h1>
        <button
          type="button"
          onClick={openCreateModal}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
        >
          <span aria-hidden="true">＋</span>
          Добавить счёт
        </button>
      </div>

      {loading && (
        <div className="flex h-64 items-center justify-center rounded-2xl bg-white shadow-sm">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
        </div>
      )}

      {!loading && error && (
        <div className="rounded-xl bg-red-50 p-4 text-sm text-red-600">
          {error}
        </div>
      )}

      {!loading && !error && accounts.length === 0 && (
        <EmptyState
          icon="💳"
          title="Счетов пока нет"
          message="У вас пока нет счетов. Создайте первый!"
          actionText="Добавить счёт"
          onAction={openCreateModal}
        />
      )}

      {!loading && !error && accounts.length > 0 && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {accounts.map((account) => {
            return (
              <article
                key={account.id}
                className="flex min-h-56 flex-col justify-between rounded-2xl bg-white p-5 shadow-sm"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">
                      {account.name}
                    </h2>
                    <div className="mt-2 inline-flex items-center gap-2 rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-600">
                      <span aria-hidden="true">{ACCOUNT_ICON[account.account_type] ?? '💼'}</span>
                      {formatAccountType(account.account_type)}
                    </div>
                  </div>
                  <span className="rounded-lg bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700">
                    {account.currency}
                  </span>
                </div>

                <div className="mt-6">
                  <p className="text-3xl font-bold text-gray-900">
                    {formatCurrency(account.balance, account.currency)}
                  </p>
                  <p className="mt-1 text-sm text-gray-400">{account.currency}</p>
                </div>

                <div className="mt-6 grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => openEditModal(account)}
                    className="rounded-lg bg-gray-100 px-3 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-200"
                  >
                    Редактировать
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDelete(account)}
                    className="rounded-lg bg-red-50 px-3 py-2 text-sm font-medium text-red-600 transition hover:bg-red-100"
                  >
                    Удалить
                  </button>
                </div>
              </article>
            )
          })}
        </div>
      )}

      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title={editingAccount ? 'Редактировать счёт' : 'Добавить счёт'}
      >
        <AccountForm
          key={editingAccount?.id ?? 'new-account'}
          initialData={editingAccount}
          onSubmit={handleSubmit}
          onCancel={closeModal}
        />
      </Modal>

      <ConfirmDialog
        isOpen={!!confirmTarget}
        title={`Удалить счёт «${confirmTarget?.name}»?`}
        message="Это действие нельзя отменить. Убедитесь, что у счёта нет транзакций."
        confirmText="Удалить"
        cancelText="Отмена"
        onConfirm={confirmDelete}
        onCancel={() => setConfirmTarget(null)}
      />
    </div>
  )
}
