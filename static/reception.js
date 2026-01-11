// I really need to learn JS. It's not far from Android's Kotlin.

async function handleCheckIn(event) {
    event.preventDefault();

    const inputField = document.getElementById('member-id-input');
    const statusDiv = document.getElementById('status-message');
    const idValue = inputField.value;

    statusDiv.textContent = 'Checking...';
    statusDiv.className = 'access-result'; 

    try {
        // Pointing to the Python route
        const response = await fetch('/api/check_member', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },

            body: JSON.stringify({ member_id: idValue }) // Send data as JSON.
        });

        const data = await response.json();

        if (data.exists && data.status === 'Active') {
            statusDiv.textContent = `Welcome, ${data.name}!`; // Uses the name from DB
            statusDiv.classList.add('success');
            inputField.value = ''; 
        } else if (data.status === 'Inactive') {
            statusDiv.textContent = 'Membership expired';
            statusDiv.classList.add('error');
        } else {
            statusDiv.textContent = 'Member not found.';
            statusDiv.classList.add('error');
        }

    } catch (error) {
        console.error('Error:', error);
        statusDiv.textContent = 'System error.';
        statusDiv.classList.add('error');
    }
}