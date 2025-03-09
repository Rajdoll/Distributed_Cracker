document.getElementById('hashFile').addEventListener('change', function(e) {
    console.log('Hash file selected:', e.target.files[0].name);
});

document.getElementById('wordlistFile').addEventListener('change', function(e) {
    console.log('Wordlist file selected:', e.target.files[0].name);
});

async function startCracking() {
    const hashFile = document.getElementById('hashFile').files[0];
    const wordlistFile = document.getElementById('wordlistFile').files[0];

    if (!hashFile || !wordlistFile) {
        alert('Please upload both hash and wordlist files!');
        return;
    }

    const formData = new FormData();
    formData.append('hash', hashFile);
    formData.append('wordlist', wordlistFile);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const taskId = data.task_id;

        // Mulai polling untuk memeriksa status
        const interval = setInterval(async () => {
            const statusResponse = await fetch(`/api/status/${taskId}`);
            const statusData = await statusResponse.json();

            // Update progress bar
            document.getElementById('progressBar').style.width = `${Math.min(statusData.progress, 100)}%`; // Batasi ke 100%

            // Hanya tampilkan hasil jika progress 100%
            if (statusData.progress >= 100) {
                document.getElementById('result').innerText = statusData.result;
                clearInterval(interval);
            } else {
                document.getElementById('result').innerText = "Cracking in progress...";
            }
        }, 1000);
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('result').innerText = `Error: ${error.message}`;
    }
}