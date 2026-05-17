import { useCallback, useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { getCategories } from '../api/categories'
import { getAnalytics } from '../api/transactions'
import LoadingSpinner from '../components/LoadingSpinner'
import StatCard from '../components/StatCard'
import { formatCurrency } from '../utils/formatters'

function getWeekRange() {
  const now = new Date()
  const day = now.getDay() || 7
  const from = new Date(now)
  from.setDate(now.getDate() - day + 1)
  from.setHours(0, 0, 0, 0)
  const to = new Date(from)
  to.setDate(from.getDate() + 6)
  to.setHours(23, 59, 59, 999)
  return { from: from.toISOString(), to: to.toISOString() }
}

function getMonthRange() {
  const now = new Date()
  return {
    from: new Date(now.getFullYear(), now.getMonth(), 1).toISOString(),
    to: new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59).toISOString(),
  }
}

function getYearRange() {
  const y = new Date().getFullYear()
  return {
    from: new Date(y, 0, 1).toISOString(),
    to: new Date(y, 11, 31, 23, 59, 59).toISOString(),
  }
}

function rangeFor(period, customFrom, customTo) {
  if (period === 'week') return getWeekRange()
  if (period === 'month') return getMonthRange()
  if (period === 'year') return getYearRange()
  return {
    from: customFrom ? new Date(customFrom).toISOString() : null,
    to: customTo ? new Date(customTo + 'T23:59:59').toISOString() : null,
  }
}

const PERIOD_TABS = [
  { key: 'week', label: 'Эта неделя' },
  { key: 'month', label: 'Этот месяц' },
  { key: 'year', label: 'Этот год' },
  { key: 'custom', label: 'Произвольный' },
]

const FALLBACK_COLORS = ['#6366f1', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316', '#84cc16']

const tooltipFmt = (value) => [formatCurrency(value), 'Сумма']

export default function AnalyticsPage() {
  const [period, setPeriod] = useState('month')
  const [customFrom, setCustomFrom] = useState('')
  const [customTo, setCustomTo] = useState('')
  const [analytics, setAnalytics] = useState(null)
  const [categoryMap, setCategoryMap] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Load categories once for color/type lookup
  useEffect(() => {
    getCategories()
      .then(({ data }) => {
        const map = Object.fromEntries(data.map((c) => [c.id, c]))
        setCategoryMap(map)
      })
      .catch(() => {})
  }, [])

  const load = useCallback(async () => {
    const { from, to } = rangeFor(period, customFrom, customTo)
    setLoading(true)
    setError('')
    try {
      const { data } = await getAnalytics(from, to)
      setAnalytics(data)
    } catch {
      setError('Не удалось загрузить аналитику')
    } finally {
      setLoading(false)
    }
  }, [period, customFrom, customTo])

  useEffect(() => {
    if (period !== 'custom' || (customFrom && customTo)) load()
  }, [load, period, customFrom, customTo])

  const income = analytics ? Number(analytics.summary.total_income) : 0
  const expense = analytics ? Number(analytics.summary.total_expense) : 0
  const balance = income - expense

  // Pie data — expense categories only
  const pieData = (analytics?.by_category ?? [])
    .filter((item) => {
      if (!item.category_id) return false
      const cat = categoryMap[item.category_id]
      return cat?.category_type === 'expense'
    })
    .map((item, i) => ({
      name: item.category_name,
      value: Number(item.total_amount),
      color: categoryMap[item.category_id]?.color ?? FALLBACK_COLORS[i % FALLBACK_COLORS.length],
    }))
    .filter((d) => d.value > 0)

  // Bar data — all categories with type coloring
  const barData = (analytics?.by_category ?? [])
    .filter((item) => item.category_name && Number(item.total_amount) > 0)
    .map((item, i) => {
      const cat = categoryMap[item.category_id]
      return {
        name: item.category_name,
        amount: Number(item.total_amount),
        fill: cat?.category_type === 'income' ? '#22c55e' : '#ef4444',
      }
    })

  const inputCls = 'rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100'

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-gray-900">Аналитика</h1>

      {/* Period selector */}
      <div className="flex flex-wrap items-end gap-3">
        <div className="flex gap-1 rounded-xl bg-gray-100 p-1">
          {PERIOD_TABS.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setPeriod(key)}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                period === key ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {period === 'custom' && (
          <div className="flex items-center gap-2">
            <input type="date" value={customFrom} onChange={(e) => setCustomFrom(e.target.value)} className={inputCls} />
            <span className="text-gray-400">—</span>
            <input type="date" value={customTo} onChange={(e) => setCustomTo(e.target.value)} className={inputCls} />
          </div>
        )}
      </div>

      {error && <div className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-600">{error}</div>}

      {loading ? (
        <div className="flex h-64 items-center justify-center">
          <LoadingSpinner size="lg" text="Загружаем данные…" />
        </div>
      ) : (
        <>
          {/* Stat cards */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <StatCard title="Доходы за период" value={formatCurrency(income)} icon="📈" color="green" />
            <StatCard title="Расходы за период" value={formatCurrency(expense)} icon="📉" color="red" />
            <StatCard title="Баланс" value={formatCurrency(balance)} icon="💰" color={balance >= 0 ? 'blue' : 'red'} />
          </div>

          <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
            {/* Pie chart */}
            <section className="rounded-2xl bg-white p-5 shadow-sm">
              <h2 className="mb-4 font-semibold text-gray-800">Расходы по категориям</h2>
              {pieData.length === 0 ? (
                <p className="py-8 text-center text-sm text-gray-400">Нет данных за период</p>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={110}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      labelLine={false}
                    >
                      {pieData.map((entry, i) => (
                        <Cell key={i} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={tooltipFmt} />
                    <Legend
                      formatter={(value, entry) => (
                        <span className="text-xs text-gray-700">{value}: {formatCurrency(entry.payload.value)}</span>
                      )}
                    />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </section>

            {/* Bar chart */}
            <section className="rounded-2xl bg-white p-5 shadow-sm">
              <h2 className="mb-4 font-semibold text-gray-800">Доходы и расходы по категориям</h2>
              {barData.length === 0 ? (
                <p className="py-8 text-center text-sm text-gray-400">Нет данных за период</p>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={barData} margin={{ top: 4, right: 8, left: 8, bottom: 40 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis
                      dataKey="name"
                      tick={{ fontSize: 11 }}
                      angle={-35}
                      textAnchor="end"
                      interval={0}
                    />
                    <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                    <Tooltip formatter={tooltipFmt} />
                    <Bar dataKey="amount" name="Сумма" radius={[4, 4, 0, 0]}>
                      {barData.map((entry, i) => (
                        <Cell key={i} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </section>
          </div>
        </>
      )}
    </div>
  )
}
