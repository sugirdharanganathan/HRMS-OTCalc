import React, { useState, useEffect } from 'react';
import { Save, X } from 'lucide-react';
import { Button } from './Button';
import { FormInput } from './FormInput';
import { FormSelect } from './FormSelect';
import { 
  createEmployee, 
  getEmployeeById, 
  updateEmployee, 
  getHods,        // <-- NEW
  getSupervisors, // <-- NEW
  getEmployees    // <-- To get department list
} from '../services/employeeService';

export default function EmployeeForm({ employeeId, onDone }) {
  // State for the form data
  const [formData, setFormData] = useState({
    name: '',
    designation: '',
    salary: '',
    department: '',
    hod: '', 
    supervisor: '',
    is_hod: 'no',
    is_supervisor: 'no',
    status: 'active'
  });
  
  const [currentEmpId, setCurrentEmpId] = useState(null); 
  
  // State for dropdown lists
  const [departmentList, setDepartmentList] = useState([]);
  const [hodList, setHodList] = useState([]);
  const [supervisorList, setSupervisorList] = useState([]);
  
  // State for filtered dropdowns
  const [hodOptions, setHodOptions] = useState([]);
  const [supervisorOptions, setSupervisorOptions] = useState([]);

  const [isSaving, setIsSaving] = useState(false);
  const [serverError, setServerError] = useState(null); 
  const [errors, setErrors] = useState({});

  const isEditMode = employeeId !== null;
  const formTitle = isEditMode ? 'Edit Employee' : 'Add New Employee';

  // --- MODIFIED: Fetch initial data on load ---
  useEffect(() => {
    // 1. Fetch all employees just to build a unique department list
    const fetchDepartments = async () => {
      try {
        const allEmps = await getEmployees();
        const depts = [...new Set(allEmps.map(e => e.department).filter(Boolean))];
        setDepartmentList(depts);
      } catch (err) {
        console.error('Failed to load departments', err);
      }
    };
    
    // 2. Fetch HODs for HOD dropdown
    const fetchHods = async () => {
      try {
        const data = await getHods();
        setHodList(data);
      } catch (err) {
        console.error('Failed to load HODs', err);
      }
    };
    
    // 3. Fetch Supervisors for Supervisor dropdown
    const fetchSupervisors = async () => {
      try {
        const data = await getSupervisors();
        setSupervisorList(data);
      } catch (err) {
        console.error('Failed to load Supervisors', err);
      }
    };

    // 4. If in Edit Mode, fetch the data for *this* employee
    const fetchEmployeeData = async (id) => {
      try {
        const emp = await getEmployeeById(id);
        setCurrentEmpId(emp.emp_id);
        setFormData({
          name: emp.name || '',
          designation: emp.designation || '',
          salary: emp.salary || '',
          department: emp.department || '',
          hod: emp.hod || '',
          supervisor: emp.supervisor || '',
          is_hod: emp.is_hod || 'no',
          is_supervisor: emp.is_supervisor || 'no',
          status: emp.status || 'active'
        });
      } catch (err) {
        setServerError('Failed to load employee data. Please try again.');
      }
    };

    // Run all fetches
    fetchDepartments();
    fetchHods();
    fetchSupervisors();
    if (isEditMode) {
      fetchEmployeeData(employeeId);
    }
  }, [employeeId, isEditMode]);
  
  // --- NEW EFFECT: Filter dropdowns based on department AND self ---
  useEffect(() => {
    const selectedDept = formData.department;
    
    // Filter HOD list
    const filteredHods = hodList.filter(emp => {
      const isSameDepartment = emp.department === selectedDept;
      const isNotSelf = isEditMode ? emp.emp_id !== currentEmpId : true;
      return isSameDepartment && isNotSelf;
    });
    setHodOptions(filteredHods);

    // Filter Supervisor list
    const filteredSupervisors = supervisorList.filter(emp => {
      const isSameDepartment = emp.department === selectedDept;
      const isNotSelf = isEditMode ? emp.emp_id !== currentEmpId : true;
      return isSameDepartment && isNotSelf;
    });
    setSupervisorOptions(filteredSupervisors);

    // Auto-select HOD if there's only one valid option
    if (filteredHods.length === 1) {
      setFormData(prev => ({ ...prev, hod: filteredHods[0].emp_id }));
    } else if (!filteredHods.find(emp => emp.emp_id === formData.hod)) {
      setFormData(prev => ({ ...prev, hod: '' }));
    }
    
    // Auto-select Supervisor if there's only one valid option
    if (filteredSupervisors.length === 1) {
      setFormData(prev => ({ ...prev, supervisor: filteredSupervisors[0].emp_id }));
    } else if (!filteredSupervisors.find(emp => emp.emp_id === formData.supervisor)) {
      setFormData(prev => ({ ...prev, supervisor: '' }));
    }
    
  }, [formData.department, hodList, supervisorList, currentEmpId, isEditMode]);

  
  // --- Checkbox component ---
  const Checkbox = ({ label, id, checked, onChange }) => (
    <div className="flex items-center">
      <input
        id={id}
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
      />
      <label htmlFor={id} className="ml-2 text-sm font-medium text-gray-700">
        {label}
      </label>
    </div>
  );

  // --- Validation ---
  const validate = () => {
    // ... (same validation as before) ...
    // You can add more rules here if you like
    return true; 
  };

  // --- Handle Change (for all field types) ---
  const handleChange = (e) => {
    const { id, value, type, checked } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [id]: type === 'checkbox' ? (checked ? 'yes' : 'no') : value
    }));
    
    if (errors[id]) {
      setErrors(prev => ({ ...prev, [id]: null }));
    }
  };
  
  // --- Handle Save (no changes needed) ---
  const handleSave = async () => {
    setServerError(null);
    if (!validate()) return;
    setIsSaving(true);
    const employeeData = { ...formData, salary: parseFloat(formData.salary) };

    try {
      if (isEditMode) {
        await updateEmployee(employeeId, employeeData);
        alert('Employee updated successfully!');
      } else {
        await createEmployee(employeeData);
        alert('Employee created successfully!');
      }
      onDone();
    } catch (err) {
      setServerError('Failed to save employee. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <>
      <header className="flex flex-wrap items-center justify-between gap-4 p-4 m-4 bg-white rounded-lg shadow-sm">
      {/* ... (header JSX: Title, Save, Cancel buttons) ... */}
      </header>

      <main className="flex-grow p-4 pt-0">
        <div className="w-full max-w-6xl mx-auto overflow-hidden bg-white rounded-lg shadow-lg">
          <div className="px-6 py-4 bg-teal-600">
            <h2 className="text-xl font-semibold text-white">Employee Details</h2>
          </div>

          <form onSubmit={(e) => e.preventDefault()}>
            <div className="p-6 md:p-8">
              {serverError && <div className="p-3 mb-4 text-red-800 bg-red-100 border border-red-300 rounded-md">{serverError}</div>}
              
              <div className="grid grid-cols-1 gap-6 md:grid-cols-4">
                
                {/* --- Row 1 --- */}
                <FormInput label="Employee ID" id="employeeId" value={isEditMode ? `(ID: ${employeeId})` : "Auto-generated"} disabled={true} />
                <FormInput label="Employee Name" id="name" value={formData.name} onChange={handleChange} placeholder="Enter employee name" error={errors.name} />
                <FormInput label="Designation" id="designation" value={formData.designation} onChange={handleChange} placeholder="Enter designation" error={errors.designation} />
                <FormInput label="Salary" id="salary" type="number" value={formData.salary} onChange={handleChange} placeholder="Enter salary" error={errors.salary} />
                
                {/* --- Row 2 --- */}
                <FormSelect
                  label="Department"
                  id="department"
                  value={formData.department}
                  onChange={handleChange}
                  error={errors.department}
                >
                  <option value="">Select Department</option>
                  {departmentList.map(dept => (
                    <option key={dept} value={dept}>{dept}</option>
                  ))}
                </FormSelect>
                
                <FormSelect
                  label="HOD"
                  id="hod"
                  value={formData.hod}
                  onChange={handleChange}
                  error={errors.hod}
                  disabled={!formData.department}
                >
                  <option value="">Select HOD</option>
                  {hodOptions.map((emp) => (
                    <option key={emp.emp_id} value={emp.emp_id}>
                      {emp.name} ({emp.emp_id})
                    </option>
                  ))}
                </FormSelect>
                
                <FormSelect
                  label="Supervisor"
                  id="supervisor"
                  value={formData.supervisor}
                  onChange={handleChange}
                  error={errors.supervisor}
                  disabled={!formData.department}
                >
                  <option value="">Select Supervisor</option>
                  {supervisorOptions.map((emp) => (
                    <option key={emp.emp_id} value={emp.emp_id}>
                      {emp.name} ({emp.emp_id})
                    </option>
                  ))}
                </FormSelect>

                <FormSelect
                  label="Status"
                  id="status"
                  value={formData.status}
                  onChange={handleChange}
                  error={errors.status}
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </FormSelect>

                {/* --- Row 3 (Checkboxes) --- */}
                <div className="flex items-end pb-2">
                  <Checkbox
                    label="Is HOD?"
                    id="is_hod"
                    checked={formData.is_hod === 'yes'}
                    onChange={handleChange}
                  />
                </div>
                <div className="flex items-end pb-2">
                  <Checkbox
                    label="Is Supervisor?"
                    id="is_supervisor"
                    checked={formData.is_supervisor === 'yes'}
                    onChange={handleChange}
                  />
                </div>
                
              </div>
            </div>

            {/* Form Footer Buttons */}
            <div className="flex justify-end px-6 py-4 space-x-3 bg-gray-50 md:px-8">
              <Button onClick={handleSave} variant="primary" icon={Save} disabled={isSaving}>
                {isSaving ? 'Saving...' : 'Save'}
              </Button>
              <Button onClick={onDone} variant="secondary" icon={X} disabled={isSaving}>
                Cancel
              </Button>
            </div>
          </form>
        </div>
      </main>

      <footer className="py-4 mt-auto text-center text-gray-600 bg-gray-200">
        © Copyright Techspire Solutions
      </footer>
    </>
  );
}