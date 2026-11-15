import { House } from "lucide-react"
import { Progress, ProgressLabel } from "@/components/ui/progress"
import { IconButton } from "@maxhub/max-ui"
import { Link } from "react-router-dom"

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
        <Link to="/home" className="relative block w-fit shrink-0">
          <h1 className="relative z-10 font-unbounded text-xl font-semibold tracking-[-0.04em] text-max-text-primary">
            МедВед
          </h1>

          <span className="absolute top-4 left-20 z-20 -rotate-6 font-doctor text-2xl leading-none whitespace-nowrap text-max-text-themed">
            Я рядом
          </span>
        </Link>

        <IconButton
          size="small"
          variant="secondary"
          onClick={onHome}
          aria-label="Помощь"
        >
          <House className="size-5" strokeWidth={1.7} />
        </IconButton>
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
