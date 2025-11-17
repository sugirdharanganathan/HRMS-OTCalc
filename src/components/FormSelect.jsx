import React from 'react';
import { ChevronDown } from 'lucide-react';

// Make sure "export const" is here
export const FormSelect = ({ label, id, value, onChange, children }) => (
  <div className="flex flex-col">
    <label htmlFor={id} className="mb-1 text-sm font-medium text-gray-700">
      {label}
    </label>
    <div className="relative">
      <select
        id={id}
        value={value}
        onChange={onChange}
        className="w-full px-4 py-2 pr-10 text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm appearance-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        {children}
      </select>
      <ChevronDown
        className="absolute w-5 h-5 text-gray-400 pointer-events-none"
        style={{ top: '50%', right: '0.75rem', transform: 'translateY(-50%)' }}
      />
    </div>
  </div>
);