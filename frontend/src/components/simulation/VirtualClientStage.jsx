import { useState } from 'react'

export default function VirtualClientStage({
  clientName = 'Nadia Putri',
  clientStatus = 'Mendengarkan aktif',
  onSendMessage,
  isProcessing = false,
  isTranscriptOpen = true,
  onOpenTranscript,
}) {
  const [inputText, setInputText] = useState('')
  const [isBioOpen, setIsBioOpen] = useState(true)
  const [isMicActive, setIsMicActive] = useState(false)
  const [isCamActive, setIsCamActive] = useState(true)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!inputText.trim() || isProcessing) return
    onSendMessage(inputText.trim())
    setInputText('')
  }

  return (
    <div
      className="flex-1 flex flex-col items-center justify-between p-4 md:p-6 relative overflow-hidden select-none"
      style={{
        background:
          'radial-gradient(circle at 50% 28%, #453b6a 0%, #352f55 55%, #2a2444 100%)',
      }}
    >
      {/* Ambient Studio Lighting Glow */}
      <div className="absolute w-[460px] h-[460px] rounded-full bg-gradient-to-tr from-[#65587c]/25 via-[#503a73]/25 to-[#f5b51b]/15 blur-3xl pointer-events-none -translate-y-6" />

      {/* Floating Toggle Button for Transcript (muncul di kanan saat panel tertutup) */}
      {!isTranscriptOpen && onOpenTranscript && (
        <button
          type="button"
          onClick={onOpenTranscript}
          title="Buka Transkrip Sesi"
          className="absolute right-4 top-4 z-30 flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-white text-[#352f55] shadow-xl hover:shadow-2xl border border-slate-100 text-xs font-bold transition-all cursor-pointer hover:bg-slate-50"
        >
          <span className="material-symbols-outlined text-[17px] text-[#f5b51b]">
            forum
          </span>
          <span>Transkrip</span>
        </button>
      )}

      {/* 3D Avatar Center Display */}
      <div className="flex-1 flex flex-col items-center justify-center w-full z-10 my-auto">
        <div className="relative flex flex-col items-center justify-center">
          {/* Pulsing Golden Glow behind Avatar */}
          <div className="absolute -top-3 w-44 h-44 rounded-full bg-[#f5b51b]/15 blur-2xl animate-pulse pointer-events-none" />

          {/* Avatar Container */}
          <div className="p-4 rounded-full bg-[#27213f]/70 backdrop-blur-md border border-white/20 shadow-2xl mb-2.5">
            <svg
              className="w-36 h-36 md:w-40 md:h-40 text-[#cfc0e9] drop-shadow-[0_10px_20px_rgba(0,0,0,0.5)]"
              fill="currentColor"
              viewBox="0 0 200 200"
            >
              <path
                d="M100 28 C82 28 69 42 69 61 C69 77 78 88 88 94 C88 98 86 103 82 108 C64 116 46 130 42 154 L158 154 C154 130 136 116 118 108 C114 103 112 98 112 94 C122 88 131 77 131 61 C131 42 118 28 100 28 Z"
                fill="#3f2e54"
                opacity="0.95"
              />
              <ellipse cx="100" cy="58" fill="#d7cefe" opacity="0.4" rx="24" ry="29" />
              <path
                d="M52 148 C58 128 76 117 100 117 C124 117 142 128 148 148 Z"
                fill="#544570"
                opacity="0.75"
              />
              <circle cx="93" cy="58" fill="#ffffff" opacity="0.95" r="2.5" />
              <circle cx="107" cy="58" fill="#ffffff" opacity="0.95" r="2.5" />
              <path
                d="M96 71 Q100 74 104 71"
                fill="none"
                opacity="0.8"
                stroke="#ffffff"
                strokeLinecap="round"
                strokeWidth="1.5"
              />
            </svg>
          </div>
        </div>

        {/* Client Name & Live Status Badge (Crisp White Card) */}
        <div className="flex flex-col items-center mt-3">
          <div className="flex items-center gap-1.5">
            <h2 className="text-white text-base md:text-lg font-bold drop-shadow-sm">
              {clientName}
            </h2>
            <span className="text-[#cfc0e9] text-xs font-medium">· Klien Virtual</span>
          </div>

          <div className="flex items-center gap-2 mt-1.5 px-3 py-1 rounded-full bg-white shadow-md border border-slate-100">
            <div className="flex items-center gap-1 h-2.5 text-[#f5b51b]">
              <span
                className="w-1 h-2 bg-[#f5b51b] rounded-full animate-bounce"
                style={{ animationDelay: '0.1s' }}
              />
              <span
                className="w-1 h-3 bg-[#f5b51b] rounded-full animate-bounce"
                style={{ animationDelay: '0.25s' }}
              />
              <span
                className="w-1 h-2 bg-[#f5b51b] rounded-full animate-bounce"
                style={{ animationDelay: '0.4s' }}
              />
            </div>
            <span className="text-xs text-[#1e1a34] font-semibold">
              {isProcessing ? 'Sedang memproses...' : clientStatus}
            </span>
          </div>
        </div>
      </div>

      {/* Floating Bottom-Left Controls (Camera Preview & Client Bio) */}
      <div className="hidden lg:flex absolute bottom-5 left-5 flex-col gap-2.5 z-30 max-w-[240px]">
        {/* Crisp White Info Klien Card */}
        <div className="rounded-xl p-3 shadow-xl transition-all duration-300 bg-white border border-slate-100 text-[#1e1a34]">
          <div
            className="flex items-center justify-between cursor-pointer"
            onClick={() => setIsBioOpen((prev) => !prev)}
          >
            <div className="flex items-center gap-1.5">
              <span className="material-symbols-outlined text-[#f5b51b] text-base">
                badge
              </span>
              <span className="text-xs font-bold text-[#1e1a34]">Info Klien</span>
            </div>
            <span className="material-symbols-outlined text-slate-400 text-base">
              {isBioOpen ? 'expand_less' : 'expand_more'}
            </span>
          </div>

          {isBioOpen && (
            <div className="mt-2 pt-2 flex flex-col gap-1 border-t border-slate-100 text-[11px]">
              <div className="flex justify-between items-center">
                <span className="text-slate-500 font-medium">Nama:</span>
                <span className="font-bold text-[#1e1a34]">{clientName}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-500 font-medium">Usia:</span>
                <span className="font-semibold text-slate-700">19 th · Perempuan</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-500 font-medium">Status:</span>
                <span className="font-semibold text-slate-700">Sem. 3 · Psikologi</span>
              </div>
              <div className="mt-1 p-2 rounded-lg text-[10px] leading-relaxed text-slate-600 bg-slate-50 border border-slate-200/80">
                Kewalahan membagi waktu kuliah &amp; organisasi, memicu kelelahan mental.
              </div>
            </div>
          )}
        </div>

        {/* Crisp White Mini Self-Camera Card */}
        <div className="w-38 rounded-xl overflow-hidden shadow-xl flex flex-col justify-between p-2.5 bg-white border border-slate-100">
          <div className="flex items-center justify-between mb-1.5">
            <div className="flex items-center gap-1 bg-slate-100 px-1.5 py-0.5 rounded-full border border-slate-200/80">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span className="text-[9px] font-bold text-[#1e1a34] tracking-wider">
                Anda
              </span>
            </div>
            <span className="material-symbols-outlined text-slate-400 text-xs">
              {isCamActive ? 'videocam' : 'videocam_off'}
            </span>
          </div>

          {/* Video Preview Box */}
          <div className="w-full h-14 rounded-lg bg-[#241d3b] flex items-center justify-center relative overflow-hidden mb-1.5">
            <span className="material-symbols-outlined text-2xl text-[#cfc0e9]/50">
              person
            </span>
          </div>

          {/* Camera Toggle Button */}
          <button
            type="button"
            onClick={() => setIsCamActive((prev) => !prev)}
            className="w-full bg-slate-100 hover:bg-slate-200 text-[#1e1a34] py-1 px-2 rounded-lg text-[10px] font-semibold flex items-center justify-center gap-1 transition-colors cursor-pointer border border-slate-200/60"
            title={isCamActive ? 'Matikan Kamera' : 'Nyalakan Kamera'}
          >
            <span className="material-symbols-outlined text-xs text-[#352f55]">
              {isCamActive ? 'videocam' : 'videocam_off'}
            </span>
            <span>{isCamActive ? 'Kamera Aktif' : 'Kamera Mati'}</span>
          </button>
        </div>
      </div>

      {/* Crisp White Input Teks Bar Card */}
      <div className="w-full max-w-lg z-20 pb-1 px-2">
        <form
          onSubmit={handleSubmit}
          className="flex items-center gap-2 bg-white border border-slate-100 rounded-2xl p-1.5 shadow-2xl"
        >
          {/* Counselor Text Input Field */}
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={isProcessing}
            placeholder="Tuliskan respons refleksi atau pertanyaan konseling..."
            className="flex-1 bg-slate-50 border border-slate-200/80 rounded-xl px-3.5 py-2 text-xs md:text-sm text-[#1e1a34] placeholder-slate-400 focus:outline-none focus:border-[#f5b51b] focus:bg-white transition"
          />

          {/* Mic Toggle Button (Voice Option) */}
          <button
            type="button"
            onClick={() => setIsMicActive((prev) => !prev)}
            className={`w-9 h-9 rounded-xl flex items-center justify-center transition shrink-0 cursor-pointer border ${
              isMicActive
                ? 'bg-[#f5b51b] text-[#352f55] border-[#f5b51b] shadow-sm'
                : 'bg-slate-100 hover:bg-slate-200 text-slate-600 border-slate-200/80'
            }`}
            title={isMicActive ? 'Matikan Mikrofon' : 'Gunakan Input Suara'}
          >
            <span className="material-symbols-outlined text-lg">
              {isMicActive ? 'mic' : 'mic_none'}
            </span>
          </button>

          {/* Send Button */}
          <button
            type="submit"
            disabled={!inputText.trim() || isProcessing}
            className="px-3.5 h-9 rounded-xl bg-[#f5b51b] hover:bg-[#ffd05b] disabled:opacity-50 disabled:cursor-not-allowed text-[#352f55] font-bold text-xs flex items-center gap-1 transition shadow-sm cursor-pointer shrink-0"
          >
            <span className="material-symbols-outlined text-base">send</span>
          </button>
        </form>
      </div>
    </div>
  )
}
