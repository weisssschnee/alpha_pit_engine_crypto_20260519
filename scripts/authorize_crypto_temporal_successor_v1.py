from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


def _committed_blob_sha(repo_root: Path, revision: str, path: str) -> str:
    object_id = subprocess.check_output(
        ["git", "rev-parse", f"{revision}:{path}"], cwd=repo_root, text=True
    ).strip()
    payload = subprocess.check_output(
        ["git", "cat-file", "blob", object_id], cwd=repo_root
    )
    return hashlib.sha256(payload).hexdigest().upper()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize the sole external one-time successor authorization. "
            "The resulting authorization-only change must be reviewed and committed "
            "before the canonical runner can consume it."
        )
    )
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--runtime-date", required=True)
    parser.add_argument("--authorization-decision-id", required=True)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    sys.path.insert(0, str(repo_root))
    from alphafactory_crypto.broad_search.temporal_successor_v1 import (
        AUTHORIZED_STATUS,
        NOT_AUTHORIZED_STATUS,
        SUCCESSOR_AUTHORIZATION_SCOPE,
        SUCCESSOR_AUTHORIZATION_PATH,
        SUCCESSOR_CAMPAIGN,
        SUCCESSOR_COMPONENT_PATHS,
        authorization_content_sha,
        executor_workspace_identity,
    )

    path = repo_root / SUCCESSOR_AUTHORIZATION_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    if (
        payload.get("status") != NOT_AUTHORIZED_STATUS
        or payload.get("run_authorized") is not False
        or payload.get("consumed") is not False
    ):
        raise RuntimeError("successor authorization template is not available")
    if subprocess.run(
        ["git", "diff", "--quiet"], cwd=repo_root, check=False
    ).returncode != 0 or subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=repo_root, check=False
    ).returncode != 0:
        raise RuntimeError("authorization must start from a clean implementation commit")
    implementation_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip()
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=repo_root, text=True
    ).strip()
    decision_id = str(args.authorization_decision_id).strip()
    if not branch:
        raise RuntimeError("successor authorization requires a named branch")
    if not decision_id:
        raise RuntimeError("successor authorization decision id is required")
    updated = {
        key: value for key, value in payload.items() if key != "authorization_sha256"
    }
    updated.update(
        {
            "status": AUTHORIZED_STATUS,
            "run_authorized": True,
            "authorized_implementation_sha": implementation_sha,
            "authorized_component_sha256": {
                component: _committed_blob_sha(repo_root, implementation_sha, component)
                for component in SUCCESSOR_COMPONENT_PATHS
            },
            "expected_branch": branch,
            "runtime_id": f"{SUCCESSOR_CAMPAIGN}_{args.runtime_date}",
            "executor_identity": executor_workspace_identity(repo_root),
            "run_authorization": {
                "authority": "CURRENT_USER_INSTRUCTION",
                "decision_id": decision_id,
                "scope": SUCCESSOR_AUTHORIZATION_SCOPE,
            },
        }
    )
    updated["authorization_sha256"] = authorization_content_sha(updated)
    temporary = path.with_name(path.name + ".authorizing.tmp")
    temporary.write_text(
        json.dumps(updated, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)
    print(json.dumps(updated, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
