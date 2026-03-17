import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import api from '../api/axios'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/auth/login', { email, password })

      const res = await api.get('/auth/me')
      login(res.data)
      navigate(res.data.role === 'admin' ? '/admin/slots' : '/dashboard')
    } catch {
      setError('Invalid email or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0f0f0f] flex">

      <div className="hidden lg:flex w-1/2 flex-col justify-between p-16 border-r border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-[#e8ff47] rounded-sm" />
          <span className="text-white font-mono text-sm tracking-[0.2em] uppercase">ParkOS</span>
        </div>

        <div>
          <p className="text-white/40 font-mono text-xs tracking-widest uppercase mb-8">
            Slot Management System
          </p>
          <h1 className="text-white text-6xl font-light leading-none tracking-tight mb-6">
            Smart<br />
            <span className="text-[#e8ff47]">Parking</span><br />
            Infrastructure
          </h1>
          <p className="text-white/60 text-sm leading-relaxed max-w-xs font-light">
            Lane-based queue allocation with real-time slot tracking and automated billing.
          </p>
        </div>

        <div className="flex gap-8">
          {['Queue', 'Dynamic', 'Walk-in'].map(label => (
            <div key={label}>
              <div className="w-1 h-1 bg-[#e8ff47] rounded-full mb-2" />
              <span className="text-white/30 text-xs font-mono">{label}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-sm">

          <div className="flex items-center gap-3 mb-12 lg:hidden">
            <div className="w-7 h-7 bg-[#e8ff47] rounded-sm" />
            <span className="text-white font-mono text-sm tracking-[0.2em] uppercase">ParkOS</span>
          </div>

          <div className="mb-10">
            <h2 className="text-white text-3xl font-light mb-2">Sign in</h2>
            <p className="text-white/30 text-sm font-mono">Enter your credentials to continue</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-white/60 text-xs font-mono tracking-widest uppercase mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                className="w-full bg-white/5 border border-white/10 text-white text-sm px-4 py-3 rounded-lg
                           focus:outline-none focus:border-[#e8ff47]/60 focus:bg-white/8
                           placeholder:text-white/20 transition-colors font-mono"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label className="block text-white/60 text-xs font-mono tracking-widest uppercase mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                className="w-full bg-white/5 border border-white/10 text-white text-sm px-4 py-3 rounded-lg
                           focus:outline-none focus:border-[#e8ff47]/60 focus:bg-white/8
                           placeholder:text-white/20 transition-colors font-mono"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <div className="flex items-center gap-2 text-red-400 text-xs font-mono bg-red-400/10 px-4 py-3 rounded-lg border border-red-400/20">
                <span className="w-1 h-1 bg-red-400 rounded-full shrink-0" />
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#e8ff47] text-[#0f0f0f] text-sm font-mono font-bold
                         tracking-widest uppercase py-3 rounded-lg mt-2
                         hover:bg-[#d4eb3a] active:scale-[0.98]
                         disabled:opacity-50 disabled:cursor-not-allowed
                         transition-all duration-150"
            >
              {loading ? 'Signing in...' : 'Sign in →'}
            </button>
          </form>

          <p className="text-white/40 text-xs font-mono text-center mt-8">
            No account?{' '}
            <Link to="/signup" className="text-[#e8ff47]/70 hover:text-[#e8ff47] transition-colors">
              Create one
            </Link>
          </p>

        </div>
      </div>
    </div>
  )
}