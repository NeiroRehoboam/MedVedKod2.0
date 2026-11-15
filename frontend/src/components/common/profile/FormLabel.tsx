import type { ComponentProps } from "react"
import { Typography } from "@maxhub/max-ui"
import { cn } from "cn"

type FormLabelProps = ComponentProps<typeof Typography.Label> & {
  htmlFor?: string
  required?: boolean
}

export function FormLabel({
  children,
  className,
  variant = "large",
  htmlFor,
  required = false,
  ...props
}: FormLabelProps) {
  return (
    <label htmlFor={htmlFor} className={cn("mb-3 block", className)}>
      <Typography.Label
        variant={variant}
        className="text-base! leading-6!"
        {...props}
      >
        {children}
        {required && (
          <span className="ml-1 text-red-500" aria-hidden="true">
            *
          </span>
        )}
      </Typography.Label>
    </label>
  )
}
