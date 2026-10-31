export default function WelcomeBanner({ userName = 'Rani' }) {
  return (
    <div className="flex flex-col md:flex-row md:items-end justify-between gap-3">
      {/* Sambutan Personal */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-1.5">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-[#f5b51b]" />
          <span className="text-[11px] text-[#d3daea] font-medium tracking-wide">
            Tahun Ajaran 2026/2027 · Semester Ganjil
          </span>
        </div>
        <h1 className="text-xl md:text-2xl text-white tracking-tight font-bold">
          Halo, {userName} 👋
        </h1>
        <p className="text-xs md:text-sm text-[#d3daea] max-w-xl leading-relaxed">
          Selamat datang di ruang belajar SafeSesi. Latih keterampilan konseling dan
          refleksi secara terarah dalam lingkungan simulasi yang aman.
        </p>
      </div>

      {/* Quick Action Card Mini (Compact Crisp White Card) */}
      <div className="flex items-center gap-2.5 bg-white px-3.5 py-2 rounded-xl shadow-sm border border-white/20 self-start md:self-auto cursor-pointer hover:shadow-md transition-all duration-200">
        <div className="w-8 h-8 rounded-lg bg-[#ede9fe] text-[#352f55] flex items-center justify-center shrink-0">
          <span className="material-symbols-outlined text-[18px]">auto_stories</span>
        </div>
        <div className="flex flex-col">
          <span className="text-xs font-bold text-[#1e1a34]">
            Panduan MI Terintegrasi
          </span>
          <span className="text-[11px] text-[#64748b]">
            Pedoman OARS &amp; Refleksi
          </span>
        </div>
      </div>
    </div>
  )
}
