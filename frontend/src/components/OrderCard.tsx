import type { Order } from '../types'
import StatusBadge from './StatusBadge'

interface Props {
  order: Order
}

export default function OrderCard({ order }: Props) {
  return (
    <div className="card">
      <div className="flex justify-between items-start mb-2">
        <span className="font-bold text-lg">#{order.id}</span>
        <StatusBadge status={order.status} />
      </div>

      <div className="space-y-1 text-sm text-gray-600">
        <div className="flex justify-between">
          <span>ЖВ: <strong>{order.jv_qty}</strong></span>
          <span>ЛВ: <strong>{order.lv_qty}</strong></span>
          <span>Всего: <strong>{order.total_qty}</strong></span>
        </div>

        {order.delivery_date && (
          <div>
            Дата доставки: <strong>{order.delivery_date}</strong>
          </div>
        )}

        {order.comment && (
          <div className="text-gray-500 italic">{order.comment}</div>
        )}

        <div className="text-xs text-gray-400 pt-1">
          {new Date(order.created_at).toLocaleString('ru-RU')}
        </div>
      </div>
    </div>
  )
}
