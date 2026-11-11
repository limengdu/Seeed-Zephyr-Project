import * as path from "path";
import * as fs from "fs";
import * as vscode from "vscode";
import { runCapture } from "../cli/cliBridge";
import { CliInvocation, locateCli } from "../cli/cliLocator";
import { Board, Catalog } from "../model/types";
import type { ProjectInfo } from "../statusBar";

export interface ProjectSettings {
  board?: string;
  port?: string;
  portDescription?: string;
}

interface SerialPortInfo {
  device: string;
  description: string;
}

export type ProjectPortDecision =
  | { kind: "keep"; port: string }
  | { kind: "assign"; port: SerialPortInfo }
  | { kind: "missing" }
  | { kind: "choose" };

// Returns how a project gets its serial port from a saved value and the detected list.
// 返回项目如何从已保存值和检测列表取得串口。
export function decideProjectPort(
  savedPort: string | undefined,
  detected: readonly SerialPortInfo[],
  forcePick: boolean,
): ProjectPortDecision {
  const saved = savedPort?.trim() || undefined;
  if (saved && !forcePick) {
    return { kind: "keep", port: saved };
  }
  if (!forcePick && detected.length === 0) {
    return { kind: "missing" };
  }
  if (!forcePick && detected.length === 1) {
    return { kind: "assign", port: detected[0] };
  }
  return { kind: "choose" };
}

interface PortPick extends vscode.QuickPickItem {
  autoDetect?: boolean;
  port?: string;
  portDescription?: string;
}

const STORAGE_PREFIX = "seeedZephyr.projectSettings:";

export function getProjectSettings(
  context: vscode.ExtensionContext,
  project: ProjectInfo,
): ProjectSettings {
  return context.globalState.get<ProjectSettings>(projectSettingsKey(project), {});
}

export function getEffectiveBoard(
  context: vscode.ExtensionContext,
  project: ProjectInfo,
): string | undefined {
  return getProjectSettings(context, project).board ?? project.board;
}

export function getEffectivePort(
  context: vscode.ExtensionContext,
  project: ProjectInfo,
): string | undefined {
  return getProjectSettings(context, project).port;
}

export async function selectProjectBoard(
  context: vscode.ExtensionContext,
  project: ProjectInfo,
  catalog: Catalog | undefined,
): Promise<string | undefined> {
  if (!catalog) {
    void vscode.window.showErrorMessage(
      "No catalog loaded. Select the repository folder first.",
    );
    return undefined;
  }
  const current = getEffectiveBoard(context, project);
  const pick = await vscode.window.showQuickPick(
    selectableBoards(catalog).map((board) => ({
      label: board.displayName,
      description: board.id,
      detail: `${board.zephyrTarget} - ${board.status}`,
      board,
      picked: board.id === current,
    })),
    { placeHolder: "Select board for this project" },
  );
  if (!pick) {
    return undefined;
  }
  await updateProjectSettings(context, project, { board: pick.board.id });
  return pick.board.id;
}

export async function selectProjectPort(
  context: vscode.ExtensionContext,
  project: ProjectInfo,
  repoRoot: string | undefined,
): Promise<string | undefined> {
  return resolveProjectPort(context, project, repoRoot, { forcePick: true });
}

export async function resolveProjectPort(
  context: vscode.ExtensionContext,
  project: ProjectInfo,
  repoRoot: string | undefined,
  options: { forcePick?: boolean } = {},
): Promise<string | undefined> {
  const current = getEffectivePort(context, project);
  const forcePick = options.forcePick === true;
  // Returns the saved port without scanning when the picker was not requested.
  // 未要求打开选择框时，直接返回已保存端口，不再扫描。
  const saved = decideProjectPort(current, [], forcePick);
  if (saved.kind === "keep") {
    return saved.port;
  }

  const ports = await listSerialPorts(context, repoRoot);
  if (!ports) {
    return undefined;
  }

  const decision = decideProjectPort(current, ports, forcePick);
  if (decision.kind === "missing") {
    void vscode.window.showWarningMessage(
      "No serial port detected. Connect a board and try again.",
    );
    return undefined;
  }
  if (decision.kind === "assign") {
    await updateProjectSettings(context, project, {
      port: decision.port.device,
      portDescription: decision.port.description,
    });
    void vscode.window.showInformationMessage(
      `Serial port detected: ${decision.port.device}`,
    );
    return decision.port.device;
  }
  if (decision.kind === "keep") {
    return decision.port;
  }

  const choices: PortPick[] = [
    {
      label: "Auto Detector",
      description: "detect at upload or monitor time",
      autoDetect: true,
      picked: !current,
    },
    ...ports.map((port) => ({
      label: port.device,
      description: port.description,
      port: port.device,
      portDescription: port.description,
      picked: port.device === current,
    })),
  ];

  const pick = await vscode.window.showQuickPick(
    choices,
    {
      title: "Select Serial Port",
      placeHolder: "Select the connected board serial port",
    },
  );
  if (!pick) {
    return undefined;
  }

  if (pick.autoDetect) {
    await updateProjectSettings(context, project, {
      port: undefined,
      portDescription: undefined,
    });
    void vscode.window.showInformationMessage("Serial port set to Auto Port.");
    return undefined;
  }

  await updateProjectSettings(context, project, {
    port: pick.port,
    portDescription: pick.portDescription,
  });
  return pick.port;
}

