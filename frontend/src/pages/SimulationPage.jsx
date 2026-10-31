import { useState } from 'react'
import SimulationHeader from '../components/simulation/SimulationHeader'
import VirtualClientStage from '../components/simulation/VirtualClientStage'
import TranscriptPanel from '../components/simulation/TranscriptPanel'

const INITIAL_MESSAGES = [
  {
    sender: 'counselor',
    name: 'Rani Aulia',
    time: '03:45',
    text: 'Bisa kamu ceritakan apa yang saat ini paling menyita waktumu?',
  },
  {
    sender: 'client',
    name: 'Nadia Putri',
    time: '03:52',
    text: 'Jadwal kuliah semester ini cukup padat, ditambah lagi ada persiapan proker himpunan yang tenggatnya berdekatan...',
  },
  {
    sender: 'counselor',
    name: 'Rani Aulia',
    time: '04:05',
    text: 'Tampaknya kamu merasa tertekan ketika beberapa tanggung jawab datang bersamaan.',
  },
  {
    sender: 'client',
    name: 'Nadia Putri',
    time: '04:11',
    text: 'Iya, betul sekali... rasanya bingung harus mulai dari mana.',
  },
]

export default function SimulationPage({
  scenario = {
    title: 'Menghadapi kewalahan oleh kesibukan',
    category: 'Latihan Kelas',
    clientName: 'Nadia Putri',
  },
  onExitSession,
}) {
  const [messages, setMessages] = useState(INITIAL_MESSAGES)
  const [isProcessing, setIsProcessing] = useState(false)
  const [clientStatus, setClientStatus] = useState('Mendengarkan aktif')

  // State untuk Panel Transkrip (Buka/Tutup & Ukuran Lebar)
  const [isTranscriptOpen, setIsTranscriptOpen] = useState(true)
  const [transcriptWidth, setTranscriptWidth] = useState(340)

  const getCurrentTime = () => {
    const now = new Date()
    return `${String(now.getMinutes()).padStart(2, '0')}:${String(
      now.getSeconds()
    ).padStart(2, '0')}`
  }

  const handleSendMessage = (text) => {
    const counselorMsg = {
      sender: 'counselor',
      name: 'Rani Aulia',
      time: getCurrentTime(),
      text,
    }

    setMessages((prev) => [...prev, counselorMsg])
    setIsProcessing(true)
    setClientStatus('Sedang merespons...')

    // Simulasi respons interaktif dari klien virtual
    setTimeout(() => {
      const clientReplies = [
        'Kadang aku merasa kalau aku menolak tugas himpunan, teman-teman akan kecewa padaku.',
        'Aku mencoba bikin to-do list, tapi pas lihat daftarnya malah tambah cemas dan pusing.',
        'Menurutmu wajar gak sih kalau aku merasa ingin istirahat dulu sejenak dari semua ini?',
        'Iya, rasanya seperti dituntut sempurna di semua hal, padahal tenagaku ada batasnya.',
      ]

      const randomReply =
        clientReplies[Math.floor(Math.random() * clientReplies.length)]

      const clientMsg = {
        sender: 'client',
        name: scenario.clientName || 'Nadia Putri',
        time: getCurrentTime(),
        text: randomReply,
      }

      setMessages((prev) => [...prev, clientMsg])
      setIsProcessing(false)
      setClientStatus('Mendengarkan aktif')
    }, 1200)
  }

  const handleStartResize = (e) => {
    e.preventDefault()
    const startX = e.clientX
    const startWidth = transcriptWidth

    const handleMouseMove = (moveEvent) => {
      const delta = startX - moveEvent.clientX
      const newWidth = Math.min(Math.max(startWidth + delta, 260), 560)
      setTranscriptWidth(newWidth)
    }

    const handleMouseUp = () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseup', handleMouseUp)
  }

  const handleConfirmExit = () => {
    if (
      window.confirm(
        'Apakah Anda yakin ingin mengakhiri sesi latihan ini sekarang?'
      )
    ) {
      if (onExitSession) onExitSession()
    }
  }

  return (
    <div className="w-full h-screen flex flex-col bg-[#352f55] text-white overflow-hidden select-none">
      {/* 1. Header Bar: Navbar Putih dengan Timer di samping tombol Akhiri Sesi */}
      <SimulationHeader
        scenarioTitle={scenario.title}
        category={scenario.category}
        onExitSession={handleConfirmExit}
        isTranscriptOpen={isTranscriptOpen}
        onToggleTranscript={() => setIsTranscriptOpen((prev) => !prev)}
      />

      {/* 2. Workspace Area: Background Ungu Beranda (#352f55) */}
      <div className="flex-1 flex flex-col md:flex-row relative w-full h-[calc(100vh-56px)] overflow-hidden bg-[#352f55]">
        {/* Central Stage */}
        <VirtualClientStage
          clientName={scenario.clientName}
          clientStatus={clientStatus}
          onSendMessage={handleSendMessage}
          isProcessing={isProcessing}
          isTranscriptOpen={isTranscriptOpen}
          onOpenTranscript={() => setIsTranscriptOpen(true)}
        />

        {/* Right Transcript Panel: Collapsible & Resizable */}
        {isTranscriptOpen && (
          <TranscriptPanel
            messages={messages}
            width={transcriptWidth}
            onClose={() => setIsTranscriptOpen(false)}
            onStartResize={handleStartResize}
          />
        )}
      </div>
    </div>
  )
}
