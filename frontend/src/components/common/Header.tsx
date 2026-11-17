import { MessageCircleQuestionMark } from "lucide-react"
import { Link, useNavigate } from "react-router-dom"
import { IconButton } from "@maxhub/max-ui"
import { DoctorSignature } from "./typography/DoctorSignature"

export const Header = () => {
  const navigate = useNavigate()

  return (
    <header className="mb-7 flex items-center justify-between gap-4">
      <Link to="/home" className="relative block w-fit shrink-0">
        <h1 className="relative z-10 font-unbounded text-xl font-semibold tracking-[-0.04em] text-max-text-primary">
          МедВедь
        </h1>

        <DoctorSignature className="absolute top-4 left-20 z-20 -rotate-6">
          С заботой о вас
        </DoctorSignature>
      </Link>

      <IconButton
        size="small"
        variant="secondary"
        onClick={() => navigate("/references")}
        aria-label="Помощь"
      >
        <MessageCircleQuestionMark size={21} strokeWidth={1.7} />
      </IconButton>
    </header>
  )
}
