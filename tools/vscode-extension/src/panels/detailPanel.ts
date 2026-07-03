import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";
import { Board, Example, ExpansionBoard, GroveExample, GroveModule } from "../model/types";
import { escapeHtml, renderHtml } from "./webviewHtml";
import { SEEED_PANEL_COLUMN } from "./panelColumn";

// A detail view target chosen from the catalog tree.
// 从目录树里选中的详情查看目标。
export type DetailTarget =
  | { kind: "example"; example: Example; board: Board }
  | { kind: "board"; board: Board }
  | { kind: "module"; module: GroveModule }
  | { kind: "groveExample"; example: GroveExample; module: GroveModule }
  | { kind: "expansion"; expansion: ExpansionBoard };

// A single reusable webview panel that shows details for the selected item.
// 一个可复用的 webview 面板,显示选中条目的详情。
export class DetailPanel {
  private static current: DetailPanel | undefined;
  private readonly panel: vscode.WebviewPanel;

  static show(target: DetailTarget): void {
    if (DetailPanel.current) {
      DetailPanel.current.update(target);
      DetailPanel.current.panel.reveal(SEEED_PANEL_COLUMN, true);
      return;
    }
    const panel = vscode.window.createWebviewPanel(
      "seeedZephyrDetail",
      "XIAO Detail",
      SEEED_PANEL_COLUMN,
      { enableScripts: false, retainContextWhenHidden: true },
    );
    DetailPanel.current = new DetailPanel(panel);
    DetailPanel.current.update(target);
  }

  private constructor(panel: vscode.WebviewPanel) {
    this.panel = panel;
    this.panel.onDidDispose(() => {
      DetailPanel.current = undefined;
    });
  }

  private update(target: DetailTarget): void {
    const { title, body } = renderTarget(target);
    this.panel.title = title;
    this.panel.webview.html = renderHtml(this.panel.webview, title, body);
  }
}

function renderTarget(target: DetailTarget): { title: string; body: string } {
  switch (target.kind) {
    case "example":
      return renderExample(target.example, target.board);
    case "board":
      return renderBoard(target.board);
    case "module":
      return renderModule(target.module);
    case "groveExample":
      return renderGroveExample(target.example, target.module);
    case "expansion":
      return renderExpansion(target.expansion);
  }
}

function badge(status: string): string {
  return `<span class="badge badge-${escapeHtml(status)}">${escapeHtml(status)}</span>`;
}

function row(key: string, value: string): string {
  return `<tr><td class="key">${escapeHtml(key)}</td><td>${value}</td></tr>`;
}

