import { spawn } from "child_process";
import * as fs from "fs";
import * as https from "https";
import * as os from "os";
import * as path from "path";
import * as vscode from "vscode";
import {
  BLOB_LIST_FORMAT,
  BlobEntry,
  blobCacheName,
  isNewestRelease,
  modulesWithBlobs,
  parseBlobList,
  parseReleases,
  Release,
  repoTag,
} from "../versions/releases";
import {
  manifestDir,
  readRepoVersion,
  readVersionState,
  readZephyrInstalled,
  westCommandPath,
  zephyrWorkspacePath,
} from "../versions/versionState";
import { installManagedCliRelease, usesManagedCli } from "./environmentCommands";

const RELEASES_URL =
  "https://raw.githubusercontent.com/limengdu/Seeed-Zephyr-Project/main/metadata/versions.yaml";
const RELEASES_STATE_KEY = "seeedZephyr.releases";
const RELEASES_TIMEOUT_MS = 8000;
const BLOB_CACHE_DIR = ".seeed-blob-cache";

interface StepResult {
  ok: boolean;
  stdout: string;
  message: string;
}

class SwitchError extends Error {}

let output: vscode.OutputChannel | undefined;

// Returns the release list saved from the last successful download.
// 返回上次成功下载后保存的版本列表。
export function cachedReleases(context: vscode.ExtensionContext): Release[] | undefined {
  return context.globalState.get<Release[]>(RELEASES_STATE_KEY);
}

// Switches the repository examples, Zephyr workspace, and managed CLI to one release.
// 把仓库示例、Zephyr 工作区和插件管理的 CLI 一起切换到某个发布版本。
export async function switchVersion(
  repoRoot: string | undefined,
  context: vscode.ExtensionContext,
  onUpdated: () => void,
): Promise<void> {
  if (!repoRoot) {
    void vscode.window.showErrorMessage("Select the seeed-zephyr repository folder first.");
    return;
  }

  const releases = await loadReleases(context, repoRoot);
  if (!releases) {
    void vscode.window.showErrorMessage(
      "The release list is unavailable. Connect to the network and try again.",
    );
    return;
  }

  const state = readVersionState(repoRoot, releases);
  const picked = await vscode.window.showQuickPick(
    releases.map((release, index) => ({
      label: release.version,
      description: `Zephyr ${release.zephyr}${index === 0 ? " · latest" : ""}`,
      detail: release.version === state.repoVersion ? "current examples" : undefined,
      release,
    })),
    { placeHolder: "Select a seeed-zephyr version (examples, Zephyr, and CLI switch together)" },
  );
  if (!picked) {
    return;
  }
  const release = picked.release;

  const workspace = zephyrWorkspacePath();
  const problem = await precheck(repoRoot, workspace);
  if (problem) {
    void vscode.window.showErrorMessage(problem);
    return;
  }

  const managed = usesManagedCli(repoRoot, context.globalStorageUri.fsPath);
  const sdkDir = path.join(os.homedir(), `zephyr-sdk-${release.sdk}`);
  const detail = [
    `Examples: ${repoRoot} → ${isNewestRelease(releases, release) ? "latest main" : repoTag(release)}`,
    `Zephyr: ${workspace} → ${release.zephyr}`,
    managed ? `CLI: managed seeed-zephyr → ${release.version}` : "CLI: the selected CLI stays as configured",
    fs.existsSync(sdkDir) ? `SDK: ${sdkDir}` : `SDK: install Zephyr SDK ${release.sdk} to build (${sdkDir})`,
    "",
    "A version used for the first time is downloaded; switching back to it later runs offline.",
  ].join("\n");
  const confirmed = await vscode.window.showWarningMessage(
    `Switch to seeed-zephyr ${release.version} with Zephyr ${release.zephyr}?`,
    { modal: true, detail },
    "Switch",
  );
  if (confirmed !== "Switch") {
    return;
  }

  const channel = outputChannel();
  channel.show(true);
  channel.appendLine(`=== Switching to seeed-zephyr ${release.version} (Zephyr ${release.zephyr})`);

  try {
    await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: `Switching to seeed-zephyr ${release.version}`,
        cancellable: false,
      },
      async (progress) => {
        progress.report({ message: `Zephyr ${release.zephyr}` });
        await switchZephyr(workspace, release, (message) => progress.report({ message }));
        progress.report({ message: "examples" });
        await switchRepository(repoRoot, releases, release);
      },
    );
  } catch (error) {
    onUpdated();
    channel.appendLine(`!!! ${String((error as Error).message ?? error)}`);
    void vscode.window.showErrorMessage(
      `Version switch stopped: ${(error as Error).message}. See the "Seeed XIAO Versions" output for details.`,
    );
    return;
  }

  if (managed && !(await installManagedCliRelease(context, onUpdated, release.version))) {
    onUpdated();
    return;
  }

  onUpdated();
  channel.appendLine(`=== Now on seeed-zephyr ${release.version} with Zephyr ${readZephyrInstalled(workspace)}`);
  void vscode.window.showInformationMessage(
    `Switched to seeed-zephyr ${release.version} with Zephyr ${release.zephyr}.`,
  );
}

