import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import api from '../api/axios'

export default function Signup() {
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/auth/sign-up', form)
      navigate('/login')
    } catch {
      setError('Email already in use or invalid details')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0f0f0f] flex">

      {/* Left panel */}
      <div className="hidden lg:flex w-1/2 flex-col justify-between p-16 border-r border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-[#e8ff47] rounded-sm" />
          <span className="text-white font-mono text-sm tracking-[0.2em] uppercase">ParkOS</span>
        </div>

        <div>
          <p className="text-white/20 font-mono text-xs tracking-widest uppercase mb-8">
            New Account
          </p>
          <h1 className="text-white text-6xl font-light leading-none tracking-tight mb-6">
            Join the<br />
            <span className="text-[#e8ff47]">System</span>
          </h1>
          <p className="text-white/40 text-sm leading-relaxed max-w-xs font-light">
            Register to access queue and dynamic parking. Your sessions and billing history in one place.
          </p>
        </div>

        {/* Decorative slot grid */}
        <div className="grid grid-cols-6 gap-1.5">
          {Array.from({ length: 18 }).map((_, i) => (
            <div
              key={i}
              className={`h-1.5 rounded-full ${
                [2, 5, 9, 14].includes(i)
                  ? 'bg-[#e8ff47]'
                  : 'bg-white/10'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Right panel — form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-sm">

          <div className="flex items-center gap-3 mb-12 lg:hidden">
            <div className="w-7 h-7 bg-[#e8ff47] rounded-sm" />
            <span className="text-white font-mono text-sm tracking-[0.2em] uppercase">ParkOS</span>
          </div>

          <div className="mb-10">
            <h2 className="text-white text-3xl font-light mb-2">Create account</h2>
            <p className="text-white/30 text-sm font-mono">Fill in your details below</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {[
              { label: 'Full Name', name: 'name', type: 'text', placeholder: 'John Doe' },
              { label: 'Email', name: 'email', type: 'email', placeholder: 'you@example.com' },
              { label: 'Password', name: 'password', type: 'password', placeholder: '8+ characters' },
            ].map(field => (
              <div key={field.name}>
                <label className="block text-white/40 text-xs font-mono tracking-widest uppercase mb-2">
                  {field.label}
                </label>
                <input
                  type={field.type}
                  name={field.name}
                  value={form[field.name as keyof typeof form]}
                  onChange={handleChange}
                  required
                  className="w-full bg-white/5 border border-white/10 text-white text-sm px-4 py-3 rounded-lg
                             focus:outline-none focus:border-[#e8ff47]/60
                             placeholder:text-white/20 transition-colors font-mono"
                  placeholder={field.placeholder}
                />
              </div>
            ))}

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
              {loading ? 'Creating...' : 'Create account →'}
            </button>
          </form>

          <p className="text-white/20 text-xs font-mono text-center mt-8">
            Already registered?{' '}
            <Link to="/login" className="text-[#e8ff47]/70 hover:text-[#e8ff47] transition-colors">
              Sign in
            </Link>
          </p>

        </div>
      </div>
    </div>
  )
}