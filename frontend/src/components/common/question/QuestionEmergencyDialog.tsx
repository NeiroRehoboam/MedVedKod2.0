import { ArrowUpRight } from "lucide-react"

import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Button } from "@/components/ui/button"

type QuestionEmergencyDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  onContinue: () => void
}

export function QuestionEmergencyDialog({
  open,
  onOpenChange,
  onContinue,
}: QuestionEmergencyDialogProps) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent className="gap-0 overflow-hidden bg-background">
        <div>
          <AlertDialogHeader className="gap-3 text-left">
            <AlertDialogTitle className="w-full font-unbounded text-2xl font-medium tracking-tighter">
              Возможно, нужна
              <br />
              срочная помощь
            </AlertDialogTitle>

            <AlertDialogDescription>
              Вы упомянули боль. При некоторых симптомах важно не откладывать
              обращение за помощью.
            </AlertDialogDescription>
          </AlertDialogHeader>

          {/* Крупный номер */}
          <div className="relative mt-8 overflow-hidden rounded-[22px] border border-red-100 bg-red-50 px-5 pt-5 pb-4">
            <div className="flex items-start justify-between">
              <span className="text-xs font-medium text-red-800">
                Единый номер экстренных служб
              </span>
            </div>

            <div className="mt-3 font-unbounded text-7xl leading-none font-medium tracking-[-0.09em] text-red-800">
              112
            </div>
            <p className="mt-3 text-xs leading-5 text-red-900/75">
              При сильной боли в груди, затруднённом дыхании или потере сознания
              немедленно вызывайте помощь.
            </p>
            <a
              href="tel:112"
              className="mt-5 flex h-12 w-full items-center justify-between rounded-full bg-red-800 px-5 text-sm font-semibold text-white transition-colors hover:bg-red-900"
            >
              Позвонить
              <ArrowUpRight className="size-5" />
            </a>
          </div>

          {/* Вторичные действия */}
          <div className="pt-5">
            <Button
              type="button"
              variant="secondary"
              onClick={onContinue}
              className="h-12 w-full"
            >
              Продолжить опрос
              <ArrowUpRight className="size-4" />
            </Button>
          </div>
        </div>
      </AlertDialogContent>
    </AlertDialog>
  )
}
