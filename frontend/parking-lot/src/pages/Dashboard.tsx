import { useAuth } from '../context/AuthContext'
import { Link } from 'react-router-dom'

const userActions = [
  {
    to: '/dynamic-entry',
    label: 'Dynamic Park',
    sub: 'Random slot, leave anytime',
    tag: 'INSTANT',
    tagColor: 'bg-[#e8ff47] text-[#0f0f0f]',
  },
  {
    to: '/queue-entry',
    label: 'Queue Park',
    sub: 'Reserve a slot by time window',
    tag: 'SCHEDULED',
    tagColor: 'bg-white/10 text-white/60',
  },
  {
    to: '/my-sessions',
    label: 'My Sessions',
    sub: 'View active and past sessions',
    tag: 'HISTORY',
    tagColor: 'bg-white/10 text-white/60',
  },
]

export default function Dashboard() {
  const { user } = useAuth()

  return (
    <div className="max-w-2xl mx-auto py-12 px-4">

      <div className="mb-12">
        <p className="text-white/40 font-mono text-xs tracking-widest uppercase mb-3">
          Welcome back
        </p>
        <h1 className="text-white text-4xl font-light">
          {user?.email?.split('@')[0]}
        </h1>
        <div className="w-12 h-px bg-[#e8ff47] mt-4" />
      </div>

    
      <div className="space-y-3">
        {userActions.map(action => (
          <Link
            key={action.to}
            to={action.to}
            className="flex items-center justify-between
                       bg-white/3 border border-white/8
                       hover:border-white/20 hover:bg-white/6
                       rounded-xl p-5 group transition-all duration-200"
          >
            <div>
              <div className="flex items-center gap-3 mb-1">
                <span className="text-white font-light text-lg">{action.label}</span>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${action.tagColor}`}>
                  {action.tag}
                </span>
              </div>
              <p className="text-white/30 text-sm font-mono">{action.sub}</p>
            </div>
            <span className="text-white/40 group-hover:text-white/60 text-xl transition-colors">
              →
            </span>
          </Link>
        ))}
      </div>

    </div>
  )
}