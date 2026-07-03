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

interface PythonInvocation {
  command: string;
  baseArgs: string[];
  display: string;
}

interface CliInvocation {
  command: string;
  display: string;
  source: "configured" | "managed" | "repo" | "path";
}

interface ManagedCliInstallOptions {
  version?: string;
  forceReinstall?: boolean;
}

const INSTALL_COMMAND =
  "curl -fsSL https://raw.githubusercontent.com/limengdu/Seeed-Zephyr-Project/main/install.sh | bash";
const DEFAULT_MANAGED_CLI_VERSION = "0.4.0";
const PYPI_VERSION_RETRIES = 3;
const PYPI_VERSION_TIMEOUT_MS = 15000;
const PIP_RETRIES = "5";
const PIP_TIMEOUT_SECONDS = "30";

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
  await installManagedCliVersion(context, onUpdated, {});
}

// Reinstalls the latest published seeed-zephyr package into extension storage.
// 重新安装最新发布的 seeed-zephyr 包到插件存储目录。
export async function reinstallManagedCli(
  context: vscode.ExtensionContext,
  onUpdated: () => void,
): Promise<void> {
  await installManagedCliVersion(context, onUpdated, { forceReinstall: true });
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
  await installManagedCliVersion(context, onUpdated, { version });
}

// Verifies the CLI command currently selected by the extension.
// 验证插件当前选择的 CLI 命令。
export async function verifyCli(
  repoRoot: string | undefined,
  context: vscode.ExtensionContext,
  onUpdated: () => void,
): Promise<void> {
  const cli = resolveActiveCli(repoRoot, context.globalStorageUri.fsPath);
  if (!cli) {
    void vscode.window.showErrorMessage("No seeed-zephyr CLI is configured.");
    return;
  }

  const result = await vscode.window.withProgress<ProcessResult>(
    {
      location: vscode.ProgressLocation.Notification,
      title: "Verifying seeed-zephyr CLI",
      cancellable: false,
    },
    () => runProcess(cli.command, ["info", "--json"]),
  );
  if (!result.ok) {
    void vscode.window.showErrorMessage(`CLI verification failed: ${result.message}`);
    return;
  }

  const version = parseCliVersion(result.stdout);
  const compatibility = await verifyCliCompatibility(cli.command);
  if (!compatibility.ok) {
    void vscode.window.showErrorMessage(`CLI compatibility check failed: ${compatibility.message}`);
    return;
  }
  if (cli.source === "managed" && version) {
    await vscode.workspace
      .getConfiguration("seeedZephyr")
      .update("managedCliVersion", version, vscode.ConfigurationTarget.Global);
  }
  onUpdated();
  void vscode.window.showInformationMessage(
    `CLI verified: ${cli.display} (${version ?? "unknown"})`,
  );
}

