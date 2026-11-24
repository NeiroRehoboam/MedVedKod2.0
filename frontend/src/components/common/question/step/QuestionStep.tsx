import { useRef, useState } from "react"
import { Spinner, Textarea } from "@maxhub/max-ui"

import type { QuestionFlow } from "@/hooks/useQuestionFlow"

import { AnswersSheet } from "./AnswersSheet"
import { QuestionCard } from "./QuestionCard"
import { QuestionEmergencyDialog } from "../emergency/QuestionEmergencyDialog"
import { QuestionNavigation } from "./QuestionNavigation"
import { PageDescription } from "../../typography"
import { VoiceInput } from "../../VoiceInput"

type QuestionStepProps = {
  flow: QuestionFlow
}

export function QuestionStep({ flow }: QuestionStepProps) {
  const [isListening, setIsListening] = useState(false)
  const voiceBaseRef = useRef("")

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
    isPending,
  } = flow

  return (
    <>
      <section
        className="relative flex min-h-0 w-full flex-1 flex-col"
        aria-busy={isPending}
      >
        {/* Загрузка */}
        {isPending && (
          <div
            className="absolute inset-0 z-20 flex flex-col items-center justify-center gap-4 px-6"
            role="status"
          >
            <Spinner className="size-8" />

            <PageDescription variant="description">
              Обрабатываем ответ…
            </PageDescription>
          </div>
        )}

        {/* Содержимое вопроса */}
        <div
          className={`flex min-h-0 flex-1 flex-col ${
            isPending ? "pointer-events-none invisible" : ""
          }`}
          inert={isPending}
        >
          {/* Карточка вопроса */}
          <div className="flex flex-1 flex-col justify-center py-5">
            <QuestionCard
              key={question.id}
              question={question}
              answer={answer}
              onAnswer={updateAnswer}
              readOnly={flow.readOnly}
            />
          </div>

          {/* Ответ и навигация */}
          <div className="mt-auto shrink-0 space-y-5">
            <div className="space-y-3">
              <div className="flex flex-wrap items-baseline justify-between gap-1 px-1">
                <label htmlFor="question-answer">
                  <PageDescription variant="description" color="primary">
                    {question.options.length > 0
                      ? "Или ответьте своими словами"
                      : "Ваш ответ"}
                  </PageDescription>
                </label>
              </div>

              <div className="relative">
                <Textarea
                  id="question-answer"
                  key={question.id}
                  value={answer}
                  onChange={(event) => updateAnswer(event.target.value)}
                  readOnly={isListening || flow.readOnly || isPending}
                  placeholder="Напишите или расскажите, как вы себя чувствуете…"
                  className="min-h-30 p-1"
                />

                {!flow.readOnly && (
                  <div className="absolute right-3 bottom-3">
                    <VoiceInput
                      key={question.id}
                      onListeningChange={(listening) => {
                        setIsListening(listening)

                        if (listening) {
                          voiceBaseRef.current = answer
                        }
                      }}
                      onTranscript={(text) => {
                        const base = voiceBaseRef.current.trim()

                        updateAnswer(
                          [base, text.trim()].filter(Boolean).join(" ")
                        )
                      }}
                    />
                  </div>
                )}
              </div>
            </div>

            <QuestionNavigation
              canBack={
                !isListening &&
                !isPending &&
                (flow.isCompleted
                  ? index > 0
                  : !flow.response?.safety.should_stop)
              }
              canNext={canNext && !isListening && !isPending}
              isLast={isLast}
              canSkip={false}
              onBack={handleBack}
              onNext={handleNext}
              onOpenAnswers={() => {
                if (!isListening && !isPending) {
                  setSheetOpen(true)
                }
              }}
            />

            {flow.error && <p role="alert">{flow.error}</p>}

            {!flow.isCompleted &&
              flow.response?.safety.should_stop &&
              !emergencyOpen && (
                <div>
                  <p role="alert">{flow.response.safety.recommended_action}</p>

                  <button type="button" onClick={continueAfterEmergency}>
                    Перейти к результату
                  </button>
                </div>
              )}
          </div>
        </div>
      </section>

      <AnswersSheet
        open={sheetOpen}
        onOpenChange={setSheetOpen}
        questions={flow.questions}
        answers={answers}
        currentIndex={index}
        onSelect={selectQuestion}
        isCompleted={flow.isCompleted}
      />

      <QuestionEmergencyDialog
        open={emergencyOpen}
        onOpenChange={setEmergencyOpen}
        onContinue={continueAfterEmergency}
        safety={flow.response?.safety}
      />
    </>
  )
}
