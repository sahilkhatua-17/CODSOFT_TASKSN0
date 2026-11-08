const lengthSlider = document.getElementById("lengthSlider");
const lengthDisplay = document.getElementById("lengthDisplay");
const passwordOutput = document.getElementById("passwordOutput");
const copyBtn = document.getElementById("copyBtn");
const generateBtn = document.getElementById("generateBtn");
const alertMsg = document.getElementById("alertMsg");

// Update length display as slider moves
lengthSlider.addEventListener("input", function () {
  lengthDisplay.textContent = lengthSlider.value;
});

// Fetch and display newly generated password
async function generatePassword() {
  alertMsg.textContent = "";
  alertMsg.className = "alert";

  const options = {
    length: parseInt(lengthSlider.value, 10),
    uppercase: document.getElementById("uppercase").checked,
    lowercase: document.getElementById("lowercase").checked,
    numbers: document.getElementById("numbers").checked,
    symbols: document.getElementById("symbols").checked
  };

  try {
    const res = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(options)
    });

    const data = await res.json();
    if (!res.ok) {
      alertMsg.textContent = data.error || "Could not generate password.";
      return;
    }

    passwordOutput.value = data.password;
    copyBtn.textContent = "Copy";
  } catch (err) {
    alertMsg.textContent = "Something went wrong. Please try again.";
  }
}

generateBtn.addEventListener("click", generatePassword);

// Copy password to clipboard
copyBtn.addEventListener("click", function () {
  if (!passwordOutput.value) return;

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(passwordOutput.value).then(onCopySuccess);
  } else {
    passwordOutput.select();
    document.execCommand("copy");
    onCopySuccess();
  }
});

function onCopySuccess() {
  copyBtn.textContent = "Copied!";
  alertMsg.textContent = "Password copied to clipboard!";
  alertMsg.className = "alert success";
  setTimeout(function () {
    copyBtn.textContent = "Copy";
    alertMsg.textContent = "";
    alertMsg.className = "alert";
  }, 2000);
}