export function displayBoard(
  context: vscode.ExtensionContext,
  project: ProjectInfo,
): string {
  return getEffectiveBoard(context, project) ?? "Select Board";
}

export function displayPort(
  context: vscode.ExtensionContext,
  project: ProjectInfo,
): string {
  const port = getEffectivePort(context, project);
  return port ? path.basename(port) : "Auto Port";
}

async function updateProjectSettings(
  context: vscode.ExtensionContext,
  project: ProjectInfo,
  patch: ProjectSettings,
): Promise<void> {
  const next = pruneUndefined({
    ...getProjectSettings(context, project),
    ...patch,
  });
  await context.globalState.update(projectSettingsKey(project), next);
}

async function listSerialPorts(
  context: vscode.ExtensionContext,
  repoRoot: string | undefined,
): Promise<SerialPortInfo[] | undefined> {
  const cli = locateCli(repoRoot);
  const result = await runCapture(cli, ["list", "ports", "--json"]);
  if (!result.ok) {
    await showPortDetectionFailure(context, repoRoot, cli, result.message);
    return undefined;
  }
  try {
    const parsed = JSON.parse(result.stdout) as Array<Partial<SerialPortInfo>>;
    return parsed
      .filter((port) => typeof port.device === "string")
      .map((port) => ({
        device: port.device ?? "",
        description: typeof port.description === "string"
          ? port.description
          : port.device ?? "",
      }));
  } catch {
    void vscode.window.showErrorMessage(
      `Port detection returned unreadable data from ${cli.display}.`,
    );
    return undefined;
  }
}

async function showPortDetectionFailure(
  context: vscode.ExtensionContext,
  repoRoot: string | undefined,
  cli: CliInvocation,
  message: string,
): Promise<void> {
  if (isOutdatedCliMessage(message)) {
    await showOutdatedCliMessage(context, repoRoot, cli);
    return;
  }
  void vscode.window.showErrorMessage(`Port detection failed from ${cli.display}: ${message}`);
}

async function showOutdatedCliMessage(
  context: vscode.ExtensionContext,
  repoRoot: string | undefined,
  cli: CliInvocation,
): Promise<void> {
  const repoCli = repositoryCliPath(repoRoot);
  const actions = [
    ...(repoCli ? ["Use Repository CLI"] : []),
    "Install Latest CLI",
    "Select CLI Path",
  ];
  const picked = await vscode.window.showErrorMessage(
    `${cli.display} is too old for serial port detection. Update the CLI or select the repository CLI.`,
    ...actions,
  );

  if (picked === "Use Repository CLI" && repoCli) {
    await vscode.workspace
      .getConfiguration("seeedZephyr")
      .update("cliPath", repoCli, vscode.ConfigurationTarget.Global);
    void vscode.window.showInformationMessage(`CLI selected: ${repoCli}`);
    return;
  }
  if (picked === "Install Latest CLI") {
    await vscode.commands.executeCommand("seeedZephyr.installManagedCli");
    return;
  }
  if (picked === "Select CLI Path") {
    await vscode.commands.executeCommand("seeedZephyr.selectCliPath");
  }
}

function isOutdatedCliMessage(message: string): boolean {
  return (
    message.includes("invalid choice: 'ports'") ||
    message.includes('invalid choice: "ports"') ||
    message.includes("choose from boards, examples, grove, expansion")
  );
}

function repositoryCliPath(repoRoot: string | undefined): string | undefined {
  if (!repoRoot) {
    return undefined;
  }
  const wrapper = path.join(repoRoot, "scripts", "seeed-zephyr");
  return isExecutable(wrapper) ? wrapper : undefined;
}

function isExecutable(file: string): boolean {
  try {
    fs.accessSync(file, fs.constants.X_OK);
    return true;
  } catch {
    return false;
  }
}

function selectableBoards(catalog: Catalog): Board[] {
  return catalog.boards.filter((board) => board.status !== "unsupported");
}

function projectSettingsKey(project: ProjectInfo): string {
  return `${STORAGE_PREFIX}${project.appDir}`;
}

function pruneUndefined(settings: ProjectSettings): ProjectSettings {
  return Object.fromEntries(
    Object.entries(settings).filter(([, value]) => value !== undefined && value !== ""),
  ) as ProjectSettings;
}
