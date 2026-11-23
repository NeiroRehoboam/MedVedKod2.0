const API_URL = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "")

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)

    this.name = "ApiError"
    this.status = status
  }
}
function getCsrfToken() {
  const cookie = document.cookie
    .split("; ")
    .find((item) => item.startsWith("csrftoken="))

  return cookie
    ? decodeURIComponent(cookie.slice("csrftoken=".length))
    : undefined
}

export async function customFetch<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const method = (options.method ?? "GET").toUpperCase()
  const headers = new Headers(options.headers)

  if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
    const csrfToken = getCsrfToken()

    if (csrfToken) {
      headers.set("X-CSRFToken", csrfToken)
    }
  }

  const response = await fetch(`${API_URL}${url}`, {
    ...options,
    headers,
    credentials: "include",
  })

  if (!response.ok) {
    throw new ApiError(response.status, `Ошибка API: ${response.status}`)
  }

  const data = response.status === 204 ? undefined : await response.json()

  return {
    data,
    status: response.status,
    headers: response.headers,
  } as T
}
