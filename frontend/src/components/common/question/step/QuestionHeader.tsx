import { House } from "lucide-react"
import { Progress, ProgressLabel } from "@/components/ui/progress"
import { IconButton } from "@maxhub/max-ui"
import { Link } from "react-router-dom"
import { DoctorSignature } from "../../typography"

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

          <DoctorSignature className="absolute top-4 left-20 z-20 -rotate-6">
            Я рядом
          </DoctorSignature>
        </Link>

        <IconButton
          size="small"
          variant="secondary"
          onClick={onHome}
          aria-label="Главная"
        >
          <House className="size-5" strokeWidth={1.7} />
        </IconButton>
      </div>

      {questionIndex !== undefined && totalQuestions !== undefined && (
        <Progress
          value={questionIndex + 1}
          max={totalQuestions}
          className="gap-3 **:data-[slot=progress-indicator]:rounded-max-medium **:data-[slot=progress-indicator]:bg-max-text-themed **:data-[slot=progress-indicator]:transition-[width] **:data-[slot=progress-track]:h-2 **:data-[slot=progress-track]:bg-max-tertiary **:data-[slot=progress-indicator]:motion-reduce:transition-none"
        >
          <ProgressLabel className="text-sm font-normal text-max-text-secondary">
            Вопрос{" "}
            <span className="font-semibold text-max-text-primary">
              {questionIndex + 1}
            </span>{" "}
            из {totalQuestions}
          </ProgressLabel>
        </Progress>
      )}
    </header>
  )
}
