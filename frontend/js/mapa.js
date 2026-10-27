let mapaLeaflet = null;
let camadaMarcadores = null;

function iconePorAr(classificacao) {
  const cores = {
    boa: "#22c55e",
    moderada: "#84cc16",
    ruim_para_sensiveis: "#eab308",
    insalubre: "#f97316",
    muito_insalubre: "#ef4444",
    perigosa: "#d946ef",
  };
  const cor = cores[classificacao] || "#27c7c9";
  return L.divIcon({
    className: "",
    html: `<div style="width:18px;height:18px;border-radius:50%;background:${cor};border:2px solid white;box-shadow:0 0 0 4px rgba(39,199,201,0.25)"></div>`,
    iconSize: [18, 18],
  });
}

async function carregarMapa() {
  const [estacoes, ultimas] = await Promise.all([ApiEstacao.estacoes(), ApiEstacao.ultimas()]);
  if (!mapaLeaflet) {
    mapaLeaflet = L.map("mapa-estacoes").setView([-23.56, -46.65], 13);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap",
    }).addTo(mapaLeaflet);
    camadaMarcadores = L.layerGroup().addTo(mapaLeaflet);
  }
  camadaMarcadores.clearLayers();

  const lista = document.getElementById("lista-estacoes-mapa");
  lista.innerHTML = "";

  estacoes.forEach((estacao) => {
    const leitura = ultimas.find((item) => item.estacao_id === estacao.id);
    const popup = leitura
      ? `<strong>${estacao.nome}</strong><br>${estacao.bairro}<br>Temp: ${leitura.temperatura.toFixed(1)} °C<br>Umidade: ${leitura.umidade.toFixed(0)}%<br>Ar: ${UtilEstacao.rotuloAr(leitura.classificacao_ar)}`
      : `<strong>${estacao.nome}</strong><br>Sem leituras ainda`;
    const marcador = L.marker([estacao.latitude, estacao.longitude], {
      icon: iconePorAr(leitura ? leitura.classificacao_ar : "moderada"),
    }).bindPopup(popup);
    marcador.addTo(camadaMarcadores);

    const card = document.createElement("article");
    card.className = "glass rounded-xl p-4";
    card.innerHTML = `
      <h3 class="font-semibold">${estacao.nome}</h3>
      <p class="text-sm text-slate-300">${estacao.bairro} · ${estacao.cidade}</p>
      <p class="text-xs text-slate-400 mt-1">${estacao.latitude.toFixed(4)}, ${estacao.longitude.toFixed(4)}</p>
      <p class="mt-2">${leitura ? UtilEstacao.formatarNumero(leitura.temperatura, 1, " °C") : "--"}</p>
    `;
    card.addEventListener("click", () => {
      mapaLeaflet.setView([estacao.latitude, estacao.longitude], 15);
      marcador.openPopup();
    });
    lista.appendChild(card);
  });
}

async function localizarCidadao() {
  const status = document.getElementById("status-geo");
  if (!navigator.geolocation) {
    status.textContent = "Geolocalização não suportada neste navegador.";
    return;
  }
  status.textContent = "Obtendo sua posição...";
  navigator.geolocation.getCurrentPosition(
    async (posicao) => {
      try {
        const lat = posicao.coords.latitude;
        const lng = posicao.coords.longitude;
        const proximas = await ApiEstacao.estacoesProximas(lat, lng);
        if (!mapaLeaflet) {
          await carregarMapa();
        }
        L.circleMarker([lat, lng], {
          radius: 8,
          color: "#f4c95d",
          fillColor: "#f4c95d",
          fillOpacity: 0.9,
        })
          .bindPopup("Você está aqui")
          .addTo(mapaLeaflet);
        mapaLeaflet.setView([lat, lng], 14);
        if (proximas.length > 0) {
          const maisProxima = proximas[0];
          status.textContent = `Estação mais próxima: ${maisProxima.nome} a ${maisProxima.distancia_km.toFixed(2)} km (vetor Δx=${maisProxima.vetor.dx_km} km, Δy=${maisProxima.vetor.dy_km} km).`;
        } else {
          status.textContent = "Nenhuma estação ativa encontrada.";
        }
      } catch (erro) {
        status.textContent = erro.message;
      }
    },
    () => {
      status.textContent = "Não foi possível obter a localização. Permita o acesso no navegador.";
    }
  );
}

document.addEventListener("DOMContentLoaded", async () => {
  try {
    await carregarMapa();
  } catch (erro) {
    document.getElementById("status-geo").textContent = erro.message;
  }
  document.getElementById("btn-localizar").addEventListener("click", localizarCidadao);
  window.setInterval(carregarMapa, 15000);
});
