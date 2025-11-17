import axios from 'axios';

const API_URL = 'http://localhost:8000/api/employees';

/**
 * Fetches all employees.
 * Corresponds to: GET /api/employees/
 */
export const getEmployees = async () => {
  try {
    const response = await axios.get(`${API_URL}/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching employees:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Fetches a single employee by their primary ID.
 * Corresponds to: GET /api/employees/{id}
 */
export const getEmployeeById = async (id) => {
  try {
    const response = await axios.get(`${API_URL}/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching employee ${id}:`, error.response?.data || error.message);
    throw error;
  }
};

/**
 * Creates a new employee.
 * Corresponds to: POST /api/employees/
 */
export const createEmployee = async (employeeData) => {
  try {
    const response = await axios.post(`${API_URL}/`, employeeData);
    return response.data;
  } catch (error) {
    console.error('Error creating employee:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Updates an existing employee by their primary ID.
 * Corresponds to: PUT /api/employees/{id}
 */
export const updateEmployee = async (id, employeeData) => {
  try {
    const response = await axios.put(`${API_URL}/${id}`, employeeData);
    return response.data;
  } catch (error) {
    console.error(`Error updating employee ${id}:`, error.response?.data || error.message);
    throw error;
  }
};

/**
 * Deletes an employee by their primary ID.
 * Corresponds to: DELETE /api/employees/{id}
 */
export const deleteEmployee = async (id) => {
  try {
    const response = await axios.delete(`${API_URL}/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting employee ${id}:`, error.response?.data || error.message);
    throw error;
  }
};

/**
 * Downloads the employee data as an Excel file.
 * Corresponds to: GET /api/employees/export-excel
 */
export const exportToExcel = async () => {
  try {
    const response = await axios.get(`${API_URL}/export-excel`, {
      responseType: 'blob',
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'employee_data.xlsx');
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
    
  } catch (error) {
    console.error('Error exporting to Excel:', error.response?.data || error.message);
    throw error;
  }
};

export const getHods = async () => {
  try {
    const response = await axios.get(`${API_URL}/hods`);
    return response.data;
  } catch (error) {
    console.error('Error fetching HODs:', error.response?.data || error.message);
    throw error;
  }
};

// --- NEW: Function to get Supervisors ---
export const getSupervisors = async () => {
  try {
    const response = await axios.get(`${API_URL}/supervisors`);
    return response.data;
  } catch (error) {
    console.error('Error fetching Supervisors:', error.response?.data || error.message);
    throw error;
  }
};