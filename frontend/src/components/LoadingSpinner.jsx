const SIZES = { sm: 'h-5 w-5 border-2', md: 'h-8 w-8 border-4', lg: 'h-12 w-12 border-4' }

export default function LoadingSpinner({ size = 'md', text }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <div className={`animate-spin rounded-full border-blue-600 border-t-transparent ${SIZES[size]}`} />
      {text && <p className="text-sm text-gray-500">{text}</p>}
    </div>
  )
}
