export default function Navbar({
  isSidebarOpen = true,
  onToggleSidebar,
  onLogout,
}) {
  return (
    <header className="fixed top-0 left-0 right-0 h-14 z-50 flex items-center justify-between px-5 bg-white border-b border-slate-200 rounded-b-2xl shadow-xs">
      {/* Brand & Subtitle + Sidebar Toggle */}
      <div className="flex items-center gap-3">
        {/* Toggle Sidebar Button */}
        {onToggleSidebar && (
          <button
            type="button"
            onClick={onToggleSidebar}
            className="w-8 h-8 rounded-lg text-[#352f55] hover:bg-slate-100 flex items-center justify-center transition cursor-pointer"
            title={isSidebarOpen ? 'Sembunyikan Sidebar' : 'Tampilkan Sidebar'}
          >
            <span className="material-symbols-outlined text-[20px]">
              {isSidebarOpen ? 'menu_open' : 'menu'}
            </span>
          </button>
        )}

        <div className="flex flex-col">
          <span className="text-lg leading-tight tracking-tight flex items-center font-bold">
            <span className="text-[#f5b51b]">Safe</span>
            <span className="text-[#352f55]">Sesi</span>
          </span>
          <span className="text-[11px] text-[#64748b]">
            Psikologi · Universitas Padjadjaran
          </span>
        </div>

        <div className="h-5 w-px bg-slate-200 hidden md:block" />

        <span className="text-xs text-[#1e1a34] font-medium hidden md:inline-block">
          Ruang Belajar Konseling Virtual
        </span>
      </div>

      {/* Action / Profile Badges */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-100 text-[#1e1a34] text-xs font-semibold border border-slate-200/80">
          <span className="material-symbols-outlined text-[14px] text-[#64748b]">
            verified
          </span>
          <span>Akademik UNPAD</span>
        </div>

        {onLogout ? (
          <button
            type="button"
            onClick={onLogout}
            title="Keluar Akun"
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-100 hover:bg-red-50 hover:text-red-600 text-slate-700 text-xs font-semibold border border-slate-200/80 transition cursor-pointer"
          >
            <span className="material-symbols-outlined text-[15px]">logout</span>
            <span className="hidden sm:inline">Keluar</span>
          </button>
        ) : (
          <div className="w-7 h-7 rounded-full bg-[#352f55] flex items-center justify-center cursor-pointer hover:opacity-90 transition-opacity">
            <span className="material-symbols-outlined text-white text-[16px]">
              person
            </span>
          </div>
        )}
      </div>
    </header>
  )
}
