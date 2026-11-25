import { useState } from "react"
import { Segmented } from "@maxhub/max-ui"
import { PaymentPreference } from "@/components/common/profile/PaymentPreference"
import {
  AnamnesisForm,
  PageDescription,
  PageTitle,
  ProfileActions,
} from "@/components/common"

export function ProfilePage() {
  const [tab, setTab] = useState("anamnesis")
  return (
    <div className="relative">
      <div className="space-y-4">
        <PageTitle as="h1">Профиль</PageTitle>

        <PageDescription>
          Расскажите о своём здоровье, чтобы МедВедь мог учитывать ваши
          особенности при обращениях.
        </PageDescription>
      </div>

      <div className="mt-8 max-w-lg">
        <Segmented
          activeItem={tab}
          items={[
            { id: "anamnesis", title: "Анамнез" },
            { id: "payment", title: "Оплата" },
          ]}
          onClick={setTab}
        />
      </div>

      <section className="mt-10" hidden={tab !== "anamnesis"}>
        <div className="space-y-4">
          <PageTitle as="h2">Анамнез</PageTitle>
          <PageDescription>Все поля необязательны.</PageDescription>
        </div>

        <AnamnesisForm>
          <ProfileActions />
        </AnamnesisForm>
      </section>
      {tab === "payment" && (
        <section className="mt-10">
          <PageTitle as="h2">Оплата</PageTitle>
          <PageDescription>
            Выберите приоритетный тип оплаты. Учтём его в маршруте обращения.
          </PageDescription>
          <PaymentPreference />
        </section>
      )}
    </div>
  )
}
