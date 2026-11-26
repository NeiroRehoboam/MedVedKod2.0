import type { ComponentProps } from "react"
import { Spinner } from "@maxhub/max-ui"

import { useAiSessions } from "@/hooks/useAiSessions"
import { AppealItem } from "./AppealItem"
import { EmptyAppeals } from "./EmptyAppeals"
import { PageTitle } from "../typography"

type Appeal = ComponentProps<typeof AppealItem>["appeal"]

type AppealsHistoryProps = {
  onNewAppeal: () => void
  onAppealClick: (id: Appeal["id"]) => void
}

export function AppealsHistory({
  onNewAppeal,
  onAppealClick,
}: AppealsHistoryProps) {
  const sessionsQuery = useAiSessions()

  const appeals: Appeal[] = (sessionsQuery.data ?? []).map((session) => ({
    id: String(session.id),

    title: session.title || "Новое обращение",
    summary: session.summary?.trim() || undefined,

    date: session.created_at
      ? new Intl.DateTimeFormat("ru-RU", {
          day: "numeric",
          month: "long",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        }).format(new Date(session.created_at))
      : "Дата не указана",
    status: session.status === "COMPLETED" ? "completed" : "in_progress",
  }))
  return (
    <section className="mt-10">
      <div className="mb-5">
        <PageTitle as="h3">Мои обращения</PageTitle>
      </div>

      {sessionsQuery.isPending ? (
        <div className="flex justify-center py-12">
          <Spinner className="size-7" />
        </div>
      ) : sessionsQuery.isError ? (
        <div className="py-8 text-center">
          <p className="text-sm text-max-text-secondary">
            Не удалось загрузить обращения
          </p>

          <button
            type="button"
            onClick={() => sessionsQuery.refetch()}
            className="mt-3 text-sm font-medium text-max-text-primary underline underline-offset-4"
          >
            Попробовать снова
          </button>
        </div>
      ) : appeals.length > 0 ? (
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
