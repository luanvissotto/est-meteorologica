let mapaLeaflet = null;
let camadaMarcadores = null;

// Coordenadas centrais de São José do Rio Preto - SP
const LAT_RIO_PRETO = -20.8113;
const LNG_RIO_PRETO = -49.3758;

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
    const latInicial = estacoes.length > 0 ? estacoes[0].latitude : LAT_RIO_PRETO;
    const lngInicial = estacoes.length > 0 ? estacoes[0].longitude : LNG_RIO_PRETO;
    mapaLeaflet = L.map("mapa-estacoes").setView([latInicial, lngInicial], 13);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(mapaLeaflet);
    camadaMarcadores = L.layerGroup().addTo(mapaLeaflet);
  }
  camadaMarcadores.clearLayers();

  const lista = document.getElementById("lista-estacoes-mapa");
  lista.innerHTML = "";

  if (estacoes.length === 0) {
    lista.innerHTML = '<p class="text-slate-400">Nenhuma estação cadastrada.</p>';
    return;
  }

  estacoes.forEach((estacao) => {
    const leitura = ultimas.find((item) => item.estacao_id === estacao.id);
    const popup = leitura
      ? `<strong>${estacao.nome}</strong><br><span class="text-xs text-slate-500">${estacao.cidade || "São José do Rio Preto"} - ${estacao.bairro || "SP"}</span><br>Temp: ${leitura.temperatura.toFixed(1)} °C<br>Umidade: ${leitura.umidade.toFixed(0)}%<br>Luz: ${leitura.luminosidade.toFixed(0)}%<br>Ar: ${UtilEstacao.rotuloAr(leitura.classificacao_ar)}`
      : `<strong>${estacao.nome}</strong><br><span class="text-xs text-slate-500">${estacao.cidade || "São José do Rio Preto"} - ${estacao.bairro || "SP"}</span><br><span style="color:#94a3b8">Aguardando leituras do ESP32...</span>`;
    const marcador = L.marker([estacao.latitude, estacao.longitude], {
      icon: iconePorAr(leitura ? leitura.classificacao_ar : "boa"),
    }).bindPopup(popup);
    marcador.addTo(camadaMarcadores);

    const card = document.createElement("article");
    card.className = "glass rounded-xl p-4 cursor-pointer hover:border-cyan-400/50 transition";
    card.innerHTML = `
      <div class="flex items-center justify-between gap-2">
        <h3 class="font-semibold">${estacao.nome}</h3>
        <span class="text-xs text-cyan-400">${estacao.cidade || "S. J. do Rio Preto"}</span>
      </div>
      <p class="text-sm text-slate-300 mt-1">${estacao.descricao || "Estação meteorológica ESP32"}</p>
      <p class="text-xs text-slate-400 mt-1">Coords: ${estacao.latitude.toFixed(4)}, ${estacao.longitude.toFixed(4)}</p>
      <p class="mt-2 text-sm">${leitura ? `Última temp: <strong>${UtilEstacao.formatarNumero(leitura.temperatura, 1, " °C")}</strong> | Luz: <strong>${UtilEstacao.formatarNumero(leitura.luminosidade, 0, "%")}</strong>` : '<span class="text-cyan-300">Aguardando dados do ESP32...</span>'}</p>
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
        mapaLeaflet.setView([lat, lng], 13);
        if (proximas.length > 0) {
          const maisProxima = proximas[0];
          status.textContent = `Estação mais próxima: ${maisProxima.nome} a ${maisProxima.distancia_km.toFixed(2)} km de você.`;
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

document.addEventListener("DOMContentLoaded", () => {
  carregarMapa();
  document.getElementById("btn-localizar").addEventListener("click", localizarCidadao);
  window.setInterval(carregarMapa, 10000);
});
