# Onboarding And Distribution Design

## 1. Onboarding Goal

Onboarding starts from a user result and includes environment setup as one step:

```text
find an example -> build it -> flash it -> understand it -> modify it -> contribute back
```

Environment setup prepares the toolchain and then points users to repository
examples and projects.

One-sentence summary: onboarding should lead users to repository examples and
projects as quickly as possible.

## 2. User Entry Points

The repository should support four entry points:

- board-first: "I have XIAO ESP32C6. What can I run?"
- Grove-first: "I have Grove DHT20. Which examples exist?"
- capability-first: "I need I2C, BLE, Wi-Fi, ADC, display, or low power."
- project-first: "I want a complete sensor/display/wireless project."

One-sentence summary: users start from hardware or intent.

## 3. Setup Layer

Setup scripts should:

- install or verify Zephyr tooling
- prepare the Zephyr workspace
- fetch required blobs when needed
- print the next repository example/project command

They should point users to the next repository example or project command.

One-sentence summary: setup opens the door and points at this repository's
content.

## 4. Distribution Layers

| Layer | Purpose | User action |
| --- | --- | --- |
| L1 setup scripts | prepare local toolchain | run one script |
| L2 example build scripts or CLI | build repository content | build selected example |
| L3 project generator | create custom project from known assets | choose hardware and source asset |
| L4 VS Code plugin | browse and create visually | select, preview, create |

One-sentence summary: each layer should reduce friction around examples and
projects.

## 5. Contribution Onboarding

External contributors should be able to:

1. choose an example/project category
2. copy a documented structure
3. run local validation
4. record build or hardware evidence
5. open a contribution that maintainers can review predictably

One-sentence summary: contribution onboarding is part of product onboarding.

## 6. Implementation Priorities

1. Make at least one repository example build from the project root.
2. Add scripts or CLI commands for building examples.
3. Add contribution documentation.
4. Add platform setup improvements.
5. Add manifest/container/plugin layers only after examples exist.

One-sentence summary: content first, tooling second, polish third.
