import { defineConfig } from "orval"

export default defineConfig({
  api: {
    input: "http://127.0.0.1:8000/api/schema/",
    output: {
      mode: "tags-split",
      target: "./src/api/generated",
      schemas: "./src/api/generated/models",
      client: "react-query",
      httpClient: "fetch",
      override: {
        mutator: {
          path: "./src/api/fetcher.ts",
          name: "customFetch",
        },
      },
    },
  },
})