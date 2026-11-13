import { useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Message, MessageContent } from "@/components/ui/message"
import { Bubble, BubbleContent } from "@/components/ui/bubble"
import type { Question } from "@/data/questions-patient.mock"

type QuestionCardProps = {
  question: Question
  answer: string
  onAnswer: (value: string) => void
}

export function QuestionCard({
  question,
  answer,
  onAnswer,
}: QuestionCardProps) {
  const headingRef = useRef<HTMLHeadingElement>(null)

  useEffect(() => {
    window.scrollTo(0, 0)
    headingRef.current?.focus({ preventScroll: true })
  }, [])

  return (
    <section className="w-full space-y-7" aria-labelledby="question-heading">
      <div className="space-y-3">
        <Message>
          <MessageContent className="w-full">
            <Bubble className="w-full max-w-full">
              <BubbleContent className="px-5 py-4 text-lg sm:text-xl">
                <h1
                  ref={headingRef}
                  id="question-heading"
                  tabIndex={-1}
                  className="outline-none"
                >
                  {question.text}
                </h1>
              </BubbleContent>
            </Bubble>
          </MessageContent>
        </Message>
      </div>

      {question.options.length > 0 && (
        <div
          className="space-y-3"
          role="group"
          aria-labelledby="question-options-label"
        >
          <p
            id="question-options-label"
            className="text-xs font-medium text-muted-foreground"
          >
            Выберите подходящий вариант
          </p>

          <div className="flex flex-wrap gap-2">
            {question.options.map((option) => {
              const selected = answer === option

              return (
                <Button
                  key={option}
                  type="button"
                  variant={selected ? "default" : "outline"}
                  aria-pressed={selected}
                  onClick={() => onAnswer(option)}
                  className={`min-h-11 rounded-full px-5 text-sm transition-colors ${
                    selected
                      ? "bg-foreground text-background hover:bg-foreground/90"
                      : ""
                  }`}
                >
                  {option}
                </Button>
              )
            })}
          </div>
        </div>
      )}
    </section>
  )
}
