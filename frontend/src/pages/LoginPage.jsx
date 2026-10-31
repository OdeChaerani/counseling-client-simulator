import AuthBackground from '../components/auth/AuthBackground'
import AuthHero from '../components/auth/AuthHero'
import LoginForm from '../components/auth/LoginForm'

export default function LoginPage({ onLogin }) {
  const handleLoginSubmit = (credentials) => {
    if (onLogin) {
      onLogin(credentials)
    }
  }

  return (
    <main className="w-full min-h-screen flex items-center justify-center relative bg-[#352f55] select-none">
      <div className="min-h-screen w-full flex flex-col lg:flex-row relative overflow-hidden">
        {/* 1. Dynamic SVG Background */}
        <AuthBackground />

        {/* 2. Left Column: Brand & Academic Manifesto */}
        <AuthHero />

        {/* 3. Right Column: Authentication Card */}
        <section className="flex-1 flex items-center justify-center p-6 sm:p-10 lg:p-12 xl:p-16 relative overflow-hidden z-10">
          <LoginForm onSubmit={handleLoginSubmit} />
        </section>
      </div>
    </main>
  )
}

