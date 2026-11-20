import { BottomSheet, Button } from "@maxhub/max-ui"
import { PageDescription, PageTitle } from "../../typography"

type QuestionExitSheetProps = {
  open: boolean
  onClose: () => void
  onSave: () => Promise<void>
  onDiscard: () => void
  isSaving?: boolean
  error?: string | null
}

export function QuestionExitSheet({
  open,
  onClose,
  onSave,
  onDiscard,
  isSaving = false,
  error,
}: QuestionExitSheetProps) {
  return (
    <BottomSheet
      open={open}
      onClose={() => {
        if (!isSaving) onClose()
      }}
      enableDrag={!isSaving}
    >
      <div className="mx-auto flex w-full max-w-lg flex-col gap-5">
        <div className="flex shrink-0 flex-col gap-3 pt-2">
          <PageTitle as="h4">Завершить диалог?</PageTitle>
          <PageDescription>
            Вы можете сохранить свои ответы и продолжить диалог позже или выйти
            без сохранения.
          </PageDescription>
        </div>
        <div className="mt-3 flex w-full flex-col gap-2">
          <Button
            size="medium"
            variant="primary"
            stretched
            disabled={isSaving}
            onClick={() => void onSave()}
          >
            {isSaving ? "Сохраняем..." : "Сохранить и выйти"}
          </Button>

          <Button
            size="medium"
            variant="secondary"
            stretched
            disabled={isSaving}
            onClick={onDiscard}
          >
            Выйти без сохранения
          </Button>
        </div>
        {error && (
          <p role="alert" className="mt-4 text-sm text-red-500">
            {error}
          </p>
        )}
      </div>
    </BottomSheet>
  )
}
