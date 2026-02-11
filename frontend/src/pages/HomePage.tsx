import { Link } from 'react-router-dom'
import { useTelegram } from '../hooks/useTelegram'

const menuItems = [
  { path: '/new-order', icon: '📝', label: 'Новый заказ', desc: 'Оформить доставку воды' },
  { path: '/status', icon: '📊', label: 'Статус заказа', desc: 'Текущий активный заказ' },
  { path: '/orders', icon: '📋', label: 'История', desc: 'Все ваши заказы' },
  { path: '/addresses', icon: '📍', label: 'Мои адреса', desc: 'Управление адресами' },
]

export default function HomePage() {
  const { fullName } = useTelegram()

  return (
    <div>
      <div className="text-center mb-6">
        <div className="text-4xl mb-2">💧</div>
        <h2 className="text-xl font-bold">
          {fullName ? `Привет, ${fullName}!` : 'Добро пожаловать!'}
        </h2>
        <p className="text-gray-500 text-sm mt-1">Служба доставки питьевой воды</p>
      </div>

      <div className="space-y-3">
        {menuItems.map((item) => (
          <Link key={item.path} to={item.path} className="card block hover:shadow-md transition-shadow">
            <div className="flex items-center gap-4">
              <span className="text-3xl">{item.icon}</span>
              <div>
                <div className="font-semibold">{item.label}</div>
                <div className="text-sm text-gray-500">{item.desc}</div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
