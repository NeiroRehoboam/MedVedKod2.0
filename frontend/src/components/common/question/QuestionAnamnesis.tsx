import { useEffect } from "react"
import { AnamnesisForm } from "@/components/common/profile/AnamnesisForm"
import { QuestionHeader } from "./QuestionHeader"

type Props = {
  onContinue: () => void
  onBack: () => void
  onHome: () => void
}

export function QuestionAnamnesis({ onContinue, onBack, onHome }: Props) {
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [])

  return (
    <main className="min-h-dvh bg-max-surface">
      <div className="mx-auto w-full max-w-3xl px-5 pt-6 pb-[max(32px,env(safe-area-inset-bottom))] sm:px-8 sm:pt-8">
        <QuestionHeader onHome={onHome} />
        <section className="mt-10 sm:mt-14" aria-labelledby="anamnesis-heading">
          <h1
            id="anamnesis-heading"
            className="font-unbounded text-2xl leading-snug font-medium tracking-[-0.04em] sm:text-3xl"
          >
            Проверим анамнез
          </h1>
          <p className="mt-4 max-w-lg leading-6 text-muted-foreground">
            Здесь данные из вашего профиля. Если всё верно, нажмите «Далее».
            Если что-то изменилось - поправьте или дополните.
          </p>
          <p className="mt-3 text-sm leading-6 text-muted-foreground">
            Все поля необязательны. Изменения сохранятся в профиле.
          </p>
          <AnamnesisForm onContinue={onContinue} onBack={onBack} />
        </section>
      </div>
    </main>
  )
}
