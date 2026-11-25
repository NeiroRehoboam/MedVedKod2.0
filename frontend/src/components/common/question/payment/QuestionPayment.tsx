import { useEffect } from "react"
import { Button } from "@maxhub/max-ui"
import { ArrowLeft } from "lucide-react"

import { PaymentPreference } from "../../profile/PaymentPreference"
import { PageDescription, PageTitle } from "../../typography"

type QuestionPaymentProps = {
  onContinue: (id: number) => void
  onBack: () => void
}

export function QuestionPayment({ onContinue, onBack }: QuestionPaymentProps) {
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

      <PaymentPreference onSaved={onContinue} />

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
      </div>
    </section>
  )
}