async function loadReleases(
  context: vscode.ExtensionContext,
  repoRoot: string,
): Promise<Release[] | undefined> {
  try {
    const releases = parseReleases(await download(RELEASES_URL));
    await context.globalState.update(RELEASES_STATE_KEY, releases);
    return releases;
  } catch {
    return readVersionState(repoRoot, cachedReleases(context)).releases;
  }
}

async function precheck(repoRoot: string, workspace: string): Promise<string | undefined> {
  const repoStatus = await run("git", ["-C", repoRoot, "status", "--porcelain", "--untracked-files=no"]);
  if (!repoStatus.ok) {
    return `The repository folder is not a Git checkout: ${repoRoot}`;
  }
  if (repoStatus.stdout.trim()) {
    return `The repository has local changes. Commit or stash them, then switch versions: ${repoRoot}`;
  }
  if (!fs.existsSync(path.join(workspace, ".west")) || !fs.existsSync(westCommandPath(workspace))) {
    return `The Zephyr workspace is not set up at ${workspace}. Run Full Setup first.`;
  }
  const zephyrStatus = await run("git", [
    "-C",
    manifestDir(workspace),
    "status",
    "--porcelain",
    "--untracked-files=no",
  ]);
  if (zephyrStatus.ok && zephyrStatus.stdout.trim()) {
    return `The Zephyr checkout has local changes. Commit or stash them, then switch versions: ${manifestDir(workspace)}`;
  }
  return undefined;
}

export async function switchRepository(repoRoot: string, releases: Release[], release: Release): Promise<void> {
  await step("git", ["-C", repoRoot, "fetch", "--tags", "origin"], { optional: true });
  if (isNewestRelease(releases, release)) {
    const branch = await defaultBranch(repoRoot);
    await step("git", ["-C", repoRoot, "checkout", branch]);
    await step("git", ["-C", repoRoot, "pull", "--no-ff"], { optional: true });
  } else {
    await step("git", ["-C", repoRoot, "checkout", "--detach", `refs/tags/${repoTag(release)}`]);
  }
  const version = readRepoVersion(repoRoot);
  if (version !== release.version) {
    throw new SwitchError(`the repository reports version ${version ?? "unknown"} after checkout`);
  }
}

export async function switchZephyr(
  workspace: string,
  release: Release,
  report: (message: string) => void,
): Promise<void> {
  const west = westCommandPath(workspace);
  const zephyrDir = manifestDir(workspace);
  const tag = `refs/tags/${release.zephyr}`;
  const current = readZephyrInstalled(workspace);
  const headCommit = (await run("git", ["-C", zephyrDir, "rev-parse", "HEAD"])).stdout.trim();
  const tagCommit = (await run("git", ["-C", zephyrDir, "rev-parse", "-q", "--verify", `${tag}^{commit}`])).stdout.trim();
  if (current === release.zephyr && headCommit && headCommit === tagCommit) {
    log(`Zephyr is already at ${release.zephyr}.`);
    return;
  }

  const cacheDir = path.join(workspace, BLOB_CACHE_DIR);
  fs.mkdirSync(cacheDir, { recursive: true });
  await westStep(west, workspace, ["config", "blobs.auto-cache", cacheDir]);

  report("saving current blobs");
  const before = parseBlobList((await westStep(west, workspace, ["blobs", "list", "-f", BLOB_LIST_FORMAT])).stdout);
  seedBlobCache(before, cacheDir);
  if (current) {
    await anchorProjects(west, workspace, current);
  }

  report(`moving Zephyr to ${release.zephyr}`);
  if (!tagCommit) {
    await step("git", ["-C", zephyrDir, "fetch", "--depth=1", "origin", `${tag}:${tag}`]);
  }
  await step("git", ["-C", zephyrDir, "checkout", "--detach", tag]);

  report("updating modules");
  await westStep(west, workspace, ["update", "-n", "-o=--depth=1"]);

  const modules = modulesWithBlobs(before);
  if (modules.length > 0) {
    report("restoring blobs");
    await westStep(west, workspace, ["blobs", "fetch", ...modules]);
  }
  await anchorProjects(west, workspace, release.zephyr);

  report("installing Python requirements");
  await westStep(west, workspace, ["packages", "pip", "--install"]);

  const installed = readZephyrInstalled(workspace);
  if (installed !== release.zephyr) {
    throw new SwitchError(`the Zephyr workspace reports ${installed ?? "unknown"} after the switch`);
  }
}

