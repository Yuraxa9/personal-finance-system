import { useEffect, useState } from 'react'
import { getAccounts } from '../api/accounts'
import { getAnalytics, getTransactions } from '../api/transactions'
import StatCard from '../components/StatCard'

const ACCOUNT_TYPE_LABEL = { cash: 'Наличные', card: 'Карта', savings: 'Накопления' }
const TX_TYPE_LABEL = { income: 'Доход', expense: 'Расход', transfer: 'Перевод' }
const TX_TYPE_COLOR = { income: 'text-green-600', expense: 'text-red-500', transfer: 'text-blue-500' }

function fmt(amount) {
  return Number(amount).toLocaleString('ru-RU', { style: 'currency', currency: 'RUB' })
}

function thisMonthRange() {
  const now = new Date()
  const from = new Date(now.getFullYear(), now.getMonth(), 1).toISOString()
  const to = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59).toISOString()
  return { from, to }
}

export default function DashboardPage() {
  const [accounts, setAccounts] = useState([])
  const [transactions, setTransactions] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const { from, to } = thisMonthRange()
        const [accRes, txRes, analyticsRes] = await Promise.all([
          getAccounts(),
          getTransactions({ limit: 5 }),
          getAnalytics(from, to),
        ])
        setAccounts(accRes.data)
        setTransactions(txRes.data)
        setAnalytics(analyticsRes.data)
      } catch {
        setError('Не удалось загрузить данные')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-xl bg-red-50 p-4 text-red-600">{error}</div>
    )
  }

  const totalBalance = accounts.reduce((sum, a) => sum + Number(a.balance), 0)
  const income = analytics ? Number(analytics.summary.total_income) : 0
  const expense = analytics ? Number(analytics.summary.total_expense) : 0

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-gray-900">Дашборд</h1>

      {/* Stat cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard title="Общий баланс" value={fmt(totalBalance)} icon="💰" color="blue" />
        <StatCard title="Доходы за месяц" value={fmt(income)} icon="📈" color="green" />
        <StatCard title="Расходы за месяц" value={fmt(expense)} icon="📉" color="red" />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Accounts */}
        <section className="rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="mb-4 font-semibold text-gray-800">Мои счета</h2>
          {accounts.length === 0 ? (
            <p className="text-sm text-gray-400">Счетов пока нет</p>
          ) : (
            <ul className="flex flex-col gap-3">
              {accounts.map((a) => (
                <li key={a.id} className="flex items-center justify-between rounded-xl bg-gray-50 px-4 py-3">
                  <div>
                    <p className="font-medium text-gray-800">{a.name}</p>
                    <p className="text-xs text-gray-400">{ACCOUNT_TYPE_LABEL[a.account_type] ?? a.account_type}</p>
                  </div>
                  <span className="font-semibold text-gray-900">{fmt(a.balance)}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Recent transactions */}
        <section className="rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="mb-4 font-semibold text-gray-800">Последние транзакции</h2>
          {transactions.length === 0 ? (
            <p className="text-sm text-gray-400">Транзакций пока нет</p>
          ) : (
            <ul className="flex flex-col gap-3">
              {transactions.slice(0, 5).map((tx) => (
                <li key={tx.id} className="flex items-center justify-between rounded-xl bg-gray-50 px-4 py-3">
                  <div>
                    <p className="text-sm font-medium text-gray-800">
                      {tx.description || TX_TYPE_LABEL[tx.transaction_type]}
                    </p>
                    <p className="text-xs text-gray-400">
                      {new Date(tx.date).toLocaleDateString('ru-RU')}
                    </p>
                  </div>
                  <span className={`font-semibold ${TX_TYPE_COLOR[tx.transaction_type]}`}>
                    {tx.transaction_type === 'income' ? '+' : '−'}{fmt(tx.amount)}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  )
}
