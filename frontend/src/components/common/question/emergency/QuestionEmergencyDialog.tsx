import { ArrowUpRight } from "lucide-react"
import { BottomSheet, Button } from "@maxhub/max-ui"
import { PageDescription, PageTitle } from "../../typography"

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
    <BottomSheet open={open} onClose={() => onOpenChange(false)}>
      <div className="mx-auto flex w-full max-w-lg flex-col gap-5">
        <div className="flex flex-col gap-3 pt-2">
          <PageTitle as="h3">
            Возможно, нужна
            <br />
            срочная помощь
          </PageTitle>

          <PageDescription>
            Вы упомянули боль. При некоторых симптомах важно не откладывать
            обращение за помощью.
          </PageDescription>
        </div>

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
      </div>
    </BottomSheet>
  )
}
