export default function Input({
  label,
  type = 'text',
  value,
  onChange,
  error,
  placeholder,
  ...props
}) {
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label className="text-sm font-medium text-gray-700">{label}</label>
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        {...props}
        className={`w-full rounded-lg border px-3 py-2 text-sm outline-none transition focus:ring-2 ${
          error
            ? 'border-red-400 focus:ring-red-200'
            : 'border-gray-300 focus:border-blue-400 focus:ring-blue-100'
        }`}
      />
      {error && <span className="text-xs text-red-500">{error}</span>}
    </div>
  )
}
