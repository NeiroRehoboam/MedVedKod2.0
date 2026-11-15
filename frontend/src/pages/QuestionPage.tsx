import { useNavigate } from "react-router-dom"

import {
  QuestionAnamnesis,
  QuestionFinish,
  QuestionPayment,
  QuestionWelcome,
  QuestionStep,
} from "@/components/common"

import { useQuestionFlow } from "@/hooks/useQuestionFlow"

export function QuestionPage() {
  const navigate = useNavigate()
  const flow = useQuestionFlow()

  const goHome = () => navigate("/home")

  switch (flow.step) {
    case "welcome":
      return (
        <QuestionWelcome
          onStart={() => flow.setStep("anamnesis")}
          onHome={goHome}
        />
      )

    case "anamnesis":
      return (
        <QuestionAnamnesis
          onContinue={() => flow.setStep("questions")}
          onBack={() => flow.setStep("welcome")}
          onHome={goHome}
        />
      )

    case "questions":
      return <QuestionStep flow={flow} onHome={goHome} />

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
          onHome={goHome}
        />
      )

    case "finished":
      return <QuestionFinish payment={flow.payment ?? undefined} />
  }
}
