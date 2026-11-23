import { useCallback, useRef, useState } from "react"
import type { PaymentType } from "@/data/payment.mock"
import type { AiSessionResponse } from "@/api/generated/models"
import { useAiSessionsMessageCreate, useAiSessionsCompleteCreate } from "@/api/generated/ai-sessions/ai-sessions"

export type QuestionStepType = "welcome" | "anamnesis" | "questions" | "payment" | "finished"

export function useQuestionFlow(sessionId?: string) {
  const [response, setResponse] = useState<AiSessionResponse>()
  const [step, setStep] = useState<QuestionStepType>("welcome")
  const [index, setIndex] = useState(0)
  const [drafts, setDrafts] = useState<Record<number, string>>({})
  const [payment, setPayment] = useState<PaymentType | null>(null)
  const [sheetOpen, setSheetOpen] = useState(false)
  const [emergencyOpen, setEmergencyOpen] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const busy = useRef(false)
  const sendMessage = useAiSessionsMessageCreate()
  const complete = useAiSessionsCompleteCreate()
  const questions = response?.questions ?? []
  const question = questions[index]
  const answers = Object.fromEntries(questions.map((item) => [item.id, item.answer_text ?? ""]))
  const answered = Boolean(question?.answer_text?.trim())
  const answer = answered ? question.answer_text ?? "" : drafts[question?.id] ?? ""
  const stopped = response?.safety.should_stop === true
  const isPending = sendMessage.isPending || complete.isPending
  const isLast = Boolean(response && !response.next_question)
  const canNext = !stopped && !isPending && Boolean(question && answer.trim())

  const applyResponse = useCallback((data: AiSessionResponse) => {
    setResponse(data)
    const nextIndex = data.next_question
      ? data.questions.findIndex((item) => item.id === data.next_question?.id)
      : data.questions.length - 1
    setIndex(Math.max(0, nextIndex))
    if (data.safety.should_stop) setEmergencyOpen(true)
  }, [])

  const handleNext = async () => {
    if (!canNext || busy.current || !sessionId) return
    busy.current = true
    setError(null)
    try {
      let current = response
      if (!answered) {
        const result = await sendMessage.mutateAsync({
          sessionId: Number(sessionId),
          data: { content: answer.trim(), question_id: question.id },
        })
        current = result.data
        applyResponse(current)
      }
      if (!current || current.safety.should_stop) return
      if (current.next_question) {
        setIndex(Math.max(0, current.questions.findIndex((item) => item.id === current.next_question?.id)))
        return
      }
      const result = await complete.mutateAsync({ sessionId: Number(sessionId) })
      applyResponse(result.data)
      if (!result.data.safety.should_stop) setStep("payment")
    } catch {
      setError("Не удалось отправить данные. Попробуйте ещё раз.")
    } finally {
      busy.current = false
    }
  }

  const selectQuestion = (nextIndex: number) => {
    if (busy.current || stopped || !questions[nextIndex]) return
    setIndex(nextIndex)
    setSheetOpen(false)
  }

  const resetFlow = () => {
    setStep("welcome")
    setResponse(undefined)
    setIndex(0)
    setDrafts({})
    setPayment(null)
    setSheetOpen(false)
    setEmergencyOpen(false)
    setError(null)
  }

  return {
    step, setStep, index, question, answer, answers, questions,
    updateAnswer: (value: string) => {
      if (!busy.current && !stopped && !answered && question) {
        setDrafts((prev) => ({ ...prev, [question.id]: value }))
      }
    },
    isLast, canNext, handleNext,
    handleBack: () => {
      if (busy.current || stopped) return
      if (index > 0) selectQuestion(index - 1)
      else setStep("anamnesis")
    },
    payment, setPayment, sheetOpen, setSheetOpen, selectQuestion,
    emergencyOpen, setEmergencyOpen,
    continueAfterEmergency: () => {
      setEmergencyOpen(false)
      setStep("finished")
    },
    resetFlow, applyResponse, response, isPending, error,
    readOnly: answered || stopped || isPending,
  }
}

export type QuestionFlow = ReturnType<typeof useQuestionFlow>
