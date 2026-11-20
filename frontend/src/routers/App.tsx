import { AuthGate } from "@/components/auth/AuthGate"
import { RouterComponent } from "./_index"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthGate>
        <RouterComponent />
      </AuthGate>
    </QueryClientProvider>
  )
}

export default App
