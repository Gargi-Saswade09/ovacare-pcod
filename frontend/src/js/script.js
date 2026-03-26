// =============================
// Load Navbar and Footer
// =============================

function loadComponent(id, file) {
    fetch(file)
        .then(response => response.text())
        .then(data => {
            document.getElementById(id).innerHTML = data;
        });
}

document.addEventListener("DOMContentLoaded", () => {

    if (document.getElementById("navbar")) {
        loadComponent("navbar", "../components/navbar.html");
    }

    if (document.getElementById("footer")) {
        loadComponent("footer", "../components/footer.html");
    }

});


// =============================
// BMI Calculator
// =============================

function calculateBMI(weight, height) {

    height = height / 100;

    return (weight / (height * height)).toFixed(2);

}


// =============================
// PCOD Test Form Submission
// =============================

const testForm = document.getElementById("pcodForm");

if (testForm) {

testForm.addEventListener("submit", async function(e){

e.preventDefault();

const age = document.getElementById("age").value;
const weight = document.getElementById("weight").value;
const height = document.getElementById("height").value;

const irregular = document.getElementById("irregular").value;
const acne = document.getElementById("acne").value;
const hair = document.getElementById("hair").value;
const mood = document.getElementById("mood").value;
const family = document.getElementById("family").value;
const insulin = document.getElementById("insulin").value;

const bmi = calculateBMI(weight, height);

const data = {

age: Number(age),
bmi: Number(bmi),
irregular_periods: Number(irregular),
acne: Number(acne),
hair_growth: Number(hair),
mood_swings: Number(mood),
family_history: Number(family),
insulin_resistance: Number(insulin)

};

try{

const response = await fetch("http://127.0.0.1:5000/predict",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify(data)

});

const result = await response.json();

localStorage.setItem("pcod_result", JSON.stringify(result));

window.location.href = "Result.html";

}catch(error){

alert("Error connecting to server");

}

});

}


// =============================
// Display Result Page
// =============================

const resultDiv = document.getElementById("riskLevel");

if(resultDiv){

const result = JSON.parse(localStorage.getItem("pcod_result"));

if(result){

document.getElementById("riskLevel").innerText = result.risk_level;

document.getElementById("riskScore").innerText = result.risk_score + "%";

if(typeof drawRiskChart === "function"){
drawRiskChart(result.risk_score);
}

}

}


// =============================
// Dashboard Data
// =============================

const historyTable = document.getElementById("historyTable");

if(historyTable){

let results = JSON.parse(localStorage.getItem("history")) || [];

results.forEach(r => {

const row = document.createElement("tr");

row.innerHTML = `
<td>${r.date}</td>
<td>${r.risk_level}</td>
<td>${r.risk_score}%</td>
`;

historyTable.appendChild(row);

});

}