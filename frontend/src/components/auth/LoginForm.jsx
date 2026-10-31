import { useState } from 'react'

export default function LoginForm({ onSubmit, isLoading = false }) {
  const [username, setUsername] = useState('180110230045')
  const [password, setPassword] = useState('••••••••')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!username.trim()) {
      setError('Harap masukkan Username atau NIM Anda.')
      return
    }
    if (!password) {
      setError('Harap masukkan kata sandi Anda.')
      return
    }
    setError('')
    if (onSubmit) {
      onSubmit({ username, password })
    }
  }

  return (
    <div
      className="w-full max-w-md bg-white rounded-2xl shadow-2xl p-6 sm:p-8 md:p-9 transition-all relative z-10 border border-slate-100"
      style={{
        boxShadow:
          '0 20px 40px -15px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.08)',
      }}
    >
      {/* Card Header */}
      <div className="mb-6">
        <h2 className="text-xl sm:text-2xl text-[#1e1a34] mb-1.5 font-bold tracking-tight">
          Masuk ke <span className="text-[#f5b51b]">Safe</span>
          <span className="text-[#352f55]">Sesi</span>
        </h2>
        <p className="text-xs sm:text-sm text-slate-500 leading-relaxed">
          Gunakan akun universitas yang telah terdaftar untuk memulai sesi praktik konseling.
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-2.5 rounded-lg bg-red-50 border border-red-200 text-red-600 text-xs flex items-center gap-2">
          <span className="material-symbols-outlined text-[16px]">error</span>
          <span>{error}</span>
        </div>
      )}

      {/* Login Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Username / NIM */}
        <div>
          <label
            htmlFor="username"
            className="block text-xs font-semibold text-[#1e1a34] mb-1.5"
          >
            Username / NIM
          </label>
          <div className="relative rounded-xl shadow-xs">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
              <span className="material-symbols-outlined text-[18px]">badge</span>
            </div>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Contoh: 180110230045"
              required
              className="w-full h-10 pl-9 pr-3.5 bg-slate-50 text-[#1e1a34] text-xs sm:text-sm rounded-xl border border-slate-200 placeholder-slate-400 outline-none transition focus:bg-white focus:border-[#352f55] focus:ring-1 focus:ring-[#352f55]"
            />
          </div>
        </div>

        {/* Password */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label
              htmlFor="password"
              className="text-xs font-semibold text-[#1e1a34]"
            >
              Kata Sandi
            </label>
          </div>
          <div className="relative rounded-xl shadow-xs">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
              <span className="material-symbols-outlined text-[18px]">key</span>
            </div>
            <input
              id="password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Masukkan kata sandi akun"
              required
              className="w-full h-10 pl-9 pr-10 bg-slate-50 text-[#1e1a34] text-xs sm:text-sm rounded-xl border border-slate-200 placeholder-slate-400 outline-none transition focus:bg-white focus:border-[#352f55] focus:ring-1 focus:ring-[#352f55]"
            />
            <button
              type="button"
              onClick={() => setShowPassword((prev) => !prev)}
              aria-label={showPassword ? 'Sembunyikan kata sandi' : 'Tampilkan kata sandi'}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600 transition cursor-pointer"
            >
              <span className="material-symbols-outlined text-[18px]">
                {showPassword ? 'visibility_off' : 'visibility'}
              </span>
            </button>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full h-10 mt-2 bg-[#f5b51b] hover:bg-[#e2a613] disabled:opacity-60 disabled:cursor-not-allowed text-[#1e1a34] font-bold text-xs sm:text-sm rounded-xl shadow-xs active:scale-[0.99] transition flex items-center justify-center gap-1.5 cursor-pointer"
        >
          {isLoading ? (
            <span>Memproses...</span>
          ) : (
            <>
              <span>Masuk</span>
              <span className="material-symbols-outlined text-[18px]">
                arrow_forward
              </span>
            </>
          )}
        </button>
      </form>

      {/* Card Footer */}
      <div className="mt-5 pt-3.5 border-t border-slate-100 text-center">
        <p className="text-[11px] text-slate-500 leading-relaxed">
          Akun diberikan oleh Pengelola / Admin Praktikum.
          <br />
          Lupa kata sandi?
          <button
            type="button"
            onClick={() => alert('Silakan hubungi staf admin laboratorium konseling untuk reset kata sandi.')}
            className="font-semibold text-[#7b5800] underline hover:text-[#5d4200] transition ml-1 cursor-pointer"
          >
            Hubungi Admin
          </button>
        </p>
      </div>
    </div>
  )
}

