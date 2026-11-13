import { Toaster } from "@/components/ui/toast"
import { RouterComponent } from "./_index"

function App() {
  return (
    <>
      <RouterComponent />
      <Toaster timeout={3000} />
    </>
  )
}

export default App
