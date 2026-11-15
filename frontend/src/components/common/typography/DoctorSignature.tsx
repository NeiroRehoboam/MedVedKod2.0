import type { HTMLAttributes, ReactNode } from "react"
import { cn } from "cn"

type DoctorSignatureProps = HTMLAttributes<HTMLSpanElement> & {
  children: ReactNode
}

export function DoctorSignature({
  children,
  className,
  ...props
}: DoctorSignatureProps) {
  return (
    <span
      className={cn(
        "inline-block font-doctor text-2xl leading-none whitespace-nowrap text-max-text-themed",
        className
      )}
      {...props}
    >
      {children}
    </span>
  )
}
