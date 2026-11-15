import { ArrowRight } from "lucide-react"
import { useNavigate } from "react-router-dom"
import shapeImage from "@/assets/shapes/shape-1.svg"
import { Button } from "@maxhub/max-ui"
import {
  DoctorSignature,
  PageDescription,
  PageTitle,
} from "@/components/common"

export function InitialPage() {
  const navigate = useNavigate()

  return (
    <main className="relative isolate flex min-h-dvh flex-col overflow-hidden">
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
          <PageTitle className="text-5xl!">
            Привет!
            <br />Я МедВед
          </PageTitle>

          <DoctorSignature className="ml-20 -rotate-4 text-4xl">
            С заботой о вас
          </DoctorSignature>

          <div className="mt-7 max-w-sm leading-7">
            <PageDescription>
              Помогу разобраться с жалобами и подскажу, к какому специалисту
              обратиться.
            </PageDescription>
          </div>
        </section>

        <footer className="space-y-4">
          <Button
            disabled={false}
            loading={false}
            size="large"
            variant="primary"
            iconAfter={<ArrowRight />}
            className="max-button-between w-full"
            onClick={() => navigate("/home")}
          >
            Начать консультацию
          </Button>

          <div className="max-w-sm text-center leading-5">
            <PageDescription color="tertiary" variant="description">
              МедВед не ставит диагноз и не заменяет консультацию врача.
            </PageDescription>
          </div>
        </footer>
      </div>
    </main>
  )
}
