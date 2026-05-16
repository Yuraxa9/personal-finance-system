export default function Modal({ isOpen, onClose, title, children }) {
  if (!isOpen) return null

  function handleBackdropClick(event) {
    if (event.target === event.currentTarget) {
      onClose()
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 px-4 py-6 motion-safe:animate-[modal-fade_160ms_ease-out]"
      onMouseDown={handleBackdropClick}
      role="presentation"
    >
      <div
        className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl motion-safe:animate-[modal-scale_180ms_ease-out]"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div className="mb-5 flex items-start justify-between gap-4">
          <h2 id="modal-title" className="text-xl font-semibold text-gray-900">
            {title}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1 text-gray-400 transition hover:bg-gray-100 hover:text-gray-700"
            aria-label="Закрыть"
          >
            ✕
          </button>
        </div>

        {children}
      </div>
    </div>
  )
}
