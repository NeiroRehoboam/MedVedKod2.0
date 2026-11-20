import { useState } from "react"
import { questions } from "@/data/questions-patient.mock"
import type { PaymentType } from "@/data/payment.mock"

export type QuestionStepType =
  | "welcome"
  | "anamnesis"
  | "questions"
  | "payment"
  | "finished"

export function useQuestionFlow() {
  const [step, setStep] = useState<QuestionStepType>("welcome")
  const [index, setIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [payment, setPayment] = useState<PaymentType | null>(null)

  const [sheetOpen, setSheetOpen] = useState(false)
  const [emergencyOpen, setEmergencyOpen] = useState(false)
  const [emergencyShown, setEmergencyShown] = useState(false)

  const question = questions[index]
  const answer = answers[question.id] ?? ""

  const isLast = index === questions.length - 1
  const canNext = Boolean(question.optional || answer.trim())

  const updateAnswer = (value: string) => {
    setAnswers((prev) => ({
      ...prev,
      [question.id]: value,
    }))
  }

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

  const handleBack = () => {
    if (index > 0) {
      setIndex((prev) => prev - 1)
    } else {
      setStep("anamnesis")
    }
  }

  const selectQuestion = (nextIndex: number) => {
    setIndex(nextIndex)
    setSheetOpen(false)
  }

  const continueAfterEmergency = () => {
    setEmergencyOpen(false)
    goNext()
  }

  const resetFlow = () => {
    setStep("welcome")
    setIndex(0)
    setAnswers({})
    setPayment(null)
    setSheetOpen(false)
    setEmergencyOpen(false)
    setEmergencyShown(false)
  }

  return {
    step,
    setStep,

    index,
    question,
    answer,
    answers,
    updateAnswer,

    isLast,
    canNext,
    handleNext,
    handleBack,

    payment,
    setPayment,

    sheetOpen,
    setSheetOpen,
    selectQuestion,

    emergencyOpen,
    setEmergencyOpen,
    continueAfterEmergency,

    resetFlow,
  }
}

export type QuestionFlow = ReturnType<typeof useQuestionFlow>