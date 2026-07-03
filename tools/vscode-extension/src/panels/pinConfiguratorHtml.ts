import * as vscode from "vscode";

export interface PinDiagramPin {
  id: string;
  type: string;
  status: "power" | "reserved" | "bus" | "selectable" | "default" | "incompatible" | "free";
  role?: string;
  reason?: string;
  chip_pin?: string;
  bus?: string;
  bus_role?: string;
  rail?: string;
}

export interface PinRole {
  role: string;
  assigned: string;
  default: string;
  allowed: string[];
}

export interface PinDiagramData {
  board_id: string;
  form_factor: string;
  example: {
    ref: string;
    interface: string;
    pin_policy: string;
  };
  layout: {
    left?: string[];
    right?: string[];
  };
  pins: PinDiagramPin[];
  roles: PinRole[];
}

export type PinAssignments = Record<string, string>;

// Vertical pad band of the board image, as fractions of the image height.
// 板子图上焊盘带的上下边界，用图片高度的比例表示。
export interface PadBand {
  top: number;
  bottom: number;
}

export interface PinConfiguratorState {
  title: string;
  mode: "create" | "edit";
  data: PinDiagramData;
  assignments: PinAssignments;
  boardImage?: string;
  padBand?: PadBand;
}

export function renderPinConfiguratorHtml(
  webview: vscode.Webview,
  state: PinConfiguratorState,
): string {
  const nonce = makeNonce();
  const payload = safeJson(state);
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'nonce-${nonce}'; script-src 'nonce-${nonce}'; img-src ${webview.cspSource} https:;">
<style nonce="${nonce}">${STYLES}</style>
<title>${escapeHtml(state.title)}</title>
</head>
<body>
<main>
  <header>
    <h1>${escapeHtml(state.title)}</h1>
    <p class="subtitle">${escapeHtml(state.data.board_id)} · ${escapeHtml(state.data.example.ref)}</p>
  </header>
  <section class="shell">
    <section class="pinout" id="pinout" aria-label="XIAO pinout"></section>
    <aside class="side">
      <h2>Pin roles</h2>
      <div id="roles"></div>
      <div class="actions">
        <button id="save">Save</button>
        <button id="reset" class="secondary">Reset to defaults</button>
      </div>
      <p class="hint" id="hint"></p>
      <h2>Legend</h2>
      <ul class="legend">
        <li><span class="swatch selectable"></span>Selectable</li>
        <li><span class="swatch assigned"></span>Assigned</li>
        <li><span class="swatch reserved"></span>Reserved</li>
        <li><span class="swatch bus"></span>Fixed bus</li>
        <li><span class="swatch power"></span>Power</li>
      </ul>
    </aside>
  </section>
</main>
<script nonce="${nonce}">
const vscode = acquireVsCodeApi();
const state = ${payload};
let selectedRole = state.data.roles[0]?.role ?? "";
let assignments = { ...state.assignments };

function byId(id) {
  return document.getElementById(id);
}

function pinMap() {
  return new Map(state.data.pins.map((pin) => [pin.id, pin]));
}

function activeRole() {
  return state.data.roles.find((role) => role.role === selectedRole);
}

function assignedRoleForPin(pinId) {
  return Object.entries(assignments).find(([, value]) => value === pinId)?.[0];
}

function roleAllowedPins(roleName) {
  return new Set(state.data.roles.find((role) => role.role === roleName)?.allowed ?? []);
}

function canAssign(pin) {
  if (!selectedRole || !pin || state.data.example.pin_policy !== "selectable") {
    return false;
  }
  const allowed = roleAllowedPins(selectedRole);
  return allowed.has(pin.id) && !["power", "reserved", "bus", "incompatible"].includes(pin.status);
}

function makePin(pin, side) {
  const assignedRole = assignedRoleForPin(pin.id);
  const button = document.createElement("button");
  button.className = ["pin", side, pin.status, assignedRole ? "assigned" : "",
    pin.status === "default" ? "is-default" : "", canAssign(pin) ? "clickable" : ""]
    .filter(Boolean)
    .join(" ");
  button.disabled = !canAssign(pin);
  button.title = [pin.id, pin.chip_pin ? "chip " + pin.chip_pin : "", pin.reason ?? "", assignedRole ? "assigned to " + assignedRole : ""]
    .filter(Boolean)
    .join(" · ");
  const meta = assignedRole ?? pin.reason ?? pin.chip_pin ?? pin.rail ?? pin.status;
  button.innerHTML = '<span class="pin-id">' + pin.id + '</span><span class="pin-meta">' + meta + '</span>';
  button.addEventListener("click", () => {
    if (canAssign(pin)) {
      assignments[selectedRole] = pin.id;
      render();
    }
  });
  return button;
}

// Even fractions for 7 pads inside the measured band, inset by ~half a pad so row
// centers land on pad centers rather than the band's outer edge.
// 在测得的焊盘带内为 7 个焊盘取等距比例，向内缩约半个焊盘，使行中心对准焊盘中心。
function padFractions(count) {
  const band = state.padBand;
  const inset = (band.bottom - band.top) * 0.05;
  const top = band.top + inset;
  const bottom = band.bottom - inset;
  const fracs = [];
  for (let i = 0; i < count; i += 1) {
    fracs.push(count === 1 ? (top + bottom) / 2 : top + (bottom - top) * (i / (count - 1)));
  }
  return fracs;
}

function renderPinout() {
  const root = byId("pinout");
  root.innerHTML = "";
  const left = state.data.layout.left ?? [];
  const right = state.data.layout.right ?? [];
  const pins = pinMap();
  const caption = state.data.example.interface + " · " + state.data.example.pin_policy;

  if (state.boardImage && state.padBand) {
    root.className = "pinout overlay";
    const stageRow = document.createElement("div");
    stageRow.className = "stage-row";

    const stage = document.createElement("div");
    stage.className = "board-stage";
    const img = document.createElement("img");
    img.className = "board-img";
    img.src = state.boardImage;
    img.alt = state.data.board_id;
    stage.appendChild(img);

    const build = (ids, side) => {
      const rail = document.createElement("div");
      rail.className = "rail " + side;
      const fracs = padFractions(ids.length);
      ids.forEach((id, i) => {
        const pin = pins.get(id);
        if (!pin) return;
        const row = makePin(pin, side);
        row.style.top = (fracs[i] * 100) + "%";
        rail.appendChild(row);
      });
      return rail;
    };
    stageRow.appendChild(build(left, "left"));
    stageRow.appendChild(stage);
    stageRow.appendChild(build(right, "right"));
    root.appendChild(stageRow);

    const cap = document.createElement("div");
    cap.className = "board-caption";
    cap.textContent = caption;
    root.appendChild(cap);
    return;
  }

  // Fallback: two plain columns around a labelled rectangle.
  // 回退：无图时用矩形加左右两列。
  root.className = "pinout columns";
  const col = (ids, side) => {
    const c = document.createElement("div");
    c.className = "pin-column";
    ids.forEach((id) => {
      const pin = pins.get(id);
      if (pin) c.appendChild(makePin(pin, side));
    });
    return c;
  };
  root.appendChild(col(left, "left"));
  const body = document.createElement("div");
  body.className = "board-body";
  body.innerHTML = '<div class="board-title">XIAO</div><div class="board-subtitle">' + caption + '</div>';
  root.appendChild(body);
  root.appendChild(col(right, "right"));
}

function renderRoles() {
  const container = byId("roles");
  container.innerHTML = "";
  if (state.data.example.pin_policy !== "selectable") {
    const note = document.createElement("p");
    note.className = "hint";
    note.textContent = "This fixed-bus module is read-only here. Use the highlighted bus pins for wiring.";
    container.appendChild(note);
    byId("save").disabled = true;
    byId("reset").disabled = true;
    return;
  }
  byId("save").disabled = false;
  byId("reset").disabled = false;
  for (const role of state.data.roles) {
    const row = document.createElement("button");
    row.className = "role" + (role.role === selectedRole ? " active" : "");
    row.innerHTML = '<span>' + role.role + '</span><strong>' + (assignments[role.role] ?? role.default) + '</strong>';
    row.addEventListener("click", () => {
      selectedRole = role.role;
      render();
    });
    container.appendChild(row);
  }
}

function renderHint() {
  const role = activeRole();
  const hint = byId("hint");
  if (state.data.example.pin_policy !== "selectable") {
    hint.textContent = "Fixed buses are configured by the board connector abstraction.";
    return;
  }
  hint.textContent = role
    ? "Choose a pin for role '" + role.role + "'. Allowed: " + role.allowed.join(", ")
    : "No configurable pin roles.";
}

function render() {
  renderPinout();
  renderRoles();
  renderHint();
}

byId("save").addEventListener("click", () => {
  vscode.postMessage({ type: "save", assignments });
});

byId("reset").addEventListener("click", () => {
  assignments = Object.fromEntries(state.data.roles.map((role) => [role.role, role.default]));
  render();
});

render();
</script>
</body>
</html>`;
}

function safeJson(value: unknown): string {
  return JSON.stringify(value).replace(/</g, "\\u003c");
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function makeNonce(): string {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let text = "";
  for (let i = 0; i < 32; i += 1) {
    text += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return text;
}

const STYLES = `
body { font-family: var(--vscode-font-family); color: var(--vscode-foreground);
  margin: 0; padding: 0 18px 28px; line-height: 1.45; font-size: var(--vscode-font-size); }
h1 { font-size: 1.35em; margin: 18px 0 2px; }
h2 { font-size: 1em; margin: 18px 0 8px; }
button { font: inherit; }
.subtitle, .hint { color: var(--vscode-descriptionForeground); }
.shell { display: grid; grid-template-columns: minmax(480px, 1fr) 280px; gap: 22px; align-items: start; }

/* Overlay layout: board image centered, pin rails aligned to real pads. */
/* 叠加布局：板子图居中，引脚导轨对齐真实焊盘。 */
.pinout.overlay { display: flex; flex-direction: column; align-items: center; padding: 20px 8px; overflow-x: auto; }
.stage-row { display: flex; align-items: stretch; justify-content: center; gap: 26px; }
.board-stage { position: relative; width: 380px; flex: 0 0 auto; }
.board-img { width: 100%; display: block; }
.rail { position: relative; width: 260px; flex: 0 0 auto; }
.rail .pin { position: absolute; width: 100%; transform: translateY(-50%); }
.rail .pin::after { content: ""; position: absolute; top: 50%; width: 26px;
  border-top: 1px dashed var(--vscode-descriptionForeground); }
.rail.left .pin::after { right: -26px; }
.rail.right .pin::after { left: -26px; }
.board-caption { color: var(--vscode-descriptionForeground); margin-top: 14px; font-size: 0.95em; text-align: center; }

/* Fallback column layout when no board image is available. */
/* 无板子图时的回退两列布局。 */
.pinout.columns { display: grid; grid-template-columns: 1fr 150px 1fr; gap: 12px; align-items: center; }
.pin-column { display: flex; flex-direction: column; gap: 6px; }
.board-body { min-height: 340px; border: 1px solid var(--vscode-panel-border);
  border-radius: 18px; display: flex; flex-direction: column; align-items: center;
  justify-content: center; background: var(--vscode-editorWidget-background); }
.board-title { font-size: 1.6em; font-weight: 700; letter-spacing: 0.08em; }
.board-subtitle { color: var(--vscode-descriptionForeground); margin-top: 8px; }

.pin { position: relative; box-sizing: border-box; border: 1px solid var(--vscode-panel-border); border-radius: 8px;
  background: var(--vscode-button-secondaryBackground); color: var(--vscode-button-secondaryForeground);
  display: flex; justify-content: space-between; align-items: center; gap: 8px; padding: 9px 12px;
  text-align: left; }
.pin.is-default::before { content: "default"; position: absolute; top: -8px; left: 10px;
  font-size: 0.62em; line-height: 1.4; padding: 0 5px; border-radius: 7px;
  background: var(--vscode-badge-background); color: var(--vscode-badge-foreground);
  border: 1px solid var(--vscode-panel-border); }
.pin.right { flex-direction: row-reverse; text-align: right; }
.pin-column .pin { width: 100%; }
.pin.clickable { cursor: pointer; border-color: var(--vscode-focusBorder); }
.pin.clickable:hover { background: var(--vscode-list-hoverBackground); }
.pin.assigned { background: var(--vscode-button-background); color: var(--vscode-button-foreground); }
.pin.reserved, .pin.incompatible { opacity: 0.55; }
.pin.power { opacity: 0.8; }
.pin.bus { border-color: var(--vscode-charts-blue); }
.pin-id { font-weight: 700; font-size: 1.05em; }
.pin-meta { color: inherit; opacity: 0.78; font-size: 0.9em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.side { border: 1px solid var(--vscode-panel-border); border-radius: 10px; padding: 12px; }
.role { width: 100%; display: flex; justify-content: space-between; margin-bottom: 6px;
  padding: 8px 10px; border: 1px solid var(--vscode-panel-border); border-radius: 8px;
  color: var(--vscode-foreground); background: transparent; }
.role.active { border-color: var(--vscode-focusBorder); background: var(--vscode-list-activeSelectionBackground); }
.actions { display: flex; gap: 8px; margin-top: 14px; }
.actions button { border: 0; border-radius: 5px; padding: 7px 12px; color: var(--vscode-button-foreground);
  background: var(--vscode-button-background); cursor: pointer; }
.actions button.secondary { color: var(--vscode-button-secondaryForeground); background: var(--vscode-button-secondaryBackground); }
.actions button:disabled { opacity: 0.55; cursor: not-allowed; }
.legend { list-style: none; padding: 0; margin: 0; }
.legend li { display: flex; align-items: center; gap: 8px; margin: 6px 0; }
/* Swatches mirror the actual pin state styles above so the legend stays accurate. */
/* 色块镜像上面引脚各状态的真实样式，保证图例与引脚一致。 */
.swatch { width: 16px; height: 16px; border-radius: 5px; border: 1px solid var(--vscode-panel-border);
  background: var(--vscode-button-secondaryBackground); }
.swatch.selectable { border-color: var(--vscode-focusBorder); }
.swatch.assigned { background: var(--vscode-button-background); border-color: var(--vscode-button-background); }
.swatch.reserved { opacity: 0.55; }
.swatch.bus { border-color: var(--vscode-charts-blue); }
.swatch.power { opacity: 0.8; }
@media (max-width: 820px) {
  .shell { grid-template-columns: 1fr; }
}
`;
