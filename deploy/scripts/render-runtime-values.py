#!/usr/bin/env python3
import json
import os
import sys


def required_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def main() -> None:
    output_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), "values.runtime.yaml")
    )

    values = {
        "publicUrl": required_env("OPTIO_PUBLIC_URL"),
        "encryption": {"key": required_env("OPTIO_ENCRYPTION_KEY")},
        "externalDatabase": {"url": required_env("EXTERNAL_DATABASE_URL")},
        "externalRedis": {"url": required_env("EXTERNAL_REDIS_URL")},
        "auth": {
            "github": {
                "clientId": required_env("AUTH_GITHUB_CLIENT_ID"),
                "clientSecret": required_env("AUTH_GITHUB_CLIENT_SECRET"),
            }
        },
        "ingress": {
            "hosts": [
                {
                    "host": required_env("OPTIO_DOMAIN"),
                    "paths": [
                        {"path": "/", "pathType": "Prefix", "service": "web"},
                        {"path": "/api", "pathType": "Prefix", "service": "api"},
                        {"path": "/ws", "pathType": "Prefix", "service": "api"},
                    ],
                }
            ]
        },
    }

    if os.environ.get("GITHUB_APP_ID"):
        values["github"] = {"app": {"existingSecret": "optio-github-app"}}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(values, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
