document.addEventListener("DOMContentLoaded", () => {
  const messageBox = document.getElementById("otpMessage");

  // Show "OTP sent successfully!" message from sessionStorage
  const otpMessage = sessionStorage.getItem("otpMessage");
  if (otpMessage) {
    messageBox.textContent = otpMessage;
    messageBox.style.color = "green";
    sessionStorage.removeItem("otpMessage"); // Clear after showing
  }
});

document.getElementById("verifyForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const otp = document.getElementById("otp").value;
  const email = localStorage.getItem("emailForOtp");
  const messageBox = document.getElementById("otpMessage");
  messageBox.textContent = "";

  if (!email) {
    messageBox.textContent = "Email not found. Please signup again.";
    messageBox.style.color = "red";
    window.location.href = "/signup";
    return;
  }

  const data = { email, otp };

  try {
    // ✅ Use relative path for deployment
    const response = await fetch("/verify-otp", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (response.ok) {
      localStorage.removeItem("emailForOtp");
      messageBox.textContent = result.message || "OTP verified successfully!";
      messageBox.style.color = "green";
      setTimeout(() => {
        window.location.href = "/login";
      }, 1500);
    } else {
      messageBox.textContent = result.error || "OTP verification failed.";
      messageBox.style.color = "red";
    }
  } catch (error) {
    console.error("OTP verification error:", error);
    messageBox.textContent = "Failed to verify OTP. Please try again.";
    messageBox.style.color = "red";
  }
});
