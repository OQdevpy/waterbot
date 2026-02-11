import { Outlet, Link, useLocation } from 'react-router-dom'

const navItems = [
  { path: '/', label: 'Главная', icon: '🏠' },
  { path: '/new-order', label: 'Заказ', icon: '📝' },
  { path: '/orders', label: 'История', icon: '📋' },
  { path: '/addresses', label: 'Адреса', icon: '📍' },
  { path: '/status', label: 'Статус', icon: '📊' },
]

export default function Layout() {
  const { pathname } = useLocation()

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-primary text-white px-4 py-3 shadow-md">
        <h1 className="text-lg font-bold text-center">Доставка воды</h1>
      </header>

      {/* Content */}
      <main className="flex-1 p-4 pb-20 max-w-lg mx-auto w-full">
        <Outlet />
      </main>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg">
        <div className="max-w-lg mx-auto flex justify-around">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center py-2 px-3 text-xs transition-colors ${
                pathname === item.path
                  ? 'text-primary font-semibold'
                  : 'text-gray-500'
              }`}
            >
              <span className="text-lg mb-0.5">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </div>
      </nav>
    </div>
  )
}
