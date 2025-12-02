document.getElementById("loginForm").addEventListener("submit", async function (event) {
	    event.preventDefault();  // prevent default HTML form submit

	    const username = document.getElementById("username").value;
	    const password = document.getElementById("password").value;
	    const errorBox = document.getElementById("error");

	    // simple local password checks (your previous logic)
	    const hasLetter = /[A-Za-z]/.test(password);
	    const longEnough = password.length >= 6;

	    if (!hasLetter || !longEnough) {
		let msg = "Password must contain:";
		if (!longEnough) msg += "<br>• at least 6 characters";
		if (!hasLetter) msg += "<br>• at least one letter";
		errorBox.innerHTML = msg;
		errorBox.style.display = "block";
		return;
	    }
	    errorBox.style.display = "none";

	    // Prepare form data
	    const formData = new FormData();
	    formData.append("username", username);
	    formData.append("password", password);

	    // Send POST request to FastAPI /login
	    const response = await fetch("/login", {
		method: "POST",
		body: formData,
		redirect: "follow"
	    });

	    // If login is valid, FastAPI redirects -> browser should follow it
	    if (response.redirected) {
		window.location.href = response.url;
		return;
	    }

	    // If login failed
	    errorBox.innerHTML = "Invalid username or password.";
	    errorBox.style.display = "block";
	});

	// password reveal toggle
	const passwordField = document.getElementById("password");
	const togglePassword = document.getElementById("togglePassword");
	togglePassword.addEventListener("click", () => {
	    const type = passwordField.getAttribute("type") === "password" ? "text" : "password";
	    passwordField.setAttribute("type", type);
	    togglePassword.classList.toggle("fa-eye");
	    togglePassword.classList.toggle("fa-eye-slash");
	});