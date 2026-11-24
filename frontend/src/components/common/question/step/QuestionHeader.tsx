import { useState } from "react"
import { House } from "lucide-react"
import { IconButton } from "@maxhub/max-ui"

import { Progress, ProgressLabel } from "@/components/ui/progress"
import { DoctorSignature } from "../../typography"
import { QuestionExitSheet } from "./QuestionExitDialog"

type QuestionHeaderProps = {
  onExit: () => void
  questionIndex?: number
  totalQuestions?: number
}

export function QuestionHeader({
  onExit,
  questionIndex,
  totalQuestions,
}: QuestionHeaderProps) {
  const [exitOpen, setExitOpen] = useState(false)

  return (
    <>
      <header className="space-y-7">
        <div className="flex items-center justify-between gap-4">
          <button
            type="button"
            onClick={() => setExitOpen(true)}
            className="relative block w-fit shrink-0 text-left"
          >
            <h1 className="relative z-10 font-unbounded text-xl font-semibold tracking-[-0.04em] text-max-text-primary">
              МедВедь
            </h1>

            <DoctorSignature className="absolute top-4 left-20 z-20 -rotate-6">
              Я рядом
            </DoctorSignature>
          </button>

          <IconButton
            size="small"
            variant="secondary"
            onClick={() => setExitOpen(true)}
            aria-label="Вернуться на главную"
          >
            <House className="size-5" strokeWidth={1.7} />
          </IconButton>
        </div>

        {questionIndex !== undefined && (
          <Progress
            value={totalQuestions && totalQuestions > 1 ? questionIndex + 1 : 0}
            max={Math.max(totalQuestions ?? 1, 1)}
            className="gap-3 **:data-[slot=progress-indicator]:rounded-max-medium **:data-[slot=progress-indicator]:bg-max-text-themed **:data-[slot=progress-track]:h-2 **:data-[slot=progress-track]:bg-max-tertiary"
          >
            <ProgressLabel className="text-sm font-normal text-max-text-secondary">
              Вопрос{" "}
              <span className="font-semibold text-max-text-primary">
                {questionIndex + 1}
              </span>
              {totalQuestions !== undefined &&
                totalQuestions > 1 &&
                ` из ${totalQuestions}`}
            </ProgressLabel>
          </Progress>
        )}
      </header>

      <QuestionExitSheet
        open={exitOpen}
        onClose={() => setExitOpen(false)}
        onExit={onExit}
      />
    </>
  )
}
