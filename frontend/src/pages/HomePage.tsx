import { ArrowUpRight, Inbox } from "lucide-react"
import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import shape from "@/assets/shapes/shape-1.svg"
import { Badge } from "@/components/ui/badge"
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty"
import { mockAppeals } from "@/data/appeals.mock"

export function HomePage() {
  return (
    <div className="mx-auto w-full max-w-3xl overflow-x-clip px-6">
      {/* Главное действие */}
      <section className="relative isolate rounded-3xl border bg-background p-6 shadow-xl shadow-neutral-200/40 sm:p-8">
        {/* Декоративная фигура */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -right-3 -bottom-9 z-20 size-28 rotate-[-16deg]"
        >
          <div
            className="absolute inset-0 bg-linear-to-br from-sky-300 via-sky-600 to-sky-700"
            style={{
              maskImage: `url("${shape}")`,
              WebkitMaskImage: `url("${shape}")`,
              maskSize: "contain",
              WebkitMaskSize: "contain",
              maskRepeat: "no-repeat",
              WebkitMaskRepeat: "no-repeat",
              maskPosition: "center",
              WebkitMaskPosition: "center",
              filter: "drop-shadow(0 12px 20px rgba(14,165,233,0.2))",
            }}
          />
        </div>

        <div className="relative z-10">
          <h2 className="max-w-md font-unbounded text-2xl leading-[1.2] font-semibold tracking-[-0.045em] text-foreground">
            Что вас
            <br />
            беспокоит?
          </h2>

          <p className="mt-4 max-w-sm text-sm leading-6 text-muted-foreground">
            Расскажите о самочувствии. МедВед задаст несколько вопросов и
            поможет подготовиться к обращению к врачу.
          </p>

          <div className="mt-7 flex flex-wrap items-end justify-between gap-4">
            <Button className="h-12 px-5 font-medium">
              <Link to="/question">Начать разговор</Link> <ArrowUpRight />
            </Button>
          </div>
        </div>
      </section>
      <section className="mt-10">
        <div className="mb-6 flex items-center justify-between gap-2">
          <h2 className="max-w-md font-unbounded text-2xl leading-[1.2] font-semibold tracking-[-0.045em] text-foreground">
            Мои обращения
          </h2>
        </div>
        <div className="flex flex-col gap-2">
          {mockAppeals.length > 0 ? (
            mockAppeals.map((item, index) => (
              <div
                className="flex items-center justify-between gap-3 rounded-3xl border bg-background px-5 py-3 shadow-xs shadow-neutral-200/20"
                key={index}
              >
                <div className="flex flex-col gap-3">
                  <p className="font-semibold">
                    {item.title}
                    {item.status == "in_progress" && (
                      <Badge variant={"secondary"} className="ml-2">
                        В процессе
                      </Badge>
                    )}
                  </p>
                  <p className="text-sm text-muted-foreground">{item.date}</p>
                </div>
                <Button variant={"outline"} size={"icon-lg"}>
                  <Link to="/question">
                    <ArrowUpRight />
                  </Link>
                </Button>
              </div>
            ))
          ) : (
            <Empty>
              <EmptyHeader>
                <EmptyMedia variant="icon">
                  <Inbox />
                </EmptyMedia>

                <EmptyTitle>Обращений пока нет</EmptyTitle>

                <EmptyDescription className="w-sm">
                  Здесь будет храниться история ваших обращений. Расскажите, что
                  вас беспокоит, чтобы начать первый диалог.
                </EmptyDescription>
              </EmptyHeader>

              <EmptyContent className="flex-row justify-center gap-2">
                <Button render={<Link to="/question" />} variant={"outline"}>
                  Создать обращение
                </Button>
              </EmptyContent>
            </Empty>
          )}
        </div>
      </section>
    </div>
  )
}
