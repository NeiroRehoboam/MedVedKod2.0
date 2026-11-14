import { MessageCircleQuestionMark } from "lucide-react"
import { Link, useNavigate } from "react-router-dom"
import { Button, IconButton } from "@maxhub/max-ui"

export const Header = () => {
  const navigate = useNavigate()

  return (
    <header className="mb-7 flex items-center justify-between gap-4">
      <Link to="/home" className="relative block w-fit shrink-0">
        <h1 className="relative z-10 font-unbounded text-xl font-semibold tracking-[-0.04em] text-max-text-primary">
          МедВед
        </h1>

        <span className="absolute top-4 left-20 z-20 -rotate-6 font-doctor text-2xl leading-none whitespace-nowrap text-max-text-themed">
          С заботой о вас
        </span>
      </Link>

      <IconButton
        size="medium"
        variant="secondary"
        onClick={() => navigate("/references")}
        aria-label="Помощь"
      >
        <MessageCircleQuestionMark size={21} strokeWidth={1.7} />
      </IconButton>
    </header>
  )
}
