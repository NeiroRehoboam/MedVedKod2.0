import { useNavigate } from "react-router-dom"

import {
  QuestionAnamnesis,
  QuestionFinish,
  QuestionPayment,
  QuestionWelcome,
  QuestionStep,
  QuestionHeader,
} from "@/components/common"

import { useQuestionFlow } from "@/hooks/useQuestionFlow"
import { useStartAiSession } from "@/hooks/useAiSessions"
import { questions } from "@/data/questions-patient.mock"
import { useRef } from "react"

export function QuestionPage() {
  const navigate = useNavigate()
  const flow = useQuestionFlow()
  const startSession = useStartAiSession()

  const goHome = () => navigate("/home")

  const sessionIdRef = useRef<number | null>(null)

  const handleAnamnesisContinue = async () => {
    if (startSession.isPending) return

    if (sessionIdRef.current !== null) {
      flow.setStep("questions")
      return
    }

    try {
      const response = await startSession.mutateAsync()

      sessionIdRef.current = response.data.id
      flow.setStep("questions")
    } catch (error) {
      console.error("Не удалось создать сессию:", error)
    }
  }
  const renderStep = () => {
    switch (flow.step) {
      case "welcome":
        return (
          <QuestionWelcome
            onHome={goHome}
            onStart={() => flow.setStep("anamnesis")}
          />
        )

      case "anamnesis":
        return (
          <QuestionAnamnesis
            onContinue={handleAnamnesisContinue}
            onBack={() => flow.setStep("welcome")}
          />
        )

      case "questions":
        return <QuestionStep flow={flow} />

      case "payment":
        return (
          <QuestionPayment
            value={flow.payment}
            onChange={flow.setPayment}
            onBack={() => flow.setStep("questions")}
            onContinue={() => {
              if (flow.payment) {
                flow.setStep("finished")
              }
            }}
          />
        )

      case "finished":
        return <QuestionFinish payment={flow.payment ?? undefined} />
    }
  }

  return (
    <main className="mx-auto flex min-h-dvh max-w-3xl flex-col px-5 pt-6 pb-[max(24px,env(safe-area-inset-bottom))] sm:px-8 sm:pt-8">
      {flow.step !== "welcome" && flow.step !== "finished" && (
        <QuestionHeader
          onExit={goHome}
          questionIndex={flow.step === "questions" ? flow.index : undefined}
          totalQuestions={
            flow.step === "questions" ? questions.length : undefined
          }
        />
      )}

      <div className="flex min-h-0 flex-1 flex-col">{renderStep()}</div>
    </main>
  )
}
