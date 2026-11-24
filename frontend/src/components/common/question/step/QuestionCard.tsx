import { useEffect, useRef } from "react"
import { Typography } from "@maxhub/max-ui"
import { cn } from "cn"

import type { SessionQuestion } from "@/api/generated/models"
import { PageDescription } from "../../typography"

type QuestionCardProps = {
  question: SessionQuestion
  answer: string
  onAnswer: (value: string) => void
  readOnly?: boolean
}

export function QuestionCard({
  question,
  answer,
  onAnswer,
  readOnly = false,
}: QuestionCardProps) {
  const headingRef = useRef<HTMLHeadingElement>(null)
  const options = Array.isArray(question.options) ? question.options : []

  useEffect(() => {
    window.scrollTo(0, 0)
    headingRef.current?.focus({ preventScroll: true })
  }, [question.question_text])

  return (
    <section className="w-full space-y-7" aria-labelledby="question-heading">
      <div className="w-fit max-w-full rounded-max-medium bg-max-text-themed px-5 py-4">
        <h1
          ref={headingRef}
          id="question-heading"
          tabIndex={-1}
          className="outline-none"
        >
          <Typography.Title className="text-white">
            {question.question_text}
          </Typography.Title>
        </h1>
      </div>

      {options.length > 0 && (
        <div
          className="space-y-3"
          role="group"
          aria-labelledby="question-options-label"
        >
          <div id="question-options-label">
            <PageDescription variant="description" color="secondary">
              Выберите подходящий вариант
            </PageDescription>
          </div>

          <div className="flex flex-wrap gap-2">
            {options.map((option) => {
              const selected = answer === option.text

              return (
                <button
                  key={option.id}
                  type="button"
                  aria-pressed={selected}
                  disabled={readOnly}
                  onClick={() => onAnswer(option.text)}
                  className={cn(
                    "inline-flex min-h-10 items-center justify-center",
                    "rounded-max-medium px-4 py-2.5",
                    "text-sm leading-5 font-normal",
                    "transition-colors duration-200",
                    "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-max-text-themed",
                    selected
                      ? "bg-max-text-themed text-white"
                      : "bg-max-tertiary text-max-text-primary hover:bg-max-tertiary/80"
                  )}
                >
                  {option.text}
                </button>
              )
            })}
          </div>
        </div>
      )}
    </section>
  )
}
