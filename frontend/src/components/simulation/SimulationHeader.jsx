import { useEffect, useState } from 'react'

export default function SimulationHeader({
  scenarioTitle = 'Menghadapi kewalahan oleh kesibukan',
  category = 'Latihan Kelas',
  onExitSession,
  isTranscriptOpen = true,
  onToggleTranscript,
}) {
  const [seconds, setSeconds] = useState(252) // 04:12

  useEffect(() => {
    const timer = setInterval(() => {
      setSeconds((prev) => prev + 1)
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  const formatTimer = (totalSeconds) => {
    const mins = String(Math.floor(totalSeconds / 60)).padStart(2, '0')
    const secs = String(totalSeconds % 60).padStart(2, '0')
    return `${mins}:${secs}`
  }

  return (
    <header className="w-full h-14 bg-white border-b border-slate-200 rounded-b-2xl px-5 flex items-center justify-between z-30 shadow-xs shrink-0">
      {/* Left Section: Logo SafeSesi & Context */}
      <div className="flex items-center gap-3">
        <div className="flex items-center tracking-tight font-display text-base md:text-lg leading-none font-bold">
          <span className="text-[#f5b51b]">Safe</span>
          <span className="text-[#352f55]">Sesi</span>
        </div>

        <div className="h-5 w-px bg-slate-200 hidden sm:block" />

        <div className="flex items-center gap-2">
          <span className="text-xs md:text-sm text-[#1e1a34] font-semibold truncate max-w-[200px] sm:max-w-xs md:max-w-md">
            {scenarioTitle}
          </span>
          <span className="bg-[#ede9fe] text-[#352f55] text-[10px] font-semibold px-2.5 py-0.5 rounded-full tracking-wide uppercase shrink-0">
            {category}
          </span>
        </div>
      </div>

      {/* Right Section: Timer directly next to Akhiri Sesi + Transcript Toggle */}
      <div className="flex items-center gap-2.5">
        {/* Toggle Transkrip Button (ketika panel tertutup) */}
        {!isTranscriptOpen && onToggleTranscript && (
          <button
            type="button"
            onClick={onToggleTranscript}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-[#352f55] border border-slate-200/80 text-xs font-semibold transition-colors cursor-pointer"
            title="Buka Panel Transkrip"
          >
            <span className="material-symbols-outlined text-[16px]">forum</span>
            <span className="hidden sm:inline">Buka Transkrip</span>
          </button>
        )}

        {/* Timer Sesi Aktif */}
        <div className="flex items-center gap-2 bg-slate-100 border border-slate-200/80 px-3 py-1 rounded-full shadow-xs">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600" />
          </span>
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] text-emerald-700 font-bold tracking-wide uppercase">
              Sesi Aktif
            </span>
            <span className="text-xs font-bold tracking-wider text-[#1e1a34]">
              {formatTimer(seconds)}
            </span>
          </div>
        </div>

        {/* Tombol Akhiri Sesi */}
        <button
          type="button"
          onClick={onExitSession}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-50 hover:bg-red-100 text-red-600 border border-red-200/80 transition-colors text-xs font-semibold cursor-pointer shadow-xs"
        >
          <span className="material-symbols-outlined text-[16px]">logout</span>
          <span>Akhiri sesi</span>
        </button>
      </div>
    </header>
  )
}
