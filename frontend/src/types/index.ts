export interface User {
  id: number
  telegram_id: number
  phone: string | null
  name: string
  created_at: string
}

export interface Address {
  id: number
  user_id: number
  city: string
  district: string
  street: string
  house: string
  is_default: boolean
  created_at: string
}

export interface Order {
  id: number
  user_id: number
  address_id: number | null
  jv_qty: number
  lv_qty: number
  total_qty: number
  delivery_date: string | null
  status: OrderStatus
  comment: string | null
  created_at: string
  confirmed_at: string | null
  operator_id: number | null
}

export type OrderStatus =
  | 'draft'
  | 'new'
  | 'confirmed'
  | 'rescheduled'
  | 'in_delivery'
  | 'completed'
  | 'cancelled'
  | 'payment_pending'
  | 'paid'

export interface OrderListResponse {
  orders: Order[]
  total: number
}

export interface District {
  id: number
  district: string
  max_per_day: number
  is_active: boolean
}

export interface DeliveryDateResponse {
  delivery_date: string
  district: string
  district_remaining: number
  total_remaining: number
}
