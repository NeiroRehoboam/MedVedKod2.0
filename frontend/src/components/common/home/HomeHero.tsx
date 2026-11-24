import { ArrowUpRight } from "lucide-react"
import { Button } from "@maxhub/max-ui"
import shape from "@/assets/shapes/shape-1.svg"
import { PageDescription, PageTitle } from "../typography"

type HomeHeroProps = {
  onNewAppeal: () => void
}

export function HomeHero({ onNewAppeal }: HomeHeroProps) {
  return (
    <div className="relative isolate">
      <section className="relative z-0 rounded-max-medium bg-max-primary p-6 sm:p-8">
        <div className="space-y-3">
          <PageTitle as="h2">Что вас беспокоит?</PageTitle>

          <div className="max-w-lg!">
            <PageDescription>
              Расскажите о самочувствии. МедВедь задаст несколько вопросов и
              поможет подготовиться к обращению к врачу.
            </PageDescription>
          </div>
        </div>

        <div className="mt-8">
          <Button
            size="medium"
            variant="primary"
            iconAfter={<ArrowUpRight size={20} />}
            onClick={onNewAppeal}
          >
            Начать диалог
          </Button>
        </div>
      </section>

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
  )
}
