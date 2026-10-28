document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const interviewId = urlParams.get('id');

  if (!interviewId) {
    alert('Invalid interview session ID.');
    window.location.href = 'dashboard.html';
    return;
  }

  const btnLogout = document.getElementById('btn-logout');
  if (btnLogout) { btnLogout.addEventListener('click', () => { API.clearAuth(); window.location.href = 'login.html'; }); }

  document.getElementById('btn-view-report').href = `report.html?id=${interviewId}`;

  try {
    const interview = await API.getInterview(interviewId);
    document.getElementById('result-meta').innerText = `${interview.target_role} | ${interview.interview_type} Interview | ${interview.difficulty} Difficulty`;

    const overall = interview.overall_score || 0.0;
    document.getElementById('overall-score-display').innerText = `${overall}%`;

    let badgeText = 'Excellent Candidate Performance';
    if (overall < 60) badgeText = 'Requires Substantial Upskilling';
    else if (overall < 75) badgeText = 'Moderate Competency - Focus on Deep Concepts';
    else if (overall < 88) badgeText = 'Strong Technical Candidate';
    document.getElementById('overall-evaluation-badge').innerText = badgeText;

    document.getElementById('score-tech').innerText = `${interview.technical_score || 0}%`;
    document.getElementById('score-comm').innerText = `${interview.communication_score || 0}%`;
    document.getElementById('score-corr').innerText = `${interview.correctness_score || 0}%`;

    // Fetch Feedback
    try {
      const fb = await API.getInterviewFeedback(interviewId);
      const strList = document.getElementById('list-strengths');
      if (fb.strengths && fb.strengths.length > 0) {
        strList.innerHTML = fb.strengths.map(s => `<li>${s}</li>`).join('');
      } else {
        strList.innerHTML = `<li>Clear technical articulation</li>`;
      }

      const wkList = document.getElementById('list-weaknesses');
      const gaps = [...(fb.weaknesses || []), ...(fb.technical_gaps || [])];
      if (gaps.length > 0) {
        wkList.innerHTML = gaps.map(g => `<li>${g}</li>`).join('');
      } else {
        wkList.innerHTML = `<li>State algorithmic time and space complexity upfront</li>`;
      }
    } catch (e) {
      console.warn('Feedback not generated yet:', e);
    }

  } catch (err) {
    alert('Failed to load interview results: ' + err.message);
  }
});
