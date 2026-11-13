import { ArrowRight, House, ShieldCheck } from "lucide-react"
import { Button } from "@/components/ui/button"

type QuestionWelcomeProps = {
  onStart: () => void
  onHome: () => void
}

export function QuestionWelcome({ onStart, onHome }: QuestionWelcomeProps) {
  return (
    <div className="relative flex min-h-dvh flex-col bg-muted">
      <div className="relative mx-auto flex min-h-dvh w-full max-w-3xl flex-col px-6 pt-8 pb-[max(24px,env(safe-area-inset-bottom))] sm:px-10 sm:pt-12">
        {/* Основной контент */}
        <div className="flex flex-1 flex-col justify-center">
          <div>
            <div className="relative w-fit">
              <h1 className="font-unbounded text-4xl leading-[1.12] font-semibold tracking-[-0.055em] sm:text-5xl">
                Давайте
                <br />
                начнём
              </h1>

              {/* Рукописная подпись */}
              <span className="absolute -right-20 -bottom-6 -rotate-6 font-doctor text-2xl leading-none whitespace-nowrap text-sky-700">
                Я рядом, МедВед
              </span>
            </div>

            <p className="mt-12 max-w-lg leading-6 text-muted-foreground">
              Расскажите, что вас беспокоит. Мы зададим несколько вопросов,
              чтобы лучше понять ситуацию.
            </p>
          </div>
        </div>

        {/* Дисклеймер */}
        <div className="space-y-5">
          <div className="relative isolate rounded-3xl bg-background p-6 shadow-xl shadow-neutral-200/60 sm:p-8 border">
            <div className="mb-3 flex items-center gap-3 text-sky-700">
              <ShieldCheck className="size-5" strokeWidth={1.8} />
              <span className="text-sm font-semibold">Важно знать</span>
            </div>

            <p className="text-sm leading-6">
              МедВед помогает собрать информацию о вашем самочувствии, но не
              ставит диагноз, не назначает лечение и не заменяет консультацию
              врача.
            </p>

            <p className="mt-3 text-xs leading-5 text-muted-foreground">
              При угрозе жизни или резком ухудшении состояния обратитесь за
              экстренной медицинской помощью.
            </p>
          </div>

          {/* Навигация */}
          <div className="flex gap-2">
            <Button
              onClick={onHome}
              className="h-14 rounded-full px-6 bg-foreground hover:bg-foreground"
              variant="default"
            >
              <House className="size-4" />
              Домой
            </Button>

            <Button
              onClick={onStart}
              className="h-14 flex-1 justify-between rounded-full px-6"
            >
              Начать
              <ArrowRight className="size-5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
