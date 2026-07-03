import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";
import { commandAvailable } from "../env/environment";

// How to invoke the seeed-zephyr CLI: a command plus fixed leading arguments.
// 如何调用 seeed-zephyr CLI:一个命令加上固定的前置参数。
export interface CliInvocation {
  command: string;
  baseArgs: string[];
  env: NodeJS.ProcessEnv;
  display: string;
}

// Resolves the CLI invocation for a repo root, in priority order.
// 按优先级解析针对某个仓库根的 CLI 调用方式。
export function locateCli(repoRoot: string | undefined): CliInvocation {
  const config = vscode.workspace.getConfiguration("seeedZephyr");
  const env = { ...process.env };
  if (repoRoot) {
    env.SEEED_ZEPHYR_REPO_ROOT = repoRoot;
  }

  const python = config.get<string>("pythonPath") || "python3";

  // 1. When the repository itself is the open workspace, prefer its bundled CLI so a
  //    contributor's edits to the CLI take effect, instead of a separately installed
  //    build selected in settings. End-user setups (repo not opened as a workspace)
  //    keep using the configured/managed CLI below.
  // 1. 当打开的工作区就是本仓库时，优先用仓库自带的 CLI，让贡献者对 CLI 的改动生效，
  //    而不是设置里选择的另一份已安装 CLI。终端用户（未把仓库作为工作区打开）仍走下方
  //    配置的/托管的 CLI。
  if (repoRoot && isDevCheckoutWorkspace(repoRoot)) {
    const dev = repoCliInvocation(repoRoot, python, env);
    if (dev) {
      return dev;
    }
  }

  // 2. Explicit override from settings (installed / managed CLI).
  const override = config.get<string>("cliPath");
  if (override && commandAvailable(override)) {
    return { command: override, baseArgs: [], env, display: override };
  }

  // 3. Repo CLI fallback when available.
  if (repoRoot) {
    const repo = repoCliInvocation(repoRoot, python, env);
    if (repo) {
      return repo;
    }
  }

  // 4. Installed console script on PATH.
  return { command: "seeed-zephyr", baseArgs: [], env, display: "seeed-zephyr" };
}

// Builds an invocation for the repository's own CLI (wrapper script, or the Python
// entry point as a Windows-friendly fallback).
// 构造调用仓库自带 CLI 的方式（wrapper 脚本，或作为 Windows 兜底的 Python 入口）。
function repoCliInvocation(
  repoRoot: string,
  python: string,
  env: NodeJS.ProcessEnv,
): CliInvocation | undefined {
  const wrapper = path.join(repoRoot, "scripts", "seeed-zephyr");
  if (isExecutable(wrapper)) {
    return { command: wrapper, baseArgs: [], env, display: "scripts/seeed-zephyr" };
  }
  const script = path.join(repoRoot, "tools", "cli", "seeed_zephyr.py");
  if (fs.existsSync(script)) {
    return {
      command: python,
      baseArgs: [script],
      env,
      display: `${python} tools/cli/seeed_zephyr.py`,
    };
  }
  return undefined;
}

// True when repoRoot is both an open workspace folder and carries the CLI source,
// i.e. the user is actively working inside a repository checkout.
// 当 repoRoot 既是打开的工作区文件夹、又包含 CLI 源码时为真，即用户正在仓库检出里开发。
function isDevCheckoutWorkspace(repoRoot: string): boolean {
  const folders = vscode.workspace.workspaceFolders ?? [];
  const opened = folders.some((folder) => path.resolve(folder.uri.fsPath) === path.resolve(repoRoot));
  return opened && fs.existsSync(path.join(repoRoot, "tools", "cli", "seeed_zephyr.py"));
}

function isExecutable(file: string): boolean {
  try {
    fs.accessSync(file, fs.constants.X_OK);
    return true;
  } catch {
    return false;
  }
}
