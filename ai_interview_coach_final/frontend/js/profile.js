document.addEventListener('DOMContentLoaded', async () => {
  const btnLogout = document.getElementById('btn-logout');
  if (btnLogout) {
    btnLogout.addEventListener('click', () => { API.clearAuth(); window.location.href = 'login.html'; });
  }

  const alertBox = document.getElementById('alert-box');
  const profileForm = document.getElementById('profile-form');

  function showAlert(msg, type = 'success') {
    alertBox.innerHTML = `<div class="alert alert-${type}">${msg}</div>`;
  }

  try {
    const profile = await API.getProfile();
    document.getElementById('full_name').value = profile.full_name || '';
    document.getElementById('education').value = profile.education || '';
    document.getElementById('target_role').value = profile.target_role || 'Java Developer';
    document.getElementById('experience_level').value = profile.experience_level || 'Fresher';
    document.getElementById('skills').value = (profile.skills || []).join(', ');
    document.getElementById('programming_languages').value = (profile.programming_languages || []).join(', ');
    document.getElementById('preferred_interview_type').value = profile.preferred_interview_type || 'Technical';
    document.getElementById('preferred_difficulty').value = profile.preferred_difficulty || 'Medium';
  } catch (err) {
    console.error('Failed to load profile:', err);
  }

  profileForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const skillsArray = document.getElementById('skills').value.split(',').map(s => s.trim()).filter(Boolean);
    const langsArray = document.getElementById('programming_languages').value.split(',').map(s => s.trim()).filter(Boolean);

    const payload = {
      full_name: document.getElementById('full_name').value.trim(),
      education: document.getElementById('education').value.trim(),
      target_role: document.getElementById('target_role').value,
      experience_level: document.getElementById('experience_level').value,
      skills: skillsArray,
      programming_languages: langsArray,
      preferred_interview_type: document.getElementById('preferred_interview_type').value,
      preferred_difficulty: document.getElementById('preferred_difficulty').value
    };

    try {
      await API.updateProfile(payload);
      showAlert('Profile saved successfully! GenAI will customize your interviews based on these settings.');
    } catch (err) {
      showAlert(err.message || 'Failed to update profile.', 'danger');
    }
  });
});
