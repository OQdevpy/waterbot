import type { OrderStatus } from '../types'

const statusConfig: Record<OrderStatus, { label: string; color: string }> = {
  draft: { label: 'Черновик', color: 'bg-gray-200 text-gray-700' },
  new: { label: 'Новый', color: 'bg-blue-100 text-blue-700' },
  confirmed: { label: 'Подтверждён', color: 'bg-green-100 text-green-700' },
  rescheduled: { label: 'Перенесён', color: 'bg-yellow-100 text-yellow-700' },
  in_delivery: { label: 'В доставке', color: 'bg-purple-100 text-purple-700' },
  completed: { label: 'Выполнен', color: 'bg-green-200 text-green-800' },
  cancelled: { label: 'Отменён', color: 'bg-red-100 text-red-700' },
  payment_pending: { label: 'Ожидание оплаты', color: 'bg-orange-100 text-orange-700' },
  paid: { label: 'Оплачен', color: 'bg-emerald-100 text-emerald-700' },
}

interface Props {
  status: OrderStatus
}

export default function StatusBadge({ status }: Props) {
  const config = statusConfig[status] || { label: status, color: 'bg-gray-200 text-gray-700' }

  return (
    <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${config.color}`}>
      {config.label}
    </span>
  )
}
