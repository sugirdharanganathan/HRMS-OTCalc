import React from 'react';
import { X } from 'lucide-react';
import { Button } from './Button';

// Helper to format currency
const formatCurrency = (amount) => {
  if (!amount) return '0';
  return new Intl.NumberFormat('id-ID', {
    style: 'decimal',
    minimumFractionDigits: 0,
  }).format(amount);
};

export default function CalculationDetailsModal({ show, onClose, breakdown, employee }) {
  if (!show || !breakdown || !employee) return null;

  // Extract data from the breakdown JSON
  const baseSalary = breakdown.salary || 0;
  const otHours = breakdown.ot_hours || 0;
  const totalOtSalary = breakdown.total_ot_salary || 0;
  const bands = breakdown.bands || [];
  const netSalary = baseSalary + totalOtSalary;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-teal-600 rounded-t-lg">
          <h3 className="text-xl font-semibold text-white">
            OT Calculation Details
          </h3>
          <button onClick={onClose} className="text-white hover:text-gray-200">
            <X className="w-6 h-6" />
          </button>
        </div>
        
        {/* Content */}
        <div className="p-6 text-gray-700 space-y-4">
          <div>
            <h4 className="text-lg font-bold">{employee.emp_name} ({employee.emp_id})</h4>
            <p className="text-sm text-gray-600">{employee.designation}</p>
          </div>
          <p>
            <span className="font-medium">Base Salary:</span>{' '}
            <span className="font-bold">{formatCurrency(baseSalary)} IDR</span>
          </p>
          <p>
            <span className="font-medium">OT Hours:</span>{' '}
            <span className="font-bold">{otHours} hours</span>
          </p>
          
          <div>
            <h5 className="font-bold mb-2">Calculation Breakdown:</h5>
            <ul className="list-disc list-inside space-y-1 text-sm">
              {bands.map((band, index) => (
                <li key={index}>
                  Hour {band.name.replace('_', ' ')} ({band.hours} hrs @ {band.multiplier}&times;):{' '}
                  <span className="font-mono">{formatCurrency(band.amount)} IDR</span>
                </li>
              ))}
            </ul>
          </div>

          <hr className="my-2" />

          <p>
            <span className="font-bold text-lg">Total OT Salary:</span>{' '}
            <span className="font-bold text-lg">{formatCurrency(totalOtSalary)} IDR</span>
          </p>
          <p>
            <span className="font-bold text-lg">Net Salary:</span>{' '}
            <span className="font-bold text-lg text-blue-600">{formatCurrency(netSalary)} IDR</span>
          </p>

        </div>
        
        {/* Footer */}
        <div className="flex justify-end px-6 py-4 bg-gray-50 rounded-b-lg">
          <Button onClick={onClose} variant="secondary">
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}