import { Button } from "@maxhub/max-ui"

import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

type QuestionDeleteDialogProps = {
  open: boolean
  onClose: () => void
  onConfirm: () => void
  isPending: boolean
  isError: boolean
}

export function QuestionDeleteDialog({
  open,
  onClose,
  onConfirm,
  isPending,
  isError,
}: QuestionDeleteDialogProps) {
  return (
    <AlertDialog
      open={open}
      onOpenChange={(nextOpen) => {
        if (!nextOpen && !isPending) onClose()
      }}
    >
      <AlertDialogContent
        className="max-h-[90dvh] w-[calc(100%-2rem)] max-w-md gap-6 overflow-y-auto rounded-3xl border-0 bg-max-surface p-6"
        aria-busy={isPending}
      >
        <AlertDialogHeader className="gap-3">
          <AlertDialogTitle className="text-xl font-semibold tracking-tight text-max-text-primary">
            Удалить обращение?
          </AlertDialogTitle>
          <AlertDialogDescription>
            Обращение, все ответы и результат будут удалены из истории.
            Восстановить их не получится.
          </AlertDialogDescription>
        </AlertDialogHeader>

        {isError && (
          <p role="alert" className="text-sm text-max-text-primary">
            Не удалось удалить обращение. Попробуйте ещё раз.
          </p>
        )}

        <div className="flex w-full flex-col gap-2">
          <Button
            type="button"
            size="medium"
            variant="primary"
            stretched
            disabled={isPending}
            onClick={onConfirm}
          >
            {isPending ? "Удаляем…" : "Удалить"}
          </Button>
          <Button
            type="button"
            size="medium"
            variant="secondary"
            stretched
            disabled={isPending}
            onClick={onClose}
          >
            Отмена
          </Button>
        </div>
      </AlertDialogContent>
    </AlertDialog>
  )
}
