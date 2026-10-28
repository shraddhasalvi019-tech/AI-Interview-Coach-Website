document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const interviewId = urlParams.get('id');

  if (!interviewId) {
    alert('Invalid report session ID.');
    window.location.href = 'dashboard.html';
    return;
  }

  const btnLogout = document.getElementById('btn-logout');
  if (btnLogout) { btnLogout.addEventListener('click', () => { API.clearAuth(); window.location.href = 'login.html'; }); }

  try {
    const report = await API.getDetailedReport(interviewId);

    document.getElementById('report-candidate-name').innerText = `${report.candidate_name}'s Assessment Report`;
    document.getElementById('report-target-role').innerText = `Target Role: ${report.interview_info.target_role}`;
    document.getElementById('report-overall-score').innerText = `${report.overall_score}%`;
    document.getElementById('report-date').innerText = `Date: ${new Date(report.interview_info.created_at).toLocaleDateString()}`;

    // Info Section
    document.getElementById('info-name').innerText = report.candidate_name;
    document.getElementById('info-email').innerText = report.candidate_email;
    document.getElementById('info-edu').innerText = report.candidate_education || 'B.Tech in CS';
    document.getElementById('info-exp').innerText = report.candidate_experience || 'Fresher';

    document.getElementById('info-role').innerText = report.interview_info.target_role;
    document.getElementById('info-type').innerText = report.interview_info.interview_type;
    document.getElementById('info-diff').innerText = report.interview_info.difficulty;
    document.getElementById('info-total-q').innerText = report.questions_evaluations ? report.questions_evaluations.length : 0;

    // Dimensions
    const dim = report.dimension_scores || {};
    document.getElementById('score-tech-dim').innerText = `${dim['Technical Score'] || 0}%`;
    document.getElementById('score-comm-dim').innerText = `${dim['Communication Score'] || 0}%`;
    document.getElementById('score-relev-dim').innerText = `${dim['Relevance Score'] || 0}%`;
    document.getElementById('score-corr-dim').innerText = `${dim['Correctness Score'] || 0}%`;
    document.getElementById('score-comp-dim').innerText = `${dim['Completeness Score'] || 0}%`;

    // Questions Breakdown
    const qContainer = document.getElementById('questions-evaluation-container');
    if (report.questions_evaluations && report.questions_evaluations.length > 0) {
      qContainer.innerHTML = report.questions_evaluations.map(q => `
        <div class="q-eval-card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <strong style="color: var(--primary);">Question ${q.question_order} ${q.is_follow_up ? '(Follow-up)' : ''}</strong>
            <span class="badge badge-primary">Score: ${q.score}/10</span>
          </div>
          <div style="font-weight: 600; margin-bottom: 0.75rem; color: #1e293b;">"${q.question_text}"</div>
          
          <div style="background: #ffffff; padding: 0.75rem 1rem; border-radius: 6px; border: 1px solid var(--border); font-size: 0.95rem; margin-bottom: 0.75rem;">
            <div style="font-weight: 600; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.2rem;">CANDIDATE ANSWER:</div>
            ${q.candidate_answer}
          </div>

          <div style="font-size: 0.9rem; color: var(--text-dark);">
            <p><strong>Evaluation:</strong> ${q.feedback_text}</p>
            ${q.strengths && q.strengths.length > 0 ? `<p style="color: var(--success);"><strong>What was good:</strong> ${q.strengths.join(' • ')}</p>` : ''}
            ${q.improvements && q.improvements.length > 0 ? `<p style="color: var(--danger);"><strong>What could be improved:</strong> ${q.improvements.join(' • ')}</p>` : ''}
          </div>
        </div>
      `).join('');
    } else {
      qContainer.innerHTML = `<p style="color: var(--text-muted);">No question evaluations available.</p>`;
    }

    // AI Feedback
    const fb = report.ai_feedback || {};
    document.getElementById('list-report-strengths').innerHTML = (fb.strengths || ['Strong technical vocabulary', 'Good structural flow']).map(s => `<li>${s}</li>`).join('');
    document.getElementById('list-report-gaps').innerHTML = ([...(fb.weaknesses || []), ...(fb.technical_gaps || [])]).map(g => `<li>${g}</li>`).join('');
    document.getElementById('list-report-topics').innerHTML = (fb.recommended_topics || ['Java Collections', 'Multithreading', 'REST APIs']).map(t => `<li>${t}</li>`).join('');
    document.getElementById('list-report-tips').innerHTML = (fb.tips || ['State Big-O complexity upfront', 'Provide concrete code examples']).map(tp => `<li>${tp}</li>`).join('');

    // Sample Improvements
    const sampleContainer = document.getElementById('sample-improvement-container');
    if (fb.sample_answer_improvements && fb.sample_answer_improvements.length > 0) {
      sampleContainer.innerHTML = fb.sample_answer_improvements.map(s => `
        <div style="background: #f8fafc; padding: 1rem; border-radius: 6px; border-left: 3px solid var(--success); margin-bottom: 1rem;">
          <div style="font-weight: 600; margin-bottom: 0.3rem;">Question: ${s.question || 'Sample Question'}</div>
          <div style="font-size: 0.9rem; color: var(--danger); margin-bottom: 0.4rem;">Candidate Raw Answer: ${s.candidate_answer || 'N/A'}</div>
          <div style="font-size: 0.95rem; color: var(--success); font-weight: 500;">Exemplary Model Response: ${s.improved_answer || 'N/A'}</div>
        </div>
      `).join('');
    } else {
      sampleContainer.innerHTML = `
        <div style="background: #f8fafc; padding: 1rem; border-radius: 6px; border-left: 3px solid var(--success);">
          <div style="font-weight: 600; margin-bottom: 0.3rem;">Question: Explain HashMap internal working and collision handling in Java.</div>
          <div style="font-size: 0.95rem; color: var(--success); font-weight: 500;">Model Answer: HashMap uses key.hashCode() to derive bucket indexes. Collisions are resolved using linked lists at each bucket, converting to Red-Black Trees when bucket length exceeds 8 in Java 8+ for logarithmic O(log N) lookup safety.</div>
        </div>
      `;
    }

  } catch (err) {
    alert('Failed to load detailed report: ' + err.message);
  }
});
