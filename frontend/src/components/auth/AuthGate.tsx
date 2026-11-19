import { useEffect, useRef, useState } from "react"
import type { ReactNode } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { loginWithMax } from "@/api/auth"
import { useCurrentUser } from "@/hooks/useCurrentUser"
import { Spinner } from "@maxhub/max-ui"

type AuthGateProps = {
  children: ReactNode
}

export function AuthGate({ children }: AuthGateProps) {
  const queryClient = useQueryClient()
  const started = useRef(false)

  const [token] = useState(() =>
    new URLSearchParams(window.location.search).get("token")
  )

  const auth = useMutation({
    mutationFn: loginWithMax,

    onSuccess: () => {
      queryClient.removeQueries({
        queryKey: ["currentUser"],
        exact: true,
      })

      const url = new URL(window.location.href)
      url.searchParams.delete("token")

      window.history.replaceState(
        window.history.state,
        "",
        url.pathname + url.search + url.hash
      )
    },
  })

  useEffect(() => {
    if (!token || started.current) return

    started.current = true
    auth.mutate(token)
  }, [token, auth.mutate])

  const userQuery = useCurrentUser(!token || auth.isSuccess)

  if (token && !auth.isSuccess && auth.isError) {
    return (
      <div>
        Не удалось авторизоваться. Откройте приложение заново через MAX.
      </div>
    )
  }

  if ((token && !auth.isSuccess) || userQuery.isPending) {
    return (
      <div className="flex min-h-dvh items-center justify-center">
        <Spinner className="size-8" />
      </div>
    )
  }
  if (userQuery.isError) {
    return <div>Ошибка загрузки пользователя</div>
  }

  if (!userQuery.data) {
    return <div>Откройте сервис из бота</div>
  }

  return <>{children}</>
}
