import { useState, useEffect, useCallback } from 'react'
import { getOrders, getActiveOrder } from '../api/client'
import type { Order } from '../types'

export function useOrders(telegramId: number | null) {
  const [orders, setOrders] = useState<Order[]>([])
  const [activeOrder, setActiveOrder] = useState<Order | null>(null)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)

  const fetchOrders = useCallback(async (offset = 0) => {
    if (!telegramId) return
    setLoading(true)
    try {
      const { data } = await getOrders(telegramId, 20, offset)
      setOrders(data.orders)
      setTotal(data.total)
    } catch (e) {
      console.error('Ошибка загрузки заказов:', e)
    } finally {
      setLoading(false)
    }
  }, [telegramId])

  const fetchActive = useCallback(async () => {
    if (!telegramId) return
    try {
      const { data } = await getActiveOrder(telegramId)
      setActiveOrder(data)
    } catch {
      setActiveOrder(null)
    }
  }, [telegramId])

  useEffect(() => {
    fetchOrders()
    fetchActive()
  }, [fetchOrders, fetchActive])

  return { orders, activeOrder, total, loading, fetchOrders, fetchActive }
}
