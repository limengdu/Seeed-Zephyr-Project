import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";

export type CliSource = "configured" | "managed" | "repo" | "path" | "missing";

export interface CliState {
  found: boolean;
  source: CliSource;
  command: string;
  display: string;
}

export interface EnvironmentState {
  ready: boolean;
  repoRoot: string | undefined;
  cli: CliState;
  issues: string[];
}

// Detects the repository and CLI state used to decide whether catalog actions are enabled.
// 检测仓库和 CLI 状态，用于判断目录操作是否可用。
export function detectEnvironment(
  repoRoot: string | undefined,
  storagePath: string,
): EnvironmentState {
  const cli = detectCli(repoRoot, storagePath);
  const issues: string[] = [];
  if (!repoRoot) {
    issues.push("Repository folder is not selected.");
  }
  if (!cli.found) {
    issues.push("seeed-zephyr CLI is not configured.");
  }
  return {
    ready: Boolean(repoRoot && cli.found),
    repoRoot,
    cli,
    issues,
  };
}

export function managedCliPath(storagePath: string): string {
  const venvDir = managedCliVenvPath(storagePath);
  if (process.platform === "win32") {
    return path.join(venvDir, "Scripts", "seeed-zephyr.exe");
  }
  return path.join(venvDir, "bin", "seeed-zephyr");
}

export function managedCliPythonPath(storagePath: string): string {
  const venvDir = managedCliVenvPath(storagePath);
  if (process.platform === "win32") {
    return path.join(venvDir, "Scripts", "python.exe");
  }
  return path.join(venvDir, "bin", "python");
}

export function managedCliVenvPath(storagePath: string): string {
  return path.join(storagePath, "managed-cli-py312");
}

function detectCli(repoRoot: string | undefined, storagePath: string): CliState {
  const config = vscode.workspace.getConfiguration("seeedZephyr");
  const configured = config.get<string>("cliPath")?.trim();
  if (configured && commandAvailable(configured)) {
    return { found: true, source: "configured", command: configured, display: configured };
  }

  const managed = managedCliPath(storagePath);
  if (commandAvailable(managed)) {
    return { found: true, source: "managed", command: managed, display: managed };
  }

  if (repoRoot) {
    const wrapper = path.join(repoRoot, "scripts", "seeed-zephyr");
    if (commandAvailable(wrapper)) {
      return { found: true, source: "repo", command: wrapper, display: "scripts/seeed-zephyr" };
    }
  }

  const pathCommand = findOnPath("seeed-zephyr");
  if (pathCommand) {
    return { found: true, source: "path", command: "seeed-zephyr", display: pathCommand };
  }

  return { found: false, source: "missing", command: "", display: "missing" };
}

export function commandAvailable(command: string): boolean {
  if (!command) {
    return false;
  }
  if (command.includes("/") || command.includes("\\") || path.isAbsolute(command)) {
    return isExecutable(command);
  }
  return Boolean(findOnPath(command));
}

function findOnPath(command: string): string | undefined {
  const paths = (process.env.PATH ?? "").split(path.delimiter).filter(Boolean);
  const names =
    process.platform === "win32"
      ? [command, `${command}.exe`, `${command}.cmd`, `${command}.bat`]
      : [command];
  for (const dir of paths) {
    for (const name of names) {
      const candidate = path.join(dir, name);
      if (isExecutable(candidate)) {
        return candidate;
      }
    }
  }
  return undefined;
}

function isExecutable(file: string): boolean {
  try {
    fs.accessSync(file, fs.constants.X_OK);
    return true;
  } catch {
    return false;
  }
}
