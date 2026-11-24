const areaResultado = document.getElementById("saida");

function formatar(valor) {
  if (typeof valor === "number") {
    return String(parseFloat(valor.toPrecision(10)));
  }
  return String(valor);
}

function criar(tag, texto, classe) {
  const elemento = document.createElement(tag);
  elemento.textContent = texto;
  if (classe) {
    elemento.className = classe;
  }
  return elemento;
}

function mostrarErro(mensagem) {
  const caixa = document.createElement("div");
  caixa.append(criar("p", mensagem, "msg ruim"));
  areaResultado.replaceChildren(caixa);
}

function criarTabela(linhas) {
  const colunas = [];
  for (const linha of linhas) {
    for (const nome of Object.keys(linha)) {
      if (!colunas.includes(nome)) {
        colunas.push(nome);
      }
    }
  }

  const tabela = document.createElement("table");
  const cabecalho = document.createElement("tr");
  for (const nome of colunas) {
    cabecalho.append(criar("th", nome));
  }
  tabela.append(cabecalho);

  for (const linha of linhas) {
    const tr = document.createElement("tr");
    for (const nome of colunas) {
      let texto = "";
      if (nome in linha) {
        texto = formatar(linha[nome]);
      }
      tr.append(criar("td", texto));
    }
    tabela.append(tr);
  }

  const envoltorio = document.createElement("div");
  envoltorio.className = "tabela";
  envoltorio.append(tabela);
  return envoltorio;
}

function mostrarResultado(r) {
  const caixa = document.createElement("div");

  // mensagem (verde se deu certo, vermelha se não convergiu)
  let classeMensagem = "msg";
  if (!r.sucesso) {
    classeMensagem = "msg ruim";
  }
  caixa.append(criar("p", r.mensagem, classeMensagem));

  // valor final: um número ou uma lista (x1, x2, ...)
  let textoValor = "";
  if (Array.isArray(r.valor)) {
    for (let i = 0; i < r.valor.length; i++) {
      textoValor += r.rotulo + (i + 1) + " = " + formatar(r.valor[i]) + "\n";
    }
  } else {
    textoValor = r.rotulo + " ≈ " + formatar(r.valor);
  }
  caixa.append(criar("div", textoValor, "valor"));

  // blocos extras (matrizes L e U, polinômio, derivada...)
  for (const titulo of Object.keys(r.extra)) {
    caixa.append(criar("h3", titulo));
    caixa.append(criar("pre", r.extra[titulo]));
  }

  if (r.iteracoes.length > 0) {
    caixa.append(criar("h3", "Iterações e valores intermediários"));
    caixa.append(criarTabela(r.iteracoes));
  }
  areaResultado.replaceChildren(caixa);
}

// clique no menu: mostra só o formulário escolhido
const botoesMenu = document.querySelectorAll("nav button");
const formularios = document.querySelectorAll("form");

for (const botao of botoesMenu) {
  botao.onclick = function () {
    for (const form of formularios) {
      form.hidden = (form.dataset.chave !== botao.dataset.alvo);
    }
    for (const outro of botoesMenu) {
      outro.classList.toggle("ativo", outro === botao);
    }
    document.getElementById("inicio").hidden = true;
    areaResultado.replaceChildren();
  };
}

// clique em "Calcular": envia os campos para o Flask e mostra a resposta
for (const form of formularios) {
  form.onsubmit = async function (evento) {
    evento.preventDefault();

    const dados = {};
    for (const [nome, valor] of new FormData(form)) {
      dados[nome] = valor;
    }

    try {
      const resposta = await fetch("/api/" + form.dataset.chave, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(dados),
      });
      const json = await resposta.json();
      if (resposta.ok) {
        mostrarResultado(json);
      } else {
        mostrarErro(json.erro);
      }
    } catch (erro) {
      mostrarErro("Não foi possível falar com o servidor.");
    }
  };
}
