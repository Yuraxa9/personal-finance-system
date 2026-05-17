import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    console.error('ErrorBoundary caught an error:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 px-4 text-center">
          <div className="w-full max-w-md rounded-2xl bg-white p-10 shadow-lg">
            <div className="mb-4 text-6xl">⚠️</div>
            <h1 className="mb-2 text-xl font-bold text-gray-900">Что-то пошло не так</h1>
            <p className="mb-6 text-sm text-gray-500">
              {this.state.error?.message ?? 'Произошла непредвиденная ошибка'}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700"
            >
              Перезагрузить страницу
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
