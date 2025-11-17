import React, { useState, useEffect } from 'react';
import { Plus, FileSpreadsheet, Edit, Trash2 } from 'lucide-react';

// Reusable components
import { Button } from '../components/Button';
import { FormInput } from '../components/FormInput';
import { FormSelect } from '../components/FormSelect';

// API services
import { listAttendance, createAttendance, deleteAttendance, exportAttendanceExcel } from '../services/attendanceService';
import { getEmployees } from '../services/employeeService'; // To get employee list for the modal

// --- Helper function to parse flexible time inputs ---
/**
 * Parses a flexible time string (like "09:00 AM" or "17:30" or "2025-11-12T09:00")
 * into a Date object. Returns null if invalid.
 */
const parseTime = (val) => {
  if (!val) return null;

  // 1. Try to parse as a full ISO-like string first
  let dt = new Date(val);
  if (!isNaN(dt.getTime())) {
    return dt;
  }

  // 2. Try to parse as a time-only string (e.g., "17:30")
  const today = new Date().toISOString().split('T')[0]; // "2025-11-12"
  dt = new Date(`${today}T${val}`);
  if (!isNaN(dt.getTime())) {
    return dt;
  }
  
  // 3. Try to parse "09:00 AM" / "05:15 PM"
  const timeMatch = val.match(/(\d{1,2}):(\d{2})\s*(AM|PM)?/i);
  if (timeMatch) {
    let [_, hours, minutes, ampm] = timeMatch;
    hours = parseInt(hours, 10);
    if (ampm && /pm/i.test(ampm) && hours < 12) {
      hours += 12; // 5 PM -> 17
    }
    if (ampm && /am/i.test(ampm) && hours === 12) {
      hours = 0; // 12 AM -> 00
    }
    dt = new Date();
    dt.setHours(hours, parseInt(minutes, 10), 0, 0);
    return dt;
  }

  return null; // Invalid format
};


