import { AuthGate } from "@/components/auth/AuthGate"
import { RouterComponent } from "./_index"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MaxUI, SnackbarProvider } from "@maxhub/max-ui"

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MaxUI colorScheme="light">
        <SnackbarProvider>
          <AuthGate>
            <RouterComponent />
          </AuthGate>
        </SnackbarProvider>
      </MaxUI>
    </QueryClientProvider>
  )
}

export default App
