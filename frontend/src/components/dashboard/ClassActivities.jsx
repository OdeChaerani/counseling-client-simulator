const DEFAULT_ACTIVITIES = [
  {
    id: 'activity-1',
    category: 'Latihan Kelas',
    deadline: '28 Oktober 2026',
    title: 'Eksplorasi Empati & Pertanyaan Terbuka',
    course: 'Praktikum Konseling Dasar · Kelas A (Dr. Ratna Dewi, M.Psi.)',
    clientName: 'Nadia Putri',
    duration: '15 menit',
    focus: 'Refleksi Kompleks',
    note: 'Wajib diselesaikan sebelum praktikum',
  },
  {
    id: 'activity-2',
    category: 'Latihan Kelas',
    deadline: '5 November 2026',
    title: 'Refleksi Dua Sisi Hambatan Akademik',
    course: 'Wawancara & Observasi Klinis · Kelas B',
    clientName: 'Nadia Putri',
    duration: '20 menit',
    focus: 'Eksplorasi Ambivalensi',
    note: 'Tersedia transkrip evaluasi otomatis',
  },
]

export default function ClassActivities({
  activities = DEFAULT_ACTIVITIES,
  onStartExercise,
}) {
  return (
    <div className="flex flex-col gap-3">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#f5b51b] inline-block" />
          <h2 className="text-base md:text-lg text-white font-bold tracking-tight">
            Kegiatan kelas
          </h2>
        </div>
        <span className="text-[11px] text-[#d3daea] font-medium bg-white/10 px-2.5 py-0.5 rounded-full">
          {activities.length} Penugasan aktif
        </span>
      </div>

      {/* Activities Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {activities.map((activity) => (
          <div
            key={activity.id}
            className="bg-white p-4 md:p-5 rounded-xl shadow-xs border border-slate-100 flex flex-col justify-between hover:shadow-md transition-all duration-200"
          >
            <div className="flex flex-col">
              {/* Badge & Deadline */}
              <div className="flex items-center justify-between gap-2 flex-wrap">
                <span className="bg-[#ede9fe] text-[#352f55] text-[11px] px-2 py-0.5 rounded-full font-semibold">
                  {activity.category}
                </span>
                <div className="flex items-center gap-1 text-slate-500 text-[11px]">
                  <span className="material-symbols-outlined text-[14px]">
                    schedule
                  </span>
                  <span className="font-medium">Tenggat: {activity.deadline}</span>
                </div>
              </div>

              {/* Title & Course */}
              <h3 className="text-sm md:text-base text-[#1e1a34] mt-2 leading-snug font-bold">
                {activity.title}
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                {activity.course}
              </p>

              {/* Virtual Client Info Box */}
              <div className="mt-3 bg-slate-50 border border-slate-200/70 p-2.5 rounded-lg flex items-center gap-3">
                <div className="w-9 h-9 rounded-full shrink-0 bg-[#ede9fe] flex items-center justify-center text-[#352f55]">
                  <span className="material-symbols-outlined text-[20px]">
                    person
                  </span>
                </div>
                <div className="flex flex-col min-w-0">
                  <span className="text-xs text-[#1e1a34] font-semibold truncate">
                    Klien Virtual: {activity.clientName}
                  </span>
                  <div className="flex items-center gap-1.5 text-slate-500 text-[11px] mt-0.5 flex-wrap">
                    <span className="material-symbols-outlined text-[13px]">
                      hourglass_empty
                    </span>
                    <span>Durasi: {activity.duration}</span>
                    <span>·</span>
                    <span>Fokus: {activity.focus}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Card Footer */}
            <div className="mt-4 pt-2.5 border-t border-slate-100 flex items-center justify-between gap-2">
              <span className="text-[11px] text-slate-500">
                {activity.note}
              </span>
              <button
                type="button"
                onClick={() => onStartExercise && onStartExercise(activity)}
                className="bg-[#f5b51b] hover:bg-[#e2a613] text-[#1e1a34] px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1 transition-colors shadow-xs cursor-pointer shrink-0"
              >
                <span>Mulai latihan</span>
                <span className="material-symbols-outlined text-[16px]">
                  play_arrow
                </span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
