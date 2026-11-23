import { useEffect, useState } from "react"
import { ChevronRight } from "lucide-react"

import { Sheet, SheetContent, SheetHeader } from "@/components/ui/sheet"

import type { SessionQuestion } from "@/api/generated/models"
import { PageDescription } from "../../typography"
import {
  AlertDialogDescription,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

type AnswersSheetProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  questions: SessionQuestion[]
  answers: Record<string, string>
  currentIndex: number
  onSelect: (index: number) => void
}

function useIsMobile() {
  const [isMobile, setIsMobile] = useState(() =>
    typeof window !== "undefined"
      ? window.matchMedia("(max-width: 639px)").matches
      : false
  )

  useEffect(() => {
    const media = window.matchMedia("(max-width: 639px)")

    const handleChange = (event: MediaQueryListEvent) => {
      setIsMobile(event.matches)
    }

    setIsMobile(media.matches)

    media.addEventListener("change", handleChange)

    return () => {
      media.removeEventListener("change", handleChange)
    }
  }, [])

  return isMobile
}

export function AnswersSheet({
  open,
  onOpenChange,
  questions,
  answers,
  currentIndex,
  onSelect,
}: AnswersSheetProps) {
  const isMobile = useIsMobile()

  const handleSelect = (index: number) => {
    onSelect(index)
    onOpenChange(false)
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side={isMobile ? "bottom" : "right"}
        className={
          isMobile
            ? "flex max-h-[85dvh] min-h-0 w-full flex-col gap-0 rounded-t-3xl bg-max-surface"
            : "flex h-dvh min-h-0 w-full flex-col gap-0 rounded-l-3xl border-border bg-max-surface p-0 sm:max-w-md"
        }
      >
        {/* {isMobile && (
          <div
            aria-hidden="true"
            className="mx-auto mt-5 h-1 w-10 shrink-0 rounded-full bg-max-text-tertiary/30"
          />
        )} */}

        <SheetHeader>
          <AlertDialogTitle className="text-xl font-semibold tracking-tight text-max-text-primary">
            Мои ответы
          </AlertDialogTitle>

          <AlertDialogDescription>
            Просмотрите ответы на пройденные вопросы.
          </AlertDialogDescription>
        </SheetHeader>

        <div className="min-h-0 flex-1 scrollbar-none overflow-y-auto overscroll-contain px-5 pb-[max(2rem,env(safe-area-inset-bottom))] sm:px-6">
          <div className="divide-y divide-max-text-tertiary/15">
            {questions.map((question, index) => {
              const answer = answers[question.id]

              const isCurrent = index === currentIndex
              const isPast = index < currentIndex
              const isFuture = index > currentIndex
              const canNavigate = isPast

              return (
                <button
                  key={question.id}
                  type="button"
                  disabled={!canNavigate}
                  onClick={() => handleSelect(index)}
                  className={`group flex min-h-24 w-full items-center gap-5 py-4 text-left transition-colors ${
                    canNavigate ? "cursor-pointer" : "cursor-default"
                  }`}
                >
                  <span
                    className={`w-6 shrink-0 font-unbounded text-base text-max-text-primary tabular-nums`}
                  >
                    {String(index + 1).padStart(2, "0")}
                  </span>

                  <div className="min-w-0 flex-1 space-y-1">
                    <PageDescription
                      variant="body-strong"
                      className={`line-clamp-2 leading-4.5 ${
                        isFuture
                          ? "text-max-text-tertiary!"
                          : isCurrent
                            ? "text-max-text-themed!"
                            : "text-max-text-primary!"
                      }`}
                    >
                      {isFuture ? "Уточняющий вопрос" : question.question_text}
                    </PageDescription>
                    {/* <div
                      className={`line-clamp-2 leading-4.5 font-medium ${
                        isFuture
                          ? "text-max-text-tertiary"
                          : isCurrent
                            ? "text-max-text-themed"
                            : "text-max-text-primary"
                      }`}
                    >
                      {isFuture ? "Уточняющий вопрос" : question.text}
                    </div> */}

                    <PageDescription
                      variant="description"
                      className="line-clamp-2!"
                    >
                      {isFuture
                        ? "Появится после вашего ответа"
                        : isCurrent
                          ? "Текущий вопрос"
                          : answer?.trim() || "Нет ответа"}
                    </PageDescription>
                  </div>

                  {canNavigate && (
                    <ChevronRight
                      size={17}
                      strokeWidth={1.7}
                      className="shrink-0 text-max-text-tertiary transition-transform duration-200 group-hover:translate-x-0.5"
                    />
                  )}
                </button>
              )
            })}
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
