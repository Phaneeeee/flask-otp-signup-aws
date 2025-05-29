document.getElementById("signupForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const formData = new FormData(this);
  const data = Object.fromEntries(formData.entries());
  const messageBox = document.getElementById("message");
  messageBox.textContent = ""; // Clear previous messages

  try {
    // Use relative URL here for deployment
    const response = await fetch("/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (response.ok) {
      localStorage.setItem("emailForOtp", data.email);
      sessionStorage.setItem("otpMessage", "OTP sent successfully!");
      window.location.href = "/otp";
    } else {
      messageBox.textContent = result.error || "Signup failed.";
      messageBox.style.color = "red";
    }
  } catch (error) {
    console.error("Signup error:", error);
    messageBox.textContent = "Failed to signup. Please try again.";
    messageBox.style.color = "red";
  }
});
