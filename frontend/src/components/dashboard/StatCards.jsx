const DEFAULT_STATS = [
  {
    id: 'total-sesi',
    title: 'Total Sesi',
    value: '12',
    unit: '',
    subtitle: 'Sesi latihan yang diselesaikan',
    icon: 'check_circle',
    iconFill: 1,
    barColor: '#352f55',
    progressPercent: 100,
  },
  {
    id: 'skenario-dicoba',
    title: 'Skenario Dicoba',
    value: '5',
    unit: '/ 12',
    subtitle: 'Eksplorasi konteks percakapan',
    icon: 'explore',
    iconFill: 0,
    barColor: '#f5b51b',
    progressPercent: 41.6,
  },
  {
    id: 'waktu-latihan',
    title: 'Waktu Latihan',
    value: '184',
    unit: 'menit',
    subtitle: 'Akumulasi durasi sesi selesai',
    icon: 'timer',
    iconFill: 0,
    barColor: '#352f55',
    progressPercent: 76,
  },
  {
    id: 'kelas-aktif',
    title: 'Kelas Aktif',
    value: '2',
    unit: '',
    subtitle: 'Kelas praktikum aktif',
    icon: 'school',
    iconFill: 0,
    barColor: '#f5b51b',
    progressPercent: 100,
  },
]

export default function StatCards({ stats = DEFAULT_STATS }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
      {stats.map((stat) => (
        <div
          key={stat.id}
          className="bg-white p-3.5 rounded-xl shadow-xs border border-slate-100 flex flex-col justify-between transition-all duration-200 hover:-translate-y-0.5"
        >
          {/* Header */}
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs font-semibold text-slate-500">
              {stat.title}
            </span>
            <div className="w-7 h-7 rounded-lg bg-[#ede9fe] flex items-center justify-center text-[#352f55]">
              <span
                className="material-symbols-outlined text-[17px]"
                style={
                  stat.iconFill
                    ? { fontVariationSettings: "'FILL' 1" }
                    : undefined
                }
              >
                {stat.icon}
              </span>
            </div>
          </div>

          {/* Value */}
          <div className="mt-2.5 flex flex-col">
            <div className="flex items-baseline gap-1.5">
              <span className="text-2xl font-bold text-[#1e1a34] leading-tight">
                {stat.value}
              </span>
              {stat.unit && (
                <span className="text-xs text-slate-500 font-medium">
                  {stat.unit}
                </span>
              )}
            </div>
            <span className="text-[11px] text-slate-500 mt-0.5 truncate">
              {stat.subtitle}
            </span>
          </div>

          {/* Progress Bar */}
          <div className="mt-2.5 w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                backgroundColor: stat.barColor,
                width: `${stat.progressPercent}%`,
              }}
            />
          </div>
        </div>
      ))}
    </div>
  )
}
