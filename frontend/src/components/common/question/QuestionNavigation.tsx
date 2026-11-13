import { ArrowLeft, ArrowRight, Check } from "lucide-react"
import { Button } from "@/components/ui/button"

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
        variant="ghost"
        onClick={onOpenAnswers}
        className="h-12 px-4"
      >
        Мои ответы
      </Button>

      <div className="ml-auto flex gap-2">
        {canBack && (
          <Button
            type="button"
            variant="outline"
            size="icon"
            onClick={onBack}
            aria-label="Предыдущий вопрос"
            className="size-12 shrink-0 border-border bg-background text-foreground hover:bg-background/80"
          >
            <ArrowLeft className="size-5" strokeWidth={2} />
          </Button>
        )}
        <Button
          type="button"
          size={isLast ? "default" : "icon"}
          disabled={!canNext}
          onClick={onNext}
          aria-label={
            canSkip ? "Пропустить" : isLast ? "Завершить" : "Следующий вопрос"
          }
          className={isLast ? "h-12 gap-2 px-5" : "size-12"}
        >
          {isLast && (canSkip ? "Пропустить" : "Завершить")}
          {canSkip ? (
            <ArrowRight size={20} />
          ) : isLast ? (
            <Check size={20} />
          ) : (
            <ArrowRight size={20} />
          )}
        </Button>
      </div>
    </div>
  )
}
