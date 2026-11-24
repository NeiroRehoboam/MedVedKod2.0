import { useEffect, useRef, useState } from "react"
import type { ReactNode } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Spinner } from "@maxhub/max-ui"

import { loginWithDemo, loginWithMax, USE_MOCK_AUTH } from "@/api/auth"

import { useCurrentUser } from "@/hooks/useCurrentUser"

type AuthGateProps = {
  children: ReactNode
}

export function AuthGate({ children }: AuthGateProps) {
  const queryClient = useQueryClient()
  const started = useRef(false)

  const [token] = useState(() =>
    new URLSearchParams(window.location.search).get("token")
  )

  const needsLogin = USE_MOCK_AUTH || Boolean(token)

  const auth = useMutation({
    mutationFn: async () => {
      if (USE_MOCK_AUTH) {
        await loginWithDemo()
        return
      }

      if (token) {
        await loginWithMax(token)
      }
    },

    onSuccess: async () => {
      // Обновляем информацию о пользователе
      queryClient.removeQueries({
        queryKey: ["currentUser"],
        exact: true,
      })

      // Удаляем JWT из адресной строки после успешного входа
      if (!USE_MOCK_AUTH && token) {
        const url = new URL(window.location.href)
        url.searchParams.delete("token")

        window.history.replaceState(
          window.history.state,
          "",
          url.pathname + url.search + url.hash
        )
      }
    },
  })

  const { mutate } = auth

  useEffect(() => {
    if (!needsLogin || started.current) return

    started.current = true
    mutate()
  }, [needsLogin, mutate])

  const userQuery = useCurrentUser(!needsLogin || auth.isSuccess)

  const isLoading =
    (needsLogin && !auth.isSuccess && !auth.isError) ||
    (userQuery.isPending && !userQuery.isError)

  if (isLoading) {
    return (
      <div className="flex min-h-dvh items-center justify-center">
        <Spinner className="size-8" />
      </div>
    )
  }

  if (auth.isError) {
    return (
      <div className="flex min-h-dvh items-center justify-center px-6 text-center">
        {USE_MOCK_AUTH
          ? "Не удалось войти в деморежим."
          : "Не удалось авторизоваться через MAX. Откройте приложение заново."}
      </div>
    )
  }

  if (userQuery.isError) {
    return <div>Ошибка загрузки пользователя</div>
  }

  if (userQuery.data) {
    return (
      <div className="p-5">
        <p>Mock: {String(USE_MOCK_AUTH)}</p>
        <p>Token: {String(Boolean(token))}</p>
        <p>Needs login: {String(needsLogin)}</p>
        <p>Auth success: {String(auth.isSuccess)}</p>
        <p>User success: {String(userQuery.isSuccess)}</p>
      </div>
    )
  }

  return <>{children}</>
}
