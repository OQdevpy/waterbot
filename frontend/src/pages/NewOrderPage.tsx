import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTelegram } from '../hooks/useTelegram'
import { getAddresses, getDistricts, addAddress, createOrder } from '../api/client'
import type { Address, District } from '../types'

export default function NewOrderPage() {
  const { telegramId } = useTelegram()
  const navigate = useNavigate()

  const [step, setStep] = useState<'address' | 'qty' | 'confirm'>('address')
  const [addresses, setAddresses] = useState<Address[]>([])
  const [districts, setDistricts] = useState<District[]>([])
  const [selectedAddress, setSelectedAddress] = useState<number | null>(null)
  const [showNewAddress, setShowNewAddress] = useState(false)

  // Новый адрес
  const [city, setCity] = useState('')
  const [district, setDistrict] = useState('')
  const [street, setStreet] = useState('')
  const [house, setHouse] = useState('')

  // Количество
  const [jvQty, setJvQty] = useState(0)
  const [lvQty, setLvQty] = useState(0)
  const [comment, setComment] = useState('')

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!telegramId) return
    getAddresses(telegramId).then(({ data }) => setAddresses(data)).catch(() => {})
    getDistricts().then(({ data }) => setDistricts(data)).catch(() => {})
  }, [telegramId])

  const handleAddAddress = async () => {
    if (!telegramId || !city || !district || !street || !house) return
    setLoading(true)
    try {
      const { data } = await addAddress(telegramId, {
        city, district, street, house, is_default: addresses.length === 0,
      })
      setAddresses([...addresses, data])
      setSelectedAddress(data.id)
      setShowNewAddress(false)
      setStep('qty')
    } catch {
      setError('Ошибка добавления адреса')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (!telegramId || !selectedAddress) return
    if (jvQty + lvQty < 1) {
      setError('Укажите хотя бы 1 бутыль')
      return
    }

    setLoading(true)
    setError('')
    try {
      const { data } = await createOrder(telegramId, {
        address_id: selectedAddress,
        jv_qty: jvQty,
        lv_qty: lvQty,
        comment: comment || undefined,
      })
      navigate('/status')
      alert(`Заказ №${data.id} принят! Дата: ${data.delivery_date}`)
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Ошибка создания заказа')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Новый заказ</h2>

      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded-xl mb-4 text-sm">{error}</div>
      )}

      {/* Шаг 1: Адрес */}
      {step === 'address' && (
        <div>
          <h3 className="font-semibold mb-3">Выберите адрес доставки:</h3>

          {addresses.map((addr) => (
            <button
              key={addr.id}
              onClick={() => { setSelectedAddress(addr.id); setStep('qty') }}
              className={`card w-full text-left ${selectedAddress === addr.id ? 'ring-2 ring-primary' : ''}`}
            >
              <div className="font-medium">
                {addr.is_default && '⭐ '}{addr.city}, {addr.street}, {addr.house}
              </div>
              <div className="text-sm text-gray-500">{addr.district}</div>
            </button>
          ))}

          {!showNewAddress ? (
            <button onClick={() => setShowNewAddress(true)} className="btn-secondary mt-3">
              + Новый адрес
            </button>
          ) : (
            <div className="card mt-3 space-y-3">
              <input placeholder="Город" value={city} onChange={(e) => setCity(e.target.value)} className="input-field" />
              <select value={district} onChange={(e) => setDistrict(e.target.value)} className="input-field">
                <option value="">Район</option>
                {districts.map((d) => <option key={d.id} value={d.district}>{d.district}</option>)}
              </select>
              <input placeholder="Улица" value={street} onChange={(e) => setStreet(e.target.value)} className="input-field" />
              <input placeholder="Дом / кв." value={house} onChange={(e) => setHouse(e.target.value)} className="input-field" />
              <button onClick={handleAddAddress} className="btn-primary" disabled={loading}>
                {loading ? 'Сохранение...' : 'Сохранить и выбрать'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Шаг 2: Количество */}
      {step === 'qty' && (
        <div className="space-y-4">
          <h3 className="font-semibold">Укажите количество:</h3>

          <div className="card">
            <label className="block text-sm font-medium mb-2">ЖВ (Живая вода, 19л)</label>
            <div className="flex items-center gap-4">
              <button onClick={() => setJvQty(Math.max(0, jvQty - 1))} className="btn-secondary w-12 h-12 !p-0 text-xl">-</button>
              <span className="text-2xl font-bold w-12 text-center">{jvQty}</span>
              <button onClick={() => setJvQty(jvQty + 1)} className="btn-secondary w-12 h-12 !p-0 text-xl">+</button>
            </div>
          </div>

          <div className="card">
            <label className="block text-sm font-medium mb-2">ЛВ (Лечебная вода, 19л)</label>
            <div className="flex items-center gap-4">
              <button onClick={() => setLvQty(Math.max(0, lvQty - 1))} className="btn-secondary w-12 h-12 !p-0 text-xl">-</button>
              <span className="text-2xl font-bold w-12 text-center">{lvQty}</span>
              <button onClick={() => setLvQty(lvQty + 1)} className="btn-secondary w-12 h-12 !p-0 text-xl">+</button>
            </div>
          </div>

          <textarea
            placeholder="Комментарий (необязательно)"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            className="input-field"
            rows={2}
          />

          <div className="flex gap-3">
            <button onClick={() => setStep('address')} className="btn-secondary flex-1">Назад</button>
            <button onClick={() => setStep('confirm')} className="btn-primary flex-1"
              disabled={jvQty + lvQty < 1}>
              Далее
            </button>
          </div>
        </div>
      )}

      {/* Шаг 3: Подтверждение */}
      {step === 'confirm' && (
        <div className="space-y-4">
          <h3 className="font-semibold">Подтвердите заказ:</h3>

          <div className="card">
            <div className="space-y-2 text-sm">
              <div>ЖВ: <strong>{jvQty}</strong></div>
              <div>ЛВ: <strong>{lvQty}</strong></div>
              <div>Всего: <strong>{jvQty + lvQty}</strong></div>
              {comment && <div>Комментарий: {comment}</div>}
            </div>
          </div>

          <div className="flex gap-3">
            <button onClick={() => setStep('qty')} className="btn-secondary flex-1">Назад</button>
            <button onClick={handleSubmit} className="btn-primary flex-1" disabled={loading}>
              {loading ? 'Отправка...' : 'Подтвердить'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
