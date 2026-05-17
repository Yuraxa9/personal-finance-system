import { useEffect, useState } from 'react'
import { getAccounts } from '../api/accounts'
import { getTransactions } from '../api/transactions'
import { changePassword, updateProfile } from '../api/users'
import Button from '../components/Button'
import Input from '../components/Input'
import useAuthStore from '../store/authStore'
import useToastStore from '../store/toastStore'

export default function ProfilePage() {
  const { user, loadUser } = useAuthStore()
  const addToast = useToastStore((s) => s.addToast)

  const [fullName, setFullName] = useState(user?.full_name ?? '')
  const [profileLoading, setProfileLoading] = useState(false)

  const [currentPwd, setCurrentPwd] = useState('')
  const [newPwd, setNewPwd] = useState('')
  const [confirmPwd, setConfirmPwd] = useState('')
  const [pwdError, setPwdError] = useState('')
  const [pwdLoading, setPwdLoading] = useState(false)

  const [accountCount, setAccountCount] = useState('—')
  const [txCount, setTxCount] = useState('—')

  useEffect(() => {
    Promise.all([getAccounts(), getTransactions({})])
      .then(([accRes, txRes]) => {
        setAccountCount(accRes.data.length)
        setTxCount(txRes.data.length)
      })
      .catch(() => {})
  }, [])

  // Keep fullName in sync if user is loaded after mount
  useEffect(() => {
    if (user?.full_name) setFullName(user.full_name)
  }, [user?.full_name])

  async function handleProfileSubmit(e) {
    e.preventDefault()
    if (!fullName.trim()) return
    setProfileLoading(true)
    try {
      await updateProfile(fullName.trim())
      await loadUser()
      addToast('Профиль обновлён', 'success')
    } catch {
      addToast('Не удалось обновить профиль', 'error')
    } finally {
      setProfileLoading(false)
    }
  }

  async function handlePasswordSubmit(e) {
    e.preventDefault()
    if (newPwd.length < 8) { setPwdError('Минимум 8 символов'); return }
    if (newPwd !== confirmPwd) { setPwdError('Пароли не совпадают'); return }
    setPwdError('')
    setPwdLoading(true)
    try {
      await changePassword(currentPwd, newPwd)
      setCurrentPwd('')
      setNewPwd('')
      setConfirmPwd('')
      addToast('Пароль успешно изменён', 'success')
    } catch {
      addToast('Неверный текущий пароль', 'error')
    } finally {
      setPwdLoading(false)
    }
  }

  const sectionCls = 'rounded-2xl bg-white p-6 shadow-sm'
  const h2Cls = 'mb-5 text-base font-semibold text-gray-800'

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-gray-900">Профиль</h1>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Personal data */}
        <section className={sectionCls}>
          <h2 className={h2Cls}>Личные данные</h2>
          <form onSubmit={handleProfileSubmit} className="flex flex-col gap-4">
            <Input
              label="Имя"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Иван Иванов"
            />
            <Input
              label="Email"
              value={user?.email ?? ''}
              readOnly
              className="cursor-not-allowed bg-gray-50"
            />
            <Button type="submit" loading={profileLoading}>
              Сохранить изменения
            </Button>
          </form>
        </section>

        {/* Change password */}
        <section className={sectionCls}>
          <h2 className={h2Cls}>Смена пароля</h2>
          <form onSubmit={handlePasswordSubmit} className="flex flex-col gap-4">
            <Input
              label="Текущий пароль"
              type="password"
              value={currentPwd}
              onChange={(e) => setCurrentPwd(e.target.value)}
              placeholder="••••••••"
            />
            <Input
              label="Новый пароль"
              type="password"
              value={newPwd}
              onChange={(e) => setNewPwd(e.target.value)}
              placeholder="Минимум 8 символов"
            />
            <Input
              label="Подтвердите пароль"
              type="password"
              value={confirmPwd}
              onChange={(e) => setConfirmPwd(e.target.value)}
              placeholder="••••••••"
              error={pwdError}
            />
            <Button type="submit" loading={pwdLoading}>
              Сменить пароль
            </Button>
          </form>
        </section>
      </div>

      {/* Stats */}
      <section className={sectionCls}>
        <h2 className={h2Cls}>Статистика</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="rounded-xl bg-gray-50 px-5 py-4">
            <p className="text-xs text-gray-500">Дата регистрации</p>
            <p className="mt-1 font-semibold text-gray-800">
              {user?.created_at
                ? new Date(user.created_at).toLocaleDateString('ru-RU', {
                    day: '2-digit', month: 'long', year: 'numeric',
                  })
                : '—'}
            </p>
          </div>
          <div className="rounded-xl bg-gray-50 px-5 py-4">
            <p className="text-xs text-gray-500">Счетов</p>
            <p className="mt-1 text-2xl font-bold text-gray-800">{accountCount}</p>
          </div>
          <div className="rounded-xl bg-gray-50 px-5 py-4">
            <p className="text-xs text-gray-500">Транзакций</p>
            <p className="mt-1 text-2xl font-bold text-gray-800">{txCount}</p>
          </div>
        </div>
      </section>
    </div>
  )
}
