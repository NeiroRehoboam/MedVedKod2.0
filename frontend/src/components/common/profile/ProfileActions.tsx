import { Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

export function ProfileActions() {
  return (
    <div className="space-y-2 pt-2">
      <Button type="submit" className="h-14 w-full">
        Сохранить изменения
      </Button>

      <AlertDialog>
        <AlertDialogTrigger
          className="w-full"
          render={
            <Button
              type="button"
              variant="destructive"
              className="h-14 w-full"
            />
          }
        >
          <Trash2 className="size-4" />
          Удалить аккаунт
        </AlertDialogTrigger>

        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Удалить аккаунт?</AlertDialogTitle>
            <AlertDialogDescription>
              История обращений и данные анамнеза будут удалены без возможности
              восстановления.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Отмена</AlertDialogCancel>
            <AlertDialogAction variant={"destructive"} onClick={() => {}}>
              Удалить
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
