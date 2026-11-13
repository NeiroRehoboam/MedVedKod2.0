import { MessageCircleQuestionMark } from "lucide-react"
import { Button } from "../ui/button"
import { Link } from "react-router-dom"

export const Header = () => {
  return (
    <header className="mb-7 flex items-center justify-between gap-4">
      <div className="relative w-fit">
        <h1 className="relative z-10 font-unbounded text-xl font-semibold tracking-[-0.04em]">
          МедВед
        </h1>

        <span className="absolute top-4 left-20 z-20 -rotate-6 font-doctor text-2xl leading-none whitespace-nowrap text-sky-600 sm:text-2xl">
          С заботой о вас
        </span>
      </div>

      <Button
        nativeButton={false}
        render={<Link to="/references" />}
        variant="outline"
        size="icon-lg"
        aria-label="Помощь"
        className="size-11 shrink-0 rounded-full border-none bg-background/70 shadow-sm backdrop-blur-xl"
      >
        <MessageCircleQuestionMark className="size-5" strokeWidth={1.7} />
      </Button>
    </header>
  )
}
