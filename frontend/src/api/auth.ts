import {
  authDemoCreate,
  authMaxLoginCreate,
  authMeRetrieve,
} from "@/api/generated/auth/auth"

export const USE_MOCK_AUTH = import.meta.env.VITE_MOCK_AUTH === "true"

export async function loginWithDemo() {
  return authDemoCreate()
}

export async function loginWithMax(token: string) {
  if (!token.trim()) {
    throw new Error("Токен MAX отсутствует")
  }

  return authMaxLoginCreate({ token })
}

export async function getCurrentUser() {
  try {
    const response = await authMeRetrieve()
    return response.data
  } catch (error) {
    if (
      error instanceof Error &&
      "status" in error &&
      (error.status === 401 || error.status === 403)
    ) {
      return null
    }

    throw error
  }
}
