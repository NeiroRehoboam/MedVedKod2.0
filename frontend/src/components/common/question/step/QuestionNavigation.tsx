import { Button, IconButton } from "@maxhub/max-ui"
import { ArrowLeft, ArrowRight, Check } from "lucide-react"

type QuestionNavigationProps = {
  canBack: boolean
  canNext: boolean
  isLast: boolean
  canSkip?: boolean
  onBack: () => void
  onNext: () => void
  onOpenAnswers: () => void
}

export function QuestionNavigation({
  canBack,
  canNext,
  isLast,
  canSkip = false,
  onBack,
  onNext,
  onOpenAnswers,
}: QuestionNavigationProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <Button
        type="button"
        size="small"
        variant="ghost"
        onClick={onOpenAnswers}
      >
        Мои ответы
      </Button>

      <div className="ml-auto flex gap-2">
        {canBack && (
          <IconButton
            type="button"
            variant="secondary"
            size="medium"
            onClick={onBack}
            aria-label="Предыдущий вопрос"
          >
            <ArrowLeft className="size-5" strokeWidth={2} />
          </IconButton>
        )}
        {canSkip ? (
          <Button
            type="button"
            size="medium"
            variant="primary"
            disabled={!canNext}
            onClick={onNext}
          >
            Пропустить
          </Button>
        ) : (
          <IconButton
            type="button"
            size="medium"
            disabled={!canNext}
            onClick={onNext}
            aria-label={isLast ? "Завершить" : "Следующий вопрос"}
          >
            {isLast ? <Check size={20} /> : <ArrowRight size={20} />}
          </IconButton>
        )}
      </div>
    </div>
  )
}
