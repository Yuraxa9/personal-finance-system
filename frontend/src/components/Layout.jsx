import { NavLink, useNavigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'

const NAV = [
  { to: '/dashboard', label: 'Дашборд', icon: '📊' },
  { to: '/accounts', label: 'Счета', icon: '💳' },
  { to: '/transactions', label: 'Транзакции', icon: '💸' },
  { to: '/categories', label: 'Категории', icon: '🏷️' },
  { to: '/analytics', label: 'Аналитика', icon: '📈' },
]

export default function Layout({ children }) {
  const { user, logoutAction } = useAuthStore()
  const navigate = useNavigate()

  function handleLogout() {
    logoutAction()
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="flex w-60 flex-col bg-gray-900 text-white">
        <div className="px-6 py-5">
          <span className="text-lg font-bold tracking-tight">💰 FinanceApp</span>
        </div>

        <nav className="flex flex-1 flex-col gap-1 px-3 py-2">
          {NAV.map(({ to, label, icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                }`
              }
            >
              <span>{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main area */}
      <div className="flex flex-1 flex-col">
        {/* Topbar */}
        <header className="flex items-center justify-between border-b bg-white px-6 py-3 shadow-sm">
          <span className="text-sm text-gray-500">
            Привет, <span className="font-medium text-gray-800">{user?.full_name ?? '...'}</span>
          </span>
          <button
            onClick={handleLogout}
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-600 transition hover:bg-gray-50 hover:text-red-500"
          >
            Выйти
          </button>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  )
}
