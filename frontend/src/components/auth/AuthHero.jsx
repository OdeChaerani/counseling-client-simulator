export default function AuthHero() {
  return (
    <section
      className="lg:w-[46%] xl:w-[44%] w-full text-white p-6 sm:p-10 lg:p-12 xl:p-14 flex flex-col justify-between relative overflow-hidden shrink-0 z-10"
      style={{
        background:
          'linear-gradient(135deg, rgba(28, 23, 48, 0.82) 0%, rgba(42, 35, 68, 0.62) 100%)',
        backdropFilter: 'blur(10px)',
      }}
    >
      {/* Ambient Subtle Background Glow */}
      <div className="absolute -top-28 -left-28 w-80 h-80 bg-[#605982]/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-20 -right-20 w-72 h-72 bg-[#605982]/15 rounded-full blur-3xl pointer-events-none" />

      {/* Top Header / Identification */}
      <div className="relative z-10">
        <div className="inline-flex items-center gap-3.5 flex-wrap">
          <div className="flex items-center font-display text-xl sm:text-2xl tracking-tight font-bold">
            <span className="text-[#f5b51b]">Safe</span>
            <span className="text-white">Sesi</span>
          </div>

          <div className="hidden sm:block h-4 w-[1.5px] bg-[#e6deff]/30 rounded-full" />

          <span className="text-xs sm:text-sm text-[#e6deff]/90 tracking-wide font-medium">
            Psikologi · Universitas Padjadjaran
          </span>
        </div>
      </div>

      {/* Middle Content: Manifesto & Purpose */}
      <div className="relative z-10 py-8 lg:py-6 my-auto">

        {/* Heading */}
        <h1 className="font-display text-2xl sm:text-3xl lg:text-4xl text-white tracking-tight leading-tight mb-4 font-bold">
          Ruang belajar.
          <br />
          <span className="text-[#ebddff] font-normal">Percakapan bermakna.</span>
        </h1>

        {/* Description */}
        <p className="text-xs sm:text-sm text-[#e6deff]/90 leading-relaxed max-w-lg mb-6">
          Platform interaktif bagi mahasiswa psikologi untuk melatih keterampilan
          percakapan konseling secara aman dan terarah.
        </p>

        {/* Golden Accent Bar */}
        <div className="w-12 h-1 bg-[#f5b51b] rounded-full shadow-xs mb-8" />

        {/* Supportive Badges */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-6 border-t border-white/10 max-w-lg">
          <div className="flex items-start gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center shrink-0 text-[#ffdea5] mt-0.5 border border-white/10">
              <span className="material-symbols-outlined text-[18px]">
                psychology_alt
              </span>
            </div>
            <div>
              <p className="text-xs sm:text-sm text-white font-semibold leading-snug">
                Motivational Interviewing
              </p>
              <p className="text-[11px] text-[#e6deff]/70 mt-0.5">
                Kerangka OARS interaktif
              </p>
            </div>
          </div>

          <div className="flex items-start gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center shrink-0 text-[#ffdea5] mt-0.5 border border-white/10">
              <span className="material-symbols-outlined text-[18px]">
                verified_user
              </span>
            </div>
            <div>
              <p className="text-xs sm:text-sm text-white font-semibold leading-snug">
                Ruang Aman Belajar
              </p>
              <p className="text-[11px] text-[#e6deff]/70 mt-0.5">
                Eksplorasi tanpa penghakiman
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Principle Tagline */}
      <div className="relative z-10 pt-4 border-t border-white/10 lg:border-none">
        <p className="text-[11px] text-[#e6deff]/80">
          <span className="text-[#f5b51b] font-semibold">Safe</span>
          <span className="text-white font-semibold">Sesi</span>
          <span className="text-[#e6deff]/80">
            {' '}
            © 2026 · Fakultas Psikologi, Universitas Padjadjaran
          </span>
        </p>
      </div>
    </section>
  )
}