// Copies blobs already on disk into the auto-cache so switching back restores them offline.
// 把磁盘上已有的 blobs 复制进自动缓存，切换回来时可离线还原。
function seedBlobCache(entries: BlobEntry[], cacheDir: string): void {
  let copied = 0;
  for (const entry of entries) {
    if (entry.status !== "A") {
      continue;
    }
    const target = path.join(cacheDir, blobCacheName(entry));
    if (!fs.existsSync(target)) {
      fs.copyFileSync(entry.abspath, target);
      copied += 1;
    }
  }
  log(`Blob cache: ${copied} file(s) added in ${cacheDir}`);
}

// Records each project's current commit under refs/seeed/<zephyr> so git gc keeps it.
// 在 refs/seeed/<zephyr> 记录每个项目的当前提交，避免 git gc 清掉该版本。
function anchorProjects(west: string, workspace: string, zephyrVersion: string): Promise<StepResult> {
  return westStep(west, workspace, ["forall", "-c", `git update-ref refs/seeed/${zephyrVersion} HEAD`], {
    optional: true,
  });
}

async function defaultBranch(repoRoot: string): Promise<string> {
  const result = await run("git", ["-C", repoRoot, "symbolic-ref", "--short", "refs/remotes/origin/HEAD"]);
  const ref = result.ok ? result.stdout.trim() : "";
  return ref.startsWith("origin/") ? ref.slice("origin/".length) : "main";
}

function westStep(
  west: string,
  workspace: string,
  args: string[],
  options: { optional?: boolean } = {},
): Promise<StepResult> {
  const venvBin = path.dirname(west);
  const env = { ...process.env, PATH: `${venvBin}${path.delimiter}${process.env.PATH ?? ""}` };
  return step(west, args, { ...options, cwd: workspace, env });
}

async function step(
  command: string,
  args: string[],
  options: { optional?: boolean; cwd?: string; env?: NodeJS.ProcessEnv } = {},
): Promise<StepResult> {
  log(`$ ${[path.basename(command), ...args].join(" ")}`);
  const result = await run(command, args, options.cwd, options.env, true);
  if (!result.ok) {
    if (options.optional) {
      log(`(continuing) ${result.message}`);
      return result;
    }
    throw new SwitchError(result.message);
  }
  return result;
}

function run(
  command: string,
  args: string[],
  cwd?: string,
  env?: NodeJS.ProcessEnv,
  echo = false,
): Promise<StepResult> {
  return new Promise((resolve) => {
    const child = spawn(command, args, { cwd, env });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
      if (echo) {
        outputChannel().append(chunk.toString());
      }
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
      if (echo) {
        outputChannel().append(chunk.toString());
      }
    });
    child.on("error", (error) => resolve({ ok: false, stdout, message: error.message }));
    child.on("close", (code) => {
      const lastLine = (text: string) =>
        text.split("\n").map((line) => line.trim()).filter(Boolean).pop() ?? "";
      resolve({
        ok: code === 0,
        stdout,
        message:
          code === 0
            ? ""
            : lastLine(stderr) || lastLine(stdout) || `${path.basename(command)} exited with code ${code ?? "unknown"}`,
      });
    });
  });
}

function download(url: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const request = https
      .get(url, (response) => {
        if (response.statusCode !== 200) {
          response.resume();
          reject(new Error(`HTTP ${response.statusCode ?? "unknown"}`));
          return;
        }
        let body = "";
        response.on("data", (chunk) => {
          body += chunk.toString();
        });
        response.on("end", () => resolve(body));
      })
      .on("error", reject);
    request.setTimeout(RELEASES_TIMEOUT_MS, () => request.destroy(new Error("request timed out")));
  });
}

function outputChannel(): vscode.OutputChannel {
  output ??= vscode.window.createOutputChannel("Seeed XIAO Versions");
  return output;
}

function log(line: string): void {
  outputChannel().appendLine(line);
}

