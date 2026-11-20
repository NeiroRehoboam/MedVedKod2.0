import {
  createContext,
  useContext,
  useState,
  type ReactNode,
} from "react"
import { MaxUI } from "@maxhub/max-ui"

type ColorScheme = "light" | "dark"

type ThemeContextValue = {
  colorScheme: ColorScheme
  toggleColorScheme: () => void
}

const ThemeContext = createContext<ThemeContextValue | null>(null)

export function AppThemeProvider({
  children,
}: {
  children: ReactNode
}) {
  const [colorScheme, setColorScheme] = useState<ColorScheme>(() => {
    const saved = localStorage.getItem("color-scheme")

    return saved === "dark" ? "dark" : "light"
  })

  const toggleColorScheme = () => {
    setColorScheme((current) => {
      const next = current === "light" ? "dark" : "light"

      localStorage.setItem("color-scheme", next)

      return next
    })
  }

  return (
    <ThemeContext.Provider
      value={{ colorScheme, toggleColorScheme }}
    >
      <MaxUI colorScheme={colorScheme}>
        {children}
      </MaxUI>
    </ThemeContext.Provider>
  )
}

export function useAppTheme() {
  const context = useContext(ThemeContext)

  if (!context) {
    throw new Error("useAppTheme must be used within AppThemeProvider")
  }

  return context
}