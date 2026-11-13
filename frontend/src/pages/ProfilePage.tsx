import { AnamnesisForm } from "@/components/common"

export function ProfilePage() {
  return (
    <div className="relative">
      <div className="relative mx-auto max-w-3xl px-6">
        <h1 className="font-unbounded text-4xl font-medium tracking-[-0.065em]">
          Профиль
        </h1>

        <p className="mt-4 max-w-lg leading-6 text-muted-foreground">
          Расскажите о своём здоровье, чтобы МедВед мог учитывать ваши
          особенности при обращениях.
        </p>

        <section className="mt-10">
          <h2 className="font-unbounded text-2xl font-medium tracking-[-0.045em]">
            Анамнез
          </h2>
          <p className="mt-2 text-muted-foreground">Все поля необязательны.</p>

          <AnamnesisForm />
        </section>
      </div>
    </div>
  )
}
