// ======================================
// API Base URL
// ======================================

const API_BASE_URL = "http://127.0.0.1:5000";


// ======================================
// USER AUTHENTICATION
// ======================================

// Signup User
async function signupUser(userData) {

try{

const response = await fetch(`${API_BASE_URL}/signup`, {

method: "POST",

headers: {
"Content-Type": "application/json"
},

body: JSON.stringify(userData)

});

const data = await response.json();

return data;

}catch(error){

console.error("Signup Error:", error);
return { error: "Unable to connect to server" };

}

}



// Login User
async function loginUser(userData) {

try{

const response = await fetch(`${API_BASE_URL}/login`, {

method: "POST",

headers: {
"Content-Type": "application/json"
},

body: JSON.stringify(userData)

});

const data = await response.json();

if(data.token){

localStorage.setItem("token", data.token);
localStorage.setItem("user", JSON.stringify(data.user));

}

return data;

}catch(error){

console.error("Login Error:", error);
return { error: "Unable to connect to server" };

}

}



// Logout
function logoutUser(){

localStorage.removeItem("token");
localStorage.removeItem("user");

window.location.href = "Login.html";

}



// ======================================
// PCOD PREDICTION
// ======================================

async function predictPCOD(testData){

try{

const response = await fetch(`${API_BASE_URL}/predict`, {

method: "POST",

headers: {
"Content-Type": "application/json"
},

body: JSON.stringify(testData)

});

const data = await response.json();

return data;

}catch(error){

console.error("Prediction Error:", error);

return { error: "Server connection failed" };

}

}



// ======================================
// SAVE TEST RESULT
// ======================================

async function saveResult(resultData){

try{

const token = localStorage.getItem("token");

const response = await fetch(`${API_BASE_URL}/save-result`, {

method:"POST",

headers:{

"Content-Type":"application/json",
"Authorization":`Bearer ${token}`

},

body:JSON.stringify(resultData)

});

const data = await response.json();

return data;

}catch(error){

console.error("Save Error:", error);

return {error:"Could not save result"};

}

}



// ======================================
// GET USER HISTORY
// ======================================

async function getUserHistory(){

try{

const token = localStorage.getItem("token");

const response = await fetch(`${API_BASE_URL}/history`, {

method:"GET",

headers:{
"Authorization":`Bearer ${token}`
}

});

const data = await response.json();

return data;

}catch(error){

console.error("History Error:", error);

return [];

}

}