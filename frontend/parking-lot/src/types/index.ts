export interface User {
  email: string
  role: 'user' | 'admin'
  id: number
}

export interface ParkingSlot {
  id: number
  slot_number: string
  slot_type: 'QUEUE' | 'DYNAMIC'
  floor: string
  lane: number | null
  position: number | null
  status: 'AVAILABLE' | 'OCCUPIED'
}

export interface ParkingSession {
  id: number
  vehicle_number: string
  vehicle_type: 'CAR' | 'BIKE' | 'TRUCK'
  slot_id: number
  parking_type: 'QUEUE' | 'DYNAMIC'
  entry_time: string
  expected_exit_time: string | null
  actual_exit_time: string | null
  status: 'ACTIVE' | 'COMPLETED'
  amount_charged: number | null
  user_id: number | null
}

export interface Ticket {
  ticket_id: string
  vehicle_number: string
  vehicle_type: string
  slot_number: string
  floor: string
  lane: number | null
  position: number | null
  parking_type: string
  entry_time: string
  expected_exit_time: string | null
  exit_time: string | null
  duration: string | null
  amount_charged: number | null
  status: string
}

export interface QueueEntryRequest {
  vehicle_number: string
  vehicle_type: 'CAR' | 'BIKE' | 'TRUCK'
  entry_time: string
  expected_exit_time: string
}

export interface DynamicEntryRequest {
  vehicle_number: string
  vehicle_type: 'CAR' | 'BIKE' | 'TRUCK'
}

export interface WalkInRequest {
  vehicle_number: string
  vehicle_type: 'CAR' | 'BIKE' | 'TRUCK'
  slot_id?: number
}