import axios from 'axios';
const API_URL = 'http://localhost:8000/api/ot-approval';

/**
 * Fetches all pending OT approval records.
 * Corresponds to: GET /api/ot-approval/pending
 */
export const getPendingApprovals = async () => {
  try {
    const response = await axios.get(`${API_URL}/pending`);
    return response.data;
  } catch (error) {
    console.error('Error fetching pending approvals:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Approves a pending OT record.
 * Corresponds to: PUT /api/ot-approval/{emp_id}/approve
 */
export const approveOt = async (empId) => {
  try {
    const payload = { approved_by: "Admin" }; 
    const response = await axios.put(`${API_URL}/${empId}/approve`, payload);
    return response.data;
  } catch (error) {
    console.error('Error approving OT:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Rejects a pending OT record.
 * Corresponds to: PUT /api/ot-approval/{emp_id}/reject
 */
export const rejectOt = async (empId) => {
  try {
    const payload = { approved_by: "Admin", approval_notes: "Rejected" };
    const response = await axios.put(`${API_URL}/${empId}/reject`, payload);
    return response.data;
  } catch (error) {
    console.error('Error rejecting OT:', error.response?.data || error.message);
    throw error;
  }
};

// --- NEW FUNCTIONS FOR THE CALCULATION PAGE ---

/**
 * Fetches ALL OT approval records, not just pending.
 * Corresponds to: GET /api/ot-approval/
 */
export const getAllApprovals = async (period_month) => {
  try {
    const params = period_month ? { period_month } : {};
    const response = await axios.get(`${API_URL}/`, { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching all approvals:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Triggers a calculation/sync for an employee and period.
 * Corresponds to: POST /api/ot-approval/sync
 */
export const syncOtCalculation = async (emp_id, period_month) => {
  try {
    const payload = { emp_id, period_month };
    const response = await axios.post(`${API_URL}/sync`, payload);
    return response.data;
  } catch (error) {
    console.error('Error syncing OT calculation:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Sends a calculated record for approval.
 * Corresponds to: POST /api/ot-approval/{emp_id}/send
 */
export const sendForApproval = async (empId) => {
  try {
    const response = await axios.post(`${API_URL}/${empId}/send`);
    return response.data;
  } catch (error) {
    console.error('Error sending for approval:', error.response?.data || error.message);
    throw error;
  }
};