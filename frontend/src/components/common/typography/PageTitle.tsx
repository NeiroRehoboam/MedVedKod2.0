
import type { ComponentProps } from "react"
import { Typography } from "@maxhub/max-ui"
import { cn } from "cn"

type HeadingTag = "h1" | "h2" | "h3" | "h4"

type PageTitleProps = ComponentProps<typeof Typography.Title> & {
  as?: HeadingTag
}

const headingSizes: Record<HeadingTag, string> = {
  h1: "text-4xl! leading-[1.15]!",
  h2: "text-3xl! leading-tight!",
  h3: "text-2xl! leading-snug!",
  h4: "text-xl! leading-snug!",
}

export function PageTitle({
  children,
  className,
  variant = "large-strong",
  as: Tag = "h1",
  ...props
}: PageTitleProps) {
  return (
    <Tag>
      <Typography.Title
        variant={variant}
        className={cn(
          "font-unbounded! tracking-tight!",
          headingSizes[Tag],
          className,
        )}
        {...props}
      >
        {children}
      </Typography.Title>
    </Tag>
  )
}
