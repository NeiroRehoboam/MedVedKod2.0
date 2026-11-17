import { ArrowRight, House, ShieldCheck } from "lucide-react"
import { Button, Typography } from "@maxhub/max-ui"
import { DoctorSignature, PageDescription, PageTitle } from "../../typography"

type QuestionWelcomeProps = {
  onStart: () => void
  onHome: () => void
}

export function QuestionWelcome({ onStart, onHome }: QuestionWelcomeProps) {
  return (
    <div className="relative flex min-h-dvh flex-col">
      <div className="relative mx-auto flex min-h-dvh w-full max-w-3xl flex-col px-6 pt-8 pb-[max(24px,env(safe-area-inset-bottom))] sm:px-10 sm:pt-12">
        {/* Основной контент */}
        <div className="flex flex-1 flex-col justify-center">
          <div className="relative w-fit">
            <PageTitle>
              Давайте
              <br />
              начнём
            </PageTitle>

            <DoctorSignature className="absolute -right-20 -bottom-6 ml-20 -rotate-5 text-3xl">
              Я рядом, МедВедь
            </DoctorSignature>
          </div>

          <div className="mt-12">
            <PageDescription>
              Расскажите, что вас беспокоит. Мы зададим несколько вопросов,
              чтобы лучше понять ситуацию.
            </PageDescription>
          </div>
        </div>

        {/* Дисклеймер */}
        <div className="space-y-5">
          <div className="relative rounded-max-medium bg-max-primary p-6 shadow-sm sm:p-8">
            <div className="mb-3 flex items-center gap-3 text-max-text-themed!">
              <ShieldCheck className="size-5" strokeWidth={1.8} />

              <Typography.Text
                variant="body"
                color="primary"
                className="text-max-text-themed!"
              >
                Важно знать
              </Typography.Text>
            </div>

            <PageDescription color="primary" className="text-sm!">
              МедВедь помогает собрать информацию о вашем самочувствии, но не
              ставит диагноз, не назначает лечение и не заменяет консультацию
              врача.
            </PageDescription>
            <div className="pt-2">
              <PageDescription color="secondary" variant="description">
                При угрозе жизни или резком ухудшении состояния обратитесь за
                экстренной медицинской помощью.
              </PageDescription>
            </div>
          </div>

          {/* Навигация */}
          <div className="flex gap-2">
            <Button
              className="max-button-align"
              onClick={onHome}
              variant="secondary"
              iconBefore={<House className="size-4" />}
            >
              Домой
            </Button>
            <Button
              onClick={onStart}
              className="max-button-between w-full flex-1"
              iconAfter={<ArrowRight className="size-5" />}
            >
              Начать
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
