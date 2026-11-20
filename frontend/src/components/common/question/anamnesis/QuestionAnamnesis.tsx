import { useEffect } from "react"
import { QuestionActions } from "./QuestionActions"
import { PageDescription, PageTitle } from "../../typography"
import { AnamnesisForm } from "../../profile/AnamnesisForm"

type Props = {
  onContinue: () => void
  onBack: () => void
}

export function QuestionAnamnesis({ onContinue, onBack }: Props) {
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [])

  return (
    <section className="mt-10 sm:mt-14" aria-labelledby="anamnesis-heading">
      <div className="space-y-4">
        <PageTitle as="h3">Проверим анамнез</PageTitle>
        <PageDescription>
          Здесь данные из вашего профиля. Если всё верно, нажмите «Далее». Если
          что-то изменилось — поправьте или дополните.
        </PageDescription>

        <PageDescription variant="description">
          Все поля необязательны. Изменения сохранятся в профиле.
        </PageDescription>
      </div>

      <AnamnesisForm onSuccess={onContinue}>
        <QuestionActions onBack={onBack} />
      </AnamnesisForm>
    </section>
  )
}
