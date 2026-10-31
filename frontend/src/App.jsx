import { useState } from 'react'
import DashboardLayout from './components/layout/DashboardLayout'
import DashboardPage from './pages/DashboardPage'
import SimulationPage from './pages/SimulationPage'
import LoginPage from './pages/LoginPage'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [activeTab, setActiveTab] = useState('beranda')
  const [currentScenario, setCurrentScenario] = useState(null)
  const [isSimulating, setIsSimulating] = useState(false)

  const handleLogin = (credentials) => {
    console.log('Login berhasil:', credentials)
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
    setIsSimulating(false)
    setCurrentScenario(null)
    setActiveTab('beranda')
  }

  const handleStartExercise = (activity) => {
    setCurrentScenario({
      title: activity.title,
      category: activity.category,
      clientName: activity.clientName,
    })
    setIsSimulating(true)
  }

  const handleExitSimulation = () => {
    setIsSimulating(false)
    setCurrentScenario(null)
  }

  // Jika belum login, tampilkan halaman Login
  if (!isAuthenticated) {
    return <LoginPage onLogin={handleLogin} />
  }

  // Jika sedang dalam ruang simulasi, render layar penuh SimulationPage
  if (isSimulating) {
    return (
      <SimulationPage
        scenario={currentScenario || undefined}
        onExitSession={handleExitSimulation}
      />
    )
  }

  return (
    <DashboardLayout
      activeTab={activeTab}
      onSelectTab={setActiveTab}
      onLogout={handleLogout}
    >
      {activeTab === 'beranda' && (
        <DashboardPage onStartExercise={handleStartExercise} />
      )}

      {activeTab === 'latihan-mandiri' && (
        <div className="bg-white p-6 md:p-8 rounded-2xl shadow-xs border border-slate-100 flex flex-col items-center justify-center text-center gap-3 py-14">
          <div className="w-12 h-12 rounded-xl bg-[#ede9fe] text-[#352f55] flex items-center justify-center">
            <span className="material-symbols-outlined text-[28px]">
              psychology
            </span>
          </div>
          <h2 className="text-lg md:text-xl text-[#1e1a34] font-bold">
            Ruang Latihan Mandiri
          </h2>
          <p className="text-xs md:text-sm text-[#64748b] max-w-md">
            Mulai simulasi konseling dengan klien virtual untuk mengasah keterampilan
            refleksi dan pertanyaan terbuka.
          </p>
          <button
            type="button"
            onClick={() =>
              handleStartExercise({
                title: 'Latihan Mandiri Eksplorasi Hambatan Belajar',
                category: 'Latihan Bebas',
                clientName: 'Nadia Putri',
              })
            }
            className="mt-2 bg-[#f5b51b] hover:bg-[#e2a613] text-[#1e1a34] px-4 py-2 rounded-xl text-xs md:text-sm font-bold flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer"
          >
            <span className="material-symbols-outlined text-[18px]">
              play_arrow
            </span>
            <span>Masuk Ruang Simulasi</span>
          </button>
        </div>
      )}

      {activeTab === 'kelas-saya' && (
        <div className="bg-white p-6 md:p-8 rounded-2xl shadow-xs border border-slate-100 flex flex-col items-center justify-center text-center gap-3 py-14">
          <div className="w-12 h-12 rounded-xl bg-[#ede9fe] text-[#352f55] flex items-center justify-center">
            <span className="material-symbols-outlined text-[28px]">school</span>
          </div>
          <h2 className="text-lg md:text-xl text-[#1e1a34] font-bold">
            Kelas Praktikum Saya
          </h2>
          <p className="text-xs md:text-sm text-[#64748b] max-w-md">
            Daftar penugasan terstruktur dari dosen pengampu praktikum konseling Anda.
          </p>
          <button
            type="button"
            onClick={() => setActiveTab('beranda')}
            className="mt-2 bg-[#f5b51b] hover:bg-[#e2a613] text-[#1e1a34] px-4 py-2 rounded-xl text-xs md:text-sm font-bold flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer"
          >
            <span>Kembali ke Beranda</span>
          </button>
        </div>
      )}

      {activeTab === 'riwayat' && (
        <div className="bg-white p-6 md:p-8 rounded-2xl shadow-xs border border-slate-100 flex flex-col items-center justify-center text-center gap-3 py-14">
          <div className="w-12 h-12 rounded-xl bg-[#ede9fe] text-[#352f55] flex items-center justify-center">
            <span className="material-symbols-outlined text-[28px]">history</span>
          </div>
          <h2 className="text-lg md:text-xl text-[#1e1a34] font-bold">
            Riwayat Sesi Konseling
          </h2>
          <p className="text-xs md:text-sm text-[#64748b] max-w-md">
            Arsip seluruh transkrip percakapan, metrik evaluasi OARS, dan catatan perkembangan klien.
          </p>
          <button
            type="button"
            onClick={() => setActiveTab('beranda')}
            className="mt-2 bg-[#f5b51b] hover:bg-[#e2a613] text-[#1e1a34] px-4 py-2 rounded-xl text-xs md:text-sm font-bold flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer"
          >
            <span>Kembali ke Beranda</span>
          </button>
        </div>
      )}
    </DashboardLayout>
  )
}

export default App
