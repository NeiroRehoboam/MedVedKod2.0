import { ArrowRight, House, ShieldCheck } from "lucide-react"
import { Button, Typography } from "@maxhub/max-ui"

type QuestionWelcomeProps = {
  onStart: () => void
  onHome: () => void
}

export function QuestionWelcome({ onStart, onHome }: QuestionWelcomeProps) {
  return (
    <div className="relative flex min-h-dvh flex-col bg-max-surface">
      <div className="relative mx-auto flex min-h-dvh w-full max-w-3xl flex-col px-6 pt-8 pb-[max(24px,env(safe-area-inset-bottom))] sm:px-10 sm:pt-12">
        {/* Основной контент */}
        <div className="flex flex-1 flex-col justify-center">
          <div>
            <div className="relative w-fit">
              <h1 className="font-unbounded text-4xl leading-[1.12] font-semibold tracking-[-0.055em]">
                <Typography.Title
                  variant="large-strong"
                  className="font-unbounded! text-4xl!"
                >
                  Давайте
                  <br />
                  начнём
                </Typography.Title>
              </h1>

              {/* Рукописная подпись */}
              <span className="absolute -right-20 -bottom-6 -rotate-5 font-doctor text-3xl leading-none whitespace-nowrap text-max-text-themed">
                Я рядом, МедВед
              </span>
            </div>

            <p className="mt-12 max-w-lg leading-6">
              <Typography.Text variant="body" color="secondary">
                Расскажите, что вас беспокоит. Мы зададим несколько вопросов,
                чтобы лучше понять ситуацию.
              </Typography.Text>
            </p>
          </div>
        </div>

        {/* Дисклеймер */}
        <div className="space-y-5">
          <div className="relative rounded-max-medium bg-max-primary p-6 shadow-xl shadow-neutral-200/60 sm:p-8">
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

            <Typography.Text
              variant="description"
              color="primary"
              className="text-sm!"
            >
              МедВед помогает собрать информацию о вашем самочувствии, но не
              ставит диагноз, не назначает лечение и не заменяет консультацию
              врача.
            </Typography.Text>

            <p className="mt-3 text-xs leading-5 text-muted-foreground">
              <Typography.Text variant="description" color="secondary">
                При угрозе жизни или резком ухудшении состояния обратитесь за
                экстренной медицинской помощью.
              </Typography.Text>
            </p>
          </div>

          {/* Навигация */}
          <div className="flex gap-2">
            <Button
              onClick={onHome}
              variant="secondary"
              iconBefore={<House className="size-4" />}
            >
              Домой
            </Button>

            <Button
              onClick={onStart}
              className="flex-1 justify-between rounded-full"
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
