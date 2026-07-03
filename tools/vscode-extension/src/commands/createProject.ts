import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";
import { Board, Catalog, Example, GroveExample, GroveModule } from "../model/types";
import { locateCli } from "../cli/cliLocator";
import { runCapture } from "../cli/cliBridge";
import { PinAssignments, PinDiagramData } from "../panels/pinConfiguratorHtml";
import { PinConfiguratorPanel } from "../panels/pinConfiguratorPanel";

export type CreatePreset =
  | { board: Board; example?: Example }
  | { groveExample: GroveExample };

type Cli = ReturnType<typeof locateCli>;

// A fully-resolved project source, ready to hand to the CLI.
// 一个已解析完成的项目来源，可直接交给 CLI。
interface CreateSpec {
  board: Board;
  defaultName: string;
  fromAsset?: string;
  blank?: boolean;
  pinAssignments?: PinAssignments;
  pinConfig?: PinConfigRequest;
}

interface PinConfigRequest {
  boardId: string;
  source: string;
}

// Runs the create-project wizard, then calls the CLI to generate the project.
// 运行创建项目向导,然后调用 CLI 生成项目。
export async function createProject(
  repoRoot: string | undefined,
  catalog: Catalog | undefined,
  extensionUri: vscode.Uri,
  preset?: CreatePreset,
): Promise<void> {
  if (!repoRoot || !catalog) {
    void vscode.window.showErrorMessage("No seeed-zephyr repository found.");
    return;
  }
  const cli = locateCli(repoRoot);
  const spec = preset
    ? await specFromPreset(catalog, preset)
    : await specFromWizard(catalog);
  if (!spec) {
    return;
  }
  if (spec.pinConfig) {
    await runCreateWithPinConfigurator(repoRoot, cli, extensionUri, spec);
    return;
  }
  await runCreate(repoRoot, cli, spec);
}

// Resolves a spec from a Catalog node click (board example or Grove example).
// 从 Catalog 节点点击(板级示例或 Grove 示例)解析来源。
async function specFromPreset(
  catalog: Catalog,
  preset: CreatePreset,
): Promise<CreateSpec | undefined> {
  if ("groveExample" in preset) {
    return specFromGroveExample(catalog, preset.groveExample);
  }
  const board = preset.board;
  if (board.examples.length === 0) {
    void vscode.window.showErrorMessage(`${board.id} has no examples to create from.`);
    return undefined;
  }
  const example = preset.example ?? (await pickExample(board));
  if (!example) {
    return undefined;
  }
  return {
    board,
    fromAsset: `${board.id}/${example.demo}`,
    defaultName: `${board.id}_${example.demo}`,
  };
}

// Asks for the source kind first, then routes to Grove / board / blank flows.
// 先询问来源类型,再分别走 Grove / 板级 / 空白 流程。
async function specFromWizard(catalog: Catalog): Promise<CreateSpec | undefined> {
  const kind = await pickSourceKind();
  if (!kind) {
    return undefined;
  }
  if (kind === "grove") {
    const module = await pickGroveModule(catalog);
    if (!module) {
      return undefined;
    }
    const example = await pickGroveExample(module);
    if (!example) {
      return undefined;
    }
    return specFromGroveExample(catalog, example);
  }
  if (kind === "board") {
    const board = await pickBoard(catalog);
    if (!board) {
      return undefined;
    }
    const example = await pickExample(board);
    if (!example) {
      return undefined;
    }
    return {
      board,
      fromAsset: `${board.id}/${example.demo}`,
      defaultName: `${board.id}_${example.demo}`,
    };
  }
  const board = await pickAnyBoard(catalog);
  if (!board) {
    return undefined;
  }
  return { board, blank: true, defaultName: `${board.id}_app` };
}

// Resolves a Grove example into a spec: pick a board, then optional pin configuration.
// 把一个 Grove 示例解析成来源:选板子,并做可选的引脚配置。
async function specFromGroveExample(
  catalog: Catalog,
  example: GroveExample,
): Promise<CreateSpec | undefined> {
  const board = await pickBoardForGroveExample(catalog, example);
  if (!board) {
    return undefined;
  }
  const source = `grove/${example.moduleId}/${example.demo}`;
  return {
    board,
    fromAsset: source,
    defaultName: `${board.id}_${example.moduleId}_${example.demo}`,
    pinConfig: example.pinPolicy === "selectable" ? { boardId: board.id, source } : undefined,
  };
}

