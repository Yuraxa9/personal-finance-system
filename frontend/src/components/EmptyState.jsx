export default function EmptyState({ icon = '📭', title, message, actionText, onAction }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl bg-white px-6 py-14 text-center shadow-sm">
      <span className="mb-3 text-5xl">{icon}</span>
      {title && <p className="text-base font-semibold text-gray-700">{title}</p>}
      {message && <p className="mt-1 text-sm text-gray-400">{message}</p>}
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="mt-5 rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
        >
          {actionText}
        </button>
      )}
    </div>
  )
}
