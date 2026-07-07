import * as vscode from "vscode";
import { locateCli } from "./cliLocator";

const TERMINAL_NAME = "Seeed XIAO Zephyr";

export type Action = "build" | "flash" | "monitor" | "debug";

// Runs a CLI action in a fresh integrated terminal so active monitors cannot consume commands.
// 在新的集成终端里跑 CLI 操作，避免正在运行的监视器吞掉命令。
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

  const terminal = createActionTerminal(repoRoot, action);
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
  options: { port?: string; monitorAfterFlash?: boolean } = {},
): void {
  const cli = locateCli(repoRoot);
  const parts = [cli.command, ...cli.baseArgs, action, board];
  // monitor uses the selected serial port; build/flash/debug take the app dir.
  // monitor 使用已选择的串口;build/flash/debug 需要应用目录。
  if (action !== "monitor") {
    parts.push("--app", appDir);
  }
  if ((action === "flash" || action === "monitor") && options.port) {
    parts.push("--port", options.port);
  }
  if (action === "flash" && options.monitorAfterFlash) {
    parts.push("--monitor");
  }
  const commandLine = parts.map(quoteArg).join(" ");

  const terminal = createActionTerminal(repoRoot, action);
  terminal.show();
  terminal.sendText(commandLine);
}

function createActionTerminal(
  repoRoot: string | undefined,
  action: Action,
): vscode.Terminal {
  return vscode.window.createTerminal({
    name: `${TERMINAL_NAME}: ${actionLabel(action)}`,
    cwd: repoRoot,
    env: repoRoot ? { SEEED_ZEPHYR_REPO_ROOT: repoRoot } : undefined,
  });
}

function actionLabel(action: Action): string {
  switch (action) {
    case "build":
      return "Build";
    case "flash":
      return "Upload";
    case "monitor":
      return "Monitor";
    case "debug":
      return "Debug";
  }
}

// Quotes an argument for a POSIX shell when it contains spaces or special characters.
// 当参数含空格或特殊字符时,为 POSIX shell 加引号。
function quoteArg(arg: string): string {
  if (/^[A-Za-z0-9_/.-]+$/.test(arg)) {
    return arg;
  }
  return `'${arg.replace(/'/g, "'\\''")}'`;
}
