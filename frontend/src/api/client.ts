import axios from 'axios'
import type { User, Address, Order, OrderListResponse, District } from '../types'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// === Пользователи ===
export const getUser = (telegramId: number) =>
  api.get<User>(`/users/tg/${telegramId}`)

export const registerUser = (data: { telegram_id: number; name: string; phone: string }) =>
  api.post<User>('/users/', data)

// === Адреса ===
export const getAddresses = (telegramId: number) =>
  api.get<Address[]>(`/addresses/user/${telegramId}`)

export const addAddress = (telegramId: number, data: Omit<Address, 'id' | 'user_id' | 'created_at'>) =>
  api.post<Address>(`/addresses/user/${telegramId}`, data)

export const deleteAddress = (addressId: number) =>
  api.delete(`/addresses/${addressId}`)

// === Заказы ===
export const createOrder = (
  telegramId: number,
  data: { address_id: number; jv_qty: number; lv_qty: number; comment?: string }
) => api.post<Order>(`/orders/user/${telegramId}`, data)

export const getOrders = (telegramId: number, limit = 20, offset = 0) =>
  api.get<OrderListResponse>(`/orders/user/${telegramId}`, { params: { limit, offset } })

export const getActiveOrder = (telegramId: number) =>
  api.get<Order | null>(`/orders/user/${telegramId}/active`)

export const getLastCompleted = (telegramId: number) =>
  api.get<Order | null>(`/orders/user/${telegramId}/last-completed`)

export const updateOrder = (orderId: number, data: Partial<Order>) =>
  api.patch<Order>(`/orders/${orderId}`, data)

// === Районы ===
export const getDistricts = () =>
  api.get<District[]>('/districts/')

export default api
