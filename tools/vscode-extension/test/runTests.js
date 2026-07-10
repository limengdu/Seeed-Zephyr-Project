// Bundles and runs TypeScript tests with the extension's existing esbuild dependency.
// 使用插件已有的 esbuild 依赖打包并运行 TypeScript 测试。
const { spawnSync } = require("node:child_process");
const os = require("node:os");
const path = require("node:path");
const esbuild = require("esbuild");

const output = path.join(os.tmpdir(), "seeed-zephyr-vscode-tests.cjs");

esbuild.buildSync({
  entryPoints: [path.join(__dirname, "projectDiscovery.test.ts")],
  bundle: true,
  outfile: output,
  format: "cjs",
  platform: "node",
  target: "node18",
  logLevel: "silent",
});

const result = spawnSync(process.execPath, ["--test", output], {
  stdio: "inherit",
});

process.exit(result.status ?? 1);
