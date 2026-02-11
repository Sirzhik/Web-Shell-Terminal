document.addEventListener('change', async (e) => {
    const target = e.target;
    
    if (target.getAttribute('name') === 'userGroup' && target.dataset.userId) {
        
        const userId = parseInt(target.dataset.userId);
        const groupId = parseInt(target.dataset.groupId);

        const allRadios = document.querySelectorAll('input[name="userGroup"]');
        allRadios.forEach(r => r.disabled = true);

        const payload = {
            user_id: userId,
            group_id: groupId
        };

        console.log('Sending update for user:', userId, 'to group:', groupId);

        try {
            const response = await fetch('/admin/set_group_for_user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.text();
                console.error('Server error details:', errorData);
                throw new Error(`Server returned ${response.status}`);
            }

            console.log(`Success: User ${userId} assigned to group ${groupId}`);

        } catch (error) {
            console.error('Update error:', error);
            alert('Error updating user group: ' + error.message);
        } finally {
            allRadios.forEach(r => r.disabled = false);
        }
    }
});