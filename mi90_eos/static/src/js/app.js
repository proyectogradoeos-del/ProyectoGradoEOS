function drawPie(id, segments) {
  const canvas = document.getElementById(id);
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  const total = segments.reduce((acc, seg) => acc + seg.value, 0) || 1;
  let angle = -Math.PI / 2;
  
  segments.forEach(segment => {
    const sliceAngle = (segment.value / total) * Math.PI * 2;
    ctx.beginPath();
    ctx.moveTo(canvas.width / 2, canvas.height / 2);
    ctx.arc(canvas.width / 2, canvas.height / 2, Math.min(canvas.width, canvas.height) / 2 - 2, angle, angle + sliceAngle);
    ctx.closePath();
    ctx.fillStyle = segment.color;
    ctx.fill();
    angle += sliceAngle;
  });
}

function setActive() {
  const path = location.pathname.split('/').pop() || 'dashboard';
  document.querySelectorAll('.nav a').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href.includes(path)) {
      link.classList.add('active');
    }
  });
}

// Inicializar el dashboard cuando se carga
document.addEventListener('DOMContentLoaded', function() {
  setActive();
  
  // Dibujar el gráfico de pastel para las rocas
  const rockSegments = [
    { value: 1, color: '#22c55e' }, // Completadas
    { value: 2, color: '#3b82f6' }, // En curso
    { value: 0, color: '#ef4444' }  // Fuera de curso
  ];
  
  drawPie('rockPie', rockSegments);
});
