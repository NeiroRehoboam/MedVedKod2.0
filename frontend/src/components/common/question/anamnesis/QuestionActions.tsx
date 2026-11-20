import { ArrowLeft, ArrowRight } from "lucide-react"
import { Button } from "@maxhub/max-ui"

type QuestionActionsProps = {
  onBack: () => void
}

export function QuestionActions({ onBack }: QuestionActionsProps) {
  return (
    <div className="flex gap-2 pt-2">
      <Button
        type="button"
        variant="secondary"
        onClick={onBack}
        iconBefore={<ArrowLeft className="size-4" />}
      >
        Назад
      </Button>

      <Button
        type="submit"
        className="max-button-between flex-1"
        iconAfter={<ArrowRight className="size-4" />}
      >
        Далее
      </Button>
    </div>
  )
}
