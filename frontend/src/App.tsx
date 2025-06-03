// src/App.tsx
import React from "react"
import { Routes, Route, Navigate } from "react-router-dom"

import { LoginButton } from "./features/auth/LoginButton"
import { OAuthCallback } from "./features/auth/OAuthCallback"
import { PrivateRoute } from "./components/PrivateRoute"

import Home               from "./pages/Home"
import Dashboard          from "./pages/Dashboard"
import DailyLeaderboard   from "./pages/DailyLeaderboard"
import { StreakLeaderboard } from "./pages/StreakLeaderboard"

import CreateTeamPage         from "./pages/CreateTeamPage"
import TeamLeaderboardPage    from "./pages/TeamLeaderboardPage"

const App: React.FC = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginButton />} />
      <Route path="/oauth/callback" element={<OAuthCallback />} />

      {/* Private (authenticated) area */}
      <Route element={<PrivateRoute />}>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/daily-leaderboard" element={<DailyLeaderboard />} />
        <Route path="/streak-leaderboard" element={<StreakLeaderboard />} />

        {/* Create a team at /team/create */}
        <Route path="/team/create" element={<CreateTeamPage />} />

        {/* View a specific team’s live leaderboard at /team/:teamName */}
        <Route
          path="/team/:teamName"
          element={<TeamLeaderboardPage />}
        />

        {/* Redirect “/team” (no teamName) to /team/create */}
        <Route
          path="/team"
          element={<Navigate to="/team/create" replace />}
        />
      </Route>
    </Routes>
  )
}

export default App
