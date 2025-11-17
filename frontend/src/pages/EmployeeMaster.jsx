import React, { useState } from 'react';
import EmployeeList from '../components/EmployeeList';
import EmployeeForm from '../components/EmployeeForm';

export default function EmployeeMaster() {
  const [view, setView] = useState('list'); // 'list', 'create', 'edit'
  const [currentEmployeeId, setCurrentEmployeeId] = useState(null);

  const showCreateForm = () => {
    setCurrentEmployeeId(null);
    setView('create');
  };

  const showEditForm = (id) => {
    setCurrentEmployeeId(id);
    setView('edit');
  };

  const showListView = () => {
    setCurrentEmployeeId(null);
    setView('list');
  };

  return (
    // --- MODIFIED LINE ---
    // Removed 'overflow-auto' and added 'h-full'
    // This div will now take up the full height of its container
    <div className="flex flex-col flex-1 h-full">
      {view === 'list' && (
        <EmployeeList
          onAddEmployee={showCreateForm}
          onEditEmployee={showEditForm}
        />
      )}
      
      {(view === 'create' || view === 'edit') && (
        <EmployeeForm
          employeeId={currentEmployeeId} // null for 'create', ID for 'edit'
          onDone={showListView} // Function to go back to the list
        />
      )}
    </div>
  );
}