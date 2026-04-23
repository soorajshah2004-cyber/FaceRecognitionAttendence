// Get elements
const table = document.getElementById("table");
const emptyMsg = document.getElementById("empty-msg");

// Load attendance data from server and show in table
function loadAttendance() {
    fetch('/attendance')
        .then(res => res.json())
        .then(data => {

            // Reset table with headers
            table.innerHTML = `
                <tr>
                    <th>Name</th>
                    <th>Time</th>
                </tr>
            `;

            // Show or hide the empty message
            if (data.data.length === 0) {
                emptyMsg.style.display = "block";
            } else {
                emptyMsg.style.display = "none";
            }

            // Add each row to the table
            data.data.forEach(row => {
                let tr = document.createElement("tr");

                let name = document.createElement("td");
                name.innerText = row[0];

                let time = document.createElement("td");
                time.innerText = row[1];

                tr.appendChild(name);
                tr.appendChild(time);
                table.appendChild(tr);
            });
        });
}

// Clear attendance and reload table
function resetAttendance() {
    fetch('/reset').then(loadAttendance);
}

// Auto-refresh every 2 seconds
setInterval(loadAttendance, 2000);

// Load once immediately on page open
loadAttendance();
