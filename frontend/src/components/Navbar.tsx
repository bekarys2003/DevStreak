// src/components/Navbar.tsx

import React from 'react'
import { Link } from 'react-router-dom'

export const Navbar: React.FC = () => (
  <nav className="bg-gray-800 text-white px-4 py-2 flex space-x-4">
    <Link to="/global" className="hover:underline">Global Leaderboard</Link>
    <Link to="/team"   className="hover:underline">Team Leaderboard</Link>
  </nav>
)

export default Navbar
