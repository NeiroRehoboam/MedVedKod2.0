import { useEffect, useRef } from "react"
import { Button, Typography } from "@maxhub/max-ui"

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
  }, [question.text])

  return (
    <section className="w-full space-y-7" aria-labelledby="question-heading">
      <div className="rounded-max-medium bg-max-text-themed px-5 py-4">
        <h1
          ref={headingRef}
          id="question-heading"
          tabIndex={-1}
          className="outline-none"
        >
          <Typography.Title className="text-white">
            {question.text}
          </Typography.Title>
        </h1>
      </div>

      {question.options.length > 0 && (
        <div
          className="space-y-3"
          role="group"
          aria-labelledby="question-options-label"
        >
          <div id="question-options-label">
            <Typography.Text variant="body" color="secondary">
              Выберите подходящий вариант
            </Typography.Text>
          </div>

          <div className="flex flex-wrap gap-2">
            {question.options.map((option) => {
              const selected = answer === option

              return (
                <Button
                  key={option}
                  type="button"
                  size="xsmall"
                  variant={selected ? "primary" : "secondary"}
                  aria-pressed={selected}
                  onClick={() => onAnswer(option)}
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
