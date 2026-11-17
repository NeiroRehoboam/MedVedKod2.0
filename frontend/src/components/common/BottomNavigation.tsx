import { House, UserRound, Plus } from "lucide-react"
import { Link, useLocation, useNavigate } from "react-router-dom"

const items = [
  {
    to: "/home",
    label: "Главная",
    icon: House,
    paths: ["/home", "/references"],
  },
  {
    to: "/profile",
    label: "Профиль",
    icon: UserRound,
    paths: ["/profile"],
  },
]

export function BottomNavigation() {
  const navigate = useNavigate()
  const { pathname } = useLocation()

  return (
    <div className="pointer-events-none fixed inset-x-0 bottom-[max(20px,env(safe-area-inset-bottom))] z-50 mx-auto max-w-3xl">
      <div className="mx-auto flex w-full items-center justify-between gap-3 px-4 sm:px-6">
        {/* Основная навигация */}
        <nav
          aria-label="Основная навигация"
          className="pointer-events-auto flex shrink-0 items-center gap-1 rounded-max-large bg-[#202124] p-1.5 shadow-lg"
        >
          {items.map(({ to, label, icon: Icon, paths }) => {
            const isActive = paths.some(
              (path) =>
                pathname === path || pathname.startsWith(`${path}/`),
            )

            return (
              <Link
                key={to}
                to={to}
                aria-label={label}
                aria-current={isActive ? "page" : undefined}
                className="relative flex size-12 items-center justify-center rounded-max-medium"
              >
                {isActive && (
                  <span
                    aria-hidden="true"
                    className="absolute inset-0 rounded-max-medium bg-white"
                  />
                )}

                <Icon
                  aria-hidden="true"
                  strokeWidth={1.8}
                  className={`relative z-10 size-5 transition-colors duration-200 ${
                    isActive ? "text-[#202124]" : "text-white/65"
                  }`}
                />
              </Link>
            )
          })}
        </nav>

        {/* Создание обращения */}
        <div className="pointer-events-auto shrink-0">
          <button
            type="button"
            aria-label="Создать обращение"
            onClick={() => navigate("/question")}
            className="flex size-14 items-center justify-center rounded-max-medium bg-[#202124] text-white shadow-lg transition-transform duration-200 active:scale-95"
          >
            <Plus
              className="size-5"
              strokeWidth={2.5}
              aria-hidden="true"
            />
          </button>
        </div>
      </div>
    </div>
  )
}