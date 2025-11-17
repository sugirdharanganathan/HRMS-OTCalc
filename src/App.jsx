import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import EmployeeMaster from './pages/EmployeeMaster';
import AttendancePage from './pages/AttendancePage';
import OTApprovalPage from './pages/OTApprovalPage'; // The purple "Approval" page
import OTCalculationPage from './pages/OTCalculationPage'; // <-- Import the new blue "Config" page

export default function App() {
  const [currentPage, setCurrentPage] = useState('Employees');

  const renderPage = () => {
    switch (currentPage) {
      case 'Employees':
        return <EmployeeMaster />;
      case 'Attendance':
        return <AttendancePage />;
      case 'OT Config': // <-- This now renders the new Calculation page
        return <OTCalculationPage />;
      case 'OT Calc': // <-- This renders the Approval page
        return <OTApprovalPage />;
      case 'Reports':
        return <div>Reports Page Not Built Yet</div>;
      default:
        return <EmployeeMaster />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar currentPage={currentPage} setCurrentPage={setCurrentPage} />
      <div className="flex-1 flex flex-col overflow-hidden">
        {renderPage()}
      </div>
    </div>
  );
}