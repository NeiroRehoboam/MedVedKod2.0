import { useAppTheme } from "@/components/providers/AppThemeProvider"
import { Segmented } from "@maxhub/max-ui"

export function ProfileTheme() {
  const { colorScheme, toggleColorScheme } = useAppTheme()

  const items = [
    { id: "light", title: "Светлая" },
    { id: "dark", title: "Тёмная" },
  ]

  return (
    <div className="flex flex-col gap-4">
      <div className="space-y-1">
        <p className="text-base font-medium text-max-text-primary">
          Тема оформления
        </p>
        <p className="text-sm text-max-text-secondary">
          Выберите удобный внешний вид приложения.
        </p>
      </div>

      <Segmented
        activeItem={colorScheme}
        items={items}
        onClick={(id) => {
          if (id !== colorScheme) {
            toggleColorScheme()
          }
        }}
      />
    </div>
  )
}