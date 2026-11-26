
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
  onExit: () => void
  onDelete?: () => void
  deleteDisabled?: boolean
}

export function QuestionExitSheet({
  open,
  onClose,
  onExit,
  onDelete,
  deleteDisabled,
}: QuestionExitSheetProps) {
  return (
    <AlertDialog open={open} onOpenChange={(nextOpen) => {
      if (!nextOpen) onClose()
    }}>
      <AlertDialogContent className="max-h-[90dvh] w-[calc(100%-2rem)] max-w-md gap-6 overflow-y-auto rounded-3xl border-0 bg-max-surface p-6">
        <AlertDialogHeader className="gap-3">
          <AlertDialogTitle className="text-xl font-semibold tracking-tight text-max-text-primary">
            Выйти из диалога?
          </AlertDialogTitle>

          <AlertDialogDescription>
            Ваше обращение останется в истории. Вы сможете вернуться к
            нему позже.
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="flex w-full flex-col gap-2">
          <Button
            type="button"
            size="medium"
            variant="primary"
            stretched
            onClick={onExit}
          >
            Выйти
          </Button>

          <Button
            type="button"
            size="medium"
            variant="secondary"
            stretched
            onClick={onClose}
          >
            Продолжить диалог
          </Button>
          {onDelete && (
            <Button
              type="button"
              size="medium"
              variant="secondary"
              stretched
              disabled={deleteDisabled}
              onClick={() => {
                onClose()
                onDelete()
              }}
            >
              Удалить обращение
            </Button>
          )}
        </div>
      </AlertDialogContent>
    </AlertDialog>
  )
}
