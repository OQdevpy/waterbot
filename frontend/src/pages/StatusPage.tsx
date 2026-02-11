import { useTelegram } from '../hooks/useTelegram'
import { useOrders } from '../hooks/useOrders'
import StatusBadge from '../components/StatusBadge'

export default function StatusPage() {
  const { telegramId } = useTelegram()
  const { activeOrder, loading } = useOrders(telegramId)

  if (loading) {
    return <div className="text-center py-8 text-gray-500">Загрузка...</div>
  }

  if (!activeOrder) {
    return (
      <div className="text-center py-8">
        <div className="text-4xl mb-2">📊</div>
        <p className="text-gray-500">Нет активного заказа</p>
      </div>
    )
  }

  const steps = [
    { key: 'new', label: 'Новый' },
    { key: 'confirmed', label: 'Подтверждён' },
    { key: 'in_delivery', label: 'В доставке' },
    { key: 'completed', label: 'Выполнен' },
  ]

  const statusOrder = ['new', 'confirmed', 'rescheduled', 'in_delivery', 'completed']
  const currentIdx = statusOrder.indexOf(activeOrder.status)

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Статус заказа</h2>

      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <span className="text-2xl font-bold">#{activeOrder.id}</span>
          <StatusBadge status={activeOrder.status} />
        </div>

        {/* Прогресс-бар */}
        <div className="flex items-center justify-between mb-6">
          {steps.map((s, i) => {
            const isActive = currentIdx >= statusOrder.indexOf(s.key)
            return (
              <div key={s.key} className="flex flex-col items-center flex-1">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                    isActive ? 'bg-primary text-white' : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {i + 1}
                </div>
                <span className={`text-xs mt-1 ${isActive ? 'text-primary font-medium' : 'text-gray-400'}`}>
                  {s.label}
                </span>
              </div>
            )
          })}
        </div>

        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">ЖВ:</span>
            <strong>{activeOrder.jv_qty}</strong>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">ЛВ:</span>
            <strong>{activeOrder.lv_qty}</strong>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Всего:</span>
            <strong>{activeOrder.total_qty}</strong>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Дата доставки:</span>
            <strong>{activeOrder.delivery_date || '—'}</strong>
          </div>
          {activeOrder.comment && (
            <div className="pt-2 border-t">
              <span className="text-gray-500">Комментарий:</span>
              <p className="mt-1">{activeOrder.comment}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
