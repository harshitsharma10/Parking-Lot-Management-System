import type { Ticket } from '../types'

function formatTime(iso: string) {
  return new Date(iso).toLocaleString('en-IN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-white text-xs font-mono uppercase tracking-widest">{label}</span>
      <span className="text-white text-sm font-mono">{value}</span>
    </div>
  )
}

export default function TicketCard({ ticket }: { ticket: Ticket }) {
  return (
    <div className="w-full max-w-sm mx-auto">

      <div className="bg-[#161616] border border-white/10 rounded-2xl overflow-hidden">

        <div className="px-6 pt-6 pb-5 border-b border-white/8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-5 h-5 bg-[#e8ff47] rounded-sm" />
              <span className="text-white font-mono text-xs tracking-[0.2em] uppercase">ParkOS</span>
            </div>
            <span className={`text-[10px] font-mono px-2 py-1 rounded-full
              ${ticket.status === 'ACTIVE'
                ? 'bg-[#e8ff47] text-[#0f0f0f] font-bold'
                : 'bg-white/10 text-white'
              }`}>
              {ticket.status}
            </span>
          </div>
          <p className="text-white font-mono text-xs tracking-widest">{ticket.ticket_id}</p>
          <p className="text-white text-3xl font-light mt-1 tracking-widest">
            {ticket.vehicle_number}
          </p>
        </div>

        <div className="relative flex items-center py-0">
          <div className="w-4 h-4 bg-[#0f0f0f] rounded-full absolute -left-2 border-r border-white/10" />
          <div className="flex-1 border-t border-dashed border-white/10 mx-6" />
          <div className="w-4 h-4 bg-[#0f0f0f] rounded-full absolute -right-2 border-l border-white/10" />
        </div>

        <div className="px-6 py-5 space-y-3">
          <Row label="Type" value={`${ticket.vehicle_type} · ${ticket.parking_type}`} />
          <Row label="Slot" value={ticket.slot_number} />
          <Row label="Floor" value={ticket.floor} />
          {ticket.lane !== null && ticket.position !== null && (
            <Row label="Lane / Position" value={`Lane ${ticket.lane}, Pos ${ticket.position}`} />
          )}
          <Row label="Entry" value={formatTime(ticket.entry_time)} />
          {ticket.exit_time
            ? <Row label="Exit" value={formatTime(ticket.exit_time)} />
            : ticket.expected_exit_time
              ? <Row label="Expected Exit" value={formatTime(ticket.expected_exit_time)} />
              : null
          }
          {ticket.duration && (
            <Row label="Duration" value={ticket.duration} />
          )}
        </div>

        <div className="relative flex items-center py-0">
          <div className="w-4 h-4 bg-[#0f0f0f] rounded-full absolute -left-2 border-r border-white/10" />
          <div className="flex-1 border-t border-dashed border-white/10 mx-6" />
          <div className="w-4 h-4 bg-[#0f0f0f] rounded-full absolute -right-2 border-l border-white/10" />
        </div>

        <div className="px-6 py-5 flex justify-between items-center">
          <span className="text-white text-xs font-mono uppercase tracking-widest">
            {ticket.status === 'ACTIVE' ? 'Estimated' : 'Amount Charged'}
          </span>
          <span className="text-[#e8ff47] text-3xl font-light">
            {ticket.amount_charged !== null ? `₹${ticket.amount_charged}` : '—'}
          </span>
        </div>

      </div>
    </div>
  )
}