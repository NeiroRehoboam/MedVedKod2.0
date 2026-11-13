import { Button } from "@/components/ui/button"
import { ArrowRight } from "lucide-react"
import { useNavigate } from "react-router-dom"
import shapeImage from "@/assets/shapes/shape-1.svg"

export function InitialPage() {
  const navigate = useNavigate()

  return (
    <main className="relative isolate flex min-h-dvh flex-col overflow-hidden bg-muted">
      {/* Декоративная фигура */}
      <img
        src={shapeImage}
        alt=""
        aria-hidden="true"
        className="pointer-events-none absolute top-[12%] -right-32 -z-10 w-105 max-w-none rotate-[-18deg] opacity-15 brightness-0 hue-rotate-170 invert-70"
      />
      <div className="relative mx-auto flex w-full max-w-xl flex-1 flex-col px-6 pt-8 pb-[max(32px,env(safe-area-inset-bottom))] sm:px-10">
        <section
          className="flex flex-1 flex-col justify-center py-16"
          aria-labelledby="welcome-heading"
        >
          <div>
            <h1
              id="welcome-heading"
              className="font-unbounded text-5xl leading-[1.18] font-medium tracking-[-0.04em] sm:text-5xl"
            >
              Привет!
              <br />Я МедВед
            </h1>

            <p className="mt-2 ml-20 w-fit -rotate-4 font-doctor text-4xl leading-none text-primary sm:ml-32">
              С заботой о вас
            </p>

            <p className="mt-10 max-w-sm text-base leading-7 text-muted-foreground">
              Помогу разобраться с жалобами и подскажу, к какому специалисту
              обратиться.
            </p>
          </div>
        </section>

        <footer className="space-y-5">
          <Button
            size="lg"
            className="h-14 w-full justify-between px-6 text-base font-medium"
            onClick={() => navigate("/home")}
          >
            Начать консультацию
            <ArrowRight className="size-5" />
          </Button>

          <p className="max-w-sm px-1 text-center text-xs leading-5 text-muted-foreground">
            МедВед не ставит диагноз и не заменяет консультацию врача.
          </p>
        </footer>
      </div>
    </main>
  )
}
