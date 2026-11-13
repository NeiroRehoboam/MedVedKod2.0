import { House } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Progress, ProgressLabel } from "@/components/ui/progress"

type QuestionHeaderProps = {
  onHome: () => void
  questionIndex?: number
  totalQuestions?: number
}

export function QuestionHeader({
  onHome,
  questionIndex,
  totalQuestions,
}: QuestionHeaderProps) {
  return (
    <header className="space-y-7">
      <div className="flex items-center justify-between gap-4">
        <div className="relative w-fit pb-3">
          <p className="font-unbounded text-xl font-semibold tracking-[-0.04em]">
            МедВедь
          </p>
          <span className="absolute top-5 left-20 -rotate-6 font-doctor text-2xl leading-none whitespace-nowrap text-primary">
            Я рядом
          </span>
        </div>
        <Button
          type="button"
          variant="outline"
          size="icon-lg"
          className="size-11 rounded-full bg-background hover:bg-background/80"
          onClick={onHome}
          aria-label="Вернуться на главную"
        >
          <House className="size-5" strokeWidth={1.7} />
        </Button>
      </div>

      {questionIndex !== undefined && totalQuestions !== undefined && (
        <Progress
          value={questionIndex + 1}
          max={totalQuestions}
          className="gap-3 **:data-[slot=progress-indicator]:rounded-full **:data-[slot=progress-indicator]:transition-[width] **:data-[slot=progress-track]:h-1 **:data-[slot=progress-track]:bg-border **:data-[slot=progress-indicator]:motion-reduce:transition-none"
        >
          <ProgressLabel className="text-sm font-normal text-muted-foreground">
            Вопрос{" "}
            <span className="font-semibold text-foreground">
              {questionIndex + 1}
            </span>{" "}
            из {totalQuestions}
          </ProgressLabel>
        </Progress>
      )}
    </header>
  )
}
