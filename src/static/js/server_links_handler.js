document.addEventListener('change', async (e) => {
    const target = e.target;
    
    if (target.type === 'checkbox' && target.dataset.groupId && target.dataset.serverId) {
        
        const groupId = target.dataset.groupId;
        const serverId = target.dataset.serverId;
        const isChecked = target.checked;

        target.disabled = true;

        const payload = {
            group_id: parseInt(groupId),
            server_id: parseInt(serverId)
        };

        const url = isChecked 
            ? '/admin/link_group_to_server' 
            : '/admin/remove_link_group_to_server';
        
        const method = isChecked ? 'POST' : 'DELETE';

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.text();
                console.error('Server error details:', errorData);
                throw new Error(`Request failed with status ${response.status}`);
            }

            console.log(`Success: ${isChecked ? 'linked' : 'unlinked'} group ${groupId} and server ${serverId}`);

        } catch (error) {
            console.error('Update error:', error);
            target.checked = !isChecked;
            alert('Error updating link: ' + error.message);
        } finally {
            target.disabled = false;
        }
    }
});