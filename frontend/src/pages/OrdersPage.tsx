import { useTelegram } from '../hooks/useTelegram'
import { useOrders } from '../hooks/useOrders'
import OrderCard from '../components/OrderCard'

export default function OrdersPage() {
  const { telegramId } = useTelegram()
  const { orders, total, loading } = useOrders(telegramId)

  if (loading) {
    return <div className="text-center py-8 text-gray-500">Загрузка...</div>
  }

  if (!orders.length) {
    return (
      <div className="text-center py-8">
        <div className="text-4xl mb-2">📋</div>
        <p className="text-gray-500">У вас пока нет заказов</p>
      </div>
    )
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">
        История заказов <span className="text-sm font-normal text-gray-500">({total})</span>
      </h2>
      <div className="space-y-3">
        {orders.map((order) => (
          <OrderCard key={order.id} order={order} />
        ))}
      </div>
    </div>
  )
}
