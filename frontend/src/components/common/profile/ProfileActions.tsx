import { useState } from "react"
import { BottomSheet, Button, Typography } from "@maxhub/max-ui"
import { PageDescription, PageTitle } from "../typography"

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

      <BottomSheet open={open} onClose={() => setOpen(false)}>
        <div className="flex flex-col gap-6">
          <div className="flex flex-col gap-3 pt-2 text-center">
            <PageTitle as="h4">Удалить аккаунт?</PageTitle>
            <PageDescription>
              История обращений и данные анамнеза будут удалены без возможности
              восстановления.
            </PageDescription>
          </div>

          <div className="flex flex-col gap-2">
            <Button
              type="button"
              size="medium"
              variant="destructive"
              stretched
              onClick={handleDelete}
            >
              Удалить аккаунт
            </Button>
            <Button
              type="button"
              size="medium"
              variant="secondary"
              stretched
              onClick={() => setOpen(false)}
            >
              Отмена
            </Button>
          </div>
        </div>
      </BottomSheet>
    </div>
  )
}
