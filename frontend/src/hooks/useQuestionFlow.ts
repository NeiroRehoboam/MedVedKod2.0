import { useCallback, useRef, useState } from "react"
import { useQueryClient } from "@tanstack/react-query"
import type { AiSessionResponse } from "@/api/generated/models"
import {
  useAiSessionsMessageCreate,
  useAiSessionsCompleteCreate,
  useAiSessionsQuestionsPartialUpdate,
  getAiSessionsListQueryKey,
  getAiSessionsRetrieveQueryKey,
  getAiSessionsInitialQuestionRetrieveQueryKey,
  getAiSessionsResultRetrieveQueryKey,
} from "@/api/generated/ai-sessions/ai-sessions"

export type QuestionStepType =
  | "welcome"
  | "anamnesis"
  | "questions"
  | "payment"
  | "finished"

export function useQuestionFlow(
  sessionId?: string,
  completedSession = false
) {
  const [response, setResponse] = useState<AiSessionResponse>()
  const queryClient = useQueryClient()
  const [step, setStep] = useState<QuestionStepType>("payment")
  const [index, setIndex] = useState(0)
  const [drafts, setDrafts] = useState<Record<number, string>>({})
  const [payment, setPayment] = useState<number | null>(null)
  const [sheetOpen, setSheetOpen] = useState(false)
  const [emergencyOpen, setEmergencyOpen] = useState(false)
  const [emergencyPending, setEmergencyPending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const busy = useRef(false)

  const sendMessage = useAiSessionsMessageCreate()
  const complete = useAiSessionsCompleteCreate()
  const updateAnswerMutation = useAiSessionsQuestionsPartialUpdate()

  const questions = response?.questions ?? []
  const question = questions[index]

  const answers = Object.fromEntries(
    questions.map((item) => [item.id, item.answer_text ?? ""])
  )

  const isCompleted =
    completedSession || response?.session.status === "COMPLETED"

  const answered = Boolean(question?.answer_text?.trim())

  const answer =
    isCompleted
      ? question?.answer_text ?? ""
      : drafts[question?.id] ?? question?.answer_text ?? ""

  const answerChanged = answered && answer.trim() !== question.answer_text?.trim()

  const stopped =
    emergencyPending ||
    (!isCompleted && response?.safety.should_stop === true)

  const isPending =
    sendMessage.isPending || complete.isPending || updateAnswerMutation.isPending

  const isLast =
    !isCompleted && Boolean(response && !response.next_question)

  const canNext =
    !stopped &&
    !isPending &&
    (isCompleted
      ? index < questions.length - 1
      : Boolean(question && answer.trim()))

  const applyResponse = useCallback(
    (data: AiSessionResponse, fromSubmission = false) => {
      setResponse(data)

      if (fromSubmission) {
        void queryClient.invalidateQueries({ queryKey: getAiSessionsListQueryKey() })
        // Активный экран уже получил актуальные данные из mutation.
        for (const queryKey of [
          getAiSessionsRetrieveQueryKey(String(data.session.id)),
          getAiSessionsInitialQuestionRetrieveQueryKey(data.session.id),
          getAiSessionsResultRetrieveQueryKey(data.session.id),
        ]) {
          void queryClient.invalidateQueries({ queryKey, refetchType: "none" })
        }
      }

      // Критический случай при прохождении текущего опроса.
      // Проверяем ДО обработки статуса COMPLETED.
      if (fromSubmission && data.safety.should_stop) {
        setIndex((prev) => Math.max(0, Math.min(prev, data.questions.length - 1)))
        setEmergencyPending(true)
        setEmergencyOpen(true)
        setSheetOpen(false)
        return
      }

      const nextIndex =
        data.session.status === "COMPLETED"
          ? 0
          : data.next_question
            ? data.questions.findIndex(
                (item) => item.id === data.next_question?.id
              )
            : data.questions.length - 1

      setIndex(Math.max(0, nextIndex))

      // Восстановление незавершённой критической сессии.
      if (
        data.session.status !== "COMPLETED" &&
        data.safety.should_stop
      ) {
        setEmergencyPending(true)
        setEmergencyOpen(true)
      }
    },
    [queryClient]
  )

  const handleNext = async () => {
    if (!canNext || busy.current || !sessionId) return

    // Просмотр завершённой сессии без запросов к API.
    if (isCompleted) {
      setIndex(index + 1)
      return
    }

    busy.current = true
    setError(null)

    try {
      let current = response

      if (!answered || answerChanged) {
        const result = answered
          ? await updateAnswerMutation.mutateAsync({
              sessionId: Number(sessionId),
              questionId: question.id,
              data: { answer_text: answer.trim() },
            })
          : await sendMessage.mutateAsync({
              sessionId: Number(sessionId),
              data: {
                content: answer.trim(),
                question_id: question.id,
              },
            })

        current = result.data

        setDrafts((prev) => {
          if (answerChanged) return {}
          const next = { ...prev }
          delete next[question.id]
          return next
        })
        applyResponse(current, true)
      }

      if (!current) return

      // При критическом состоянии ждём действия в модалке.
      if (current.safety.should_stop) return

      if (current.session.status === "COMPLETED") {
        setStep("payment")
        return
      }

      if (current.next_question) {
        setIndex(
          Math.max(
            0,
            current.questions.findIndex(
              (item) => item.id === current.next_question?.id
            )
          )
        )
        return
      }

      const result = await complete.mutateAsync({
        sessionId: Number(sessionId),
      })

      applyResponse(result.data, true)

      if (!result.data.safety.should_stop) {
        setStep("payment")
      }
    } catch {
      setError(
        answerChanged
          ? "Не удалось сохранить ответ. Попробуйте ещё раз."
          : "Не удалось отправить данные. Попробуйте ещё раз."
      )
    } finally {
      busy.current = false
    }
  }

  const selectQuestion = (nextIndex: number) => {
    if (busy.current || stopped || !questions[nextIndex]) return

    setIndex(nextIndex)
    setSheetOpen(false)
    setError(null)
  }

  const resetFlow = () => {
    setStep("welcome")
    setResponse(undefined)
    setIndex(0)
    setDrafts({})
    setPayment(null)
    setSheetOpen(false)
    setEmergencyOpen(false)
    setEmergencyPending(false)
    setError(null)
  }

  return {
    step,
    setStep,
    index,
    question,
    answer,
    answers,
    questions,

    updateAnswer: (value: string) => {
      if (
        !busy.current &&
        !isCompleted &&
        !stopped &&
        question
      ) {
        setDrafts((prev) => ({
          ...prev,
          [question.id]: value,
        }))
      }
    },

    isCompleted,
    isLast,
    canNext,
    handleNext,

    handleBack: () => {
      if (busy.current || stopped) return

      if (index > 0) {
        selectQuestion(index - 1)
      } else if (!isCompleted) {
        setStep("anamnesis")
      }
    },

    payment,
    setPayment,
    sheetOpen,
    setSheetOpen,
    selectQuestion,

    emergencyOpen,
    setEmergencyOpen,
    emergencyPending,

    continueAfterEmergency: () => {
      setEmergencyOpen(false)
      setEmergencyPending(false)
      setStep("finished")
    },

    resetFlow,
    applyResponse,
    response,
    isPending,
    error,

    readOnly:
      isCompleted || stopped || isPending,
  }
}

export type QuestionFlow = ReturnType<typeof useQuestionFlow>
