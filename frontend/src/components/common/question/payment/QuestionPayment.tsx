import { useEffect } from "react"
import { Button } from "@maxhub/max-ui"
import { ArrowLeft, ArrowRight, Check } from "lucide-react"

import { paymentOptions, type PaymentType } from "@/data/payment.mock"
import { QuestionHeader } from "../step/QuestionHeader"
import { PageDescription, PageTitle } from "../../typography"

type QuestionPaymentProps = {
  value: PaymentType | null
  onChange: (value: PaymentType) => void
  onContinue: () => void
  onBack: () => void
  onHome: () => void
}

export function QuestionPayment({
  value,
  onChange,
  onContinue,
  onBack,
  onHome,
}: QuestionPaymentProps) {
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [])

  return (
    <main className="min-h-dvh">
      <div className="mx-auto max-w-3xl px-5 py-6 sm:px-8">
        <QuestionHeader onHome={onHome} />

        <div className="mt-12 space-y-4">
          <PageTitle as="h3">Как вам удобнее обратиться к врачу?</PageTitle>

          <PageDescription>
            Выберите приоритетный тип оплаты. Учтём его в маршруте обращения.
          </PageDescription>
        </div>

        <div
          role="radiogroup"
          aria-label="Приоритетный тип оплаты"
          className="my-8 flex flex-col gap-3"
        >
          {paymentOptions.map((option) => {
            const selected = value === option.id

            return (
              <button
                key={option.id}
                type="button"
                role="radio"
                aria-checked={selected}
                onClick={() => onChange(option.id)}
                className={`flex w-full items-center justify-between gap-4 rounded-max-medium px-5 py-4 text-left transition-colors ${
                  selected
                    ? "bg-max-tertiary"
                    : "bg-max-secondary hover:bg-max-tertiary"
                }`}
              >
                <div className="flex min-w-0 flex-1 flex-col gap-1">
                  <span className="text-base font-medium text-max-text-primary">
                    {option.label}
                  </span>

                  <span className="text-sm leading-5 text-max-text-secondary">
                    {option.description}
                  </span>
                </div>

                <span
                  className={`flex size-5 shrink-0 items-center justify-center rounded-full border-2 transition-colors ${
                    selected
                      ? "border-max-text-primary bg-max-text-primary text-max-text-primary-inverse"
                      : "border-max-text-tertiary"
                  }`}
                >
                  {selected && (
                    <Check
                      size={14}
                      className="text-current"
                      strokeWidth={3}
                      aria-hidden="true"
                    />
                  )}
                </span>
              </button>
            )
          })}
        </div>

        <div className="flex gap-2">
          <Button
            type="button"
            size="large"
            variant="secondary"
            iconBefore={<ArrowLeft size={18} />}
            onClick={onBack}
          >
            Назад
          </Button>

          <Button
            type="button"
            size="large"
            variant="primary"
            className="max-button-between flex-1"
            disabled={!value}
            iconAfter={<ArrowRight size={20} />}
            onClick={onContinue}
          >
            Завершить
          </Button>
        </div>
      </div>
    </main>
  )
}
