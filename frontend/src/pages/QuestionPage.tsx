import { useRef, useState } from "react"
import { useNavigate } from "react-router-dom"
import { QuestionCard } from "@/components/common/question/QuestionCard"
import { QuestionNavigation } from "@/components/common/question/QuestionNavigation"
import { AnswersSheet } from "@/components/common/question/AnswersSheet"
import { questions } from "@/data/questions-patient.mock"
import { Textarea } from "@/components/ui/textarea"
import { QuestionWelcome } from "@/components/common/question/QuestionWelcome"
import { QuestionFinish } from "@/components/common/question/QuestionFinish"
import { QuestionHeader } from "@/components/common/question/QuestionHeader"
import { QuestionAnamnesis } from "@/components/common/question/QuestionAnamnesis"
import { Label } from "@/components/ui/label"
import { QuestionPayment } from "@/components/common/question/QuestionPayment"
import type { PaymentType } from "@/data/payment.mock"
import { QuestionEmergencyDialog } from "@/components/common/question/QuestionEmergencyDialog"
// import { VoiceInput } from "@/components/common/VoiceInput"

export function QuestionPage() {
  const navigate = useNavigate()
  const [index, setIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [sheetOpen, setSheetOpen] = useState(false)
  const [step, setStep] = useState<
    "welcome" | "anamnesis" | "questions" | "payment" | "finished"
  >("welcome")
  const [payment, setPayment] = useState<PaymentType | null>(null)
  const question = questions[index]
  const answer = answers[question.id] ?? ""
  const isLast = index === questions.length - 1
  const canNext = Boolean(question.optional || answer.trim())
  const [emergencyOpen, setEmergencyOpen] = useState(false)
  const [emergencyShown, setEmergencyShown] = useState(false)
  const voiceBaseRef = useRef("")
  const updateAnswer = (value: string) => {
    setAnswers((prev) => ({ ...prev, [question.id]: value }))
  }
  const [isListening, setIsListening] = useState(false)
  const goNext = () => {
    if (isLast) {
      setStep("payment")
      return
    }

    setIndex((prev) => prev + 1)
  }
  const handleNext = () => {
    if (!canNext) return

    const hasPain = /боль/i.test(answer)

    if (hasPain && !emergencyShown) {
      setEmergencyShown(true)
      setEmergencyOpen(true)
      return
    }

    goNext()
  }
  if (step === "welcome") {
    return (
      <QuestionWelcome
        onStart={() => setStep("anamnesis")}
        onHome={() => navigate("/home")}
      />
    )
  }
  if (step === "anamnesis") {
    return (
      <QuestionAnamnesis
        onContinue={() => setStep("questions")}
        onBack={() => setStep("welcome")}
        onHome={() => navigate("/home")}
      />
    )
  }
  if (step === "finished") {
    return <QuestionFinish payment={payment ?? undefined} />
  }
  if (step === "payment") {
    return (
      <QuestionPayment
        value={payment}
        onChange={setPayment}
        onBack={() => setStep("questions")}
        onContinue={() => {
          if (payment) setStep("finished")
        }}
        onHome={() => navigate("/home")}
      />
    )
  }

  return (
    <main className="flex min-h-dvh flex-col bg-muted">
      <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col px-5 pt-6 pb-[max(24px,env(safe-area-inset-bottom))] sm:px-8 sm:pt-8">
        <QuestionHeader
          onHome={() => navigate("/home")}
          questionIndex={index}
          totalQuestions={questions.length}
        />

        {/* Основной контейнер с карточкой вопроса */}
        <div className="flex flex-1 flex-col justify-center py-8 sm:py-12">
          <QuestionCard
            key={question.id}
            question={question}
            answer={answer}
            onAnswer={updateAnswer}
          />
        </div>

        {/* Поле для ввода ответа и кнопки навигации */}
        <div className="mt-auto space-y-5">
          <div className="space-y-3">
            <div className="flex flex-wrap items-baseline justify-between gap-2 px-1">
              <Label htmlFor="question-answer" className="text-sm font-medium">
                {question.options.length > 0
                  ? "Или ответьте своими словами"
                  : "Ваш ответ"}
              </Label>
              {question.optional && (
                <span className="text-xs text-muted-foreground">
                  Необязательно
                </span>
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
                className="min-h-28 resize-none rounded-3xl border-border bg-background px-5 py-4 pr-16 pb-14 text-base leading-6"
              />

              <div className="absolute right-3 bottom-3">
                {/* <VoiceInput
                  key={question.id}
                  onListeningChange={(listening) => {
                    setIsListening(listening)

                    if (listening) {
                      voiceBaseRef.current = answers[question.id] ?? ""
                    }
                  }}
                  onTranscript={(text) => {
                    const base = voiceBaseRef.current.trim()

                    setAnswers((prev) => ({
                      ...prev,
                      [question.id]: [base, text].filter(Boolean).join(" "),
                    }))
                  }}
                /> */}
              </div>
            </div>

            {question.optional && (
              <p
                id="answer-hint"
                className="px-1 text-sm leading-5 text-muted-foreground"
              >
                Если больше нечего добавить, можно пропустить.
              </p>
            )}
          </div>
          <QuestionNavigation
            canBack
            canNext={canNext}
            isLast={isLast}
            canSkip={Boolean(question.optional && !answer.trim())}
            onBack={() =>
              index > 0 ? setIndex((prev) => prev - 1) : setStep("anamnesis")
            }
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
        onSelect={(nextIndex) => {
          setIndex(nextIndex)
          setSheetOpen(false)
        }}
      />

      <QuestionEmergencyDialog
        open={emergencyOpen}
        onOpenChange={setEmergencyOpen}
        onContinue={() => {
          setEmergencyOpen(false)
          goNext()
        }}
      />
    </main>
  )
}
