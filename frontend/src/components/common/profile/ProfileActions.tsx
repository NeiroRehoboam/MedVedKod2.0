import { useState } from "react"
import { Trash2 } from "lucide-react"
import { BottomSheet, Button, Typography } from "@maxhub/max-ui"

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

      <BottomSheet
        open={open}
        onClose={() => setOpen(false)}
        title="Удалить аккаунт?"
      >
        <div className="flex flex-col gap-5">
          <Typography.Text variant="body" color="secondary">
            История обращений и данные анамнеза будут удалены без возможности
            восстановления.
          </Typography.Text>

          <div className="flex flex-col gap-2">
            <Button
              type="button"
              size="large"
              variant="secondary"
              stretched
              onClick={() => setOpen(false)}
            >
              Отмена
            </Button>

            <Button
              type="button"
              size="large"
              variant="destructive"
              stretched
              onClick={handleDelete}
            >
              Удалить аккаунт
            </Button>
          </div>
        </div>
      </BottomSheet>
    </div>
  )
}
