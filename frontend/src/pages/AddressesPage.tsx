import { useState, useEffect } from 'react'
import { useTelegram } from '../hooks/useTelegram'
import { getAddresses, addAddress, deleteAddress } from '../api/client'
import AddressForm from '../components/AddressForm'
import type { Address } from '../types'

export default function AddressesPage() {
  const { telegramId } = useTelegram()
  const [addresses, setAddresses] = useState<Address[]>([])
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(false)

  const fetchAddresses = async () => {
    if (!telegramId) return
    try {
      const { data } = await getAddresses(telegramId)
      setAddresses(data)
    } catch {}
  }

  useEffect(() => {
    fetchAddresses()
  }, [telegramId])

  const handleAdd = async (data: { city: string; district: string; street: string; house: string }) => {
    if (!telegramId) return
    setLoading(true)
    try {
      await addAddress(telegramId, { ...data, is_default: addresses.length === 0 })
      setShowForm(false)
      fetchAddresses()
    } catch {}
    setLoading(false)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Удалить адрес?')) return
    try {
      await deleteAddress(id)
      fetchAddresses()
    } catch {}
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Мои адреса</h2>

      {addresses.length === 0 && !showForm && (
        <div className="text-center py-8">
          <div className="text-4xl mb-2">📍</div>
          <p className="text-gray-500">Нет сохранённых адресов</p>
        </div>
      )}

      {addresses.map((addr) => (
        <div key={addr.id} className="card">
          <div className="flex justify-between items-start">
            <div>
              <div className="font-medium">
                {addr.is_default && '⭐ '}{addr.city}, {addr.street}, {addr.house}
              </div>
              <div className="text-sm text-gray-500">{addr.district}</div>
            </div>
            <button
              onClick={() => handleDelete(addr.id)}
              className="text-red-400 hover:text-red-600 text-sm"
            >
              Удалить
            </button>
          </div>
        </div>
      ))}

      {showForm ? (
        <div className="card">
          <h3 className="font-semibold mb-3">Новый адрес</h3>
          <AddressForm onSubmit={handleAdd} loading={loading} />
          <button onClick={() => setShowForm(false)} className="btn-secondary mt-3">
            Отмена
          </button>
        </div>
      ) : (
        addresses.length < 10 && (
          <button onClick={() => setShowForm(true)} className="btn-primary mt-3">
            + Добавить адрес
          </button>
        )
      )}
    </div>
  )
}
