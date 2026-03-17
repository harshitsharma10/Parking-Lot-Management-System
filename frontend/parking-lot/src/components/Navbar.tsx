import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/axios'

const userLinks = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/dynamic-entry', label: 'Dynamic Parking' },
  { to: '/queue-entry', label: 'Queue Parking' },
  { to: '/my-sessions', label: 'My Sessions' },
]

const adminLinks = [
  { to: '/admin/slots', label: 'Slots' },
  { to: '/admin/sessions', label: 'Sessions' },
  { to: '/admin/walk-in', label: 'Walk-in' },
]

export default function Navbar() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  const links = user?.role === 'admin' ? adminLinks : userLinks

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout')
    } catch {
    
    } finally {
      logout()
      navigate('/login')
    }
  }

  return (
    <nav className="bg-[#0f0f0f] border-b border-white/10 px-6 py-4 flex items-center justify-between sticky top-0 z-50">

      <Link to={user?.role === 'admin' ? '/admin/slots' : '/dashboard'} className="flex items-center gap-3">
        <div className="w-6 h-6 bg-[#e8ff47] rounded-sm shrink-0" />
        <span className="text-white font-mono text-sm tracking-[0.2em] uppercase">ParkOS</span>
      </Link>

      <div className="hidden md:flex items-center gap-1">
        {links.map(link => {
          const active = location.pathname === link.to
          return (
            <Link
              key={link.to}
              to={link.to}
              className={`px-4 py-2 rounded-md text-xs font-mono tracking-widest uppercase transition-all duration-150
                ${active
                  ? 'bg-white/10 text-white'
                  : 'text-white hover:text-white/70 hover:bg-white/5'
                }`}
            >
              {link.label}
            </Link>
          )
        })}
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden sm:flex items-center gap-2">
          <span className={`w-1.5 h-1.5 rounded-full ${user?.role === 'admin' ? 'bg-[#e8ff47]' : 'bg-white/30'}`} />
          <span className="text-white text-xs font-mono uppercase tracking-widest">
            {user?.role ?? 'guest'}
          </span>
        </div>

        <button
          onClick={handleLogout}
          className="text-white hover:text-white/60 text-xs font-mono tracking-widest uppercase
                     transition-colors px-3 py-2 rounded-md hover:bg-white/5"
        >
          Exit
        </button>
      </div>

    </nav>
  )
}