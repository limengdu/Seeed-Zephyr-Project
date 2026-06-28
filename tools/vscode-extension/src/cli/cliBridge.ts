import { spawn } from "child_process";
import type { CliInvocation } from "./cliLocator";

export interface CliResult {
  ok: boolean;
  stdout: string;
  stderr: string;
  message: string;
}

// Runs the CLI and captures its output. For non-interactive commands like create.
// 运行 CLI 并捕获输出。用于 create 这类非交互命令。
export function runCapture(cli: CliInvocation, args: string[]): Promise<CliResult> {
  return new Promise((resolve) => {
    const child = spawn(cli.command, [...cli.baseArgs, ...args], { env: cli.env });
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
        ? stdout.trim()
        : extractError(stderr) || `Exited with code ${code ?? "unknown"}`;
      resolve({ ok, stdout, stderr, message });
    });
  });
}

// Extracts the leading "Error: ..." line the CLI prints on failure.
// 提取 CLI 失败时打印的 "Error: ..." 行。
function extractError(stderr: string): string {
  const line = stderr.split("\n").find((entry) => entry.startsWith("Error:"));
  return line ? line.replace(/^Error:\s*/, "") : stderr.trim();
}
