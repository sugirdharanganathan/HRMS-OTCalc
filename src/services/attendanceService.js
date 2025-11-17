import axios from 'axios';

// The base URL of your FastAPI backend for attendance
const API_URL = 'http://localhost:8000/api/attendance';

/**
 * Fetches all attendance records.
 * Corresponds to: GET /api/attendance/
 */
export const listAttendance = async () => {
  try {
    const response = await axios.get(`${API_URL}/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching attendance:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Creates a new attendance record.
 * Corresponds to: POST /api/attendance/
 * @param {object} attendanceData - Data matching the AttendanceCreate schema
 */
export const createAttendance = async (attendanceData) => {
  try {
    const response = await axios.post(`${API_URL}/`, attendanceData);
    return response.data;
  } catch (error) {
    console.error('Error creating attendance:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Deletes an attendance record by its ID.
 * Corresponds to: DELETE /api/attendance/{att_id}
 * @param {number} id - The ID of the attendance record
 */
export const deleteAttendance = async (id) => {
  try {
    const response = await axios.delete(`${API_URL}/${id}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting attendance:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Downloads the attendance data as an Excel file.
 * Corresponds to: GET /api/attendance/export-excel
 */
export const exportAttendanceExcel = async () => {
  try {
    const response = await axios.get(`${API_URL}/export-excel`, {
      responseType: 'blob', // Important for file downloads
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'attendance_data.xlsx');
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
    
  } catch (error) {
    console.error('Error exporting attendance to Excel:', error.response?.data || error.message);
    throw error;
  }
};

// Note: You can add `updateAttendance` here later if needed