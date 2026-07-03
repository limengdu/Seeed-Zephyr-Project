import * as fs from "fs";
import * as vscode from "vscode";
import {
  PadBand,
  PinAssignments,
  PinDiagramData,
  renderPinConfiguratorHtml,
} from "./pinConfiguratorHtml";
import { SEEED_PANEL_COLUMN } from "./panelColumn";

export interface PinConfiguratorOptions {
  title: string;
  mode: "create" | "edit";
  data: PinDiagramData;
  extensionUri: vscode.Uri;
  initialAssignments?: PinAssignments;
  onSave?: (assignments: PinAssignments) => Promise<void>;
}

type PinConfiguratorMessage =
  | { type: "save"; assignments?: PinAssignments }
  | { type: "reset" };

export class PinConfiguratorPanel {
  private static current: PinConfiguratorPanel | undefined;
  private readonly disposables: vscode.Disposable[] = [];
  private resolver: ((value: PinAssignments | undefined) => void) | undefined;

  private constructor(
    private readonly panel: vscode.WebviewPanel,
    private options: PinConfiguratorOptions,
  ) {
    this.panel.onDidDispose(() => this.dispose(undefined), undefined, this.disposables);
    this.panel.webview.onDidReceiveMessage(
      (message: PinConfiguratorMessage) => {
        void this.handleMessage(message);
      },
      undefined,
      this.disposables,
    );
  }

  static show(options: PinConfiguratorOptions): Promise<PinAssignments | undefined> {
    // Opens or reuses the pin configurator panel and resolves when the user saves or closes it.
    // 打开或复用引脚配置面板，并在用户保存或关闭时返回结果。
    if (PinConfiguratorPanel.current) {
      return PinConfiguratorPanel.current.update(options);
    }

    const panel = vscode.window.createWebviewPanel(
      "seeedZephyrPinConfigurator",
      "XIAO Pin Configurator",
      SEEED_PANEL_COLUMN,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
        localResourceRoots: [vscode.Uri.joinPath(options.extensionUri, "media")],
      },
    );
    const instance = new PinConfiguratorPanel(panel, options);
    PinConfiguratorPanel.current = instance;
    return instance.update(options);
  }

  private update(options: PinConfiguratorOptions): Promise<PinAssignments | undefined> {
    this.options = options;
    this.panel.title = options.title;
    this.panel.webview.html = renderPinConfiguratorHtml(this.panel.webview, {
      title: options.title,
      mode: options.mode,
      data: options.data,
      assignments: initialAssignments(options.data, options.initialAssignments),
      boardImage: this.boardImageSrc(options),
      padBand: padBandFor(options),
    });
    this.panel.reveal(SEEED_PANEL_COLUMN, true);
    return new Promise((resolve) => {
      this.resolver = resolve;
    });
  }

  // Resolves the board's front-render image to a webview URI, or undefined when absent.
  // 把板子正面渲染图解析为 webview URI,缺图时返回 undefined。
  private boardImageSrc(options: PinConfiguratorOptions): string | undefined {
    const file = vscode.Uri.joinPath(
      options.extensionUri,
      "media",
      "boards",
      `${options.data.board_id}.png`,
    );
    if (!fs.existsSync(file.fsPath)) {
      return undefined;
    }
    return this.panel.webview.asWebviewUri(file).toString();
  }

  private async handleMessage(message: PinConfiguratorMessage): Promise<void> {
    // Handles webview save messages; edit mode may persist through the supplied callback.
    // 处理 webview 保存消息；edit 模式可通过传入回调持久化。
    if (message.type !== "save") {
      return;
    }
    const assignments = message.assignments ?? {};
    if (this.options.onSave) {
      try {
        await this.options.onSave(assignments);
      } catch (error) {
        const detail = error instanceof Error ? error.message : String(error);
        void vscode.window.showErrorMessage(`Pin configuration failed: ${detail}`);
        return;
      }
    }
    this.resolver?.(assignments);
    this.resolver = undefined;
    if (this.options.mode === "edit") {
      void vscode.window.showInformationMessage("Pin configuration saved.");
    }
  }

  private dispose(value: PinAssignments | undefined): void {
    if (PinConfiguratorPanel.current === this) {
      PinConfiguratorPanel.current = undefined;
    }
    this.resolver?.(value);
    this.resolver = undefined;
    while (this.disposables.length > 0) {
      this.disposables.pop()?.dispose();
    }
  }
}

// Reads the measured pad band for this board from media/boards/pads.json.
// 从 media/boards/pads.json 读取该板测得的焊盘带。
function padBandFor(options: PinConfiguratorOptions): PadBand | undefined {
  const file = vscode.Uri.joinPath(options.extensionUri, "media", "boards", "pads.json");
  if (!fs.existsSync(file.fsPath)) {
    return undefined;
  }
  try {
    const all = JSON.parse(fs.readFileSync(file.fsPath, "utf-8")) as Record<string, PadBand>;
    const band = all[options.data.board_id];
    if (band && typeof band.top === "number" && typeof band.bottom === "number") {
      return band;
    }
  } catch {
    return undefined;
  }
  return undefined;
}

function initialAssignments(
  data: PinDiagramData,
  provided: PinAssignments | undefined,
): PinAssignments {
  const assignments: PinAssignments = {};
  for (const role of data.roles) {
    assignments[role.role] = provided?.[role.role] ?? role.assigned ?? role.default;
  }
  return assignments;
}
