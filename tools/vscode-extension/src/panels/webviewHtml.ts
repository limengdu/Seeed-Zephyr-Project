import * as vscode from "vscode";

// Builds a CSP-safe HTML document for the detail panel.
// 为详情面板构建带内容安全策略(CSP)的 HTML 文档。
export function renderHtml(webview: vscode.Webview, title: string, bodyHtml: string): string {
  const nonce = makeNonce();
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'nonce-${nonce}'; img-src ${webview.cspSource} https:;">
<style nonce="${nonce}">${STYLES}</style>
<title>${escapeHtml(title)}</title>
</head>
<body>
${bodyHtml}
</body>
</html>`;
}

// Escapes text for safe insertion into HTML.
// 对文本转义,使其能安全插入 HTML。
export function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function makeNonce(): string {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let text = "";
  for (let i = 0; i < 32; i += 1) {
    text += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return text;
}

const STYLES = `
body { font-family: var(--vscode-font-family); color: var(--vscode-foreground);
  padding: 0 18px 28px; line-height: 1.55; font-size: var(--vscode-font-size); }
h1 { font-size: 1.4em; margin: 18px 0 2px; }
h2 { font-size: 1.05em; margin: 22px 0 6px; border-bottom: 1px solid var(--vscode-panel-border);
  padding-bottom: 4px; }
.subtitle { color: var(--vscode-descriptionForeground); margin: 0 0 10px; }
table { border-collapse: collapse; width: 100%; }
td { padding: 3px 10px 3px 0; vertical-align: top; }
td.key { color: var(--vscode-descriptionForeground); white-space: nowrap; width: 1%; }
code { font-family: var(--vscode-editor-font-family); background: var(--vscode-textCodeBlock-background);
  padding: 1px 5px; border-radius: 4px; }
pre.readme { font-family: var(--vscode-editor-font-family); background: var(--vscode-textCodeBlock-background);
  padding: 12px; border-radius: 6px; overflow-x: auto; white-space: pre-wrap; }
ul { margin: 4px 0; padding-left: 20px; }
.badge { display: inline-block; padding: 2px 9px; border-radius: 10px; font-size: 0.8em;
  vertical-align: middle; }
.badge-hardware-tested { background: var(--vscode-testing-iconPassed, #2ea043); color: #fff; }
.badge-build-only { background: var(--vscode-charts-blue, #3794ff); color: #fff; }
.badge-experimental { background: var(--vscode-charts-yellow, #d7a000); color: #000; }
.badge-blocked { background: var(--vscode-errorForeground, #f14c4c); color: #fff; }
.badge-unsupported { background: var(--vscode-errorForeground, #f14c4c); color: #fff; }
.badge-unknown { background: var(--vscode-descriptionForeground, #888); color: #fff; }
.muted { color: var(--vscode-descriptionForeground); }
`;
