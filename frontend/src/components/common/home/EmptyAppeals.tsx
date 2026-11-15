import { Button } from "@maxhub/max-ui"
import { PageDescription, PageTitle } from "../typography"

type EmptyAppealsProps = {
  onNewAppeal: () => void
}

export function EmptyAppeals({ onNewAppeal }: EmptyAppealsProps) {
  return (
    <div className="flex flex-col items-center rounded-max-medium bg-max-secondary px-6 py-12 text-center">
      <PageTitle as="h3">Обращений пока нет</PageTitle>

      <div className="mt-3 max-w-xs leading-6">
        <PageDescription>
          Здесь будет храниться история ваших обращений. Расскажите, что вас
          беспокоит, чтобы начать первый диалог.
        </PageDescription>
      </div>

      <div className="mt-6">
        <Button
          type="button"
          variant="secondary"
          size="medium"
          onClick={onNewAppeal}
        >
          Создать обращение
        </Button>
      </div>
    </div>
  )
}
