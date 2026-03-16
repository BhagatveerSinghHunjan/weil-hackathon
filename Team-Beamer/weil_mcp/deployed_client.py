from __future__ import annotations

import asyncio
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Optional


def _ensure_local_wadk_python_path() -> None:
    wadk_python = Path(__file__).resolve().parents[2] / "wadk" / "adk" / "python"
    if wadk_python.is_dir():
        wadk_python_str = str(wadk_python)
        if wadk_python_str not in sys.path:
            sys.path.insert(0, wadk_python_str)


try:
    from weil_wallet import ContractId, PrivateKey, WeilClient, Wallet, load_wallet

    WEIL_CONTRACT_CLIENT_AVAILABLE = True
except Exception:
    _ensure_local_wadk_python_path()
    try:
        from weil_wallet import ContractId, PrivateKey, WeilClient, Wallet, load_wallet

        WEIL_CONTRACT_CLIENT_AVAILABLE = True
    except Exception:
        ContractId = PrivateKey = WeilClient = Wallet = load_wallet = None  # type: ignore[assignment]
        WEIL_CONTRACT_CLIENT_AVAILABLE = False


DEFAULT_CHAINVEST_APPLET_ID = (
    "aaaaaatg4hm23lex4jeisnflilatgn5hqhjpfh3ujc2kofr5alyxmolyce"
)


def _resolve_wallet_path() -> Optional[str]:
    repo_root = Path(__file__).resolve().parents[2]
    candidates = [
        os.getenv("CHAINVEST_WEIL_WALLET_PATH"),
        os.getenv("WEIL_WALLET_PATH"),
        os.getenv("WEIL_ACCOUNT_PATH"),
        str(repo_root.parent / ".weil" / "account.wc"),
        str(repo_root / ".weil" / "account.wc"),
    ]

    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate
    return None


def _resolve_contract_id() -> str:
    return os.getenv("CHAINVEST_WEIL_APPLET_ID", DEFAULT_CHAINVEST_APPLET_ID)


def _load_signing_wallet(wallet_path: str):
    try:
        wallet_bundle = load_wallet(wallet_path)
        return wallet_bundle.derive_account(0).to_weil_wallet()
    except Exception:
        pass

    try:
        from bip_utils import Bip32Slip10Secp256k1

        lines = Path(wallet_path).read_text(encoding="utf-8").splitlines()
        if not lines:
            raise ValueError("wallet file is empty")

        xprv = lines[0].strip()
        node = Bip32Slip10Secp256k1.FromExtendedKey(xprv)
        account_node = node.ChildKey(0)
        private_key = PrivateKey.from_bytes(account_node.PrivateKey().Raw().ToBytes())
        return Wallet(private_key)
    except Exception as exc:
        raise RuntimeError(f"unable to load signing wallet from {wallet_path}: {exc}") from exc


def _run_sync(coro):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


def _unwrap_ok_payload(raw: str) -> Any:
    payload = json.loads(raw)
    if isinstance(payload, dict) and "Ok" in payload:
        value = payload["Ok"]
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value
    return payload


async def _execute_deployed_evaluation(
    revenue: float,
    burn: float,
    cash: float,
    business_description: str,
) -> dict[str, Any]:
    if not WEIL_CONTRACT_CLIENT_AVAILABLE:
        raise RuntimeError("weil_wallet contract client is unavailable")

    wallet_path = _resolve_wallet_path()
    if not wallet_path:
        raise RuntimeError("no Weilliptic wallet file found for deployed applet execution")

    signing_wallet = _load_signing_wallet(wallet_path)
    sentinel_host = os.getenv("WEIL_SENTINEL_HOST", "https://sentinel.unweil.me")
    verify_tls = os.getenv("WEIL_SENTINEL_VERIFY", "true").lower() not in {
        "0",
        "false",
        "no",
    }

    client = WeilClient(signing_wallet, sentinel_host=sentinel_host, verify=verify_tls)
    try:
        response = await client.execute(
            ContractId(_resolve_contract_id()),
            "evaluate_startup",
            json.dumps(
                {
                    "revenue": revenue,
                    "burn": burn,
                    "cash": cash,
                    "business_description": business_description,
                }
            ),
            should_hide_args=False,
        )
    finally:
        await client.close()

    result = _unwrap_ok_payload(response.txn_result)
    if not isinstance(result, dict):
        raise RuntimeError(f"unexpected deployed applet response: {result!r}")

    result["deployment"] = {
        "source": "weilchain_applet",
        "contract_address": _resolve_contract_id(),
        "wallet_path": wallet_path,
        "status": str(getattr(response, "status", "UNKNOWN")),
        "block_height": getattr(response, "block_height", None),
        "batch_id": getattr(response, "batch_id", None),
        "creation_time": getattr(response, "creation_time", None),
    }
    return result


def evaluate_startup_on_weilchain(
    revenue: float,
    burn: float,
    cash: float,
    business_description: str,
) -> Optional[dict[str, Any]]:
    try:
        return _run_sync(_execute_deployed_evaluation(revenue, burn, cash, business_description))
    except Exception:
        return None


__all__ = [
    "DEFAULT_CHAINVEST_APPLET_ID",
    "WEIL_CONTRACT_CLIENT_AVAILABLE",
    "evaluate_startup_on_weilchain",
]
