const ApiEstacao = (() => {
  const BASE = "";

  async function requisitar(caminho) {
    const resposta = await fetch(`${BASE}${caminho}`, {
      headers: { Accept: "application/json" },
    });
    if (!resposta.ok) {
      const detalhe = await resposta.text();
      throw new Error(`Falha na API (${resposta.status}): ${detalhe}`);
    }
    return resposta.json();
  }

  function saude() {
    return requisitar("/api/v1/saude");
  }

  function resumo() {
    return requisitar("/api/v1/painel/resumo");
  }

  function estacoes(apenasAtivas = true) {
    return requisitar(`/api/v1/estacoes?apenas_ativas=${apenasAtivas}`);
  }

  function estacoesProximas(latitude, longitude) {
    return requisitar(`/api/v1/estacoes/proximas?latitude=${latitude}&longitude=${longitude}`);
  }

  function leituras(estacaoId = "", limite = 200, apenasValidas = true) {
    const query = new URLSearchParams({
      limite: String(limite),
      apenas_validas: String(apenasValidas),
    });
    if (estacaoId) {
      query.set("estacao_id", String(estacaoId));
    }
    return requisitar(`/api/v1/leituras?${query.toString()}`);
  }

  function ultimas() {
    return requisitar("/api/v1/leituras/ultimas");
  }

  function estatisticas(estacaoId = "", periodoHoras = 24) {
    const query = new URLSearchParams({ periodo_horas: String(periodoHoras) });
    if (estacaoId) {
      query.set("estacao_id", String(estacaoId));
    }
    return requisitar(`/api/v1/leituras/estatisticas?${query.toString()}`);
  }

  function alertas(apenasAtivos = true, estacaoId = "") {
    const query = new URLSearchParams({ apenas_ativos: String(apenasAtivos), limite: "100" });
    if (estacaoId) {
      query.set("estacao_id", String(estacaoId));
    }
    return requisitar(`/api/v1/alertas?${query.toString()}`);
  }

  return {
    saude,
    resumo,
    estacoes,
    estacoesProximas,
    leituras,
    ultimas,
    estatisticas,
    alertas,
  };
})();
