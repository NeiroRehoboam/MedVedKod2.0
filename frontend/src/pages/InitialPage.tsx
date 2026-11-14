import { ArrowRight } from "lucide-react"
import { useNavigate } from "react-router-dom"
import shapeImage from "@/assets/shapes/shape-1.svg"
import { Button, Typography } from "@maxhub/max-ui"

export function InitialPage() {
  const navigate = useNavigate()

  return (
    <main className="relative isolate flex min-h-dvh flex-col overflow-hidden bg-max-surface">
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
            <Typography.Title
              variant="large-strong"
              className="font-unbounded! text-5xl!"
            >
              Привет!
              <br />Я МедВед
            </Typography.Title>

            <p className="mt-2 ml-20 w-fit -rotate-4 font-doctor text-4xl leading-none text-max-text-themed sm:ml-32">
              С заботой о вас
            </p>

            <div className="max-w-sm leading-7 mt-7">
              <Typography.Text variant="body" color="secondary">
                Помогу разобраться с жалобами и подскажу, к какому специалисту
                обратиться.
              </Typography.Text>
            </div>
          </div>
        </section>

        <footer className="space-y-4">
          <Button
            disabled={false}
            loading={false}
            size="large"
            variant="primary"
            iconAfter={<ArrowRight />}
            className="w-full"
            onClick={() => navigate("/home")}
          >
            Начать консультацию
          </Button>

          <div className="max-w-sm text-center leading-5">
            <Typography.Text variant="description" color="tertiary">
              МедВед не ставит диагноз и не заменяет консультацию врача.
            </Typography.Text>
          </div>
        </footer>
      </div>
    </main>
  )
}
