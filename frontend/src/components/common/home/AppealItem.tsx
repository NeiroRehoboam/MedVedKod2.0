import { ArrowUpRight } from "lucide-react"
import { CellSimple, IconButton, StatusBadge, Typography } from "@maxhub/max-ui"

import type { Appeal } from "@/types/appeal.types"

type AppealItemProps = {
  appeal: Appeal
  onClick: (id: Appeal["id"]) => void
}

export function AppealItem({ appeal, onClick }: AppealItemProps) {
  const isActive = appeal.status === "in_progress"

  return (
    <div className="rounded-max-medium bg-max-primary p-2">
      <CellSimple
        title={
          <div className="flex flex-wrap items-center gap-2">
            <Typography.Text variant="action-large" color="primary">
              {appeal.title}
            </Typography.Text>

            {isActive && <StatusBadge status="neutral" text="В процессе" />}
          </div>
        }
        subtitle={
          <div className="flex flex-col gap-1">
            {appeal.summary && (
              <span className="line-clamp-2 break-words">{appeal.summary}</span>
            )}
            <span>{appeal.date}</span>
          </div>
        }
        subtitleMode="secondary"
        surface="default"
        separator={false}
        showChevron={false}
        after={
          <IconButton
            type="button"
            aria-label={`Открыть обращение: ${appeal.title}`}
            size="small"
            variant="secondary"
            onClick={() => onClick(appeal.id)}
          >
            <ArrowUpRight size={18} strokeWidth={1.8} />
          </IconButton>
        }
      />
    </div>
  )
}
