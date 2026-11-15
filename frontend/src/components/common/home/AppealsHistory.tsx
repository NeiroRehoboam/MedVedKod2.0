import { mockAppeals } from "@/data/appeals.mock"
import { AppealItem } from "./AppealItem"
import { EmptyAppeals } from "./EmptyAppeals"
import { PageTitle } from "../typography"

type Appeal = (typeof mockAppeals)[number]

type AppealsHistoryProps = {
  appeals: readonly Appeal[]
  onNewAppeal: () => void
  onAppealClick: (id: Appeal["id"]) => void
}

export function AppealsHistory({
  appeals,
  onNewAppeal,
  onAppealClick,
}: AppealsHistoryProps) {
  return (
    <section className="mt-10">
      <div className="mb-5">
        <PageTitle as="h3">
          Мои обращения
        </PageTitle>
      </div>

      {appeals.length > 0 ? (
        <div className="flex flex-col gap-2.5">
          {appeals.map((appeal) => (
            <AppealItem
              key={appeal.id}
              appeal={appeal}
              onClick={onAppealClick}
            />
          ))}
        </div>
      ) : (
        <EmptyAppeals onNewAppeal={onNewAppeal} />
      )}
    </section>
  )
}
