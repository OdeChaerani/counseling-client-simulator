const DEFAULT_HISTORY = [
  {
    id: 'history-1',
    title: 'Menjelajahi kebiasaan belajar',
    clientName: 'Nadia Putri',
    time: 'Kemarin, 14:20',
    duration: 'Durasi 14 mnt',
    status: 'evaluated',
    statusLabel: 'Sudah Dievaluasi',
    actionLabel: 'Lihat umpan balik',
    actionIcon: 'assessment',
  },
  {
    id: 'history-2',
    title: 'Menghadapi kecemasan ujian semester',
    clientName: 'Nadia Putri',
    time: '22 Okt 2026',
    duration: 'Durasi 18 mnt',
    status: 'completed',
    statusLabel: 'Selesai',
    actionLabel: 'Buka transkrip',
    actionIcon: 'description',
  },
  {
    id: 'history-3',
    title: 'Membangun rapport awal',
    clientName: 'Nadia Putri',
    time: '19 Okt 2026',
    duration: 'Durasi 6 mnt',
    status: 'incomplete',
    statusLabel: 'Tidak Selesai',
    actionLabel: 'Ulangi latihan',
    actionIcon: 'replay',
  },
]

function renderStatusBadge(status, label) {
  switch (status) {
    case 'evaluated':
      return (
        <span className="bg-amber-50 text-amber-800 border border-amber-200/80 text-[11px] font-semibold px-2 py-0.5 rounded-full flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-[#f5b51b]" />
          {label}
        </span>
      )
    case 'completed':
      return (
        <span className="bg-purple-50 text-purple-900 border border-purple-200/80 text-[11px] font-semibold px-2 py-0.5 rounded-full flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-[#352f55]" />
          {label}
        </span>
      )
    case 'incomplete':
    default:
      return (
        <span className="bg-red-50 text-red-700 border border-red-200/80 text-[11px] font-semibold px-2 py-0.5 rounded-full flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-red-600" />
          {label}
        </span>
      )
  }
}

export default function RecentHistory({
  history = DEFAULT_HISTORY,
  onViewAll,
  onItemAction,
}) {
  return (
    <div className="flex flex-col gap-3">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#ede9fe] inline-block" />
          <h2 className="text-base md:text-lg text-white font-bold tracking-tight">
            Riwayat terbaru
          </h2>
        </div>
        <button
          type="button"
          onClick={onViewAll}
          className="text-xs text-[#d3daea] hover:text-white flex items-center gap-1 transition-colors font-medium cursor-pointer"
        >
          <span>Lihat semua</span>
          <span className="material-symbols-outlined text-[15px]">
            arrow_forward
          </span>
        </button>
      </div>

      {/* List Card Crisp White */}
      <div className="bg-white rounded-xl shadow-xs border border-slate-100 overflow-hidden">
        <div className="divide-y divide-slate-100 flex flex-col">
          {history.map((item) => (
            <div
              key={item.id}
              className="px-4 py-3 hover:bg-slate-50 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-3"
            >
              {/* Item Info */}
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-8 h-8 rounded-full bg-[#ede9fe] flex items-center justify-center shrink-0 text-[#352f55]">
                  <span className="material-symbols-outlined text-[18px]">
                    person
                  </span>
                </div>
                <div className="flex flex-col min-w-0">
                  <span className="text-xs md:text-sm font-bold text-[#1e1a34] truncate">
                    {item.title}
                  </span>
                  <div className="flex items-center gap-1.5 text-slate-500 text-[11px] flex-wrap mt-0.5">
                    <span className="flex items-center gap-1 font-medium">
                      <span className="material-symbols-outlined text-[13px]">
                        account_circle
                      </span>
                      {item.clientName}
                    </span>
                    <span>·</span>
                    <span>{item.time}</span>
                    <span>·</span>
                    <span>{item.duration}</span>
                  </div>
                </div>
              </div>

              {/* Status & Action Button */}
              <div className="flex items-center gap-2.5 shrink-0 justify-between md:justify-end">
                {renderStatusBadge(item.status, item.statusLabel)}
                <button
                  type="button"
                  onClick={() => onItemAction && onItemAction(item)}
                  className="bg-slate-100 hover:bg-slate-200/80 text-[#1e1a34] px-2.5 py-1 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1 cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[16px] text-[#352f55]">
                    {item.actionIcon}
                  </span>
                  <span>{item.actionLabel}</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