// Shared tail: pick a parent folder and name, call the CLI, then add the project to the workspace.
// 公共收尾:选择父目录与名称,调用 CLI,然后把项目加入工作区。
async function runCreate(repoRoot: string, cli: Cli, spec: CreateSpec): Promise<boolean> {
  const parent = await vscode.window.showOpenDialog({
    canSelectFolders: true,
    canSelectFiles: false,
    canSelectMany: false,
    openLabel: "Select parent folder",
  });
  if (!parent || parent.length === 0) {
    return false;
  }

  const name = await vscode.window.showInputBox({
    prompt: "Project folder name",
    value: spec.defaultName,
  });
  if (!name) {
    return false;
  }

  const output = path.join(parent[0].fsPath, name);
  const createArgs = [
    "create",
    "--board",
    spec.board.id,
    "--output",
    output,
    ...(spec.blank ? ["--blank"] : ["--from", spec.fromAsset ?? ""]),
    ...pinArgs(spec.pinAssignments),
  ];
  const result = await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: `Creating ${name}...` },
    () => runCapture(cli, createArgs),
  );

  if (!result.ok) {
    void vscode.window.showErrorMessage(`Create failed: ${result.message}`);
    return false;
  }

  writeProjectSettings(output, repoRoot);

  // Add the project to the current window (PlatformIO-style). Adding a folder never
  // spawns a new OS window and keeps the open tabs (catalog, pin configurator) in place.
  // 把项目加入当前窗口（PlatformIO 风格）。加入文件夹不会新开系统窗口，也保留已打开的标签。
  vscode.workspace.updateWorkspaceFolders(
    vscode.workspace.workspaceFolders?.length ?? 0,
    0,
    { uri: vscode.Uri.file(output) },
  );
  void vscode.window.showInformationMessage(`Added ${name} to this window.`);
  return true;
}

type SourceKind = "grove" | "board" | "blank";

async function pickSourceKind(): Promise<SourceKind | undefined> {
  const pick = await vscode.window.showQuickPick(
    [
      {
        label: "$(circuit-board) Grove module example",
        description: "Cross-board sensor or actuator example",
        sourceKind: "grove" as SourceKind,
      },
      {
        label: "$(chip) Board example",
        description: "Minimal demo for a specific XIAO board",
        sourceKind: "board" as SourceKind,
      },
      {
        label: "$(new-file) Blank project",
        description: "Empty Zephyr application for a XIAO board",
        sourceKind: "blank" as SourceKind,
      },
    ],
    { placeHolder: "Create a project from..." },
  );
  return pick?.sourceKind;
}

async function runCreateWithPinConfigurator(
  repoRoot: string,
  cli: Cli,
  extensionUri: vscode.Uri,
  spec: CreateSpec,
): Promise<void> {
  if (!spec.pinConfig) {
    await runCreate(repoRoot, cli, spec);
    return;
  }
  const data = await loadPinDiagram(cli, spec.pinConfig.boardId, spec.pinConfig.source);
  if (!data) {
    return;
  }
  await PinConfiguratorPanel.show({
    title: "Configure Grove Pins",
    mode: "create",
    data,
    extensionUri,
    onSave: (assignments) =>
      runCreate(repoRoot, cli, {
        ...spec,
        pinAssignments: assignments,
        pinConfig: undefined,
      }),
  });
}

async function loadPinDiagram(
  cli: Cli,
  boardId: string,
  source: string,
): Promise<PinDiagramData | undefined> {
  const pinsResult = await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: "Loading pinout..." },
    () => runCapture(cli, ["show", "pins", boardId, source, "--json"]),
  );
  if (!pinsResult.ok) {
    void vscode.window.showErrorMessage(`Pinout load failed: ${pinsResult.message}`);
    return undefined;
  }
  try {
    return JSON.parse(pinsResult.stdout) as PinDiagramData;
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    void vscode.window.showErrorMessage(`Pinout output is not valid JSON: ${detail}`);
    return undefined;
  }
}

