import { ArrowUpRight } from "lucide-react"
import { Button } from "@maxhub/max-ui"

import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

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
      <AlertDialogContent className="max-h-[90dvh] w-[calc(100%-2rem)] gap-5 overflow-y-auto rounded-3xl border-0 bg-max-surface p-5 sm:p-6">
        <AlertDialogHeader className="justify-items-start gap-3 text-left">
          <AlertDialogTitle className="text-xl font-semibold tracking-tight text-max-text-primary">
            Возможно, нужна
            <br />
            срочная помощь
          </AlertDialogTitle>

          <AlertDialogDescription>
            Вы упомянули боль. При некоторых симптомах важно не откладывать
            обращение за помощью.
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="overflow-hidden rounded-max-medium bg-red-100 px-5 py-5">
          <span className="text-xs font-medium text-red-800">
            Единый номер экстренных служб
          </span>

          <div className="mt-3 font-unbounded text-6xl leading-none font-medium tracking-[-0.09em] text-red-800">
            112
          </div>

          <p className="mt-4 text-sm leading-5 text-red-900/80">
            При сильной боли в груди, затруднённом дыхании или потере сознания
            немедленно вызывайте помощь.
          </p>

          <a
            href="tel:112"
            className="mt-5 flex h-12 w-full items-center justify-between rounded-max-medium bg-red-800 px-5 text-sm font-semibold text-white transition-colors hover:bg-red-900 active:bg-red-950"
          >
            Позвонить
            <ArrowUpRight size={20} />
          </a>
        </div>

        <Button
          type="button"
          size="medium"
          variant="secondary"
          stretched
          onClick={onContinue}
        >
          Продолжить опрос
        </Button>
      </AlertDialogContent>
    </AlertDialog>
  )
}
