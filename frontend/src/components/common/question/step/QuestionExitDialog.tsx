import { Button } from "@maxhub/max-ui"

import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

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
  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen && !isSaving) {
      onClose()
    }
  }

  return (
    <AlertDialog open={open} onOpenChange={handleOpenChange}>
      <AlertDialogContent className="max-h-[90dvh] w-[calc(100%-2rem)] max-w-md gap-6 overflow-y-auto rounded-3xl border-0 bg-max-surface p-6">
        <AlertDialogHeader className="gap-3">
          <AlertDialogTitle className="text-xl font-semibold tracking-tight text-max-text-primary">
            Завершить диалог?
          </AlertDialogTitle>

          <AlertDialogDescription>
            Вы можете сохранить свои ответы и продолжить диалог позже или выйти
            без сохранения.
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="flex w-full flex-col gap-2">
          <Button
            type="button"
            size="medium"
            variant="primary"
            stretched
            disabled={isSaving}
            onClick={() => void onSave()}
          >
            {isSaving ? "Сохраняем..." : "Сохранить и выйти"}
          </Button>

          <Button
            type="button"
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
          <p role="alert" className="text-sm text-red-500">
            {error}
          </p>
        )}
      </AlertDialogContent>
    </AlertDialog>
  )
}