function pinArgs(assignments: PinAssignments | undefined): string[] {
  if (!assignments) {
    return [];
  }
  const args: string[] = [];
  for (const [role, pin] of Object.entries(assignments)) {
    args.push("--pin", `${role}=${pin}`);
  }
  return args;
}

// Records the source repo in the generated project so its status bar finds the CLI.
// 把来源仓库记录到生成的工程里,让它的状态栏能找到 CLI。
function writeProjectSettings(output: string, repoRoot: string): void {
  try {
    const vscodeDir = path.join(output, ".vscode");
    fs.mkdirSync(vscodeDir, { recursive: true });
    fs.writeFileSync(
      path.join(vscodeDir, "settings.json"),
      `${JSON.stringify({ "seeedZephyr.repoRoot": repoRoot }, null, 2)}\n`,
    );
  } catch {
    // Non-fatal: the user can set seeedZephyr.repoRoot manually.
  }
}

async function pickBoard(catalog: Catalog): Promise<Board | undefined> {
  const pick = await vscode.window.showQuickPick(
    catalog.boards
      .filter((board) => board.examples.length > 0)
      .map((board) => ({ label: board.displayName, description: board.id, board })),
    { placeHolder: "Select a board" },
  );
  return pick?.board;
}

// Board picker for blank projects: any board that has a usable Zephyr target.
// 空白项目的板子选择器:任意具备可用 Zephyr target 的板子。
async function pickAnyBoard(catalog: Catalog): Promise<Board | undefined> {
  const pick = await vscode.window.showQuickPick(
    catalog.boards
      .filter((board) => board.status !== "unsupported")
      .map((board) => ({
        label: board.displayName,
        description: `${board.id} - ${board.zephyrTarget}`,
        board,
      })),
    { placeHolder: "Select a board for the blank project" },
  );
  return pick?.board;
}

async function pickGroveModule(catalog: Catalog): Promise<GroveModule | undefined> {
  const modules = catalog.modules.filter((module) => module.examples.length > 0);
  if (modules.length === 0) {
    void vscode.window.showErrorMessage("No Grove examples are available in this repository.");
    return undefined;
  }
  const pick = await vscode.window.showQuickPick(
    modules.map((module) => ({
      label: module.displayName,
      description: `${module.interface} - ${module.examples.length} example(s)`,
      module,
    })),
    { placeHolder: "Select a Grove module" },
  );
  return pick?.module;
}

async function pickGroveExample(module: GroveModule): Promise<GroveExample | undefined> {
  if (module.examples.length === 1) {
    return module.examples[0];
  }
  const pick = await vscode.window.showQuickPick(
    module.examples.map((example) => ({
      label: example.demo,
      description: example.interface,
      example,
    })),
    { placeHolder: `Select an example from ${module.displayName}` },
  );
  return pick?.example;
}

async function pickBoardForGroveExample(
  catalog: Catalog,
  example: GroveExample,
): Promise<Board | undefined> {
  const choices = catalog.boards
    .map((board) => {
      const row = example.boardStatus.find((status) => status.boardId === board.id);
      return { board, status: row?.status ?? "pending" };
    })
    .filter((choice) => choice.status !== "excluded")
    .map((choice) => ({
      label: choice.board.displayName,
      description: `${choice.board.id} - ${choice.status}`,
      board: choice.board,
    }));
  if (choices.length === 0) {
    void vscode.window.showErrorMessage(`${example.id} has no supported boards.`);
    return undefined;
  }
  const pick = await vscode.window.showQuickPick(choices, {
    placeHolder: `Select a board for ${example.demo}`,
  });
  return pick?.board;
}

async function pickExample(board: Board): Promise<Example | undefined> {
  const pick = await vscode.window.showQuickPick(
    board.examples.map((example) => ({
      label: example.demo,
      description: example.validationStatus,
      example,
    })),
    { placeHolder: "Select an example" },
  );
  return pick?.example;
}
