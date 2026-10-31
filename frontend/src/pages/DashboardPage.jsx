import WelcomeBanner from '../components/dashboard/WelcomeBanner'
import StatCards from '../components/dashboard/StatCards'
import ClassActivities from '../components/dashboard/ClassActivities'
import RecentHistory from '../components/dashboard/RecentHistory'

export default function DashboardPage({ onStartExercise }) {
  const handleStartExercise = (activity) => {
    if (onStartExercise) {
      onStartExercise(activity)
    } else {
      console.log('Mulai latihan untuk:', activity.title)
    }
  }

  const handleViewAllHistory = () => {
    console.log('Lihat semua riwayat')
  }

  const handleHistoryAction = (item) => {
    console.log('Aksi riwayat:', item.actionLabel, item.title)
  }

  return (
    <>
      {/* 1. Header Sambutan Personal */}
      <WelcomeBanner userName="Rani" />

      {/* 2. 4 Kartu Statistik */}
      <StatCards />

      {/* 3. Kegiatan Kelas yang Menunggu */}
      <ClassActivities onStartExercise={handleStartExercise} />

      {/* 4. Riwayat Terbaru */}
      <RecentHistory
        onViewAll={handleViewAllHistory}
        onItemAction={handleHistoryAction}
      />
    </>
  )
}
