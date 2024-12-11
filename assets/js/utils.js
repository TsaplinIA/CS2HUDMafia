function copySteam64(steamID64) {
    if (!navigator.clipboard) {
        console.error("Clipboard API not supported.");
        alert("Failed to copy: Clipboard API not supported.");
        return;
    }

    navigator.clipboard.writeText(steamID64)
        .then(() => {
            // Display a success alert to the user
            successAlert(`SteamID64: ${steamID64} copied successfully!`);
        })
        .catch((error) => {
            // Log and alert the user in case of an error
            console.error("Failed to copy to clipboard:", error);
            alert("Failed to copy SteamID64. Please try again.");
        });
}

async function sendConstants(fields) {
    // Determine the base URL dynamically
    const baseUrl = window.location.origin;
    const endpointUrl = `${baseUrl}/constants/`;

    // Validate input
    if (typeof fields !== 'object' || fields === null) {
        throw new Error("Fields should be an object with field_name and value pairs.");
    }

    try {
        const response = await fetch(endpointUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(fields)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Error ${response.status}: ${errorData.detail || response.statusText}`);
        }

        const data = await response.json();
        return data;

    } catch (error) {
        console.error("Failed to send constants:", error);
        throw error;
    }
}