// --- Add/Edit Modal Component ---
const AttendanceModal = ({ show, onClose, onSave, employees }) => {
  const [empId, setEmpId] = useState('');
  const [empName, setEmpName] = useState('');
  const [clockIn, setClockIn] = useState('');
  const [clockOut, setClockOut] = useState('');
  
  // --- NEW: State for validation errors ---
  const [errors, setErrors] = useState({});

  if (!show) return null;

  // When an employee is selected, update both emp_id and name
  const handleEmployeeChange = (e) => {
    const selectedEmpId = e.target.value;
    const selectedEmployee = employees.find(emp => emp.emp_id === selectedEmpId);
    if (selectedEmployee) {
      setEmpId(selectedEmployee.emp_id);
      setEmpName(selectedEmployee.name);
    } else {
      setEmpId('');
      setEmpName('');
    }
    // Clear error on change
    if (errors.empId) setErrors(p => ({ ...p, empId: null }));
  };

  // --- NEW: Validation Function ---
  const validate = () => {
    const newErrors = {};
    const now = new Date();

    // 1. Employee
    if (!empId) {
      newErrors.empId = "Please select an employee.";
    }

    // 2. Clock In
    if (!clockIn.trim()) {
      newErrors.clockIn = "Clock In time is required.";
    }
    
    const clockInDate = parseTime(clockIn);
    if (clockIn.trim() && !clockInDate) {
      newErrors.clockIn = "Invalid time format. Use HH:MM AM/PM or YYYY-MM-DDTHH:MM.";
    } else if (clockInDate && clockInDate > now) {
      newErrors.clockIn = "Clock In time cannot be in the future.";
    }

    // 3. Clock Out
    const clockOutDate = parseTime(clockOut);
    if (clockOut.trim() && !clockOutDate) {
      newErrors.clockOut = "Invalid time format. Use HH:MM AM/PM or YYYY-MM-DDTHH:MM.";
    }
    
    // 4. Cross-Field: Clock Out vs Clock In
    if (clockInDate && clockOutDate && clockOutDate <= clockInDate) {
      newErrors.clockOut = "Clock Out time must be after Clock In time.";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // --- MODIFIED: handleSubmit ---
  const handleSubmit = () => {
    // Run validation
    if (!validate()) {
      return; // Stop if validation fails
    }
    
    // Validation passed, prepare data
    const data = {
      emp_id: empId,
      name: empName,
      // Send the raw string. The backend service is already built to parse it.
      clock_in: clockIn,
      clock_out: clockOut || null,
    };
    onSave(data);
    clearForm();
  };
  
  const clearForm = () => {
    setEmpId('');
    setEmpName('');
    setClockIn('');
    setClockOut('');
    setErrors({});
  };
  
  const handleClose = () => {
    clearForm();
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg">
        <div className="px-6 py-4 bg-gray-100 border-b rounded-t-lg">
          <h3 className="text-xl font-semibold text-gray-800">Add Attendance</h3>
        </div>
        <div className="p-6 space-y-4">
          <FormSelect
            label="Employee"
            id="employee"
            value={empId}
            onChange={handleEmployeeChange}
            error={errors.empId} // Pass error
          >
            <option value="">Select Employee</option>
            {employees.map(emp => (
              <option key={emp.emp_id} value={emp.emp_id}>
                {emp.name} ({emp.emp_id})
              </option>
            ))}
          </FormSelect>
          
          <FormInput
            label="Clock In (e.g., 09:00 AM or YYYY-MM-DDTHH:MM)"
            id="clockIn"
            type="text"
            value={clockIn}
            onChange={(e) => {
              setClockIn(e.target.value);
              if (errors.clockIn) setErrors(p => ({ ...p, clockIn: null }));
            }}
            placeholder="YYYY-MM-DDTHH:MM or 09:00 AM"
            error={errors.clockIn} // Pass error
          />
          <FormInput
            label="Clock Out (e.g., 06:15 PM or YYYY-MM-DDTHH:MM)"
            id="clockOut"
            type="text"
            value={clockOut}
            onChange={(e) => {
              setClockOut(e.target.value);
              if (errors.clockOut) setErrors(p => ({ ...p, clockOut: null }));
            }}
            placeholder="YYYY-MM-DDTHH:MM or 06:15 PM"
            error={errors.clockOut} // Pass error
          />
        </div>
        <div className="flex justify-end px-6 py-4 space-x-3 bg-gray-50 rounded-b-lg">
          <Button onClick={handleClose} variant="secondary">Cancel</Button>
          <Button onClick={handleSubmit} variant="primary">Save</Button>
        </div>
      </div>
    </div>
  );
};


// --- Main Attendance Page Component ---
// (No changes to the main component)
export default function AttendancePage() {
  const [attendanceList, setAttendanceList] = useState([]);
  const [employees, setEmployees] = useState([]); // For the modal
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const fetchData = async () => {
    try {
      setError(null);
      const [attData, empData] = await Promise.all([
        listAttendance(),
        getEmployees()
      ]);
      setAttendanceList(attData);
      setEmployees(empData);
    } catch (err) {
      setError('Failed to load data. Please try again.');
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAddAttendance = async (data) => {
    try {
      await createAttendance(data);
      setShowModal(false);
      fetchData(); // Refresh list
    } catch (err) {
      setError('Failed to save attendance. Please try again.');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this record?')) {
      try {
        await deleteAttendance(id);
        fetchData(); // Refresh list
      } catch (err) {
        setError('Failed to delete record. Please try again.');
      }
    }
  };

  const handleExport = async () => {
    try {
      await exportAttendanceExcel();
    } catch (err) {
      setError('Failed to export. Please try again.');
    }
  };

  // Helper to format time
  const formatTime = (dateTimeString) => {
    if (!dateTimeString) return 'N/A';
    try {
      // Assuming backend returns ISO string
      const date = new Date(dateTimeString);
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });
    } catch (e) {
      return dateTimeString; // Fallback
    }
  };

  return (
    <>
      <AttendanceModal
        show={showModal}
        onClose={() => setShowModal(false)}
        onSave={handleAddAttendance}
        employees={employees}
      />
      
      <div className="flex flex-col flex-1 overflow-auto">
        {/* Header */}
        <header className="flex flex-wrap items-center justify-between gap-4 p-4 m-4 bg-white rounded-lg shadow-sm">
          <h1 className="text-3xl font-bold text-blue-700">Employee Attendance</h1>
          <div className="flex items-center space-x-3">
            <Button onClick={() => setShowModal(true)} variant="primary" icon={Plus}>
              Add Attendance
            </Button>
            <Button onClick={handleExport} variant="outline" icon={FileSpreadsheet}>
              Export to Excel
            </Button>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-grow p-4 pt-0">
          <div className="w-full max-w-6xl mx-auto overflow-hidden bg-white rounded-lg shadow-lg">
            {/* Card Header */}
            <div className="px-6 py-4 bg-orange-600">
              <h2 className="text-xl font-semibold text-white">Attendance Listing</h2>
            </div>
            
            {error && <div className="p-4 m-4 text-red-800 bg-red-100 border border-red-300 rounded-md">{error}</div>}

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Emp ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Employee Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Clock In</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Clock Out</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {attendanceList.length > 0 ? (
                    attendanceList.map((att) => (
                      <tr key={att.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{att.emp_id}</td>
                        <td className="px-6 py-4 whitespace-nowPrap text-sm text-gray-700">{att.name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatTime(att.clock_in)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatTime(att.clock_out)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                          <Button onClick={() => alert('Edit not implemented yet')} variant="primary" icon={Edit} size="sm">
                            Edit
                          </Button>
                          <Button onClick={() => handleDelete(att.id)} variant="danger" icon={Trash2} size="sm">
                            Delete
                          </Button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5" className="px-6 py-4 text-center text-sm text-gray-500">No attendance records found.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="py-4 mt-auto text-center text-gray-600 bg-gray-200">
          © Copyright Techspire Solutions
        </footer>
      </div>
    </>
  );
}