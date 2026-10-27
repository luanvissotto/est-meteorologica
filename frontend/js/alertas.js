async function carregarAlertas() {
  const apenasAtivos = document.getElementById("filtro-ativos").checked;
  const alertas = await ApiEstacao.alertas(apenasAtivos);
  const lista = document.getElementById("grade-alertas");
  lista.innerHTML = "";
  if (alertas.length === 0) {
    lista.innerHTML = '<p class="text-slate-300">Não há alertas para o filtro selecionado.</p>';
    return;
  }
  alertas.forEach((alerta) => {
    const card = document.createElement("article");
    card.className = "glass rounded-2xl p-5";
    card.innerHTML = `
      <div class="flex items-center justify-between gap-3">
        <h2 class="text-lg font-semibold">${alerta.estacao_nome || "Estação " + alerta.estacao_id}</h2>
        <span class="${UtilEstacao.classeSeveridade(alerta.severidade)}">${UtilEstacao.rotuloSeveridade(alerta.severidade)}</span>
      </div>
      <p class="mt-2 text-cyan-200 font-medium">${alerta.tipo.replaceAll("_", " ")}</p>
      <p class="mt-2 text-slate-300">${alerta.mensagem}</p>
      <p class="mt-3 text-sm">Valor ${UtilEstacao.formatarNumero(alerta.valor, 1)} · limiar ${UtilEstacao.formatarNumero(alerta.limiar, 1)}</p>
      <p class="text-xs text-slate-400 mt-2">${UtilEstacao.formatarData(alerta.criado_em)}</p>
    `;
    lista.appendChild(card);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  carregarAlertas();
  document.getElementById("filtro-ativos").addEventListener("change", carregarAlertas);
  window.setInterval(carregarAlertas, 10000);
});
