import { AlertCircle, AlertTriangle } from "lucide-react"
import { useNavigate } from "react-router-dom"

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { type PaymentType } from "@/data/payment.mock"
import { Button, Typography } from "@maxhub/max-ui"

export type Urgency = "emergency" | "urgent" | "planned" | "self_care"

export type TriageResult = {
  specialist: string
  specialistDescription: string
  urgency: Urgency
  place: string
  recommendation: string
  symptoms: string[]
  reason: string
}

type QuestionFinishProps = {
  result?: TriageResult
  payment?: PaymentType
}

const urgencyConfig = {
  emergency: {
    label: "Экстренно",
    description: "Необходима немедленная медицинская помощь.",
    className: "border-red-200 bg-red-50 text-red-950",
    iconClassName: "text-red-600",
  },
  urgent: {
    label: "В течение 24 часов",
    description: "Обратитесь за медицинской помощью в ближайшие сутки.",
    className: "border-orange-200 bg-orange-50 text-orange-950",
    iconClassName: "text-orange-600",
  },
  planned: {
    label: "Планово",
    description: "Запишитесь на консультацию в плановом порядке.",
    className: "border-sky-200 bg-sky-50 text-sky-950",
    iconClassName: "text-sky-600",
  },
  self_care: {
    label: "Самопомощь",
    description: "Возможно наблюдение за состоянием дома.",
    className: "border-emerald-200 bg-emerald-50 text-emerald-950",
    iconClassName: "text-emerald-600",
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

const demoResult: TriageResult = {
  specialist: "Терапевт",
  specialistDescription:
    "Врач общей практики оценит ваше состояние и при необходимости направит к профильному специалисту.",
  urgency: "planned",
  place: "Поликлиника",
  recommendation:
    "Запишитесь на консультацию к терапевту для оценки симптомов и определения дальнейших действий.",
  symptoms: [
    "Головная боль",
    "Периодические симптомы",
    "Продолжительность — несколько дней",
  ],
  reason:
    "Это демонстрационный пример оформления результата. Реальная срочность и маршрут обращения должны определяться на основании ответов пациента и проверенных правил маршрутизации.",
}

export function QuestionFinish({ result = demoResult }: QuestionFinishProps) {
  const navigate = useNavigate()
  const urgency = urgencyConfig[result.urgency]

  return (
    <main className="min-h-dvh bg-max-surface">
      <div className="mx-auto w-full max-w-3xl px-5 pt-12 pb-12">
        {/* Заголовок */}
        <header className="mb-5">
          <div className="relative w-fit pb-3">
            <h1 className="font-unbounded text-[clamp(2.25rem,8vw,3.5rem)] leading-[1.12] font-medium tracking-[-0.06em]">
              Ваш
              <br />
              результат
            </h1>

            <p className="relative z-10 -mt-3 ml-20 w-fit -rotate-5 font-doctor text-3xl leading-none text-sky-600 sm:ml-30">
              Берегите себя!
            </p>
          </div>

          <Typography.Text variant="body" color="secondary">
            Мы собрали ваши ответы и подготовили предварительную рекомендацию.
          </Typography.Text>
        </header>

        <div className="space-y-3">
          {/* Срочность */}
          <section
            className={`flex items-start gap-3 rounded-max-medium p-4 ${urgency.className}`}
          >
            <AlertTriangle
              size={20}
              className={`mt-0.5 shrink-0 ${urgency.iconClassName}`}
            />

            <div className="flex min-w-0 flex-col gap-1">
              <p className="text-sm font-semibold">
                Срочность обращения: {urgency.label}
              </p>

              <p className="text-sm leading-5 opacity-80">
                {urgency.description}
              </p>

              {result.urgency === "emergency" && (
                <a
                  href="tel:112"
                  className="rounded-max-button-small mt-4 inline-flex items-center justify-center bg-red-800 px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-red-900"
                >
                  Позвонить 112
                </a>
              )}
            </div>
          </section>

          <section className="rounded-max-medium bg-max-card p-5">
            <Typography.Title className="font-unbounded! text-lg!">
              Рекомендации
            </Typography.Title>

            <p className="my-4">
              <Typography.Text variant="body" color="secondary">
                {result.recommendation}
              </Typography.Text>
            </p>
            <Accordion defaultValue={["plans"]} className={"border-0"}>
              <AccordionItem value="recommendation">
                <AccordionTrigger>О специалисте</AccordionTrigger>

                <AccordionContent>
                  {result.specialistDescription}
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="placen">
                <AccordionTrigger>Место обращения</AccordionTrigger>

                <AccordionContent>{result.place}</AccordionContent>
              </AccordionItem>
              <AccordionItem value="symptoms">
                <AccordionTrigger>Учтённые симптомы</AccordionTrigger>

                <AccordionContent>
                  <div className="mb-4 flex flex-wrap gap-2">
                    {result.symptoms.map((symptom, index) => (
                      <span
                        key={`${symptom}-${index}`}
                        className="inline-flex items-center rounded-max-medium bg-max-tertiary px-3 py-1.5 text-xs leading-4 font-medium text-max-text-secondary"
                      >
                        {symptom}
                      </span>
                    ))}
                  </div>
                  <p>{result.reason}</p>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </section>
        </div>

        {/* Дисклеймер */}
        <div className="mt-3 flex items-start gap-3 rounded-max-medium bg-sky-200/80 p-4">
          <AlertCircle size={18} className="mt-0.5 shrink-0 text-sky-800" />

          <p className="text-xs leading-5 text-sky-900">
            Рекомендации МедВед носят информационный характер, не являются
            медицинским диагнозом и не заменяют консультацию врача. При
            ухудшении самочувствия обратитесь за медицинской помощью. При
            признаках угрозы жизни немедленно вызовите скорую помощь.
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
            onClick={() => navigate("/question")}
          >
            Новое обращение
          </Button>
        </div>
      </div>
    </main>
  )
}