function listHtml(items: string[]): string {
  if (items.length === 0) {
    return `<span class="muted">none</span>`;
  }
  return `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

// Describes the flash path per vendor, derived from the CLI's per-board logic.
// 按厂商描述烧录方式,来源于 CLI 的板级逻辑。
function flashMethod(board: Board): string {
  switch (board.vendor) {
    case "espressif":
      return "esptool over USB serial";
    case "raspberrypi":
      return "UF2 mass storage (1200-baud bootloader request)";
    case "renesas":
      return "USB DFU bootloader (dfu-util)";
    case "silabs":
      return "PyOCD (CMSIS-DAP)";
    case "microchip":
      return "bossac (SAM-BA bootloader)";
    case "nordic":
      return board.id === "xiao_nrf52840" ? "UF2 mass storage" : "PyOCD / J-Link";
    default:
      return "see board notes";
  }
}

function renderExample(example: Example, board: Board): { title: string; body: string } {
  const title = `${board.displayName} / ${example.demo}`;
  const buildCommand = `seeed-zephyr build ${board.id} ${example.demo}`;
  const ledNote =
    example.demo === "blinky"
      ? "Uses the on-board LED via the <code>led0</code> alias."
      : board.id === "xiao_esp32c3"
        ? "This board has no on-board LED, so it ships <code>hello_world</code> instead of blinky."
        : "Prints to the Zephyr console over USB serial.";

  const fields = [
    row("Board target", `<code>${escapeHtml(example.zephyrTarget)}</code>`),
    row("Validation", badge(example.validationStatus)),
    row("Build command", `<code>${escapeHtml(buildCommand)}</code>`),
    row("Expected behavior", escapeHtml(example.expectedBehavior)),
  ];
  if (example.unsupportedReason) {
    fields.push(row("Unsupported reason", escapeHtml(example.unsupportedReason)));
  }

  const hardware = [
    row("Vendor", escapeHtml(board.vendor)),
    row("Flash method", escapeHtml(flashMethod(board))),
    row("Notes", ledNote),
  ];

  const body = `
<h1>${escapeHtml(title)} ${badge(example.validationStatus)}</h1>
<p class="subtitle">${escapeHtml(example.id)}</p>
<h2>Overview</h2>
<table>${fields.join("")}</table>
<h2>Hardware</h2>
<table>${hardware.join("")}</table>
<h2>Files</h2>
${listHtml(example.files)}
<h2>README</h2>
${readmeHtml(example.dirPath)}
`;
  return { title, body };
}

function renderBoard(board: Board): { title: string; body: string } {
  const fields = [
    row("Id", `<code>${escapeHtml(board.id)}</code>`),
    row("Vendor", escapeHtml(board.vendor)),
    row("SoC", escapeHtml(board.soc)),
    row("Zephyr target", `<code>${escapeHtml(board.zephyrTarget)}</code>`),
    row("Status", badge(board.status)),
    row("Flash method", escapeHtml(flashMethod(board))),
    row("Also known as", board.alsoKnownAs.length ? listHtml(board.alsoKnownAs) : '<span class="muted">none</span>'),
  ];
  const examples = board.examples
    .map((ex) => `<li>${escapeHtml(ex.demo)} ${badge(ex.validationStatus)}</li>`)
    .join("");
  const body = `
<h1>${escapeHtml(board.displayName)} ${badge(board.status)}</h1>
<h2>Board</h2>
<table>${fields.join("")}</table>
<h2>Examples</h2>
${examples ? `<ul>${examples}</ul>` : '<span class="muted">none</span>'}
`;
  return { title: board.displayName, body };
}

function renderModule(module: GroveModule): { title: string; body: string } {
  const fields = [
    row("Id", `<code>${escapeHtml(module.id)}</code>`),
    row("SKU", escapeHtml(module.sku)),
    row("Category", escapeHtml(module.category)),
    row("Interface", escapeHtml(module.interface)),
    row("Default address", module.defaultAddress ? `<code>${escapeHtml(module.defaultAddress)}</code>` : '<span class="muted">n/a</span>'),
    row("Default baud", module.defaultBaud !== null ? String(module.defaultBaud) : '<span class="muted">n/a</span>'),
    row("Power rail", escapeHtml(module.powerRail)),
    row("Zephyr support", escapeHtml(module.zephyrSupport)),
    row("Zephyr compatible", module.zephyrCompatible ? `<code>${escapeHtml(module.zephyrCompatible)}</code>` : '<span class="muted">n/a</span>'),
    row("Zephyr driver", module.zephyrDriver ? `<code>${escapeHtml(module.zephyrDriver)}</code>` : '<span class="muted">n/a</span>'),
  ];
  const examples = module.examples
    .map((example) => `<li>${escapeHtml(example.demo)} ${badge(primaryGroveStatus(example))}</li>`)
    .join("");
  const body = `
<h1>${escapeHtml(module.displayName)}</h1>
<p class="subtitle">${escapeHtml(module.interface)} module</p>
<h2>Module</h2>
<table>${fields.join("")}</table>
<h2>Examples</h2>
${examples ? `<ul>${examples}</ul>` : '<span class="muted">none</span>'}
<h2>Required config</h2>
${listHtml(module.requiredConfigs)}
<h2>Supported templates</h2>
${listHtml(module.supportedTemplates)}
`;
  return { title: module.displayName, body };
}

function renderGroveExample(
  example: GroveExample,
  module: GroveModule,
): { title: string; body: string } {
  const ref = `grove/${example.moduleId}/${example.demo}`;
  const title = `${module.displayName} / ${example.demo}`;
  const fields = [
    row("Example reference", `<code>${escapeHtml(ref)}</code>`),
    row("Interface", escapeHtml(example.interface)),
    row("Connector", escapeHtml(example.connector)),
    row("Pin policy", escapeHtml(example.pinPolicy)),
    row("Build command", `<code>seeed-zephyr build &lt;board_id&gt; ${escapeHtml(ref)}</code>`),
    row("Pin query", `<code>seeed-zephyr show pins &lt;board_id&gt; ${escapeHtml(ref)} --json</code>`),
    row("Expected behavior", escapeHtml(example.expectedBehavior)),
  ];
  const boardRows = example.boardStatus
    .map((status) => {
      const note = status.evidence ?? status.reason ?? "";
      return `<tr><td><code>${escapeHtml(status.boardId)}</code></td><td>${badge(status.status)}</td><td>${escapeHtml(note)}</td></tr>`;
    })
    .join("");
  const pins = example.pins.map((pin) => {
    return `${pin.role}: default ${pin.default}, allowed ${pin.allowed.join(", ")}`;
  });
  const body = `
<h1>${escapeHtml(title)} ${badge(primaryGroveStatus(example))}</h1>
<p class="subtitle">${escapeHtml(example.id)}</p>
<h2>Overview</h2>
<table>${fields.join("")}</table>
<h2>Board matrix</h2>
${boardRows ? `<table><tr><td class="key">Board</td><td class="key">Status</td><td class="key">Evidence</td></tr>${boardRows}</table>` : '<span class="muted">none</span>'}
<h2>Pin roles</h2>
${pins.length ? listHtml(pins) : '<span class="muted">fixed bus</span>'}
<h2>Files</h2>
${listHtml(example.files)}
<h2>README</h2>
${readmeHtml(example.dirPath)}
`;
  return { title, body };
}

function renderExpansion(expansion: ExpansionBoard): { title: string; body: string } {
  const fields = [
    row("Id", `<code>${escapeHtml(expansion.id)}</code>`),
    row("SKU", escapeHtml(expansion.sku)),
    row("Form factor", escapeHtml(expansion.compatibleFormFactor)),
    row("Zephyr shield", expansion.zephyrShield ? `<code>${escapeHtml(expansion.zephyrShield)}</code>` : '<span class="muted">none</span>'),
  ];
  const ports = expansion.ports
    .map((port) => `<li>${escapeHtml(port.label)} <span class="muted">(${escapeHtml(port.type)})</span></li>`)
    .join("");
  const body = `
<h1>${escapeHtml(expansion.displayName)}</h1>
<h2>Expansion board</h2>
<table>${fields.join("")}</table>
<h2>Grove ports</h2>
${ports ? `<ul>${ports}</ul>` : '<span class="muted">none</span>'}
<h2>On-board peripherals</h2>
${listHtml(expansion.onboard)}
`;
  return { title: expansion.displayName, body };
}

function primaryGroveStatus(example: GroveExample): string {
  if (example.boardStatus.some((row) => row.status === "hardware-tested")) {
    return "hardware-tested";
  }
  if (example.boardStatus.some((row) => row.status === "build-verified")) {
    return "build-verified";
  }
  if (example.boardStatus.some((row) => row.status === "build-failed")) {
    return "build-failed";
  }
  return example.boardStatus.length > 0 ? "pending" : "unknown";
}

// Reads an example README and renders it as preformatted text.
// 读取示例 README,并以预格式文本渲染。
function readmeHtml(dirPath: string): string {
  const readmePath = path.join(dirPath, "README.md");
  try {
    const text = fs.readFileSync(readmePath, "utf-8");
    return `<pre class="readme">${escapeHtml(text)}</pre>`;
  } catch {
    return `<span class="muted">No README.md in this example.</span>`;
  }
}
