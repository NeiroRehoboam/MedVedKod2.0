import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { MaxUI, SnackbarProvider } from "@maxhub/max-ui"

import "@maxhub/max-ui/dist/styles.css"
import "./index.css"

import App from "./routers/App.tsx"

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <MaxUI colorScheme="light">
      <SnackbarProvider>
        <App />
      </SnackbarProvider>
    </MaxUI>
  </StrictMode>
)
