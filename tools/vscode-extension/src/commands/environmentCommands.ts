import { spawn } from "child_process";
import * as fs from "fs";
import * as https from "https";
import * as path from "path";
import * as vscode from "vscode";
import {
  commandAvailable,
  managedCliPath,
  managedCliPythonPath,
  managedCliVenvPath,
} from "../env/environment";

interface ProcessResult {
  ok: boolean;
  stdout: string;
  stderr: string;
  message: string;
}

const INSTALL_COMMAND =
  "curl -fsSL https://raw.githubusercontent.com/limengdu/Seeed-Zephyr-Project/main/install.sh | bash";

// Starts the repository setup command in a visible terminal.
// 在可见终端中启动仓库 setup 命令。
export function setupEnvironment(): void {
  const terminal = vscode.window.createTerminal({ name: "Seeed XIAO Zephyr Setup" });
  terminal.show();
  terminal.sendText(INSTALL_COMMAND);
}

// Selects the best CLI for the current workspace.
// 为当前工作区选择最合适的 CLI。
export async function useRecommendedCli(
  repoRoot: string | undefined,
  context: vscode.ExtensionContext,
  onUpdated: () => void,
): Promise<void> {
  const repoCli = repositoryCliPath(repoRoot);
  if (repoCli) {
    const result = await runProcess(repoCli, ["info", "--json"]);
    if (!result.ok) {
      void vscode.window.showErrorMessage(`Repository CLI is not ready: ${result.message}`);
      return;
    }
    await vscode.workspace
      .getConfiguration("seeedZephyr")
      .update("cliPath", repoCli, vscode.ConfigurationTarget.Global);
    onUpdated();
    void vscode.window.showInformationMessage(cliConfiguredMessage(repoCli, result.stdout));
    return;
  }

  await installManagedCli(context, onUpdated);
}

// Configures the extension to use a seeed-zephyr command already available on PATH.
// 配置插件使用 PATH 中已有的 seeed-zephyr 命令。
export async function useExistingCli(onUpdated: () => void): Promise<void> {
  const result = await runProcess("seeed-zephyr", ["info", "--json"]);
  if (!result.ok) {
    void vscode.window.showErrorMessage(`seeed-zephyr was not found: ${result.message}`);
    return;
  }
  await vscode.workspace
    .getConfiguration("seeedZephyr")
    .update("cliPath", "seeed-zephyr", vscode.ConfigurationTarget.Global);
  onUpdated();
  void vscode.window.showInformationMessage(cliConfiguredMessage("seeed-zephyr", result.stdout));
}

// Lets the user pick a CLI executable manually.
// 让用户手动选择 CLI 可执行文件。
export async function selectCliPath(onUpdated: () => void): Promise<void> {
  const picked = await vscode.window.showOpenDialog({
    canSelectFiles: true,
    canSelectFolders: false,
    canSelectMany: false,
    openLabel: "Select seeed-zephyr CLI",
  });
  if (!picked || picked.length === 0) {
    return;
  }
  const cliPath = picked[0].fsPath;
  await vscode.workspace
    .getConfiguration("seeedZephyr")
    .update("cliPath", cliPath, vscode.ConfigurationTarget.Global);
  onUpdated();
  void vscode.window.showInformationMessage(`CLI selected: ${cliPath}`);
}

// Installs the latest published seeed-zephyr package into extension storage.
// 将最新发布的 seeed-zephyr 包安装到插件存储目录。
export async function installManagedCli(
  context: vscode.ExtensionContext,
  onUpdated: () => void,
): Promise<void> {
  const version = await latestCliVersion();
  if (!version) {
    return;
  }
  await installManagedCliVersion(context, onUpdated, version);
}

// Lets the user choose a published seeed-zephyr package version.
// 让用户选择一个已发布的 seeed-zephyr 包版本。
export async function selectManagedCliVersion(
  context: vscode.ExtensionContext,
  onUpdated: () => void,
): Promise<void> {
  const version = await chooseCliVersion();
  if (!version) {
    return;
  }
  await installManagedCliVersion(context, onUpdated, version);
}

