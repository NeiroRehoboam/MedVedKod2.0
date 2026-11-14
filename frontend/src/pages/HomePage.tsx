import { ArrowUpRight } from "lucide-react"
import { useNavigate } from "react-router-dom"
import {
  Button,
  CellSimple,
  IconButton,
  StatusBadge,
  Typography,
} from "@maxhub/max-ui"

import shape from "@/assets/shapes/shape-1.svg"
import { mockAppeals } from "@/data/appeals.mock"

export function HomePage() {
  const navigate = useNavigate()

  const handleNewAppeal = () => {
    navigate("/question")
  }

  return (
    <main className="mx-auto w-full max-w-3xl px-5 pt-3 sm:px-8">
      {/* Главное действие */}
      <div className="relative isolate">
        <section className="relative z-0 rounded-max-medium bg-max-primary p-6 sm:p-8">
          <div>
            <div>
              <Typography.Title
                variant="large-strong"
                className="font-unbounded! text-3xl!"
              >
                Что вас
                <br />
                беспокоит?
              </Typography.Title>
            </div>

            <div className="mt-4 max-w-sm leading-6">
              <Typography.Text variant="body" color="secondary">
                Расскажите о самочувствии. МедВед задаст несколько вопросов и
                поможет подготовиться к обращению к врачу.
              </Typography.Text>
            </div>

            <div className="mt-8">
              <Button
                size="medium"
                variant="primary"
                iconAfter={<ArrowUpRight size={20} />}
                onClick={handleNewAppeal}
              >
                Начать разговор
              </Button>
            </div>
          </div>
        </section>

        {/* Фигура поверх карточки */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -right-3 -bottom-9 z-10 size-30 rotate-[-16deg]"
        >
          <div
            className="absolute inset-0 bg-linear-to-br from-max-text-themed/10 via-max-text-themed/70 to-max-text-themed"
            style={{
              maskImage: `url("${shape}")`,
              WebkitMaskImage: `url("${shape}")`,
              maskSize: "contain",
              WebkitMaskSize: "contain",
              maskRepeat: "no-repeat",
              WebkitMaskRepeat: "no-repeat",
              maskPosition: "center",
              WebkitMaskPosition: "center",
            }}
          />
        </div>
      </div>

      {/* История обращений */}
      <section aria-labelledby="appeals-heading" className="mt-10">
        <div id="appeals-heading" className="mb-5">
          <Typography.Title
            variant="medium-strong"
            className="font-unbounded! text-xl!"
          >
            Мои обращения
          </Typography.Title>
        </div>

        {mockAppeals.length > 0 ? (
          <div className="flex flex-col gap-2.5">
            {mockAppeals.map((appeal) => {
              const isActive = appeal.status === "in_progress"

              return (
                <div key={appeal.id} className="rounded-max-medium bg-max-primary p-2">
                  <CellSimple
                    title={
                      <div className="flex flex-wrap items-center gap-2">
                        <span>{appeal.title}</span>

                        {isActive && (
                          <StatusBadge status="neutral" text="В процессе" />
                        )}
                      </div>
                    }
                    subtitle={appeal.date}
                    subtitleMode="secondary"
                    height="normal"
                    surface="default"
                    separator={false}
                    showChevron={false}
                    after={
                      <IconButton
                        aria-label={`Открыть обращение: ${appeal.title}`}
                        disabled={false}
                        loading={false}
                        size="small"
                        variant="secondary-contrast"
                        onClick={() => navigate("/question")}
                      >
                        <ArrowUpRight size={18} strokeWidth={1.8} />
                      </IconButton>
                    }
                  />
                </div>
              )
            })}
          </div>
        ) : (
          <div className="flex flex-col items-center rounded-max-medium bg-max-secondary px-6 py-12 text-center">
            <Typography.Title variant="large-strong" className="text-lg!">
              Обращений пока нет
            </Typography.Title>

            <div className="mt-3 max-w-xs leading-6">
              <Typography.Text variant="body" color="secondary">
                Здесь будет храниться история ваших обращений. Расскажите, что
                вас беспокоит, чтобы начать первый диалог.
              </Typography.Text>
            </div>

            <div className="mt-6">
              <Button
                variant="secondary"
                size="medium"
                onClick={handleNewAppeal}
              >
                Создать обращение
              </Button>
            </div>
          </div>
        )}
      </section>
    </main>
  )
}
