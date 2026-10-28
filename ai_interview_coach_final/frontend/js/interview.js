document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const interviewId = urlParams.get('id');

  if (!interviewId) {
    alert('Invalid interview session ID.');
    window.location.href = 'dashboard.html';
    return;
  }

  const btnLogout = document.getElementById('btn-logout');
  if (btnLogout) {
    btnLogout.addEventListener('click', () => { window.location.href = 'dashboard.html'; });
  }

  let interviewData = null;
  let currentQuestion = null;

  try {
    interviewData = await API.getInterview(interviewId);
    document.getElementById('session-role').innerText = interviewData.target_role;
    document.getElementById('session-type').innerText = interviewData.interview_type;
    document.getElementById('session-difficulty').innerText = interviewData.difficulty;

    // Load active current question
    currentQuestion = await API.getCurrentQuestion(interviewId);
    renderQuestion(currentQuestion, interviewData);

  } catch (err) {
    alert('Failed to load interview session: ' + err.message);
  }

  const answerForm = document.getElementById('answer-form');
  const btnSubmit = document.getElementById('btn-submit-answer');
  const evalModal = document.getElementById('eval-modal');

  answerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const answerText = document.getElementById('answer-input').value.trim();
    if (!answerText || !currentQuestion) return;

    btnSubmit.disabled = true;
    btnSubmit.innerText = 'Analyzing Answer with Cloud GenAI...';

    try {
      const result = await API.submitAnswer(interviewId, currentQuestion.id, answerText);
      
      // Display Realtime AI Evaluation
      if (result.evaluation) {
        evalModal.style.display = 'block';
        document.getElementById('eval-overall-score').innerText = `${result.evaluation.overall_score}/10`;
        document.getElementById('eval-corr-score').innerText = `${result.evaluation.correctness}/10`;
        document.getElementById('eval-feedback').innerText = result.evaluation.feedback_text;
        
        if (result.evaluation.strengths && result.evaluation.strengths.length > 0) {
          document.getElementById('eval-strengths').innerText = `Strengths: ${result.evaluation.strengths.join(' • ')}`;
        }
      }

      // Keep the evaluation on screen until the candidate clicks "Next"
      evalModal.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      btnSubmit.innerText = 'Review your evaluation above';
      const btnNext = document.getElementById('btn-next-question');
      btnNext.innerHTML = result.is_interview_completed ? 'View Final Report &rarr;' : 'Next Question &rarr;';
      btnNext.onclick = () => {
        evalModal.style.display = 'none';
        document.getElementById('answer-input').value = '';
        btnSubmit.disabled = false;
        btnSubmit.innerText = 'Submit Answer & Next \u2192';

        if (result.is_interview_completed) {
          window.location.href = `result.html?id=${interviewId}`;
        } else if (result.has_follow_up && result.follow_up_question) {
          currentQuestion = result.follow_up_question;
          renderQuestion(currentQuestion, interviewData);
        } else if (result.next_question) {
          currentQuestion = result.next_question;
          renderQuestion(currentQuestion, interviewData);
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
      };

    } catch (err) {
      alert('Answer submission failed: ' + err.message);
      btnSubmit.disabled = false;
      btnSubmit.innerText = 'Submit Answer & Next \u2192';
    }
  });
});

function renderQuestion(q, interviewData) {
  document.getElementById('question-text').innerText = q.question_text;
  document.getElementById('badge-category').innerText = q.category || interviewData.interview_type;
  document.getElementById('badge-skill').innerText = q.targeted_skill || 'Core Competency';

  const isFollowUp = q.is_follow_up;
  document.getElementById('follow-up-badge').style.display = isFollowUp ? 'inline-block' : 'none';

  const order = q.question_order;
  const total = interviewData.total_questions;
  document.getElementById('question-tracker').innerText = `Question ${order} of ${total}`;

  const pct = Math.min(100, Math.round((order / total) * 100));
  document.getElementById('progress-text').innerText = `${pct}%`;
  document.getElementById('progress-bar').style.width = `${pct}%`;
}
