import type { AiSessionResponse, SessionResult } from "@/api/generated/models"
import { AlertCircle, AlertTriangle, ClipboardList } from "lucide-react"
import { useNavigate } from "react-router-dom"

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { type PaymentType } from "@/data/payment.mock"
import { Button } from "@maxhub/max-ui"
import { DoctorSignature, PageDescription, PageTitle } from "../../typography"

type Urgency = "emergency" | "urgent" | "planned" | "self_care" | "undetermined"

type QuestionFinishProps = {
  result?: AiSessionResponse | SessionResult
  payment?: PaymentType
  onRestart: () => void
  onViewAnswers?: () => void
}

const urgencyConfig = {
  undetermined: {
    label: "Не определена",
    description: "",
    className: "bg-max-tertiary text-max-text-primary",
    iconClassName: "text-max-text-primary",
  },
  emergency: {
    label: "Экстренно",
    description: "Необходима немедленная медицинская помощь.",
    className: "bg-red-100 text-red-950",
    iconClassName: "text-red-700",
  },
  urgent: {
    label: "В течение 24 ч.",
    description: "Обратитесь за медицинской помощью в ближайшие сутки.",
    className: "bg-orange-100 text-orange-950",
    iconClassName: "text-orange-700",
  },
  planned: {
    label: "Планово",
    description: "Запишитесь на консультацию в плановом порядке.",
    className: "bg-sky-100 text-sky-950",
    iconClassName: "text-sky-700",
  },
  self_care: {
    label: "Самопомощь",
    description: "Возможно наблюдение за состоянием дома.",
    className: "bg-emerald-100 text-emerald-950",
    iconClassName: "text-emerald-700",
  },
} satisfies Record<
  Urgency,
  {
    label: string
    description: string
    className: string
    iconClassName: string
  }
>

