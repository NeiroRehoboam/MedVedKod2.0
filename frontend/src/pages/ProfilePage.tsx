import { AnamnesisForm } from "@/components/common"
import { Typography } from "@maxhub/max-ui"

export function ProfilePage() {
  return (
    <div className="relative">
      <div className="relative mx-auto max-w-3xl px-6">
        <Typography.Title
          variant="large-strong"
          className="font-unbounded! text-4xl!"
        >
          Профиль
        </Typography.Title>

        <p className="mt-4">
          <Typography.Text variant="body" color="secondary">
            Расскажите о своём здоровье, чтобы МедВед мог учитывать ваши
            особенности при обращениях.
          </Typography.Text>
        </p>

        <section className="mt-10">
          <Typography.Title
            variant="large-strong"
            className="font-unbounded! text-2xl!"
          >
            Анамнез
          </Typography.Title>
          <p className="mt-4">
            <Typography.Text variant="body" color="secondary">
              Все поля необязательны.
            </Typography.Text>
          </p>
          <AnamnesisForm />
        </section>
      </div>
    </div>
  )
}
