/**
 * Recebe os dados do app HC Webhook e guarda numa Planilha Google.
 * Também responde um resumo (passos, coração, atividade, sono) para o Claude ler.
 *
 * Passo a passo: veja google_planilhas/COMO_USAR.md
 */

// Troque por uma senha sua, só letras e números (ex.: a8Kd93mQz).
const CHAVE = 'TROQUE-ESTA-CHAVE';

const COLUNAS = ['chave', 'inicio', 'fim', 'valor', 'json'];

// ---------- Recebe os dados do celular ----------
function doPost(e) {
  if (!chaveOk_(e)) return json_({ ok: false, erro: 'chave inválida' });
  const dados = JSON.parse(e.postData.contents);
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    let total = 0;
    Object.keys(dados).forEach(function (tipo) {
      if (tipo === 'deleted' || !Array.isArray(dados[tipo])) return;
      total += salvar_(tipo, dados[tipo]);
    });
    if (Array.isArray(dados.deleted)) apagar_(dados.deleted);
    return json_({ ok: true, registros: total });
  } finally {
    lock.releaseLock();
  }
}

// ---------- Responde o resumo ----------
function doGet(e) {
  if (!chaveOk_(e)) return json_({ ok: false, erro: 'chave inválida' });
  return json_(resumo_(new Date()));
}

// ---------- Guardar ----------
function salvar_(tipo, registros) {
  const aba = aba_(tipo);
  const linhas = aba.getDataRange().getValues();
  const indice = {};
  for (let i = 1; i < linhas.length; i++) indice[linhas[i][0]] = i + 1;

  const novas = [];
  registros.forEach(function (r) {
    const inicio = r.start_time || r.time || r.session_end_time || '';
    const id = (r.metadata && r.metadata.id) || tipo + '|' + inicio;
    const linha = [id, inicio, r.end_time || r.session_end_time || '', valor_(r), JSON.stringify(r)];
    if (indice[id]) {
      aba.getRange(indice[id], 1, 1, COLUNAS.length).setValues([linha]);
    } else {
      indice[id] = -1;
      novas.push(linha);
    }
  });
  if (novas.length) {
    aba.getRange(aba.getLastRow() + 1, 1, novas.length, COLUNAS.length).setValues(novas);
  }
  return registros.length;
}

function apagar_(apagados) {
  apagados.forEach(function (d) {
    const aba = SpreadsheetApp.getActive().getSheetByName(d.type);
    if (!aba) return;
    const ids = aba.getRange(1, 1, aba.getLastRow(), 1).getValues();
    for (let i = ids.length - 1; i >= 1; i--) {
      if (ids[i][0] === d.id) aba.deleteRow(i + 1);
    }
  });
}

function valor_(r) {
  const campos = ['count', 'bpm', 'duration_seconds', 'meters', 'calories', 'kilograms', 'percentage'];
  for (let i = 0; i < campos.length; i++) {
    if (r[campos[i]] !== undefined) return r[campos[i]];
  }
  return '';
}

function aba_(nome) {
  const planilha = SpreadsheetApp.getActive();
  let aba = planilha.getSheetByName(nome);
  if (!aba) {
    aba = planilha.insertSheet(nome);
    aba.getRange(1, 1, 1, COLUNAS.length).setValues([COLUNAS]);
    aba.setFrozenRows(1);
  }
  return aba;
}

// ---------- Ler ----------
function registros_(tipo) {
  const aba = SpreadsheetApp.getActive().getSheetByName(tipo);
  if (!aba || aba.getLastRow() < 2) return [];
  return aba.getRange(2, 5, aba.getLastRow() - 1, 1).getValues()
    .map(function (l) { return JSON.parse(l[0]); });
}

function dia_(data, fuso) {
  return Utilities.formatDate(data, fuso, 'yyyy-MM-dd');
}

function quando_(data, fuso) {
  return Utilities.formatDate(data, fuso, "dd/MM/yyyy 'às' HH:mm");
}

function resumo_(agora) {
  const fuso = SpreadsheetApp.getActive().getSpreadsheetTimeZone();
  const hoje = dia_(agora, fuso);

  // Passos por dia
  const porDia = {};
  registros_('steps').forEach(function (r) {
    const d = dia_(new Date(r.start_time), fuso);
    porDia[d] = (porDia[d] || 0) + (r.count || 0);
  });
  const diaSemana = Number(Utilities.formatDate(agora, fuso, 'u')); // 1 = segunda
  const ultimos7 = {};
  let semana = 0;
  for (let i = 0; i < 7; i++) {
    const d = dia_(new Date(agora.getTime() - i * 86400000), fuso);
    ultimos7[d] = porDia[d] || 0;
    if (i < diaSemana) semana += porDia[d] || 0;
  }

  // Coração
  const coracao = registros_('heart_rate')
    .sort(function (a, b) { return new Date(a.time) - new Date(b.time); }).pop();

  // Atividade
  const atividade = registros_('exercise')
    .sort(function (a, b) { return new Date(a.start_time) - new Date(b.start_time); }).pop();

  // Sono
  const sono = registros_('sleep')
    .sort(function (a, b) { return new Date(a.session_end_time) - new Date(b.session_end_time); }).pop();

  return {
    gerado_em: quando_(agora, fuso),
    passos_hoje: porDia[hoje] || 0,
    passos_semana: semana,
    passos_ultimos_7_dias: ultimos7,
    ultima_frequencia_cardiaca: coracao
      ? { bpm: Math.round(coracao.bpm), quando: quando_(new Date(coracao.time), fuso) }
      : null,
    ultima_atividade: atividade
      ? {
          tipo: atividade.type,
          quando: quando_(new Date(atividade.start_time), fuso),
          minutos: Math.round((atividade.duration_seconds || 0) / 60),
          distancia_km: atividade.distance_meters ? Math.round(atividade.distance_meters / 10) / 100 : null,
        }
      : null,
    ultimo_sono: sono
      ? { horas: Math.round((sono.duration_seconds || 0) / 360) / 10, acordou: quando_(new Date(sono.session_end_time), fuso) }
      : null,
  };
}

// ---------- Utilidades ----------
function chaveOk_(e) {
  return CHAVE !== 'TROQUE-ESTA-CHAVE' && e && e.parameter && e.parameter.chave === CHAVE;
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj, null, 2))
    .setMimeType(ContentService.MimeType.JSON);
}
