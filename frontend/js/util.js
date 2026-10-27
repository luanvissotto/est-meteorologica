const UtilEstacao = (() => {
  function formatarNumero(valor, casas = 1, sufixo = "") {
    if (valor === null || valor === undefined || Number.isNaN(Number(valor))) {
      return "--";
    }
    return `${Number(valor).toFixed(casas)}${sufixo}`;
  }

  function formatarData(iso) {
    if (!iso) {
      return "sem registro";
    }
    const data = new Date(iso);
    return data.toLocaleString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function classeAr(classificacao) {
    const mapa = {
      boa: "bg-emerald-700 text-emerald-100",
      moderada: "bg-lime-700 text-lime-100",
      ruim_para_sensiveis: "bg-yellow-700 text-yellow-100",
      insalubre: "bg-orange-700 text-orange-100",
      muito_insalubre: "bg-red-800 text-red-100",
      perigosa: "bg-fuchsia-900 text-fuchsia-100",
    };
    return mapa[classificacao] || "bg-slate-700 text-slate-100";
  }

  function rotuloAr(classificacao) {
    const mapa = {
      boa: "Boa",
      moderada: "Moderada",
      ruim_para_sensiveis: "Ruim para sensíveis",
      insalubre: "Insalubre",
      muito_insalubre: "Muito insalubre",
      perigosa: "Perigosa",
    };
    return mapa[classificacao] || classificacao;
  }

  function classeSeveridade(severidade) {
    return `badge-sev-${severidade}`;
  }

  function rotuloSeveridade(severidade) {
    const mapa = {
      critica: "Crítica",
      alta: "Alta",
      media: "Média",
      baixa: "Baixa",
    };
    return mapa[severidade] || severidade;
  }

  return {
    formatarNumero,
    formatarData,
    classeAr,
    rotuloAr,
    classeSeveridade,
    rotuloSeveridade,
  };
})();
