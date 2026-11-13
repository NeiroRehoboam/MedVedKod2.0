import { useEffect } from "react"
import { Button } from "@/components/ui/button"
import { paymentOptions, type PaymentType } from "@/data/payment.mock"
import { QuestionHeader } from "./QuestionHeader"
import {
  Field,
  FieldContent,
  FieldDescription,
  FieldLabel,
  FieldTitle,
} from "@/components/ui/field"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { ArrowLeft, ArrowRight } from "lucide-react"

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
    <main className="min-h-dvh bg-muted">
      <div className="mx-auto max-w-3xl px-5 py-6 sm:px-8">
        <QuestionHeader onHome={onHome} />
        <h1 className="mt-12 font-unbounded text-2xl leading-snug font-medium">
          Как вам удобнее обратиться к врачу?
        </h1>
        <p className="mt-4 leading-6 text-muted-foreground">
          Выберите приоритетный тип оплаты. Учтём его в маршруте обращения.
        </p>
        <RadioGroup
          value={value}
          onValueChange={(nextValue) => {
            if (nextValue) onChange(nextValue)
          }}
          aria-label="Приоритетный тип оплаты"
          className="my-8"
        >
          {paymentOptions.map((option) => (
            <FieldLabel key={option.id} htmlFor={`payment-${option.id}`}>
              <Field orientation="horizontal">
                <FieldContent>
                  <FieldTitle>{option.label}</FieldTitle>
                  <FieldDescription id={`payment-${option.id}-description`}>
                    {option.description}
                  </FieldDescription>
                </FieldContent>
                <RadioGroupItem
                  value={option.id}
                  id={`payment-${option.id}`}
                  aria-describedby={`payment-${option.id}-description`}
                />
              </Field>
            </FieldLabel>
          ))}
        </RadioGroup>
        <div className="flex gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={onBack}
            className="h-14 px-5"
          >
            <ArrowLeft className="size-4" />
            Назад
          </Button>
          <Button
            disabled={!value}
            onClick={onContinue}
            className="h-14 flex-1 justify-between rounded-full px-6"
          >
            Завершить
            <ArrowRight size={20} />
          </Button>
        </div>
      </div>
    </main>
  )
}
