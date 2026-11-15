import {
  AnamnesisForm,
  PageDescription,
  PageTitle,
  ProfileActions,
} from "@/components/common"

export function ProfilePage() {
  return (
    <div className="relative">
      <div className="space-y-4">
        <PageTitle as="h1">Профиль</PageTitle>

        <PageDescription>
          Расскажите о своём здоровье, чтобы МедВед мог учитывать ваши
          особенности при обращениях.
        </PageDescription>
      </div>

      <section className="mt-10">
        <div className="space-y-4">
          <PageTitle as="h2">Анамнез</PageTitle>
          <PageDescription>Все поля необязательны.</PageDescription>
        </div>

        <AnamnesisForm>
          <ProfileActions />
        </AnamnesisForm>
      </section>
    </div>
  )
}
