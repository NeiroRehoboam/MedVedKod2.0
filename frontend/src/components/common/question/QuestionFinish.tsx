import { AlertCircle, AlertTriangle } from "lucide-react"
import { useNavigate } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { paymentOptions, type PaymentType } from "@/data/payment.mock"

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

export function QuestionFinish({
  result = demoResult,
  payment,
}: QuestionFinishProps) {
  const navigate = useNavigate()
  const urgency = urgencyConfig[result.urgency]
  const paymentOption = paymentOptions.find((option) => option.id === payment)

  return (
    <main className="min-h-dvh bg-muted">
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

          <p className="mt-2 max-w-md leading-6 text-muted-foreground">
            Мы собрали ваши ответы и подготовили предварительную рекомендацию.
          </p>
        </header>

        <div className="space-y-3">
          {/* Срочность */}
          <Alert
            className="rounded-3xl"
            variant={result.urgency == "emergency" ? "destructive" : "default"}
          >
            <AlertTriangle />
            <AlertTitle>
              Срочность обращения:{" "}
              <span className="font-semibold">{urgency.label}</span>
            </AlertTitle>
            <AlertDescription>{urgency.description}</AlertDescription>
          </Alert>

          <Card className="w-full rounded-3xl border ring-0">
            <CardHeader>
              <CardTitle className="font-unbounded text-lg">
                Рекомендации
              </CardTitle>
              <CardDescription className="text-[14px] text-foreground">
                {result.recommendation}
                {paymentOption && result.urgency !== "emergency" && (
                  <span className="mt-3 block">
                    {paymentOption.label}: {paymentOption.route}
                  </span>
                )}
              </CardDescription>
            </CardHeader>
            <CardContent>
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
                        <Badge key={`${symptom}-${index}`}>{symptom}</Badge>
                      ))}
                    </div>

                    <p>{result.reason}</p>
                  </AccordionContent>
                </AccordionItem>
              </Accordion>
            </CardContent>
          </Card>
        </div>

        {/* Дисклеймер */}
        <div className="mt-3 flex items-start gap-3 rounded-3xl bg-sky-100 p-4 shadow-2xs">
          <AlertCircle className="mt-0.5 size-4 shrink-0 text-sky-700" />

          <p className="text-xs leading-5 text-sky-900/80">
            Рекомендации МедВед носят информационный характер, не являются
            медицинским диагнозом и не заменяют консультацию врача. При
            ухудшении самочувствия обратитесь за медицинской помощью. При
            признаках угрозы жизни немедленно вызовите скорую помощь.
          </p>
        </div>

        {/* Действия */}
        <div className="mt-6 flex flex-col gap-1 sm:flex-row">
          <Button
            type="button"
            onClick={() => navigate("/home")}
            className={"h-12"}
          >
            На главную
          </Button>

          <Button
            type="button"
            variant="outline"
            onClick={() => navigate("/question")}
            className={"h-12"}
          >
            Новое обращение
          </Button>
        </div>
      </div>
    </main>
  )
}
