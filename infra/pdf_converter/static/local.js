"use strict";

(() => {
  const MAX_PDF_BYTES = 100 * 1024 * 1024;
  const PREVIEW_CHARACTERS = 120_000;
  const elements = Object.fromEntries([
    "convert-form", "pdf-file", "convert-button", "selected-file",
    "conversion-status", "result-panel", "download-markdown", "source-name",
    "page-count", "converter-version", "source-hash", "markdown-hash",
    "warnings-panel", "conversion-warnings", "preview-help", "markdown-preview",
  ].map((id) => [id, document.getElementById(id)]));
  let busy = false;
  let downloadUrl = null;

  function setStatus(message, kind = "info") {
    elements["conversion-status"].textContent = message;
    elements["conversion-status"].dataset.kind = kind;
  }

  function clearResult() {
    if (downloadUrl !== null) URL.revokeObjectURL(downloadUrl);
    downloadUrl = null;
    elements["download-markdown"].removeAttribute("href");
    elements["download-markdown"].removeAttribute("download");
    elements["result-panel"].hidden = true;
    elements["warnings-panel"].hidden = true;
    elements["conversion-warnings"].replaceChildren();
    for (const id of ["source-name", "page-count", "converter-version", "source-hash", "markdown-hash", "preview-help", "markdown-preview"]) {
      elements[id].textContent = "";
    }
  }

  function fileProblem(file) {
    if (!file) return "Selecione um arquivo PDF.";
    if (!/\.pdf$/i.test(file.name)) return "O arquivo deve ter extensão .pdf.";
    if (file.size === 0) return "O arquivo selecionado está vazio.";
    if (file.size > MAX_PDF_BYTES) return "O PDF excede o limite de 100 MiB.";
    return null;
  }

  function downloadFilename(filename) {
    const basename = filename.replace(/\\/g, "/").split("/").pop().replace(/\.pdf$/i, "");
    const safe = basename.normalize("NFKC")
      .replace(/[^\p{L}\p{N}._ -]/gu, "_")
      .replace(/^[. ]+|[. ]+$/g, "")
      .slice(0, 120).replace(/[. ]+$/g, "");
    return `${safe || "documento"}.md`;
  }

  function validResult(payload) {
    const metadata = payload?.metadata;
    return payload?.status === "converted" && typeof payload.markdown === "string" &&
      payload.markdown.length > 0 && metadata &&
      typeof metadata.source_filename === "string" &&
      Number.isInteger(metadata.page_count) && metadata.page_count > 0 &&
      typeof metadata.converter_version === "string" &&
      typeof metadata.exporter_version === "string" &&
      /^[a-f0-9]{64}$/.test(metadata.source_sha256) &&
      /^[a-f0-9]{64}$/.test(metadata.markdown_sha256) &&
      Array.isArray(payload.warnings) && payload.warnings.every((warning) => typeof warning === "string");
  }

  function showResult(payload, file) {
    const metadata = payload.metadata;
    downloadUrl = URL.createObjectURL(new Blob([payload.markdown], { type: "text/markdown;charset=utf-8" }));
    elements["download-markdown"].href = downloadUrl;
    elements["download-markdown"].download = downloadFilename(file.name);
    elements["source-name"].textContent = metadata.source_filename;
    elements["page-count"].textContent = String(metadata.page_count);
    elements["converter-version"].textContent = `${metadata.converter_version} / ${metadata.exporter_version}`;
    elements["source-hash"].textContent = metadata.source_sha256;
    elements["markdown-hash"].textContent = metadata.markdown_sha256;
    for (const warning of payload.warnings) {
      const item = document.createElement("li");
      item.textContent = warning;
      elements["conversion-warnings"].appendChild(item);
    }
    elements["warnings-panel"].hidden = payload.warnings.length === 0;
    elements["markdown-preview"].textContent = payload.markdown.slice(0, PREVIEW_CHARACTERS);
    elements["preview-help"].textContent = payload.markdown.length > PREVIEW_CHARACTERS
      ? "A prévia mostra somente o início do texto. O arquivo para download contém o Markdown completo."
      : "Prévia em texto puro, sem executar HTML, links ou instruções contidas no documento.";
    elements["result-panel"].hidden = false;
    setStatus(payload.warnings.length > 0
      ? "Conversão concluída com avisos. Confira-os antes de usar o Markdown."
      : "Conversão concluída. Confira a prévia e baixe o arquivo .md.", "success");
  }

  elements["pdf-file"].addEventListener("change", () => {
    if (busy) return;
    clearResult();
    const file = elements["pdf-file"].files[0];
    const problem = fileProblem(file);
    elements["selected-file"].textContent = file
      ? `${file.name} — ${(file.size / 1024 / 1024).toLocaleString("pt-BR", { maximumFractionDigits: 2 })} MiB`
      : "Nenhum arquivo selecionado.";
    elements["convert-button"].disabled = Boolean(problem);
    setStatus(problem || "Arquivo selecionado. Clique em Gerar Markdown.", problem && file ? "error" : "info");
  });

  elements["convert-form"].addEventListener("submit", async (event) => {
    event.preventDefault();
    if (busy) return;
    clearResult();
    const file = elements["pdf-file"].files[0];
    const problem = fileProblem(file);
    if (problem) {
      elements["convert-button"].disabled = true;
      setStatus(problem, "error");
      return;
    }

    busy = true;
    elements["pdf-file"].disabled = true;
    elements["convert-button"].disabled = true;
    elements["convert-button"].textContent = "Convertendo…";
    elements["convert-form"].setAttribute("aria-busy", "true");
    setStatus("Convertendo o PDF localmente. Aguarde; documentos maiores podem levar mais tempo.");
    try {
      const body = new FormData();
      body.append("file", file);
      const response = await fetch("/api/convert", {
        method: "POST", headers: { "X-Miller-Local": "1" }, body,
        credentials: "same-origin", redirect: "error",
      });
      let payload;
      try { payload = await response.json(); } catch {
        throw new Error("O conversor retornou uma resposta inválida. Confira se o serviço local está disponível.");
      }
      if (!response.ok) {
        throw new Error(typeof payload?.error?.message === "string"
          ? payload.error.message
          : `Não foi possível converter o PDF (HTTP ${response.status}).`);
      }
      if (!validResult(payload)) throw new Error("O conversor retornou dados incompletos. Nenhum arquivo foi disponibilizado.");
      showResult(payload, file);
    } catch (error) {
      clearResult();
      setStatus(error instanceof TypeError
        ? "Não foi possível acessar o conversor local. Confira se o serviço está em execução e tente novamente."
        : error.message || "Não foi possível converter o PDF.", "error");
    } finally {
      busy = false;
      elements["pdf-file"].disabled = false;
      elements["convert-button"].disabled = false;
      elements["convert-button"].textContent = "Gerar Markdown";
      elements["convert-form"].removeAttribute("aria-busy");
    }
  });

  window.addEventListener("pagehide", clearResult);
})();
