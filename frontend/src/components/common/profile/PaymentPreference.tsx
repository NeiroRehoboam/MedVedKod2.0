import { useState } from "react"
import { Button, Radio, Spinner, useSnackbar } from "@maxhub/max-ui"
import { useQueryClient } from "@tanstack/react-query"
import { useDictionariesPaymentTypesList } from "@/api/generated/dictionaries/dictionaries"
import {
  getPatientsPatientsListQueryKey,
  getPatientsPatientsRetrieveQueryKey,
  usePatientsPatientsList,
  usePatientsPatientsMePreferredPaymentPartialUpdate,
} from "@/api/generated/patients/patients"

export function PaymentPreference({
  onSaved,
}: {
  onSaved?: (id: number) => void
}) {
  const payments = useDictionariesPaymentTypesList({
    query: {
      staleTime: 30 * 60 * 1000,
      gcTime: 60 * 60 * 1000,
    },
  })
  const patient = usePatientsPatientsList({
    query: { staleTime: 60 * 1000 },
  })
  const current = patient.data?.data[0]
  const [selected, setSelected] = useState<number>()
  const value = selected ?? current?.preferred_payment
  const queryClient = useQueryClient()
  const { showSnackbar } = useSnackbar()
  const save = usePatientsPatientsMePreferredPaymentPartialUpdate({
    mutation: {
      onSuccess: (response) => {
        queryClient.setQueryData(
          getPatientsPatientsListQueryKey(),
          (old: typeof patient.data) =>
            old
              ? {
                  ...old,
                  data: old.data.map((item) =>
                    item.id === response.data.id ? response.data : item
                  ),
                }
              : old
        )
        queryClient.setQueryData(
          getPatientsPatientsRetrieveQueryKey(String(response.data.id)),
          response
        )
        showSnackbar({
          text: "Способ оплаты сохранён",
          caption: "Ваши данные успешно сохранены",
          duration: 3000,
          placement: "top-center",
          offset: 16,
        })
        onSaved?.(response.data.preferred_payment!)
      },
    },
  })

  if (payments.isPending || patient.isPending)
    return <Spinner aria-label="Загрузка способов оплаты" />
  if (payments.isError || patient.isError)
    return (
      <div role="alert" className="my-8 space-y-4">
        <p>Не удалось загрузить способы оплаты.</p>
        <Button
          onClick={() => {
            void payments.refetch()
            void patient.refetch()
          }}
        >
          Попробовать снова
        </Button>
      </div>
    )
  const options = payments.data.data
  const available = options.some((option) => option.id === value)

  return (
    <div>
      <div
        role="radiogroup"
        aria-label="Приоритетный тип оплаты"
        className="my-8 flex flex-col gap-3"
      >
        {options.map((option) => (
          <label
            key={option.id}
            className={`flex w-full cursor-pointer items-center justify-between gap-4 rounded-max-medium px-5 py-4 text-left transition-colors ${value === option.id ? "bg-max-accent-neutral-fade-secondary" : "bg-max-secondary"}`}
          >
            <span className="text-base font-medium text-max-text-primary">
              {option.name}
            </span>
            <Radio
              name="payment"
              aria-label={option.name}
              checked={value === option.id}
              disabled={save.isPending}
              onChange={() => {
                setSelected(option.id)
                save.reset()
              }}
            />
          </label>
        ))}
      </div>
      {!options.length && <p role="status">Нет доступных способов оплаты.</p>}
      {!current && <p role="alert">Профиль пациента не найден.</p>}
      {save.isError && (
        <p role="alert" className="mb-4 text-max-text-secondary">
          Не удалось сохранить способ оплаты. Попробуйте снова.
        </p>
      )}
      <Button
        type="button"
        size="large"
        variant="primary"
        stretched
        disabled={!current || !available || save.isPending}
        onClick={() => {
          if (onSaved && value != null && value === current?.preferred_payment)
            onSaved(value)
          else if (value != null)
            save.mutate({ data: { preferred_payment: value } })
        }}
      >
        {save.isPending ? "Сохранение…" : onSaved ? "Завершить" : "Сохранить"}
      </Button>
    </div>
  )
}
