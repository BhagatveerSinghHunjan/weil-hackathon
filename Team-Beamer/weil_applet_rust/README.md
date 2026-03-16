# ChainVest Rust MCP Applet

This directory contains the Rust WeilChain MCP applet scaffold for the
`ChainVestMCP` interface.

## What this is

- `chainvest.widl`: the MCP interface definition used for tool generation
- `src/lib.rs`: Rust applet logic matching the current deterministic scoring
- `manifest.json`: deployment metadata for Explorer or CLI-assisted packaging
- `config.yaml`: empty config because this applet does not require secrets
- `scripts/generate_bindings.sh`: WIDL server binding generation
- `scripts/build_wasm.sh`: WASM build helper

## Tooling expected by Weilliptic docs

The official MCP tutorial requires:

- Rust with the `wasm32-unknown-unknown` target
- the `widl` compiler binary in `PATH`
- the Weilliptic Rust ADK crates from the `wadk` repository

This `Cargo.toml` expects the `wadk` repository at:

`/Users/bhagatveersingh/CHAINVEST-REPO/wadk`

If you clone it elsewhere, update the dependency paths in `Cargo.toml`.

## Recommended flow

1. Clone `wadk` next to this repo.
2. Install Rust and the WASM target.
3. Install the `widl` compiler.
4. Run `widl generate chainvest.widl server rust`.
5. Compare the generated trait/types against `src/lib.rs`.
6. Build with `cargo build --target wasm32-unknown-unknown --release`.
7. Deploy the resulting `target/wasm32-unknown-unknown/release/chainvest_mcp.wasm`.

## Deploy command

The Weilliptic CLI tutorial shows deployment in this form:

`deploy --file-path target/wasm32-unknown-unknown/release/chainvest_mcp.wasm --widl-file chainvest.widl`

The deploy response includes `contract_address`. That is the Applet Id for
Icarus registration.
