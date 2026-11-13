import type { FC } from "react"
import { createBrowserRouter, RouterProvider } from "react-router-dom"
import { Layout } from "@/layouts/Layout"
import {
  HomePage,
  InitialPage,
  ProfilePage,
  QuestionPage,
  ReferencesPage,
} from "@/pages"

const router = createBrowserRouter([
  {
    path: "/",
    element: <InitialPage />,
  },
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        path: "home",
        element: <HomePage />,
      },
      {
        path: "profile",
        element: <ProfilePage />,
      },
      {
        path: "references",
        element: <ReferencesPage />,
      },
    ],
  },
  {
    path: "/question",
    element: <QuestionPage />,
  },
])

export const RouterComponent: FC = () => {
  return <RouterProvider router={router} />
}
