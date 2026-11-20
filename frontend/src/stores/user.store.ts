import type { User } from "@/types/user.types"
import { create } from "zustand"

type UserStore = {
  user: User | null
  setUser: (user: User) => void
  clearUser: () => void
}

export const useUserStore = create<UserStore>((set) => ({
  user: {
    id: "1",
    firstName: "Анна",
    lastName: "Иванова",
    middleName: "Сергеевна",
    birthDate: "1995-04-12",
    phone: "+79991234567",
  },

  setUser: (user) => set({ user }),

  clearUser: () => set({ user: null }),
}))
