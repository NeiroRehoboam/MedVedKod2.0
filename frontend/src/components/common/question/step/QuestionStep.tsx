import { useState } from "react"
import { Textarea } from "@maxhub/max-ui"

import { questions } from "@/data/questions-patient.mock"
import type { QuestionFlow } from "@/hooks/useQuestionFlow"

import { AnswersSheet } from "./AnswersSheet"
import { QuestionCard } from "./QuestionCard"
import { QuestionEmergencyDialog } from "../emergency/QuestionEmergencyDialog"
import { QuestionHeader } from "./QuestionHeader"
import { QuestionNavigation } from "./QuestionNavigation"
import { PageDescription } from "../../typography"

type QuestionStepProps = {
  flow: QuestionFlow
  onHome: () => void
}

export function QuestionStep({ flow, onHome }: QuestionStepProps) {
  const [isListening] = useState(false)

  const {
    index,
    question,
    answer,
    answers,
    updateAnswer,
    isLast,
    canNext,
    handleNext,
    handleBack,
    sheetOpen,
    setSheetOpen,
    selectQuestion,
    emergencyOpen,
    setEmergencyOpen,
    continueAfterEmergency,
  } = flow

  return (
    <main className="flex min-h-dvh flex-col max-w-3xl mx-auto">
      <div className="mx-auto flex w-full flex-1 flex-col px-5 pt-6 pb-[max(24px,env(safe-area-inset-bottom))] sm:px-8 sm:pt-8">
        <QuestionHeader
          onHome={onHome}
          questionIndex={index}
          totalQuestions={questions.length}
        />

        <div className="flex flex-1 flex-col justify-center py-5">
          <QuestionCard
            key={question.id}
            question={question}
            answer={answer}
            onAnswer={updateAnswer}
          />
        </div>

        <div className="mt-auto space-y-5">
          <div className="space-y-3">
            <div className="flex flex-wrap items-baseline justify-between gap-1 px-1">
              <label htmlFor="question-answer">
                <PageDescription variant="description" color="primary">
                  {question.options.length > 0
                    ? "Или ответьте своими словами"
                    : "Ваш ответ"}
                </PageDescription>
              </label>

              {question.optional && (
                <PageDescription variant="description" color="secondary">
                  Необязательно
                </PageDescription>
              )}
            </div>

            <div className="relative">
              <Textarea
                id="question-answer"
                key={question.id}
                value={answer}
                onChange={(event) => updateAnswer(event.target.value)}
                readOnly={isListening}
                placeholder="Напишите или расскажите, как вы себя чувствуете…"
                className="min-h-30 p-1"
              />

              {/* Здесь позже вернём VoiceInput */}
            </div>
          </div>

          <QuestionNavigation
            canBack
            canNext={canNext}
            isLast={isLast}
            canSkip={Boolean(question.optional && !answer.trim())}
            onBack={handleBack}
            onNext={handleNext}
            onOpenAnswers={() => setSheetOpen(true)}
          />
        </div>
      </div>

      <AnswersSheet
        open={sheetOpen}
        onOpenChange={setSheetOpen}
        questions={questions}
        answers={answers}
        currentIndex={index}
        onSelect={selectQuestion}
      />

      <QuestionEmergencyDialog
        open={emergencyOpen}
        onOpenChange={setEmergencyOpen}
        onContinue={continueAfterEmergency}
      />
    </main>
  )
}
