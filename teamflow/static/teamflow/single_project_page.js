document.addEventListener('DOMContentLoaded', function() {
    // Add Members
    const addMembersBtn = document.getElementById('add-members-btn');
    const membersDropdown = document.getElementById('members-dropdown');
    const memberSearchInput = document.getElementById('member-search');
    const memberSelect = document.getElementById('member-select');
    const assignTaskBtn = document.getElementById('assign-task-btn');
    const assignTaskForm = document.getElementById('assign-task-form');
    const endProjectBtn = document.getElementById('end-task-btn');

    if (!addMembersBtn || !membersDropdown || !memberSearchInput || !memberSelect || !assignTaskBtn || !assignTaskForm || !endProjectBtn) {
        console.error('One or more elements are missing.');
        return;
    }

    addMembersBtn.addEventListener('click', function() {
        const isDropdownVisible = membersDropdown.style.display === 'block';
        membersDropdown.style.display = isDropdownVisible ? 'none' : 'block';
        assignTaskForm.style.display = 'none';
    });

    // Fetch users from API
    fetch('/api/users/')
        .then(response => response.json())
        .then(data => {
            window.users = data;
            updateDropdown(data);
        })
        .catch(error => console.error('Error fetching users:', error));

    function updateDropdown(users) {
        memberSelect.innerHTML = '';
        users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.email; 
            option.textContent = user.username; 
            memberSelect.appendChild(option);
        });
    }

    memberSearchInput.addEventListener('input', function() {
        const query = memberSearchInput.value.toLowerCase();
        const filteredUsers = window.users.filter(user => 
            user.username.toLowerCase().includes(query)
        );
        updateDropdown(filteredUsers);
    });

    // Handle adding selected members
    document.getElementById('add-selected-members').addEventListener('click', function() {
        const selectedOptions = memberSelect.selectedOptions;
        const projectId = project.id;

        Array.from(selectedOptions).forEach(option => {
            const email = option.value;
            
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/projects/${projectId}/members/add/${email}/`; // Ensure this is the correct endpoint
            
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = getCookie('csrftoken'); 
            form.appendChild(csrfInput);
            
            // Adding the user email as data (if necessary for the backend)
            const emailInput = document.createElement('input');
            emailInput.type = 'hidden';
            emailInput.name = 'email'; // Ensure backend expects 'email'
            emailInput.value = email;
            form.appendChild(emailInput);
            
            document.body.appendChild(form);
            form.submit();
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    assignTaskBtn.addEventListener('click', function() {
        const isFormVisible = assignTaskForm.style.display === 'block';
        assignTaskForm.style.display = isFormVisible ? 'none' : 'block';
        endProjectBtn.style.display = 'inline';
        membersDropdown.style.display = 'none';
        addMembersBtn.style.display = 'inline';
    });

    // Handle task assignment form submission
    assignTaskForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const title = document.getElementById('task-title').value;
        const description = document.getElementById('task-description').value;
        const priority = document.getElementById('task-priority').value;
        const dueDate = document.getElementById('task-due-date').value;
        const assignedTo = document.getElementById('task-assigned-to').value;

        if (!title || !description || !priority || !dueDate || !assignedTo) {
            console.error('One or more form fields are missing values.');
            return;
        }

        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/projects/${project.id}/tasks/create/`; // Ensure this is the correct endpoint

        const titleInput = document.createElement('input');
        titleInput.type = 'hidden';
        titleInput.name = 'title';
        titleInput.value = title;
        form.appendChild(titleInput);

        const descriptionInput = document.createElement('input');
        descriptionInput.type = 'hidden';
        descriptionInput.name = 'description';
        descriptionInput.value = description;
        form.appendChild(descriptionInput);

        const priorityInput = document.createElement('input');
        priorityInput.type = 'hidden';
        priorityInput.name = 'priority';
        priorityInput.value = priority;
        form.appendChild(priorityInput);

        const dueDateInput = document.createElement('input');
        dueDateInput.type = 'hidden';
        dueDateInput.name = 'due_date';
        dueDateInput.value = dueDate;
        form.appendChild(dueDateInput);

        const assignedToInput = document.createElement('input');
        assignedToInput.type = 'hidden';
        assignedToInput.name = 'assigned_to';
        assignedToInput.value = assignedTo;
        form.appendChild(assignedToInput);

        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = getCookie('csrftoken');
        form.appendChild(csrfInput);

        document.body.appendChild(form);
        form.submit();
    });

    // Handle End Project button click
    endProjectBtn.addEventListener('click', function() {
        if (confirm('Are you sure you want to end this project?')) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/projects/${project.id}/delete/`; // Ensure this is the correct endpoint

            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = getCookie('csrftoken');
            form.appendChild(csrfInput);

            document.body.appendChild(form);
            form.submit();
        }
    });
});
