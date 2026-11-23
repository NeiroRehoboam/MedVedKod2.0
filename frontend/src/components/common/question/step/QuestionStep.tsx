import { useRef, useState } from "react"
import { Textarea } from "@maxhub/max-ui"

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
  } = flow

  return (
    <>
      <section className="flex min-h-0 w-full flex-1 flex-col">
        {/* Карточка вопроса */}
        <div className="flex flex-1 flex-col justify-center py-5">
          <QuestionCard
            key={question.id}
            question={question}
            answer={answer}
            onAnswer={updateAnswer}
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
                readOnly={isListening || flow.readOnly}
                placeholder="Напишите или расскажите, как вы себя чувствуете…"
                className="min-h-30 p-1"
              />

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

                    updateAnswer([base, text.trim()].filter(Boolean).join(" "))
                  }}
                />
              </div>
            </div>
          </div>

          <QuestionNavigation
            canBack={!isListening && !flow.isPending && !flow.response?.safety.should_stop}
            canNext={canNext && !isListening}
            isLast={isLast}
            canSkip={false}
            onBack={handleBack}
            onNext={handleNext}
            onOpenAnswers={() => {
              if (!isListening && !flow.isPending) {
                setSheetOpen(true)
              }
            }}
          />
          {flow.isPending && <p role="status">Обрабатываем ответ...</p>}
          {flow.error && <p role="alert">{flow.error}</p>}
          {flow.response?.safety.should_stop && !emergencyOpen && (
            <div>
              <p role="alert">{flow.response.safety.recommended_action}</p>
              <button type="button" onClick={continueAfterEmergency}>Перейти к результату</button>
            </div>
          )}
        </div>
      </section>

      <AnswersSheet
        open={sheetOpen}
        onOpenChange={setSheetOpen}
        questions={flow.questions}
        answers={answers}
        currentIndex={index}
        onSelect={selectQuestion}
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
