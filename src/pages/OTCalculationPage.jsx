import React, { useState, useEffect } from 'react';
import { Info, Send } from 'lucide-react';
import { Button } from '../components/Button';
import OtRuleModal from '../components/OtRuleModal'; // Info modal
import CalculationDetailsModal from '../components/CalculationDetailsModal'; // <-- Import new modal
import { getAllApprovals, sendForApproval } from '../services/otApprovalService';

export default function OTCalculationPage() {
  const [approvalList, setApprovalList] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // State for the modals
  const [showRuleModal, setShowRuleModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedRow, setSelectedRow] = useState(null); // To store all row data

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      // Fetches ALL records (not just pending) for the current period
      // We can add a period filter later if we re-add the input
      const approvalData = await getAllApprovals();
      setApprovalList(approvalData);
    } catch (err) {
      setError('Failed to load data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []); // Load once on page mount

  const handleSend = async (empId) => {
    if (!window.confirm(`Are you sure you want to send OT for ${empId} for approval?`)) {
      return;
    }
    try {
      await sendForApproval(empId);
      alert('Sent for approval!');
      loadData(); // Refresh the list
    } catch (err) {
      setError('Failed to send for approval. Please try again.');
    }
  };
  
  // --- NEW: Click handler for the Net Salary link ---
  const handleShowDetails = (row) => {
    setSelectedRow(row);
    setShowDetailModal(true);
  };

  const formatCurrency = (amount) => {
    if (!amount) return '0';
    return new Intl.NumberFormat('id-ID', {
      style: 'decimal',
      minimumFractionDigits: 0,
    }).format(amount);
  };
  
  return (
    <>
      {/* --- Render both modals --- */}
      <OtRuleModal show={showRuleModal} onClose={() => setShowRuleModal(false)} />
      <CalculationDetailsModal
        show={showDetailModal}
        onClose={() => setShowDetailModal(false)}
        breakdown={selectedRow?.breakdown}
        employee={selectedRow}
      />

      <div className="flex flex-col flex-1 overflow-auto">
        {/* Header */}
        <header className="flex flex-wrap items-center justify-between gap-4 p-4 m-4 bg-white rounded-lg shadow-sm">
          <h1 className="text-3xl font-bold" style={{ color: '#4a5568' }}>Overtime Configuration & Calculation</h1>
          <div className="flex items-center space-x-3">
            <Button 
              onClick={() => setShowRuleModal(true)} // Show info modal
              variant="primary" 
              icon={Info}
              style={{ backgroundColor: '#2C7A7B', borderColor: '#2C7A7B' }}
              className="hover:bg-teal-700 focus:ring-teal-500"
            >
              OT Calculation Details
            </Button>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-grow p-4 pt-0">
          <div className="w-full max-w-full mx-auto overflow-hidden bg-white rounded-lg shadow-lg">
            
            {/* Card Header (Blue) */}
            <div className="px-6 py-4" style={{ backgroundColor: '#4299e1' }}>
              <h2 className="text-xl font-semibold text-white">Employee Overtime (in IDR)</h2>
            </div>
            
            {error && <div className="p-4 m-4 text-red-800 bg-red-100 border border-red-300 rounded-md">{error}</div>}

            <div className="overflow-x-auto">
              <table className="w-full min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Emp ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Designation</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Base Salary</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">OT Hours</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">OT Salary</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Net Salary</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {approvalList.length > 0 ? (
                    approvalList.map((row) => (
                      <tr key={row.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{row.emp_id}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{row.emp_name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{row.designation || '-'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatCurrency(row.base_salary)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{row.ot_hours}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatCurrency(row.ot_salary)}</td>
                        
                        {/* --- MODIFIED: Clickable Net Salary --- */}
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                          <button
                            onClick={() => handleShowDetails(row)}
                            className="text-blue-600 underline hover:text-blue-800"
                          >
                            {formatCurrency(row.net_salary)}
                          </button>
                        </td>
                        
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          {row.approval_pending ? (
                            <span className="text-xs text-yellow-600 italic">Pending...</span>
                          ) : row.is_approved === true ? (
                            <span className="text-xs text-green-600 italic">Approved</span>
                          ) : row.is_approved === false ? (
                            <span className="text-xs text-red-600 italic">Rejected</span>
                          ) : (
                            <button onClick={() => handleSend(row.emp_id)} className="text-blue-600 hover:text-blue-800" title="Send for Approval">
                              <Send className="w-5 h-5" />
                            </button>
                          )}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="8" className="px-6 py-4 text-center text-sm text-gray-500">
                        {loading ? 'Loading data...' : 'No data found. Your backend may need to sync data.'}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </main>

        <footer className="py-4 mt-auto text-center text-gray-600 bg-gray-200">
          © Copyright Techspire Solutions
        </footer>
      </div>
    </>
  );
}