async function installManagedCliVersion(
  context: vscode.ExtensionContext,
  onUpdated: () => void,
  version: string,
): Promise<void> {
  const storagePath = context.globalStorageUri.fsPath;
  const venvDir = managedCliVenvPath(storagePath);
  const python = vscode.workspace.getConfiguration("seeedZephyr").get<string>("pythonPath") || "python3";

  const result = await vscode.window.withProgress<ProcessResult>(
    {
      location: vscode.ProgressLocation.Notification,
      title: `Installing seeed-zephyr ${version}`,
      cancellable: false,
    },
    async () => {
      fs.mkdirSync(storagePath, { recursive: true });
      let step = await runProcess(python, ["-m", "venv", venvDir]);
      if (!step.ok) {
        return step;
      }
      const venvPython = managedCliPythonPath(storagePath);
      step = await runProcess(venvPython, ["-m", "pip", "install", "--upgrade", "pip"]);
      if (!step.ok) {
        return step;
      }
      return runProcess(venvPython, ["-m", "pip", "install", `seeed-zephyr==${version}`]);
    },
  );

  if (!result.ok) {
    void vscode.window.showErrorMessage(`Managed CLI install failed: ${result.message}`);
    return;
  }

  const cliPath = managedCliPath(storagePath);
  const config = vscode.workspace.getConfiguration("seeedZephyr");
  await config.update("cliPath", cliPath, vscode.ConfigurationTarget.Global);
  await config.update("managedCliVersion", version, vscode.ConfigurationTarget.Global);
  onUpdated();
  void vscode.window.showInformationMessage(`Managed CLI selected: seeed-zephyr ${version}`);
}

async function latestCliVersion(): Promise<string | undefined> {
  try {
    return (await fetchPublishedVersions())[0];
  } catch (error) {
    void vscode.window.showErrorMessage(`Could not read published CLI versions: ${String(error)}`);
    return undefined;
  }
}

async function chooseCliVersion(): Promise<string | undefined> {
  try {
    const versions = await fetchPublishedVersions();
    const picked = await vscode.window.showQuickPick(
      versions.map((version, index) => ({
        label: version,
        description: index === 0 ? "latest" : undefined,
      })),
      { placeHolder: "Select seeed-zephyr CLI version" },
    );
    return picked?.label;
  } catch {
    return vscode.window.showInputBox({
      prompt: "seeed-zephyr CLI version",
      placeHolder: "0.3.0",
    });
  }
}

function fetchPublishedVersions(): Promise<string[]> {
  return new Promise((resolve, reject) => {
    https
      .get("https://pypi.org/pypi/seeed-zephyr/json", (response) => {
        if (response.statusCode !== 200) {
          reject(new Error(`PyPI returned ${response.statusCode ?? "unknown"}`));
          response.resume();
          return;
        }
        let body = "";
        response.on("data", (chunk) => {
          body += chunk.toString();
        });
        response.on("end", () => {
          try {
            const payload = JSON.parse(body) as { releases?: Record<string, unknown[]> };
            const versions = Object.entries(payload.releases ?? {})
              .filter(([, files]) => Array.isArray(files) && files.length > 0)
              .map(([version]) => version)
              .sort(compareVersionsDesc);
            resolve(versions);
          } catch (error) {
            reject(error);
          }
        });
      })
      .on("error", reject);
  });
}

function compareVersionsDesc(a: string, b: string): number {
  const left = versionParts(a);
  const right = versionParts(b);
  for (let index = 0; index < Math.max(left.length, right.length); index += 1) {
    const diff = (right[index] ?? 0) - (left[index] ?? 0);
    if (diff !== 0) {
      return diff;
    }
  }
  return b.localeCompare(a);
}

function versionParts(version: string): number[] {
  return version.split(".").map((part) => Number.parseInt(part, 10) || 0);
}

function cliConfiguredMessage(command: string, stdout: string): string {
  try {
    const info = JSON.parse(stdout) as { cli_version?: string };
    return `CLI selected: ${command} (${info.cli_version ?? "unknown"})`;
  } catch {
    return `CLI selected: ${command}`;
  }
}

function repositoryCliPath(repoRoot: string | undefined): string | undefined {
  if (!repoRoot) {
    return undefined;
  }
  const cliPath = path.join(repoRoot, "scripts", "seeed-zephyr");
  return commandAvailable(cliPath) ? cliPath : undefined;
}

function runProcess(command: string, args: string[]): Promise<ProcessResult> {
  return new Promise((resolve) => {
    const child = spawn(command, args);
    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    child.on("error", (error) => {
      resolve({ ok: false, stdout, stderr, message: error.message });
    });
    child.on("close", (code) => {
      const ok = code === 0;
      const message = ok
        ? stdout.trim() || stderr.trim()
        : firstUsefulLine(stderr) || firstUsefulLine(stdout) || `Exited with code ${code ?? "unknown"}`;
      resolve({ ok, stdout, stderr, message });
    });
  });
}

function firstUsefulLine(output: string): string {
  return output
    .split("\n")
    .map((line) => line.trim())
    .find((line) => line.length > 0) ?? "";
}
