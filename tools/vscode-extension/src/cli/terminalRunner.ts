import * as vscode from "vscode";
import { locateCli } from "./cliLocator";

const TERMINAL_NAME = "Seeed XIAO Zephyr";

export type Action = "build" | "flash" | "monitor" | "debug";

// Runs a CLI action in a reused integrated terminal so real west output streams live.
// 在复用的集成终端里跑 CLI 操作,让真实的 west 输出实时显示。
export function runAction(
  repoRoot: string | undefined,
  action: Action,
  board: string,
  demo: string | undefined,
): void {
  const cli = locateCli(repoRoot);
  const parts = [cli.command, ...cli.baseArgs, action, board];
  // monitor selects the port from the board; build/flash/debug take the demo.
  // monitor 由板子选串口;build/flash/debug 需要 demo。
  if (action !== "monitor" && demo) {
    parts.push(demo);
  }
  const commandLine = parts.map(quoteArg).join(" ");

  const terminal = getTerminal(repoRoot);
  terminal.show();
  terminal.sendText(commandLine);
}

// Runs an action against the current project directory via the CLI --app path.
// 通过 CLI 的 --app 路径,对当前工程目录运行某个操作。
export function runProjectAction(
  repoRoot: string | undefined,
  action: Action,
  board: string,
  appDir: string,
): void {
  const cli = locateCli(repoRoot);
  const parts = [cli.command, ...cli.baseArgs, action, board];
  // monitor opens the board serial port; build/flash/debug take the app dir.
  // monitor 打开板子串口;build/flash/debug 需要应用目录。
  if (action !== "monitor") {
    parts.push("--app", appDir);
  }
  const commandLine = parts.map(quoteArg).join(" ");

  const terminal = getTerminal(repoRoot);
  terminal.show();
  terminal.sendText(commandLine);
}

function getTerminal(repoRoot: string | undefined): vscode.Terminal {
  const existing = vscode.window.terminals.find((term) => term.name === TERMINAL_NAME);
  if (existing) {
    return existing;
  }
  return vscode.window.createTerminal({
    name: TERMINAL_NAME,
    cwd: repoRoot,
    env: repoRoot ? { SEEED_ZEPHYR_REPO_ROOT: repoRoot } : undefined,
  });
}

// Quotes an argument for a POSIX shell when it contains spaces or special characters.
// 当参数含空格或特殊字符时,为 POSIX shell 加引号。
function quoteArg(arg: string): string {
  if (/^[A-Za-z0-9_/.-]+$/.test(arg)) {
    return arg;
  }
  return `'${arg.replace(/'/g, "'\\''")}'`;
}
