import React from 'react';
import {
  LayoutDashboard,
  Users,
  Settings,
  CalendarCheck,
  Calculator,
  BarChart3,
} from 'lucide-react';

// NavItem now takes props from App.jsx
const NavItem = ({ icon: Icon, text, active = false, onClick }) => (
  <button // Changed to a button for a clear onClick action
    onClick={onClick}
    className={`
      flex items-center w-full px-4 py-3 rounded-lg text-gray-200 transition-colors duration-200
      ${
        active
          ? 'bg-green-500 text-white shadow-lg' // Active link style
          : 'hover:bg-gray-700 hover:text-white' // Inactive link style
      }
    `}
  >
    <Icon className="w-5 h-5" />
    <span className="ml-4 font-medium">{text}</span>
  </button>
);

// Sidebar now accepts currentPage and setCurrentPage as props
export default function Sidebar({ currentPage, setCurrentPage }) {
  return (
    <div className="flex flex-col w-64 bg-gray-800 text-white shadow-xl">
      {/* Header / Logo */}
      <div className="flex items-center justify-center h-20 border-b border-gray-700">
        <img
          src="https://placehold.co/40x40/ffffff/1f2937?text=LOGO"
          alt="BTG Logo"
          className="w-10 h-10 rounded-full"
        />
        <span className="ml-3 text-2xl font-bold text-white">OT App</span>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
        <NavItem
          icon={LayoutDashboard}
          text="Dashboard"
          active={currentPage === 'Dashboard'}
          onClick={() => setCurrentPage('Dashboard')}
        />
        <NavItem
          icon={Users}
          text="Employees"
          active={currentPage === 'Employees'}
          onClick={() => setCurrentPage('Employees')}
        />
        <NavItem
          icon={Settings}
          text="OT Config"
          active={currentPage === 'OT Config'}
          onClick={() => setCurrentPage('OT Config')}
        />
        <NavItem
          icon={CalendarCheck}
          text="Attendance"
          active={currentPage === 'Attendance'}
          onClick={() => setCurrentPage('Attendance')}
        />
        <NavItem
          icon={Calculator}
          text="OT Calc"
          active={currentPage === 'OT Calc'}
          onClick={() => setCurrentPage('OT Calc')}
        />
        <NavItem
          icon={BarChart3}
          text="Reports"
          active={currentPage === 'Reports'}
          onClick={() => setCurrentPage('Reports')}
        />
      </nav>
    </div>
  );
}