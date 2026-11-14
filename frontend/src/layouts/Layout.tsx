import { Outlet } from "react-router-dom"
import { BottomNavigation, Header } from "@/components/common"

export function Layout() {
  return (
    <div className="relative isolate flex min-h-dvh flex-col overflow-x-clip bg-max-surface">
      <div className="mx-auto w-full max-w-3xl px-6 pt-7">
        <Header />
      </div>

      <main className="relative mx-auto w-full max-w-3xl flex-1 pb-[calc(100px+env(safe-area-inset-bottom))]">
        <Outlet />
      </main>

      <BottomNavigation />
    </div>
  )
}
