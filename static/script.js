// Delete Task
const deleteButtons = document.getElementsByClassName('delete-btn');
for (const deleteButton of deleteButtons) {
  deleteButton.addEventListener('click', function () {
    const taskId = this.getAttribute('data-task-id');
    if (confirm('Are you sure you want to delete this task?')) {
      fetch(`/delete_task/${taskId}`, { method: 'POST' })
        .then(response => {
          if (response.ok) {
            location.reload();
          }
        })
        .catch(error => {
          console.error('Error:', error);
        });
    }
  });
}

// Edit Task
const editButtons = document.getElementsByClassName('edit-btn');
for (const editButton of editButtons) {
  editButton.addEventListener('click', function () {
    const taskId = this.getAttribute('data-task-id');
    location.href = `/update_task/${taskId}`;
  });
}
