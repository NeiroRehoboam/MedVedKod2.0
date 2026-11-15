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
import { DoctorSignature, PageDescription, PageTitle } from "../../typography"

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

const demoResult: TriageResult = {
  specialist: "Терапевт",
  specialistDescription:
    "Врач общей практики оценит ваше состояние и при необходимости направит к профильному специалисту.",
  urgency: "emergency",
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
    <main className="min-h-dvh">
      <div className="mx-auto w-full max-w-3xl px-5 pt-12 pb-12">
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
            Мы собрали ваши ответы и подготовили предварительную рекомендацию.
          </PageDescription>
        </header>

        <div className="space-y-3">
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

              <p className="text-sm leading-5 opacity-80">
                {urgency.description}
              </p>

              {result.urgency === "emergency" && (
                <a
                  href="tel:112"
                  className="mt-4 inline-flex items-center justify-center rounded-max-medium bg-red-800 px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-red-900"
                >
                  Позвонить 112
                </a>
              )}
            </div>
          </section>

          <section className="space-y-4 rounded-max-medium bg-max-card p-5">
            <PageTitle as="h4">Рекомендации</PageTitle>

            <PageDescription> {result.recommendation}</PageDescription>

            <Accordion defaultValue={["plans"]} className={"border-0"}>
              <AccordionItem
                value="recommendation"
                className="border-max-tertiary! bg-transparent! p-0 data-open:bg-transparent!"
              >
                <AccordionTrigger>О специалисте</AccordionTrigger>

                <AccordionContent>
                  {result.specialistDescription}
                </AccordionContent>
              </AccordionItem>
              <AccordionItem
                value="placen"
                className="border-max-tertiary! bg-transparent! p-0 data-open:bg-transparent!"
              >
                <AccordionTrigger>Место обращения</AccordionTrigger>

                <AccordionContent>{result.place}</AccordionContent>
              </AccordionItem>
              <AccordionItem
                value="symptoms"
                className="bg-transparent! data-open:bg-transparent!"
              >
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
        <div className="mt-3 flex items-start gap-3 rounded-max-medium bg-max-tertiary p-4">
          <AlertCircle
            size={18}
            className="mt-0.5 shrink-0 text-max-text-primary"
          />

          <p className="text-xs leading-5 text-max-text-primary">
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
