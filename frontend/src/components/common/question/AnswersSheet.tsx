import { Check, ChevronRight, LockKeyhole } from "lucide-react"

import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"

import {
  Item,
  ItemActions,
  ItemContent,
  ItemDescription,
  ItemMedia,
  ItemTitle,
} from "@/components/ui/item"

import type { Question } from "@/data/questions-patient.mock"

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
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="bottom"
        className="max-h-[85dvh] rounded-t-[28px] px-5 pb-8"
      >
        <SheetHeader className="px-0">
          <SheetTitle className="text-left text-xl">Мои ответы</SheetTitle>

          <SheetDescription className="text-left">
            Вернитесь к пройденным вопросам, чтобы изменить ответ.
          </SheetDescription>
        </SheetHeader>

        <div className="mt-4 min-h-0 scrollbar-none space-y-2 overflow-y-auto">
          {questions.map((question, index) => {
            const answer = question ? answers[question.id] : undefined

            const isCurrent = index === currentIndex
            const isCompleted = index < currentIndex && Boolean(answer?.trim())
            const isFuture = index > currentIndex

            const canNavigate = isCompleted && Boolean(question)

            return (
              <Item
                key={question?.id ?? `future-${index}`}
                variant="muted"
                onClick={
                  canNavigate
                    ? () => {
                        onSelect(index)
                        onOpenChange(false)
                      }
                    : undefined
                }
              >
                <ItemMedia>
                  <span
                    className={[
                      "flex size-9 items-center justify-center rounded-full text-xs font-medium",
                      isCompleted
                        ? "bg-foreground/20 text-foreground"
                        : isCurrent
                          ? "bg-foreground text-background"
                          : "bg-foreground/5 text-foreground/50",
                    ].join(" ")}
                  >
                    {isCompleted ? (
                      <Check className="size-4" />
                    ) : isFuture ? (
                      <LockKeyhole className="size-4" />
                    ) : (
                      index + 1
                    )}
                  </span>
                </ItemMedia>

                <ItemContent>
                  <ItemTitle className="text-sm leading-5">
                    {isFuture
                      ? "Уточняющий вопрос"
                      : (question?.text ?? "Уточняющий вопрос")}
                  </ItemTitle>

                  <ItemDescription className="line-clamp-2 text-xs">
                    {isFuture
                      ? "Появится после вашего ответа"
                      : isCurrent
                        ? "Текущий вопрос"
                        : answer || "Нет ответа"}
                  </ItemDescription>
                </ItemContent>

                {canNavigate && (
                  <ItemActions>
                    <ChevronRight className="size-4 text-muted-foreground" />
                  </ItemActions>
                )}
              </Item>
            )
          })}
        </div>
      </SheetContent>
    </Sheet>
  )
}
