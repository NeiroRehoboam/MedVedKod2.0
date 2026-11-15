import type { FC } from "react"
import { createBrowserRouter, RouterProvider } from "react-router-dom"

import { AppLayout } from "@/layouts/AppLayout"
import { MainLayout } from "@/layouts/MainLayout"

import {
  HomePage,
  InitialPage,
  ProfilePage,
  QuestionPage,
  ReferencesPage,
} from "@/pages"

const router = createBrowserRouter([
  {
    element: <AppLayout />,
    children: [
      {
        path: "/",
        element: <InitialPage />,
      },
      {
        element: <MainLayout />,
        children: [
          {
            path: "/home",
            element: <HomePage />,
          },
          {
            path: "/profile",
            element: <ProfilePage />,
          },
          {
            path: "/references",
            element: <ReferencesPage />,
          },
        ],
      },
      {
        path: "/question",
        element: <QuestionPage />,
      },
    ],
  },
])

export const RouterComponent: FC = () => {
  return <RouterProvider router={router} />
}