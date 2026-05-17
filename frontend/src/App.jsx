import { useEffect } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import PrivateRoute from './components/PrivateRoute'
import AccountsPage from './pages/AccountsPage'
import CategoriesPage from './pages/CategoriesPage'
import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import useAuthStore from './store/authStore'

const ComingSoon = ({ page }) => (
  <div className="flex h-full items-center justify-center text-gray-400">
    {page} — скоро будет
  </div>
)

function App() {
  const loadUser = useAuthStore((s) => s.loadUser)

  useEffect(() => {
    loadUser()
  }, [loadUser])

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <DashboardPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/accounts"
          element={
            <PrivateRoute>
              <AccountsPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/transactions"
          element={
            <PrivateRoute>
              <ComingSoon page="Транзакции" />
            </PrivateRoute>
          }
        />
        <Route
          path="/categories"
          element={
            <PrivateRoute>
              <CategoriesPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <PrivateRoute>
              <ComingSoon page="Аналитика" />
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App
