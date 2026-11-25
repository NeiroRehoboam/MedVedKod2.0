import { useEffect } from "react"

import { PaymentPreference } from "../../profile/PaymentPreference"
import { PageDescription, PageTitle } from "../../typography"

type QuestionPaymentProps = {
  isPending: boolean
  error: string | null
  onContinue: (id: number) => void
  onBack: () => void
}

export function QuestionPayment({
  isPending,
  error,
  onContinue,
  onBack,
}: QuestionPaymentProps) {
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [])

  return (
    <section className="flex min-h-0 w-full flex-1 flex-col">
      <div className="mt-10 space-y-4">
        <PageTitle as="h3">
          Как вам удобнее обратиться к врачу?
        </PageTitle>

        <PageDescription>
          Выберите приоритетный тип оплаты. Учтём его в маршруте обращения.
        </PageDescription>
      </div>

      <PaymentPreference
        isPending={isPending}
        onSaved={onContinue}
        onBack={onBack}
      />
      {error && <p role="alert">{error}</p>}
    </section>
  )
}
