import { Outlet } from "react-router-dom"
import { BottomNavigation, Header } from "@/components/common"

export function MainLayout() {
  return (
    <div className="relative isolate flex min-h-dvh flex-col overflow-x-clip">
      <div className="mx-auto w-full max-w-3xl px-5 pt-5">
        <Header />
      </div>

      <main className="relative mx-auto w-full max-w-3xl flex-1 px-5 pt-3 pb-[calc(100px+env(safe-area-inset-bottom))]">
        <Outlet />
      </main>

      <BottomNavigation />
    </div>
  )
}
