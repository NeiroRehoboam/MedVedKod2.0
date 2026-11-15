import type { ComponentProps } from "react"
import { Typography } from "@maxhub/max-ui"
import { cn } from "cn"

type PageDescriptionProps = ComponentProps<typeof Typography.Text>

export function PageDescription({
  children,
  className,
  variant = "body",
  color = "secondary",
  ...props
}: PageDescriptionProps) {
  return (
    <p>
      <Typography.Text
        variant={variant}
        color={color}
        className={cn(className)}
        {...props}
      >
        {children}
      </Typography.Text>
    </p>
  )
}
