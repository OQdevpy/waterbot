import { useEffect, useMemo } from 'react'

interface TelegramWebApp {
  initData: string
  initDataUnsafe: {
    user?: {
      id: number
      first_name: string
      last_name?: string
      username?: string
    }
  }
  ready: () => void
  close: () => void
  expand: () => void
  MainButton: {
    text: string
    show: () => void
    hide: () => void
    onClick: (cb: () => void) => void
    offClick: (cb: () => void) => void
    setParams: (params: { text?: string; color?: string }) => void
  }
  themeParams: {
    bg_color?: string
    text_color?: string
    button_color?: string
    button_text_color?: string
  }
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp
    }
  }
}

export function useTelegram() {
  const tg = useMemo(() => window.Telegram?.WebApp, [])

  useEffect(() => {
    tg?.ready()
    tg?.expand()
  }, [tg])

  const user = tg?.initDataUnsafe?.user

  return {
    tg,
    user,
    telegramId: user?.id ?? null,
    username: user?.username ?? null,
    fullName: user
      ? `${user.first_name}${user.last_name ? ' ' + user.last_name : ''}`
      : null,
  }
}
