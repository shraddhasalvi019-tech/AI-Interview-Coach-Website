document.addEventListener('DOMContentLoaded', async () => {
  const btnLogout = document.getElementById('btn-logout');
  if (btnLogout) {
    btnLogout.addEventListener('click', () => {
      API.clearAuth();
      window.location.href = 'login.html';
    });
  }

  try {
    const data = await API.getDashboard();
    
    document.getElementById('welcome-heading').innerText = `Welcome, ${data.candidate_name}`;
    document.getElementById('target-role-sub').innerText = `Target Role: ${data.target_role}`;

    document.getElementById('stat-completed').innerText = data.interviews_completed;
    document.getElementById('stat-avg').innerText = `${data.average_score}%`;
    document.getElementById('stat-best').innerText = `${data.best_score}%`;

    document.getElementById('score-tech').innerText = `${data.technical_avg}%`;
    document.getElementById('bar-tech').style.width = `${data.technical_avg}%`;

    document.getElementById('score-comm').innerText = `${data.communication_avg}%`;
    document.getElementById('bar-comm').style.width = `${data.communication_avg}%`;

    document.getElementById('score-prob').innerText = `${data.problem_solving_avg}%`;
    document.getElementById('bar-prob').style.width = `${data.problem_solving_avg}%`;

    document.getElementById('badge-strong').innerText = data.strongest_skill;
    document.getElementById('badge-improve').innerText = data.skill_to_improve;

    // Render Recent Table
    const tbody = document.getElementById('recent-table-body');
    if (data.recent_interviews && data.recent_interviews.length > 0) {
      tbody.innerHTML = data.recent_interviews.map(i => {
        const dateStr = new Date(i.created_at).toLocaleDateString();
        const scoreStr = i.overall_score != null ? `${i.overall_score}%` : 'N/A';
        const badgeClass = i.status === 'completed' ? 'badge-success' : 'badge-warning';
        return `
          <tr>
            <td>${dateStr}</td>
            <td><strong>${i.target_role}</strong></td>
            <td>${i.interview_type}</td>
            <td><span class="badge badge-primary">${i.difficulty}</span></td>
            <td><strong>${scoreStr}</strong></td>
            <td><span class="badge ${badgeClass}">${i.status}</span></td>
            <td>
              ${i.status === 'completed' 
                ? `<a href="report.html?id=${i.id}" class="btn btn-outline" style="padding: 0.25rem 0.6rem; font-size: 0.8rem;">View Report</a>` 
                : `<a href="live_interview.html?id=${i.id}" class="btn btn-primary" style="padding: 0.25rem 0.6rem; font-size: 0.8rem;">Resume</a>`}
            </td>
          </tr>
        `;
      }).join('');
    } else {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted);">No interviews conducted yet. Click "+ Start Mock Interview" above.</td></tr>`;
    }

    // Render Canvas Chart
    renderCanvasChart(data);

  } catch (err) {
    console.error('Failed to load dashboard:', err);
  }
});

function renderCanvasChart(data) {
  const canvas = document.getElementById('perf-chart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const width = canvas.width;
  const height = canvas.height;

  ctx.clearRect(0, 0, width, height);

  const labels = ['Technical', 'Communication', 'Problem Solving', 'Overall Avg'];
  const values = [data.technical_avg, data.communication_avg, data.problem_solving_avg, data.average_score];
  const colors = ['#2563eb', '#16a34a', '#d97706', '#9333ea'];

  const barWidth = 45;
  const gap = 35;
  const startX = 40;
  const chartHeight = 150;
  const startY = height - 40;

  values.forEach((val, idx) => {
    const barH = (val / 100) * chartHeight;
    const x = startX + idx * (barWidth + gap);
    const y = startY - barH;

    // Draw Bar
    ctx.fillStyle = colors[idx];
    ctx.beginPath();
    ctx.roundRect(x, y, barWidth, barH, [6, 6, 0, 0]);
    ctx.fill();

    // Draw Value on top
    ctx.fillStyle = '#0f172a';
    ctx.font = 'bold 12px Segoe UI';
    ctx.textAlign = 'center';
    ctx.fillText(`${val}%`, x + barWidth / 2, y - 6);

    // Draw Label below
    ctx.fillStyle = '#64748b';
    ctx.font = '11px Segoe UI';
    ctx.fillText(labels[idx], x + barWidth / 2, startY + 18);
  });
}
