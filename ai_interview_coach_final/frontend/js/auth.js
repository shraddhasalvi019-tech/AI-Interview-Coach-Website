document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const alertBox = document.getElementById('alert-box');

  function showAlert(message, type = 'danger') {
    alertBox.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
  }

  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;

      try {
        const data = await API.login({ email, password });
        API.setAuthToken(data.access_token);
        localStorage.setItem('user_name', data.user_name);
        localStorage.setItem('user_email', data.email);
        window.location.href = 'dashboard.html';
      } catch (err) {
        showAlert(err.message || 'Invalid email or password.');
      }
    });
  }

  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('name').value.trim();
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;

      try {
        await API.register({ name, email, password });
        showAlert('Registration successful! Logging you in...', 'success');
        
        // Auto Login
        const loginData = await API.login({ email, password });
        API.setAuthToken(loginData.access_token);
        localStorage.setItem('user_name', loginData.user_name);
        localStorage.setItem('user_email', loginData.email);
        setTimeout(() => { window.location.href = 'profile.html'; }, 800);
      } catch (err) {
        showAlert(err.message || 'Registration failed.');
      }
    });
  }
});
