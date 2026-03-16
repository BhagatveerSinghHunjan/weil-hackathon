import asyncio
import hashlib
import json
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Optional

try:
    from weil_wallet import PrivateKey, Wallet, WeilClient

    WEIL_WALLET_AVAILABLE = True
except Exception:
    PrivateKey = Wallet = WeilClient = None  # type: ignore[assignment]
    WEIL_WALLET_AVAILABLE = False


def _json_default(value: Any) -> str:
    return str(value)


def hash_data(data: Any) -> Optional[str]:
    """Convert JSON-like data to a deterministic SHA256 hash."""
    if data is None:
        return None

    serialized = json.dumps(data, sort_keys=True, default=_json_default).encode()
    return hashlib.sha256(serialized).hexdigest()


def _resolve_private_key_path() -> Optional[str]:
    candidates = [
        os.getenv("WEIL_PRIVATE_KEY_PATH"),
        os.getenv("WEIL_PRIVATE_KEY_FILE"),
        os.path.join(os.getcwd(), "private_key.wc"),
        os.path.join(os.path.dirname(__file__), "..", "private_key.wc"),
    ]

    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def _run_sync(coro):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


async def _audit_step_on_chain(payload: dict[str, Any]) -> Optional[dict[str, Any]]:
    if not WEIL_WALLET_AVAILABLE:
        return None

    key_path = _resolve_private_key_path()
    if not key_path:
        return None

    sentinel_host = os.getenv("WEIL_SENTINEL_HOST")
    verify_tls = os.getenv("WEIL_SENTINEL_VERIFY", "true").lower() not in {
        "0",
        "false",
        "no",
    }

    try:
        pk = PrivateKey.from_file(key_path)
        wallet = Wallet(pk)

        kwargs = {"verify": verify_tls}
        if sentinel_host:
            kwargs["sentinel_host"] = sentinel_host

        async with WeilClient(wallet, **kwargs) as client:
            tx = await client.audit(json.dumps(payload, default=_json_default))
            return {
                "status": str(getattr(tx, "status", "UNKNOWN")),
                "block_height": getattr(tx, "block_height", None),
                "batch_id": getattr(tx, "batch_id", None),
                "tx_idx": getattr(tx, "tx_idx", None),
                "creation_time": getattr(tx, "creation_time", None),
                "txn_result": getattr(tx, "txn_result", None),
            }
    except Exception as exc:
        return {"error": str(exc)}


def _build_onchain_payload(
    step_name: str,
    timestamp: str,
    input_hash: Optional[str],
    output_hash: Optional[str],
    state_hash: Optional[str],
) -> dict[str, Any]:
    return {
        "source": "chainvest-agent-workflow",
        "timestamp_utc": timestamp,
        "step": step_name,
        "input_hash": input_hash,
        "output_hash": output_hash,
        "state_hash": state_hash,
    }


def log_to_chain(
    state: dict[str, Any],
    step_name: str,
    input_data: Any = None,
    output_data: Any = None,
) -> dict[str, Any]:
    input_hash = hash_data(input_data)
    output_hash = hash_data(output_data)
    state_hash = hash_data(state)
    local_tx_hash = f"0x{uuid.uuid4().hex[:16]}"
    timestamp = datetime.now(timezone.utc).isoformat()

    on_chain_payload = _build_onchain_payload(
        step_name=step_name,
        timestamp=timestamp,
        input_hash=input_hash,
        output_hash=output_hash,
        state_hash=state_hash,
    )
    on_chain_result = _run_sync(_audit_step_on_chain(on_chain_payload))
    on_chain_ok = bool(on_chain_result and "error" not in on_chain_result)

    log_entry = {
        "timestamp": timestamp,
        "step": step_name,
        "input_hash": input_hash,
        "output_hash": output_hash,
        "state_hash": state_hash,
        "tx_hash": local_tx_hash,
        "on_chain": on_chain_ok,
        "on_chain_details": on_chain_result,
    }

    if "logs" not in state:
        state["logs"] = []
    if "tx_hashes" not in state:
        state["tx_hashes"] = []
    if "onchain_audit" not in state:
        state["onchain_audit"] = []

    state["logs"].append(log_entry)
    state["tx_hashes"].append(local_tx_hash)
    if on_chain_result:
        state["onchain_audit"].append(
            {
                "step": step_name,
                "timestamp": timestamp,
                "details": on_chain_result,
            }
        )

    return state

