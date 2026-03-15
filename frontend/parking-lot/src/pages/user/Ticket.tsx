import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import api from '../../api/axios'
import TicketCard from '../../components/TicketCard'
import type { Ticket } from '../../types'

export default function TicketPage() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const [ticket, setTicket] = useState<Ticket | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchTicket = async () => {
      try {
        const res = await api.get(`/parking/ticket/${sessionId}`)
        setTicket(res.data)
      } catch {
        setError('Ticket not found')
      } finally {
        setLoading(false)
      }
    }
    fetchTicket()
  }, [sessionId])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <span className="text-white/20 font-mono text-sm tracking-widest uppercase">Loading ticket...</span>
      </div>
    )
  }

  if (error || !ticket) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4">
        <p className="text-red-400 font-mono text-sm">{error}</p>
        <Link to="/my-sessions" className="text-[#e8ff47]/60 hover:text-[#e8ff47] font-mono text-xs uppercase tracking-widest transition-colors">
          ← Back to sessions
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-sm mx-auto py-12 px-4">

      <div className="mb-8">
        <Link
          to="/my-sessions"
          className="text-white/20 hover:text-white/50 font-mono text-xs tracking-widest uppercase transition-colors"
        >
          ← My Sessions
        </Link>
      </div>

      <TicketCard ticket={ticket} />

      {/* Print hint */}
      <p className="text-center text-white/15 font-mono text-xs mt-6 tracking-widest uppercase">
        {ticket.status === 'ACTIVE' ? 'Session in progress' : 'Thank you for parking with us'}
      </p>

    </div>
  )
}