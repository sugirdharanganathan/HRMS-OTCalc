import React from 'react';
import { X } from 'lucide-react';
import { Button } from './Button';

export default function OtRuleModal({ show, onClose }) {
  if (!show) return null;

  return (
    // Backdrop
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      {/* Modal Content */}
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-teal-600 rounded-t-lg">
          <h3 className="text-xl font-semibold text-white">
            Indonesian 173-Hour OT Rule Configuration
          </h3>
          <button onClick={onClose} className="text-white hover:text-gray-200">
            <X className="w-6 h-6" />
          </button>
        </div>
        
        {/* Content */}
        <div className="p-6 text-gray-700 text-lg space-y-3">
          <p>
            <span className="font-bold">Monthly base hours:</span> 173 hours
          </p>
          <ul className="list-disc list-inside space-y-2">
            <li>
              <span className="font-bold">First hour</span> &rarr;{' '}
              <span className="font-bold text-teal-700">1.5&times;</span> base hourly rate
            </li>
            <li>
              <span className="font-bold">Next 6 hours</span> (up to 7th hour) &rarr;{' '}
              <span className="font-bold text-teal-700">2&times;</span> base hourly rate
            </li>
            <li>
              <span className="font-bold">8th hour</span> &rarr;{' '}
              <span className="font-bold text-teal-700">3&times;</span> base hourly rate
            </li>
            <li>
              <span className="font-bold">9th hour and beyond</span> &rarr;{' '}
              <span className="font-bold text-teal-700">4&times;</span> base hourly rate
            </li>
          </ul>
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