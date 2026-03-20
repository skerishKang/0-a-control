#!/usr/bin/env bash
set -euo pipefail

msg="${1:-local snapshot}"

fossil addremove
fossil commit -m "$msg"