async function installManagedCliVersion(
  context: vscode.ExtensionContext,
  onUpdated: () => void,
  options: ManagedCliInstallOptions,
): Promise<void> {
  const { version, forceReinstall = false } = options;
  const storagePath = context.globalStorageUri.fsPath;
  const venvDir = managedCliVenvPath(storagePath);
  const python = await resolveManagedCliPython();
  if (!python) {
    return;
  }

  const result = await vscode.window.withProgress<ProcessResult>(
    {
      location: vscode.ProgressLocation.Notification,
      title: installProgressTitle(version, forceReinstall),
      cancellable: false,
    },
    async () => {
      fs.mkdirSync(storagePath, { recursive: true });
      let step = await runProcess(python.command, [...python.baseArgs, "-m", "venv", venvDir]);
      if (!step.ok) {
        return step;
      }
      const venvPython = managedCliPythonPath(storagePath);
      const venvVersion = await pythonExecutableVersion(venvPython);
      if (!venvVersion || !versionAtLeast(venvVersion, [3, 12, 0])) {
        return {
          ok: false,
          stdout: "",
          stderr: "",
          message: "Managed CLI venv must use Python 3.12 or newer.",
        };
      }
      step = await runProcess(venvPython, [
        "-m",
        "pip",
        "install",
        "--retries",
        PIP_RETRIES,
        "--timeout",
        PIP_TIMEOUT_SECONDS,
        "--upgrade",
        "pip",
      ]);
      if (!step.ok) {
        return step;
      }
      const packageSpec = version ? `seeed-zephyr==${version}` : "seeed-zephyr";
      const installArgs = pipInstallArgs(packageSpec, !version, forceReinstall);
      return runProcess(venvPython, installArgs);
    },
  );

  if (!result.ok) {
    void vscode.window.showErrorMessage(`CLI install failed: ${result.message}`);
    return;
  }

  const cliPath = managedCliPath(storagePath);
  const verification = await runProcess(cliPath, ["info", "--json"]);
  if (!verification.ok) {
    void vscode.window.showErrorMessage(`CLI installed but verification failed: ${verification.message}`);
    return;
  }
  const installedVersion = parseCliVersion(verification.stdout);
  if (!installedVersion) {
    void vscode.window.showErrorMessage("CLI installed but version could not be read.");
    return;
  }
  const compatibility = await verifyCliCompatibility(cliPath);
  if (!compatibility.ok) {
    void vscode.window.showErrorMessage(`CLI installed but compatibility check failed: ${compatibility.message}`);
    return;
  }

  const config = vscode.workspace.getConfiguration("seeedZephyr");
  await config.update("cliPath", cliPath, vscode.ConfigurationTarget.Global);
  await config.update("managedCliVersion", installedVersion, vscode.ConfigurationTarget.Global);
  onUpdated();
  void vscode.window.showInformationMessage(`CLI selected: seeed-zephyr ${installedVersion}`);
}

function installProgressTitle(version: string | undefined, forceReinstall: boolean): string {
  if (forceReinstall) {
    return version ? `Reinstalling seeed-zephyr ${version}` : "Reinstalling latest seeed-zephyr";
  }
  return version ? `Installing seeed-zephyr ${version}` : "Installing latest seeed-zephyr";
}

function pipInstallArgs(packageSpec: string, upgrade: boolean, forceReinstall: boolean): string[] {
  const args = [
    "-m",
    "pip",
    "install",
    "--retries",
    PIP_RETRIES,
    "--timeout",
    PIP_TIMEOUT_SECONDS,
  ];
  if (upgrade) {
    args.push("--upgrade");
  }
  if (forceReinstall) {
    args.push("--force-reinstall");
  }
  args.push(packageSpec);
  return args;
}

async function resolveManagedCliPython(): Promise<PythonInvocation | undefined> {
  for (const candidate of pythonCandidates()) {
    const version = await pythonVersion(candidate);
    if (version && versionAtLeast(version, [3, 12, 0])) {
      return candidate;
    }
  }

  void vscode.window.showErrorMessage(
    "Managed CLI requires Python 3.12 or newer. Install Python 3.12+ or set seeedZephyr.pythonPath.",
  );
  return undefined;
}

function pythonCandidates(): PythonInvocation[] {
  const configPython = vscode.workspace.getConfiguration("seeedZephyr").get<string>("pythonPath")?.trim();
  const candidates: PythonInvocation[] = [];
  if (configPython) {
    candidates.push({ command: configPython, baseArgs: [], display: configPython });
  }
  candidates.push(
    { command: "python3.13", baseArgs: [], display: "python3.13" },
    { command: "python3.12", baseArgs: [], display: "python3.12" },
    { command: "python3", baseArgs: [], display: "python3" },
  );
  if (process.platform === "darwin") {
    candidates.push(
      {
        command: "/opt/homebrew/bin/python3.13",
        baseArgs: [],
        display: "/opt/homebrew/bin/python3.13",
      },
      {
        command: "/opt/homebrew/bin/python3.12",
        baseArgs: [],
        display: "/opt/homebrew/bin/python3.12",
      },
    );
  }
  if (process.platform === "win32") {
    candidates.push(
      { command: "py", baseArgs: ["-3.13"], display: "py -3.13" },
      { command: "py", baseArgs: ["-3.12"], display: "py -3.12" },
    );
  }
  return uniquePythonCandidates(candidates);
}

async function pythonVersion(candidate: PythonInvocation): Promise<number[] | undefined> {
  const result = await runProcess(candidate.command, [
    ...candidate.baseArgs,
    "-c",
    "import sys; print('.'.join(map(str, sys.version_info[:3])))",
  ]);
  return versionFromProcessResult(result);
}

