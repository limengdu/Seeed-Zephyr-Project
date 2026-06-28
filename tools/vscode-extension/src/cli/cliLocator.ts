import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";

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

  // 1. Explicit override from settings.
  const override = config.get<string>("cliPath");
  if (override) {
    return { command: override, baseArgs: [], env, display: override };
  }

  const python = config.get<string>("pythonPath") || "python3";

  if (repoRoot) {
    // 2. Repo wrapper script (sets SEEED_ZEPHYR_REPO_ROOT and forwards).
    const wrapper = path.join(repoRoot, "scripts", "seeed-zephyr");
    if (isExecutable(wrapper)) {
      return { command: wrapper, baseArgs: [], env, display: "scripts/seeed-zephyr" };
    }
    // 3. Direct Python script (Windows fallback where the wrapper is not executable).
    const script = path.join(repoRoot, "tools", "cli", "seeed_zephyr.py");
    if (fs.existsSync(script)) {
      return {
        command: python,
        baseArgs: [script],
        env,
        display: `${python} tools/cli/seeed_zephyr.py`,
      };
    }
  }

  // 4. Installed console script on PATH.
  return { command: "seeed-zephyr", baseArgs: [], env, display: "seeed-zephyr" };
}

function isExecutable(file: string): boolean {
  try {
    fs.accessSync(file, fs.constants.X_OK);
    return true;
  } catch {
    return false;
  }
}
