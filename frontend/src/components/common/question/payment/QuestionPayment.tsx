import { useEffect } from "react"
import { Button, Radio } from "@maxhub/max-ui"
import { ArrowLeft, ArrowRight } from "lucide-react"

import { paymentOptions, type PaymentType } from "@/data/payment.mock"
import { PageDescription, PageTitle } from "../../typography"

type QuestionPaymentProps = {
  value: PaymentType | null
  onChange: (value: PaymentType) => void
  onContinue: () => void
  onBack: () => void
}

export function QuestionPayment({
  value,
  onChange,
  onContinue,
  onBack,
}: QuestionPaymentProps) {
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [])

  return (
    <section className="flex min-h-0 w-full flex-1 flex-col">
      <div className="mt-10 space-y-4">
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
            <label
              key={option.id}
              className={`flex w-full cursor-pointer items-center justify-between gap-4 rounded-max-medium px-5 py-4 text-left transition-colors ${
                selected
                  ? "bg-max-accent-neutral-fade-secondary"
                  : "bg-max-secondary"
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

              <div className="shrink-0">
                <Radio
                  name="payment"
                  aria-label={option.label}
                  checked={selected}
                  onChange={() => onChange(option.id)}
                />
              </div>
            </label>
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
    </section>
  )
}
