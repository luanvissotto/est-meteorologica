async function carregarDashboard() {
  const statusEl = document.getElementById("status-api");
  const seletor = document.getElementById("filtro-estacao");
  const kpis = {
    temperatura: document.getElementById("kpi-temperatura"),
    umidade: document.getElementById("kpi-umidade"),
    pressao: document.getElementById("kpi-pressao"),
    ar: document.getElementById("kpi-ar"),
    chuva: document.getElementById("kpi-chuva"),
    alertas: document.getElementById("kpi-alertas"),
  };

  try {
    const [saude, resumo, estacoes, ultimas, alertas] = await Promise.all([
      ApiEstacao.saude(),
      ApiEstacao.resumo(),
      ApiEstacao.estacoes(),
      ApiEstacao.ultimas(),
      ApiEstacao.alertas(true),
    ]);

    statusEl.textContent = `API ${saude.status} · ${estacoes.length} estações ativas`;
    kpis.temperatura.textContent = UtilEstacao.formatarNumero(resumo.media_temperatura, 1, " °C");
    kpis.umidade.textContent = UtilEstacao.formatarNumero(resumo.media_umidade, 1, " %");
    kpis.chuva.textContent = UtilEstacao.formatarNumero(resumo.acumulado_chuva_24h, 1, " mm");
    kpis.alertas.textContent = String(resumo.alertas_ativos);
    kpis.ar.textContent = UtilEstacao.formatarNumero(resumo.media_qualidade_ar, 0, " ppm");

    const pressoes = ultimas.map((item) => item.pressao);
    const pressaoMedia = pressoes.length
      ? pressoes.reduce((acc, valor) => acc + valor, 0) / pressoes.length
      : null;
    kpis.pressao.textContent = UtilEstacao.formatarNumero(pressaoMedia, 1, " hPa");

    const valorAtual = seletor.value;
    seletor.innerHTML = '<option value="">Todas as estações</option>';
    estacoes.forEach((estacao) => {
      const option = document.createElement("option");
      option.value = estacao.id;
      option.textContent = `${estacao.nome} · ${estacao.bairro}`;
      seletor.appendChild(option);
    });
    if (valorAtual) {
      seletor.value = valorAtual;
    }

    const estacaoId = seletor.value;
    const serie = await ApiEstacao.leituras(estacaoId, 48, true);
    GraficosEstacao.renderizarClima("grafico-clima", serie);
    GraficosEstacao.renderizarArChuva("grafico-ar", serie);

    const tbody = document.getElementById("tabela-ultimas");
    tbody.innerHTML = "";
    ultimas.forEach((leitura) => {
      const estacao = estacoes.find((item) => item.id === leitura.estacao_id);
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="px-3 py-2">${estacao ? estacao.nome : leitura.estacao_id}</td>
        <td class="px-3 py-2">${UtilEstacao.formatarNumero(leitura.temperatura, 1, " °C")}</td>
        <td class="px-3 py-2">${UtilEstacao.formatarNumero(leitura.umidade, 0, "%")}</td>
        <td class="px-3 py-2">${UtilEstacao.formatarNumero(leitura.pressao, 1)}</td>
        <td class="px-3 py-2">
          <span class="px-2 py-1 rounded-full text-xs ${UtilEstacao.classeAr(leitura.classificacao_ar)}">
            ${UtilEstacao.rotuloAr(leitura.classificacao_ar)}
          </span>
        </td>
        <td class="px-3 py-2">${UtilEstacao.formatarNumero(leitura.pluviometria, 1, " mm")}</td>
        <td class="px-3 py-2">${UtilEstacao.formatarData(leitura.coletada_em)}</td>
      `;
      tbody.appendChild(tr);
    });

    const listaAlertas = document.getElementById("lista-alertas");
    listaAlertas.innerHTML = "";
    if (alertas.length === 0) {
      listaAlertas.innerHTML = '<p class="text-slate-300">Nenhum alerta climático ativo neste momento.</p>';
    } else {
      alertas.slice(0, 6).forEach((alerta) => {
        const card = document.createElement("article");
        card.className = "glass rounded-xl p-4";
        card.innerHTML = `
          <div class="flex items-center justify-between gap-3 mb-2">
            <h3 class="font-semibold">${alerta.estacao_nome || "Estação " + alerta.estacao_id}</h3>
            <span class="${UtilEstacao.classeSeveridade(alerta.severidade)}">${UtilEstacao.rotuloSeveridade(alerta.severidade)}</span>
          </div>
          <p class="text-sm text-slate-300">${alerta.mensagem}</p>
          <p class="text-xs text-slate-400 mt-2">${UtilEstacao.formatarData(alerta.criado_em)}</p>
        `;
        listaAlertas.appendChild(card);
      });
    }
  } catch (erro) {
    statusEl.textContent = `Falha ao conectar na API: ${erro.message}`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const seletor = document.getElementById("filtro-estacao");
  seletor.addEventListener("change", carregarDashboard);
  carregarDashboard();
  window.setInterval(carregarDashboard, 8000);
});
