async function carregarFiltros() {
  const estacoes = await ApiEstacao.estacoes();
  const seletor = document.getElementById("filtro-estacao-hist");
  seletor.innerHTML = '<option value="">Todas as estações</option>';
  estacoes.forEach((estacao) => {
    const option = document.createElement("option");
    option.value = estacao.id;
    option.textContent = estacao.nome;
    seletor.appendChild(option);
  });
}

async function carregarHistorico() {
  const estacaoId = document.getElementById("filtro-estacao-hist").value;
  const apenasValidas = document.getElementById("filtro-validas").checked;
  const [leituras, estatisticas] = await Promise.all([
    ApiEstacao.leituras(estacaoId, 300, apenasValidas),
    ApiEstacao.estatisticas(estacaoId, 24),
  ]);

  const painel = document.getElementById("cards-estatisticas");
  const campos = [
    ["Temperatura", estatisticas.temperatura, "°C"],
    ["Umidade", estatisticas.umidade, "%"],
    ["Pressão", estatisticas.pressao, "hPa"],
    ["Qualidade do ar", estatisticas.qualidade_ar, "ppm"],
    ["Luminosidade", estatisticas.luminosidade, "%"],
    ["Pluviometria", estatisticas.pluviometria, "mm"],
  ];
  painel.innerHTML = campos
    .map(
      ([nome, serie, unidade]) => `
      <article class="glass rounded-xl p-4">
        <h3 class="text-sm text-slate-300">${nome}</h3>
        <p class="kpi-valor">${UtilEstacao.formatarNumero(serie.media, 1, " " + unidade)}</p>
        <p class="text-xs text-slate-400">mín ${UtilEstacao.formatarNumero(serie.minimo, 1)} · máx ${UtilEstacao.formatarNumero(serie.maximo, 1)} · σ ${UtilEstacao.formatarNumero(serie.desvio_padrao, 2)}</p>
      </article>
    `
    )
    .join("");

  GraficosEstacao.renderizarClima("grafico-hist-clima", leituras.slice(0, 80));
  GraficosEstacao.renderizarArChuva("grafico-hist-ar", leituras.slice(0, 80));

  const tbody = document.getElementById("tabela-historico");
  tbody.innerHTML = "";
  leituras.forEach((leitura) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="px-3 py-2">${leitura.estacao_id}</td>
      <td class="px-3 py-2">${UtilEstacao.formatarData(leitura.coletada_em)}</td>
      <td class="px-3 py-2">${UtilEstacao.formatarNumero(leitura.temperatura, 1)}</td>
      <td class="px-3 py-2">${UtilEstacao.formatarNumero(leitura.umidade, 1)}</td>
      <td class="px-3 py-2">${UtilEstacao.formatarNumero(leitura.pressao, 1)}</td>
      <td class="px-3 py-2">${UtilEstacao.formatarNumero(leitura.qualidade_ar, 1)}</td>
      <td class="px-3 py-2">${UtilEstacao.formatarNumero(leitura.luminosidade, 1)}</td>
      <td class="px-3 py-2">${UtilEstacao.formatarNumero(leitura.pluviometria, 1)}</td>
      <td class="px-3 py-2">${leitura.valida ? "sim" : "não"}</td>
    `;
    tbody.appendChild(tr);
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  await carregarFiltros();
  await carregarHistorico();
  document.getElementById("filtro-estacao-hist").addEventListener("change", carregarHistorico);
  document.getElementById("filtro-validas").addEventListener("change", carregarHistorico);
  document.getElementById("btn-atualizar-hist").addEventListener("click", carregarHistorico);
});
