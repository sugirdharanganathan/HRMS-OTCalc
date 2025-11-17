import React, { useState, useEffect } from 'react';
import { Check, X, Info } from 'lucide-react';
import { Button } from '../components/Button';
import OtRuleModal from '../components/OtRuleModal'; 
import { getPendingApprovals, approveOt, rejectOt } from '../services/otApprovalService';

export default function OTApprovalPage() {
  const [pendingList, setPendingList] = useState([]);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(false); // <-- 1. Define the loading state

  const loadPendingApprovals = async () => {
    try {
      setLoading(true); // <-- 2. Set loading to true
      setError(null);
      const data = await getPendingApprovals();
      setPendingList(data);
    } catch (err) {
      setError('Failed to load pending approvals.');
    } finally {
      setLoading(false); // <-- 3. Set loading to false
    }
  };

  useEffect(() => {
    loadPendingApprovals();
  }, []);

  const handleApprove = async (empId) => {
    if (window.confirm('Are you sure you want to approve this?')) {
      try {
        await approveOt(empId);
        loadPendingApprovals(); // Refresh the list
      } catch (err) {
        setError('Failed to approve. Please try again.');
      }
    }
  };
  
  const handleReject = async (empId) => {
    if (window.confirm('Are you sure you want to reject this?')) {
      try {
        await rejectOt(empId);
        loadPendingApprovals(); // Refresh the list
      } catch (err) {
        setError('Failed to reject. Please try again.');
      }
    }
  };

  const formatCurrency = (amount) => {
    if (!amount) return '0';
    return new Intl.NumberFormat('id-ID', {
      style: 'decimal',
      minimumFractionDigits: 0,
    }).format(amount);
  };
  
  const formatNetSalary = (amount) => {
    const formatted = formatCurrency(amount);
    return (
      <a href="#" className="text-blue-600 underline" onClick={(e) => e.preventDefault()}>
        {formatted}
      </a>
    );
  };

  return (
    <>
      <OtRuleModal show={showModal} onClose={() => setShowModal(false)} />

      <div className="flex flex-col flex-1 overflow-auto">
        {/* Header */}
        <header className="flex flex-wrap items-center justify-between gap-4 p-4 m-4 bg-white rounded-lg shadow-sm">
          <h1 className="text-3xl font-bold" style={{ color: '#4a5568' }}>Overtime Approval</h1>
          <div className="flex items-center space-x-3">
            <Button 
              onClick={() => setShowModal(true)}
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
            <div className="px-6 py-4" style={{ backgroundColor: '#6b46c1' }}>
              <h2 className="text-xl font-semibold text-white">Employee OT Approval (in IDR)</h2>
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
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {pendingList.length > 0 ? (
                    pendingList.map((row) => (
                      <tr key={row.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{row.emp_id}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{row.emp_name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{row.designation || '-'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatCurrency(row.base_salary)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{row.ot_hours}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatCurrency(row.ot_salary)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatNetSalary(row.net_salary)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-3">
                          <button onClick={() => handleApprove(row.emp_id)} className="text-green-600 hover:text-green-800" title="Approve">
                            <Check className="w-5 h-5" />
                          </button>
                          <button onClick={() => handleReject(row.emp_id)} className="text-red-600 hover:text-red-800" title="Reject">
                            <X className="w-5 h-5" />
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="8" className="px-6 py-4 text-center text-sm text-gray-500">
                        {/* 4. Use the loading state here */}
                        {loading ? 'Loading...' : 'No pending approvals.'}
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