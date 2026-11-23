import { ArrowRight, House, ShieldCheck } from "lucide-react"
import { Button, Typography } from "@maxhub/max-ui"
import { DoctorSignature, PageDescription, PageTitle } from "../../typography"

type QuestionWelcomeProps = {
  onStart: () => void
  onHome: () => void
  isExistingSession?: boolean
}

export function QuestionWelcome({
  onStart,
  onHome,
  isExistingSession = false,
}: QuestionWelcomeProps) {
  return (
    <section className="flex min-h-0 w-full flex-1 flex-col">
      {/* Основной контент */}
      <div className="flex flex-1 flex-col justify-center">
        <div className="relative w-fit">
          <PageTitle>
            {isExistingSession ? (
              <>
                Продолжим
                <br />
                диалог
              </>
            ) : (
              <>
                Давайте
                <br />
                начнём
              </>
            )}
          </PageTitle>

          <DoctorSignature className="absolute -right-15 -bottom-6 ml-20 -rotate-5 text-3xl">
            Я рядом, МедВедь
          </DoctorSignature>
        </div>

        <div className="mt-12">
          <PageDescription>
            {isExistingSession
              ? "Вы вернулись к своему обращению. Продолжим с того места, где остановились."
              : "Расскажите, что вас беспокоит. Мы зададим несколько вопросов, чтобы лучше понять ситуацию."}
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
            {isExistingSession ? "Продолжить" : "Начать"}
          </Button>
        </div>
      </div>
    </section>
  )
}