async function pythonExecutableVersion(command: string): Promise<number[] | undefined> {
  const result = await runProcess(command, [
    "-c",
    "import sys; print('.'.join(map(str, sys.version_info[:3])))",
  ]);
  return versionFromProcessResult(result);
}

function versionFromProcessResult(result: ProcessResult): number[] | undefined {
  if (!result.ok) {
    return undefined;
  }
  const version = firstUsefulLine(result.stdout).split(".").map((part) => Number.parseInt(part, 10));
  return version.every((part) => Number.isFinite(part)) ? version : undefined;
}

function versionAtLeast(actual: number[], minimum: number[]): boolean {
  for (let index = 0; index < minimum.length; index += 1) {
    const diff = (actual[index] ?? 0) - minimum[index];
    if (diff !== 0) {
      return diff > 0;
    }
  }
  return true;
}

function uniquePythonCandidates(candidates: PythonInvocation[]): PythonInvocation[] {
  const seen = new Set<string>();
  return candidates.filter((candidate) => {
    const key = `${candidate.command}\0${candidate.baseArgs.join("\0")}`;
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

async function chooseCliVersion(): Promise<string | undefined> {
  try {
    const versions = await retryAsync(() => fetchPublishedVersions(), PYPI_VERSION_RETRIES);
    const picked = await vscode.window.showQuickPick(
      versions.map((version, index) => ({
        label: version,
        description: index === 0 ? "latest" : undefined,
      })),
      { placeHolder: "Select seeed-zephyr CLI version" },
    );
    return picked?.label;
  } catch {
    void vscode.window.showWarningMessage(
      "Could not read published CLI versions after retries. Enter a version manually.",
    );
    return vscode.window.showInputBox({
      prompt: "seeed-zephyr CLI version",
      placeHolder: DEFAULT_MANAGED_CLI_VERSION,
      value: DEFAULT_MANAGED_CLI_VERSION,
    });
  }
}

function parseCliVersion(stdout: string): string | undefined {
  try {
    const info = JSON.parse(stdout) as { cli_version?: string };
    return info.cli_version;
  } catch {
    return undefined;
  }
}

async function verifyCliCompatibility(command: string): Promise<ProcessResult> {
  const ports = await runProcess(command, ["list", "ports", "--json"]);
  if (!ports.ok) {
    return ports;
  }
  try {
    JSON.parse(ports.stdout);
  } catch {
    return {
      ok: false,
      stdout: ports.stdout,
      stderr: ports.stderr,
      message: "Serial port detection returned invalid JSON.",
    };
  }

  return runProcess(command, ["create", "--help"]);
}

function fetchPublishedVersions(): Promise<string[]> {
  return new Promise((resolve, reject) => {
    const request = https
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
    request.setTimeout(PYPI_VERSION_TIMEOUT_MS, () => {
      request.destroy(new Error("PyPI request timed out"));
    });
  });
}

async function retryAsync<T>(operation: () => Promise<T>, attempts: number): Promise<T> {
  let lastError: unknown;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      return await operation();
    } catch (error) {
      lastError = error;
      if (attempt < attempts) {
        await delay(attempt * 500);
      }
    }
  }
  throw lastError;
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
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

function resolveActiveCli(repoRoot: string | undefined, storagePath: string): CliInvocation | undefined {
  const configured = vscode.workspace.getConfiguration("seeedZephyr").get<string>("cliPath")?.trim();
  const managed = managedCliPath(storagePath);
  if (configured && commandAvailable(configured)) {
    const source = samePath(configured, managed) ? "managed" : "configured";
    return { command: configured, display: configured, source };
  }

  if (commandAvailable(managed)) {
    return { command: managed, display: managed, source: "managed" };
  }

  const repoCli = repositoryCliPath(repoRoot);
  if (repoCli) {
    return { command: repoCli, display: "scripts/seeed-zephyr", source: "repo" };
  }

  if (commandAvailable("seeed-zephyr")) {
    return { command: "seeed-zephyr", display: "seeed-zephyr", source: "path" };
  }

  return undefined;
}

function samePath(left: string, right: string): boolean {
  try {
    return path.resolve(left) === path.resolve(right);
  } catch {
    return left === right;
  }
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
