import { useState, useEffect } from 'react'
import { getDistricts } from '../api/client'
import type { District } from '../types'

interface Props {
  onSubmit: (data: {
    city: string
    district: string
    street: string
    house: string
  }) => void
  loading?: boolean
}

export default function AddressForm({ onSubmit, loading }: Props) {
  const [city, setCity] = useState('')
  const [district, setDistrict] = useState('')
  const [street, setStreet] = useState('')
  const [house, setHouse] = useState('')
  const [districts, setDistricts] = useState<District[]>([])

  useEffect(() => {
    getDistricts()
      .then(({ data }) => setDistricts(data))
      .catch(() => {})
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (city && district && street && house) {
      onSubmit({ city, district, street, house })
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <input
        type="text"
        placeholder="Город"
        value={city}
        onChange={(e) => setCity(e.target.value)}
        className="input-field"
        required
      />

      <select
        value={district}
        onChange={(e) => setDistrict(e.target.value)}
        className="input-field"
        required
      >
        <option value="">Выберите район</option>
        {districts.map((d) => (
          <option key={d.id} value={d.district}>
            {d.district}
          </option>
        ))}
      </select>

      <input
        type="text"
        placeholder="Улица"
        value={street}
        onChange={(e) => setStreet(e.target.value)}
        className="input-field"
        required
      />

      <input
        type="text"
        placeholder="Дом / квартира"
        value={house}
        onChange={(e) => setHouse(e.target.value)}
        className="input-field"
        required
      />

      <button type="submit" className="btn-primary" disabled={loading}>
        {loading ? 'Сохранение...' : 'Сохранить адрес'}
      </button>
    </form>
  )
}
