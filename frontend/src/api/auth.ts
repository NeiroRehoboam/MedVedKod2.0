import { mockUser } from "@/data/user.mock"
import type { User } from "@/types/user.types"

const USE_MOCK = import.meta.env.VITE_MOCK_AUTH === "true"

const API_URL = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "")

const MOCK_SESSION_KEY = "medved:mock-auth"

export async function loginWithMax(token: string): Promise<void> {
  if (USE_MOCK) {
    if (!token.trim()) {
      throw new Error("Токен отсутствует")
    }

    sessionStorage.setItem(MOCK_SESSION_KEY, "true")
    return
  }

  const response = await fetch(`${API_URL}/api/auth/max-login/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ token }),
  })

  if (!response.ok) {
    throw new Error("Не удалось авторизоваться")
  }
}

export async function getCurrentUser(): Promise<User | null> {
  if (USE_MOCK) {
    const authenticated = sessionStorage.getItem(MOCK_SESSION_KEY) === "true"

    return authenticated ? mockUser : null
  }

  const response = await fetch(`${API_URL}/api/auth/me`, {
    credentials: "include",
  })

  if (response.status === 401) {
    return null
  }

  if (!response.ok) {
    throw new Error("Не удалось получить пользователя")
  }

  return response.json() as Promise<User>
}
