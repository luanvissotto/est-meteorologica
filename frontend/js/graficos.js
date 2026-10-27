const GraficosEstacao = (() => {
  let graficoClima = null;
  let graficoAr = null;

  const estiloGrade = {
    color: "rgba(255,255,255,0.08)",
  };

  function destruir(grafico) {
    if (grafico) {
      grafico.destroy();
    }
  }

  function renderizarClima(canvasId, leituras) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      return;
    }
    const ordenadas = [...leituras].sort(
      (a, b) => new Date(a.coletada_em) - new Date(b.coletada_em)
    );
    const rotulos = ordenadas.map((item) => UtilEstacao.formatarData(item.coletada_em));
    destruir(graficoClima);
    graficoClima = new Chart(canvas, {
      type: "line",
      data: {
        labels: rotulos,
        datasets: [
          {
            label: "Temperatura (°C)",
            data: ordenadas.map((item) => item.temperatura),
            borderColor: "#ef6b6b",
            backgroundColor: "rgba(239,107,107,0.15)",
            tension: 0.35,
            fill: true,
          },
          {
            label: "Umidade (%)",
            data: ordenadas.map((item) => item.umidade),
            borderColor: "#27c7c9",
            backgroundColor: "rgba(39,199,201,0.12)",
            tension: 0.35,
            fill: true,
          },
          {
            label: "Pressão (hPa)",
            data: ordenadas.map((item) => item.pressao),
            borderColor: "#f4c95d",
            yAxisID: "y1",
            tension: 0.35,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { labels: { color: "#e8f1f8" } },
        },
        scales: {
          x: { ticks: { color: "#9fb3c8", maxTicksLimit: 8 }, grid: estiloGrade },
          y: { ticks: { color: "#9fb3c8" }, grid: estiloGrade },
          y1: {
            position: "right",
            ticks: { color: "#f4c95d" },
            grid: { drawOnChartArea: false },
          },
        },
      },
    });
  }

  function renderizarArChuva(canvasId, leituras) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      return;
    }
    const ordenadas = [...leituras].sort(
      (a, b) => new Date(a.coletada_em) - new Date(b.coletada_em)
    );
    const rotulos = ordenadas.map((item) => UtilEstacao.formatarData(item.coletada_em));
    destruir(graficoAr);
    graficoAr = new Chart(canvas, {
      type: "bar",
      data: {
        labels: rotulos,
        datasets: [
          {
            type: "line",
            label: "Qualidade do ar (ppm)",
            data: ordenadas.map((item) => item.qualidade_ar),
            borderColor: "#c084fc",
            tension: 0.3,
            yAxisID: "y",
          },
          {
            type: "bar",
            label: "Chuva (mm)",
            data: ordenadas.map((item) => item.pluviometria),
            backgroundColor: "rgba(96,165,250,0.65)",
            yAxisID: "y1",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: "#e8f1f8" } } },
        scales: {
          x: { ticks: { color: "#9fb3c8", maxTicksLimit: 8 }, grid: estiloGrade },
          y: { ticks: { color: "#c084fc" }, grid: estiloGrade },
          y1: {
            position: "right",
            ticks: { color: "#60a5fa" },
            grid: { drawOnChartArea: false },
          },
        },
      },
    });
  }

  return { renderizarClima, renderizarArChuva };
})();
