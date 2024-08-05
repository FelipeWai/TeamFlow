document.addEventListener('DOMContentLoaded', function() {
    // Select all close buttons
    const closeButtons = document.querySelectorAll('.close-button');
    
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Find the closest .message-div and hide it
            const messageDiv = this.closest('.message-div');
            if (messageDiv) {
                messageDiv.style.display = 'none';
            }
        });
    });
});