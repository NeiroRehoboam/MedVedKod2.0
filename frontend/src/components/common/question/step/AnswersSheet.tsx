import { Check, ChevronRight, LockKeyhole } from "lucide-react"
import { BottomSheet } from "@maxhub/max-ui"

import type { Question } from "@/data/questions-patient.mock"
import { PageDescription, PageTitle } from "../../typography"

type AnswersSheetProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  questions: Question[]
  answers: Record<string, string>
  currentIndex: number
  onSelect: (index: number) => void
}

export function AnswersSheet({
  open,
  onOpenChange,
  questions,
  answers,
  currentIndex,
  onSelect,
}: AnswersSheetProps) {
  return (
    <BottomSheet open={open} onClose={() => onOpenChange(false)}>
      <div className="flex max-h-[75dvh] min-h-0 flex-col gap-5">
        <div className="flex shrink-0 flex-col gap-3 pt-2">
          <PageTitle as="h4">Мои ответы</PageTitle>

          <PageDescription>
            Вернитесь к пройденным вопросам, чтобы изменить ответ.
          </PageDescription>
        </div>

        <div className="min-h-0 scrollbar-none space-y-2 overflow-y-auto pb-4">
          {questions.map((question, index) => {
            const answer = answers[question.id]

            const isCurrent = index === currentIndex
            const isCompleted = index < currentIndex && Boolean(answer?.trim())
            const isFuture = index > currentIndex
            const canNavigate = isCompleted

            return (
              <button
                key={question.id}
                type="button"
                disabled={!canNavigate}
                onClick={() => {
                  onSelect(index)
                  onOpenChange(false)
                }}
                className={`flex w-full items-center gap-3 rounded-max-medium px-4 py-4 text-left transition-colors ${
                  isCurrent ? "bg-max-tertiary" : "bg-max-primary"
                } ${
                  canNavigate
                    ? "cursor-pointer hover:bg-max-tertiary"
                    : "cursor-default"
                }`}
              >
                <div
                  className={`flex size-9 shrink-0 items-center justify-center rounded-full text-xs font-medium ${
                    isCompleted
                      ? "bg-max-tertiary text-max-text-primary"
                      : isCurrent
                        ? "bg-max-text-primary text-max-text-primary-inverse"
                        : "bg-max-tertiary text-max-text-tertiary"
                  }`}
                >
                  {isCompleted ? (
                    <Check size={17} />
                  ) : isFuture ? (
                    <LockKeyhole size={16} />
                  ) : (
                    index + 1
                  )}
                </div>

                <div className="min-w-0 flex-1 space-y-1">
                  <div className="line-clamp-2 text-sm leading-5 font-medium text-max-text-primary">
                    {isFuture ? "Уточняющий вопрос" : question.text}
                  </div>

                  <div className="line-clamp-2 text-xs leading-4 text-max-text-secondary">
                    {isFuture
                      ? "Появится после вашего ответа"
                      : isCurrent
                        ? "Текущий вопрос"
                        : answer || "Нет ответа"}
                  </div>
                </div>

                {canNavigate && (
                  <ChevronRight
                    size={18}
                    className="shrink-0 text-max-text-secondary"
                  />
                )}
              </button>
            )
          })}
        </div>
      </div>
    </BottomSheet>
  )
}
