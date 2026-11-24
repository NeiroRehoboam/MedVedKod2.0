import { useNavigate } from "react-router-dom"
import { HomeHero, AppealsHistory } from "@/components/common"

export function HomePage() {
  const navigate = useNavigate()

  const handleNewAppeal = () => {
    navigate("/question")
  }

  const handleAppealClick = (id: string) => {
    navigate(`/question/${id}`)
  }

  return (
    <div>
      <HomeHero onNewAppeal={handleNewAppeal} />

      <AppealsHistory
        onNewAppeal={handleNewAppeal}
        onAppealClick={handleAppealClick}
      />
    </div>
  )
}
