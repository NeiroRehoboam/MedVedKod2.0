import { useState } from "react"
import { Button } from "@maxhub/max-ui"

import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
} from "@/components/ui/alert-dialog"

export function ProfileActions() {
  const [open, setOpen] = useState(false)

  const handleDelete = () => {
    setOpen(false)
  }

  return (
    <div className="flex flex-col gap-2 pt-2">
      <Button type="submit" size="large" variant="primary" stretched>
        Сохранить изменения
      </Button>

      <Button
        type="button"
        size="large"
        variant="secondary"
        stretched
        onClick={() => setOpen(true)}
      >
        Удалить аккаунт
      </Button>

      <AlertDialog open={open} onOpenChange={setOpen}>
        <AlertDialogContent className="w-[calc(100%-2rem)] max-w-md gap-6 rounded-3xl border-border bg-max-surface p-6">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-xl font-semibold tracking-tight text-max-text-primary">
              Удалить аккаунт?
            </AlertDialogTitle>

            <AlertDialogDescription>
              История обращений и данные анамнеза будут удалены без возможности
              восстановления.
            </AlertDialogDescription>
          </AlertDialogHeader>

          <div className="flex flex-col gap-2">
            <Button
              type="button"
              size="large"
              variant="destructive"
              stretched
              onClick={handleDelete}
            >
              Удалить аккаунт
            </Button>

            <Button
              type="button"
              size="large"
              variant="secondary"
              stretched
              onClick={() => setOpen(false)}
            >
              Отмена
            </Button>
          </div>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
