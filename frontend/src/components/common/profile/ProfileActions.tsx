import { Button } from "@maxhub/max-ui"

export function ProfileActions() {
  return (
    <div className="flex flex-col gap-2 pt-2">
      <Button type="submit" size="large" variant="primary" stretched>
        Сохранить изменения
      </Button>
    </div>
  )
}
