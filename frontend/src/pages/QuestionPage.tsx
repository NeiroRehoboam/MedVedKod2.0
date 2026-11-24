import { useEffect, useRef } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { Button, Spinner } from "@maxhub/max-ui"

import {
  QuestionAnamnesis,
  QuestionFinish,
  QuestionPayment,
  QuestionWelcome,
  QuestionStep,
  QuestionHeader,
} from "@/components/common"

import { useQuestionFlow } from "@/hooks/useQuestionFlow"
import {
  useAiSession,
  useAiSessionResult,
  useStartAiSession,
  useInitialQuestion,
} from "@/hooks/useAiSessions"

import type { AiSessionResponse } from "@/api/generated/models"
import { ArrowUpRight } from "lucide-react"

export function QuestionPage() {
  const navigate = useNavigate()
  const { sessionId } = useParams<{ sessionId: string }>()

  const startSession = useStartAiSession()
  const sessionQuery = useAiSession(sessionId)
  const isCompleted = sessionQuery.data?.session.status === "COMPLETED"
  const resultQuery = useAiSessionResult(sessionId, isCompleted)
  const flow = useQuestionFlow(sessionId, isCompleted)

  const initialQuestionQuery = useInitialQuestion(
    sessionId,
    flow.step === "questions" && sessionQuery.isSuccess && !flow.isCompleted
  )

  const initialQuestionData = sessionQuery.isSuccess
    ? isCompleted
      ? resultQuery.data?.data
      : initialQuestionQuery.data?.data
    : undefined

  const { applyResponse, setStep } = flow
  const initializedSession = useRef<string | undefined>(undefined)

  useEffect(() => {
    if (
      initialQuestionData &&
      sessionId &&
      initializedSession.current !== sessionId
    ) {
      initializedSession.current = sessionId
      applyResponse(initialQuestionData)
      if (isCompleted) setStep("finished")
    }
  }, [initialQuestionData, sessionId, applyResponse, isCompleted, setStep])

  const isExistingSession = Boolean(sessionId)
  const createdSessionId = useRef<string | null>(null)
  const creatingSession = useRef(false)

  const goHome = () => navigate("/home")

  const handleExit = () => {
    flow.resetFlow()
    goHome()
  }

  const handleRestart = () => {
    createdSessionId.current = null
    creatingSession.current = false

    flow.resetFlow()

    navigate("/question", { replace: true })
  }

  const handleAnamnesisContinue = async () => {
    if (sessionId || createdSessionId.current) {
      flow.setStep("questions")
      return
    }

    if (creatingSession.current) return

    creatingSession.current = true

    try {
      const response = await startSession.mutateAsync()
      const data: AiSessionResponse = response.data

      if (data.session?.id == null) {
        throw new Error("Бэкенд не вернул ID сессии")
      }

      const id = String(data.session.id)

      createdSessionId.current = id

      navigate(`/question/${id}`, { replace: true })
      flow.setStep("questions")
    } catch (error) {
      console.error("Не удалось создать сессию:", error)
    } finally {
      creatingSession.current = false
    }
  }
  const step = isCompleted && flow.step !== "questions" ? "finished" : flow.step

  const renderStep = () => {
    switch (step) {
      case "welcome":
        return (
          <QuestionWelcome
            onHome={goHome}
            isExistingSession={isExistingSession}
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
        if (!flow.isCompleted && initialQuestionQuery.isError) {
          return (
            <p>
              Не удалось загрузить вопрос.{" "}
              <button
                type="button"
                onClick={() => void initialQuestionQuery.refetch()}
              >
                Попробовать снова
              </button>
            </p>
          )
        }

        if (!flow.question) {
          return (
            <div
              className="flex flex-1 items-center justify-center"
              role="status"
              aria-label="Загрузка вопроса"
            >
              <Spinner className="size-8" />
            </div>
          )
        }
        return (
          <>
            <QuestionStep flow={flow} />

            {isCompleted && (
              <Button
                type="button"
                variant="secondary"
                className="max-button-between mt-5 w-full shrink-0"
                onClick={() => flow.setStep("finished")}
                iconAfter={<ArrowUpRight size={20} />}
              >
                К результату
              </Button>
            )}
          </>
        )

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
        if (isCompleted && resultQuery.isPending) {
          return (
            <div
              className="flex flex-1 items-center justify-center"
              role="status"
              aria-label="Загрузка результата"
            >
              <Spinner className="size-8" />
            </div>
          )
        }

        if (isCompleted && resultQuery.isError) {
          return (
            <div role="alert" className="py-8 text-center">
              <p className="text-max-text-primary">
                Не удалось загрузить результат
              </p>
              <button
                type="button"
                onClick={() => void resultQuery.refetch()}
                className="mt-4 text-max-text-secondary underline"
              >
                Попробовать снова
              </button>
            </div>
          )
        }

        return (
          <QuestionFinish
            result={isCompleted ? resultQuery.data?.data : flow.response}
            payment={flow.payment ?? undefined}
            onRestart={handleRestart}
            onViewAnswers={
              isCompleted && flow.questions.length > 0
                ? () => flow.setStep("questions")
                : undefined
            }
          />
        )
    }
  }

  if (isExistingSession && sessionQuery.isPending) {
    return (
      <main className="mx-auto max-w-3xl px-5 py-12">
        <p className="text-max-text-secondary">Загружаем обращение...</p>
      </main>
    )
  }

  if (isExistingSession && sessionQuery.isError) {
    return (
      <main className="mx-auto max-w-3xl px-5 py-12">
        <p className="text-max-text-primary">Не удалось загрузить обращение</p>

        <button
          type="button"
          onClick={() => void sessionQuery.refetch()}
          className="mt-4 text-max-text-secondary underline"
        >
          Попробовать снова
        </button>
      </main>
    )
  }

  return (
    <main className="mx-auto flex min-h-dvh max-w-3xl flex-col px-5 pt-6 pb-[max(24px,env(safe-area-inset-bottom))] sm:px-8 sm:pt-8">
      {step !== "welcome" && step !== "finished" && (
        <QuestionHeader
          onExit={handleExit}
          questionIndex={flow.step === "questions" ? flow.index : undefined}
          totalQuestions={
            flow.step === "questions" ? flow.questions.length : undefined
          }
        />
      )}

      <div className="flex min-h-0 flex-1 flex-col">{renderStep()}</div>
    </main>
  )
}
