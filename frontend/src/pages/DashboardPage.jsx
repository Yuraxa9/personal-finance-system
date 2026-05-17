import { useEffect, useState } from 'react'
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { getAccounts } from '../api/accounts'
import { getCategories } from '../api/categories'
import { getStats } from '../api/stats'
import { getTransactions } from '../api/transactions'
import StatCard from '../components/StatCard'
import { formatAccountType, formatCurrency, formatDateShort, formatTransactionType } from '../utils/formatters'
import useAuthStore from '../store/authStore'

const TX_TYPE_COLOR = { income: 'text-green-600', expense: 'text-red-500', transfer: 'text-blue-500' }
const FALLBACK_COLORS = ['#6366f1', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6']

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user)
  const [accounts, setAccounts] = useState([])
  const [transactions, setTransactions] = useState([])
  const [stats, setStats] = useState(null)
  const [categoryMap, setCategoryMap] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const [accRes, txRes, statsRes, catRes] = await Promise.all([
          getAccounts(),
          getTransactions({}),
          getStats(),
          getCategories(),
        ])
        setAccounts(accRes.data)
        setTransactions(txRes.data)
        setStats(statsRes.data)
        setCategoryMap(Object.fromEntries(catRes.data.map((c) => [c.id, c])))
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
    return <div className="rounded-xl bg-red-50 p-4 text-red-600">{error}</div>
  }

  const totalBalance = accounts.reduce((sum, a) => sum + Number(a.balance), 0)
  const totalIncome = stats ? Number(stats.total_income) : 0
  const totalExpense = stats ? Number(stats.total_expense) : 0

  const pieData = accounts
    .flatMap(() => [])
    .concat(
      Object.values(
        transactions
          .filter((tx) => tx.transaction_type === 'expense' && tx.category_id)
          .reduce((acc, tx) => {
            const cat = categoryMap[tx.category_id]
            if (!cat) return acc
            if (!acc[tx.category_id]) {
              acc[tx.category_id] = { name: cat.name, value: 0, color: cat.color }
            }
            acc[tx.category_id].value += Number(tx.amount)
            return acc
          }, {})
      )
    )
    .sort((a, b) => b.value - a.value)
    .slice(0, 5)
    .map((d, i) => ({ ...d, color: d.color ?? FALLBACK_COLORS[i] }))
    .filter((d) => d.value > 0)

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Добро пожаловать, {user?.full_name ?? ''}!
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          У вас {stats?.total_accounts ?? 0} {plural(stats?.total_accounts ?? 0, 'счёт', 'счёта', 'счетов')} и{' '}
          {stats?.total_transactions ?? 0}{' '}
          {plural(stats?.total_transactions ?? 0, 'транзакция', 'транзакции', 'транзакций')}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard title="Общий баланс" value={formatCurrency(totalBalance)} icon="💰" color="blue" />
        <StatCard title="Всего доходов" value={formatCurrency(totalIncome)} icon="📈" color="green" />
        <StatCard title="Всего расходов" value={formatCurrency(totalExpense)} icon="📉" color="red" />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
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
                    <p className="text-xs text-gray-400">{formatAccountType(a.account_type)}</p>
                  </div>
                  <span className="font-semibold text-gray-900">{formatCurrency(a.balance, a.currency)}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

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
                      {tx.description || formatTransactionType(tx.transaction_type)}
                    </p>
                    <p className="text-xs text-gray-400">{formatDateShort(tx.date)}</p>
                  </div>
                  <span className={`font-semibold ${TX_TYPE_COLOR[tx.transaction_type]}`}>
                    {tx.transaction_type === 'income' ? '+' : '−'}{formatCurrency(tx.amount)}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      {pieData.length > 0 && (
        <section className="rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="mb-2 font-semibold text-gray-800">Топ-5 категорий расходов</h2>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90}>
                {pieData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(v) => [formatCurrency(v), 'Сумма']} />
              <Legend
                formatter={(value, entry) => (
                  <span className="text-xs text-gray-700">{value}: {formatCurrency(entry.payload.value)}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </section>
      )}
    </div>
  )
}

function plural(n, one, few, many) {
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod10 === 1 && mod100 !== 11) return one
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return few
  return many
}
