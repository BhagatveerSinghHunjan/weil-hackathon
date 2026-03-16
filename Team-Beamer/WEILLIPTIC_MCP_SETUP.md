# ChainVest Weilliptic MCP Setup

This repo already contains a local Python MCP server in
`weil_mcp/chainvest_mcp.py`, but that is not the same thing as a deployed
WeilChain MCP applet.

If you are following the Icarus registration tutorial, the value it calls
"Applet Id" is the deployed applet address on WeilChain. You will only have
that value after you build and deploy an MCP applet.

## What is missing right now

The repo has:

- a WIDL spec at `weil_mcp/chainvest.widl`
- a local Python MCP server for development
- Python SDK wiring for wallet/audit logging

The repo does not yet have:

- a Rust or Go MCP applet project
- a compiled `.wasm` artifact for deployment
- a deployment manifest/config for Explorer-based deployment
- a deployed WeilChain contract address

Because of that, there is currently no Applet Id to paste into Icarus.

## What the docs require

According to the Weilliptic MCP tutorial, MCP server applets for WeilChain are
currently supported in Rust and Go. The register step in Icarus expects:

- a Name
- an Applet Id, which is the deployed applet address

According to the deployment tutorial, that address is returned as
`contract_address` after deployment. That is the value you later enter into
Icarus.

## Practical sequence for ChainVest

1. Keep using `weil_mcp/chainvest.widl` as the interface definition.
2. Create a Rust or Go WeilChain MCP applet project for the same tool surface.
3. Generate MCP server bindings from the WIDL file.
4. Implement the applet logic so it exposes `evaluate_startup`.
5. Compile the applet to `.wasm`.
6. Deploy the `.wasm` and `.widl` to WeilChain via CLI or Explorer.
7. Copy the returned `contract_address`.
8. Open Icarus and register:
   - Name: `chainvest`
   - Applet Id: `<contract_address>`

## What to tell your teammate

If your friend did not create and deploy the applet, then nothing is wrong with
Icarus: the Applet Id simply does not exist yet.

The missing deliverable is not "find the key". The missing deliverable is:

- build the ChainVest MCP applet
- deploy it
- use the returned contract address

## Local code impact

`weil_mcp/chainvest_mcp.py` is still useful for:

- local testing
- validating the tool contract
- matching business logic before applet implementation

But it should not be treated as the deployable artifact for Icarus.

## Source links

- Icarus registration tutorial:
  https://docs.weilliptic.ai/docs/tutorials/register_mcp/
- Create MCP server tutorial:
  https://docs.weilliptic.ai/docs/tutorials/mcp_basic
- Deploy applet tutorial:
  https://docs.weilliptic.ai/docs/tutorials/deploy_applet/
