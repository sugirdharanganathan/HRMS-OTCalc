import React from 'react';

// Make sure "export const" is here
export const FormInput = ({ label, id, value, onChange, placeholder, disabled = false, type = 'text' }) => (
  <div className="flex flex-col">
    <label htmlFor={id} className="mb-1 text-sm font-medium text-gray-700">
      {label}
    </label>
    <input
      type={type}
      id={id}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      disabled={disabled}
      className={`px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
        disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
      }`}
    />
  </div>
);