export function QuestionFinish({
  result: response,
  onRestart,
  onViewAnswers,
}: QuestionFinishProps) {
  const recommendation = response?.recommendation
  const isFallback = recommendation?.source === "fallback"
  const text = (key: string) =>
    typeof recommendation?.[key] === "string" ? recommendation[key] : ""
  const rawUrgency =
    response?.routing?.urgency ||
    text("urgency") ||
    response?.safety.urgency ||
    ""
  const normalized = rawUrgency.toLowerCase()
  const urgencyKey: Urgency =
    response?.safety.should_stop || normalized === "emergency"
      ? "emergency"
      : normalized === "urgent"
        ? "urgent"
        : normalized === "self_help" || normalized === "self_care"
          ? "self_care"
          : normalized === "planned"
            ? "planned"
            : "undetermined"
  const result = {
    urgency: urgencyKey,
    recommendation:
      response?.routing?.recommendations ||
      text("recommendation") ||
      response?.safety.recommended_action,
    specialistDescription: text("doctor"),
    place: text("place"),
    symptoms: Array.isArray(recommendation?.evidence)
      ? recommendation.evidence.filter(
          (item): item is string => typeof item === "string"
        )
      : [],
    reason:
      response?.routing?.justification ||
      text("justification") ||
      response?.safety.reason,
  }

  const isEmergency = result.urgency === "emergency"
  const showFallback = isFallback && !isEmergency

  const hasDetails = Boolean(
    result.specialistDescription || result.place || result.reason
  )

  const navigate = useNavigate()
  const urgency = urgencyConfig[result.urgency]

  return (
    <section className="mt-4 flex min-h-0 w-full flex-1 flex-col">
      {/* Заголовок */}
      <header className="relative mb-5 space-y-4">
        <div>
          <PageTitle>
            Ваш
            <br />
            результат
          </PageTitle>
          <DoctorSignature className="relative z-10 -mt-3 ml-25 -rotate-5 text-3xl">
            Берегите себя!
          </DoctorSignature>
        </div>

        <PageDescription>
          {showFallback
            ? "Не удалось сформировать индивидуальную рекомендацию."
            : "Мы собрали ваши ответы и подготовили предварительную рекомендацию."}
        </PageDescription>
      </header>

      <div className="space-y-3">
        {showFallback ? (
          <section className="flex flex-col items-center px-4 py-8 text-center">
            <PageTitle as="h4">
              Не удалось определить маршрут обращения
            </PageTitle>

            <div className="mt-3">
              <PageDescription>
                Для оценки вашего состояния рекомендуем обратиться к врачу.
              </PageDescription>
            </div>
          </section>
        ) : (
          <>
            {/* Срочность */}
            <section
              className={`flex items-start gap-3 rounded-max-medium p-4 shadow-sm ${urgency.className}`}
            >
              <AlertTriangle
                size={18}
                className={`mt-0.5 shrink-0 ${urgency.iconClassName}`}
              />

              <div className="flex min-w-0 flex-col gap-1">
                <p className="text-sm font-semibold">
                  Срочность обращения: {urgency.label}
                </p>

                {urgency.description && (
                  <p className="text-sm leading-5 opacity-80">
                    {urgency.description}
                  </p>
                )}

                {isEmergency && (
                  <a
                    href="tel:112"
                    className="mt-4 inline-flex items-center justify-center rounded-max-medium bg-red-800 px-5 py-3 text-sm font-semibold text-white"
                  >
                    Позвонить 112
                  </a>
                )}
              </div>
            </section>

            {/* Рекомендации */}
            {(result.recommendation || hasDetails) && (
              <section className="space-y-4 rounded-max-medium bg-max-card p-5">
                <PageTitle as="h4">Рекомендации</PageTitle>

                {result.recommendation && (
                  <PageDescription>{result.recommendation}</PageDescription>
                )}

                {hasDetails && (
                  <Accordion className="border-0">
                    {result.specialistDescription && (
                      <AccordionItem
                        value="specialist"
                        className="border-max-tertiary! bg-transparent! p-0 data-open:bg-transparent!"
                      >
                        <AccordionTrigger>Специалист</AccordionTrigger>

                        <AccordionContent>
                          {result.specialistDescription}
                        </AccordionContent>
                      </AccordionItem>
                    )}

                    {result.place && (
                      <AccordionItem
                        value="place"
                        className="border-max-tertiary! bg-transparent! p-0 data-open:bg-transparent!"
                      >
                        <AccordionTrigger>Место обращения</AccordionTrigger>

                        <AccordionContent>{result.place}</AccordionContent>
                      </AccordionItem>
                    )}

                    {result.reason && (
                      <AccordionItem
                        value="reason"
                        className="bg-transparent! data-open:bg-transparent!"
                      >
                        <AccordionTrigger>
                          Обоснование рекомендации
                        </AccordionTrigger>

                        <AccordionContent>{result.reason}</AccordionContent>
                      </AccordionItem>
                    )}
                  </Accordion>
                )}
              </section>
            )}
          </>
        )}
      </div>

      {/* Дисклеймер */}
      <div className="mt-3 flex items-start gap-3 rounded-max-medium bg-max-tertiary p-4">
        <AlertCircle
          size={18}
          className="mt-0.5 shrink-0 text-max-text-primary"
        />

        <p className="text-xs leading-5 text-max-text-primary">
          Рекомендации МедВедь носят информационный характер, не являются
          медицинским диагнозом и не заменяют консультацию врача. При ухудшении
          самочувствия обратитесь за медицинской помощью. При признаках угрозы
          жизни немедленно вызовите скорую помощь.
        </p>
      </div>

      {/* Действия */}
      <div className="mt-6 flex flex-col gap-2 sm:flex-row">
        <Button
          type="button"
          size="large"
          variant="primary"
          stretched
          onClick={() => navigate("/home")}
        >
          На главную
        </Button>
        <Button
          type="button"
          size="large"
          variant="secondary"
          stretched
          onClick={onRestart}
        >
          Новое обращение
        </Button>
        {onViewAnswers && (
          <Button
            type="button"
            size="large"
            variant="secondary"
            stretched
            onClick={onViewAnswers}
          >
            Мои ответы
          </Button>
        )}
      </div>
    </section>
  )
}
