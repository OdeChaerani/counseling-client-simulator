const NAV_ITEMS = [
  { id: 'beranda', label: 'Beranda', icon: 'home' },
  { id: 'latihan-mandiri', label: 'Latihan Mandiri', icon: 'psychology' },
  { id: 'kelas-saya', label: 'Kelas', icon: 'school' },
  { id: 'riwayat', label: 'Riwayat', icon: 'history' },
]

export default function Sidebar({
  activeTab = 'beranda',
  onSelectTab,
  isOpen = true,
  onLogout,
}) {
  return (
    <aside
      className={`fixed left-0 top-14 bottom-0 w-60 bg-surface-container-low shadow-xs z-40 flex flex-col justify-between p-3 border-r border-[#d3daea] transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      {/* Navigation Links */}
      <div className="flex flex-col gap-2">
        <nav className="flex flex-col gap-1">
          {NAV_ITEMS.map((item) => {
            const isActive = activeTab === item.id
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onSelectTab && onSelectTab(item.id)}
                aria-current={isActive ? 'page' : undefined}
                className={`flex items-center gap-2.5 px-3 py-2 rounded-lg transition-all text-left text-xs md:text-sm cursor-pointer ${
                  isActive
                    ? 'font-semibold text-white bg-[#352f55] shadow-xs'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`}
              >
                <span
                  className={`material-symbols-outlined text-[18px] ${
                    isActive ? 'text-white' : 'text-slate-500'
                  }`}
                >
                  {item.icon}
                </span>
                <span>{item.label}</span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* User Info Card (Bottom) */}
      <div className="flex items-center justify-between p-2 rounded-xl bg-white shadow-xs border border-slate-100">
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-7 h-7 rounded-full bg-[#352f55] flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-white text-[16px]">
              person
            </span>
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-xs font-semibold text-slate-800 truncate">
              Rani Aulia
            </span>
            <span className="text-[10px] text-slate-500 truncate">
              Mahasiswa Angkatan 2023
            </span>
          </div>
        </div>

        {onLogout && (
          <button
            type="button"
            onClick={onLogout}
            title="Keluar Akun"
            className="w-7 h-7 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 flex items-center justify-center transition cursor-pointer shrink-0"
          >
            <span className="material-symbols-outlined text-[16px]">logout</span>
          </button>
        )}
      </div>
    </aside>
  )
}
