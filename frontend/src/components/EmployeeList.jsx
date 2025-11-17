import React, { useState, useEffect } from 'react';
import { Plus, FileSpreadsheet, Edit, Trash2, Search } from 'lucide-react';
import { Button } from './Button';
import { getEmployees, deleteEmployee, exportToExcel } from '../services/employeeService';

export default function EmployeeList({ onAddEmployee, onEditEmployee }) {
  const [employees, setEmployees] = useState([]);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  const employeeNameMap = new Map(employees.map(emp => [emp.emp_id, emp.name]));
  
  const loadEmployees = async () => {
    try {
      setError(null);
      const data = await getEmployees();
      setEmployees(data);
    } catch (err) {
      setError('Failed to load employees. Please try again.');
    }
  };

  useEffect(() => {
    loadEmployees();
  }, []);

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this employee?')) {
      try {
        await deleteEmployee(id);
        loadEmployees(); // Refresh the list
      } catch (err) {
        setError('Failed to delete employee. Please try again.');
      }
    }
  };

  const handleExport = async () => {
    try {
      await exportToExcel();
    } catch (err) {
      setError('Failed to export. Please try again.');
    }
  };
  
  const formatSalary = (salary) => {
    if (!salary) return 'N/A';
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(salary);
  };

  const filteredEmployees = employees.filter(emp => {
    const search = searchTerm.toLowerCase().trim();
    return (
      emp.emp_id.toLowerCase().includes(search) ||
      emp.name.toLowerCase().includes(search) ||
      emp.designation?.toLowerCase().includes(search) ||
      emp.department?.toLowerCase().includes(search)
    );
  });

  return (
    <div className="flex flex-col h-full"> 
      {/* Header */}
      <header className="flex-shrink-0 flex flex-wrap items-center justify-between gap-4 p-4 m-4 bg-white rounded-lg shadow-sm">
        <h1 className="text-3xl font-bold text-blue-700">Employee Master</h1>
        <div className="flex items-center space-x-3">
          <Button onClick={onAddEmployee} variant="primary" icon={Plus}>
            Add New Employee
          </Button>
          <Button onClick={handleExport} variant="outline" icon={FileSpreadsheet}>
            Export to Excel
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow flex flex-col p-4 pt-0 overflow-hidden">
        <div className="w-full max-w-full mx-auto flex flex-col h-full bg-white rounded-lg shadow-lg">
          
          {/* Search Bar */}
          <div className="flex-shrink-0 p-4 border-b border-gray-200">
            <div className="relative">
              <input 
                type="text" 
                placeholder="Search by Employee ID, Name, Designation, or Department..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            </div>
          </div>

          {/* Card Header */}
          <div className="flex-shrink-0 px-6 py-4 bg-teal-600">
            <h2 className="text-xl font-semibold text-white">Employee Listing</h2>
          </div>
          
          {error && <div className="p-4 m-4 text-red-800 bg-red-100 border border-red-300 rounded-md">{error}</div>}

          {/* Table Scrolling Container */}
          <div className="flex-grow overflow-y-auto">
            <table className="w-full min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50 sticky top-0 z-10">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Emp ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Designation</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Salary (IDR)</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Department</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">HOD</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Supervisor</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredEmployees.length > 0 ? (
                  filteredEmployees.map((emp) => (
                    <tr key={emp.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{emp.emp_id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{emp.name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{emp.designation || '-'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatSalary(emp.salary)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{emp.department || '-'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                        {employeeNameMap.get(emp.hod) || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                        {employeeNameMap.get(emp.supervisor) || '-'}
                      </td>
                      
                      {/* --- THIS IS THE LINE --- 
                          'space-x-2' puts the buttons side-by-side.
                      */}
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        <Button onClick={() => onEditEmployee(emp.id)} variant="primary" icon={Edit} size="sm" />
                        <Button onClick={() => handleDelete(emp.D)} variant="danger" icon={Trash2} size="sm" />
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="8" className="px-6 py-4 text-center text-sm text-gray-500">
                      No employees found matching your search.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}