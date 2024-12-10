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