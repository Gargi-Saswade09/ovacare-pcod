async function loadDashboard(){

const userId = 1

const response = await fetch("http://127.0.0.1:5000/reports/" + userId)

const data = await response.json()

const table = document.getElementById("reportTable")

let latestRisk = "No data"

data.forEach(report => {

const row = `
<tr>
<td>${report.created_at}</td>
<td>${report.risk_level}</td>
<td>${report.bmi}</td>
</tr>
`

table.innerHTML += row

latestRisk = report.risk_level

})

document.getElementById("riskLevel").innerText = latestRisk

}

loadDashboard()