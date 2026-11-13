import { Outlet } from "react-router-dom"
import { BottomNavigation, Header } from "@/components/common"

export function Layout() {
  return (
    <div className="relative isolate min-h-dvh bg-muted">
      <div className="mx-auto w-full max-w-3xl px-6 pt-7">
        <Header />
      </div>

      <main className="relative min-h-dvh pb-25">
        <Outlet />
      </main>

      <BottomNavigation />
    </div>
  )
}
