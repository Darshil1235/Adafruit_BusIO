#!/usr/bin/env python3
import argparse
import json
import sys
from collections import Counter


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert a PLL/QPLL/GT JSON report to Markdown"
    )
    parser.add_argument(
        "json",
        nargs="?",
        default="-",
        help="Path to pll_report.json, or '-' to read from stdin (default)",
    )
    parser.add_argument(
        "--show-all-params",
        action="store_true",
        help="Show all parameter key/values instead of a curated subset",
    )
    parser.add_argument(
        "--no-hints",
        action="store_true",
        help="Do not print the Hints section",
    )
    parser.add_argument(
        "--title",
        default="PLL/QPLL Report",
        help="Override the Markdown title",
    )
    return parser.parse_args()


def load_report(json_path: str):
    try:
        if json_path == "-":
            return json.load(sys.stdin)
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found: {json_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def format_params(params: dict, show_all: bool) -> str:
    if not params:
        return ""

    if show_all:
        items = sorted(params.items(), key=lambda kv: kv[0])
    else:
        keep_keys = {
            # MMCM/PLL
            "CLKFBOUT_MULT",
            "DIVCLK_DIVIDE",
            "CLKOUT0_DIVIDE",
            "CLKIN1_PERIOD",
            # QPLL/CPLL
            "QPLL_REFCLK_DIV",
            "QPLL_FBDIV",
            "QPLL_FBDIV_RATIO",
            "CPLL_REFCLK_DIV",
            "CPLL_FBDIV",
            "CPLL_FBDIV_45",
            # GT TX/RX
            "TXOUT_DIV",
            "RXOUT_DIV",
            "TXCLK25_DIV",
            "RXCLK25_DIV",
            "RXCDR_CFG",
        }
        items = sorted(
            ((k, v) for k, v in params.items() if k in keep_keys),
            key=lambda kv: kv[0],
        )
        if not items:
            return ""

    formatted = ", ".join(f"{k}={v}" for k, v in items)
    return formatted


def print_summary(title: str, data: dict):
    summary = data.get("summary", {})
    num_items = summary.get("num_items", len(data.get("items", [])))
    print(f"## {title}")
    print(f"Found {num_items} PLL/QPLL/GT items")

    items = data.get("items", [])
    if items:
        by_type = Counter((it or {}).get("type", "") or "unknown" for it in items)
        ordered = sorted(by_type.items(), key=lambda kv: kv[0])
        counts_str = ", ".join(f"{t}:{c}" for t, c in ordered)
        print(f"By type: {counts_str}\n")
    else:
        print()


def main():
    args = parse_args()
    data = load_report(args.json)

    print_summary(args.title, data)

    for i, it in enumerate(data.get("items", []), 1):
        it = it or {}
        typ = it.get("type", "")
        prim = it.get("primitive", "")
        path = it.get("path", "")
        inst = it.get("inst")
        line = f"- [{i}] {typ} {prim} in `{path}`"
        if inst:
            line += f" inst `{inst}`"
        print(line)

        params = it.get("params", {})
        params_str = format_params(params, args.show_all_params)
        if params_str:
            print(f"  - params: {params_str}")

    hints = data.get("hints", [])
    if hints and not args.no_hints:
        print("\n## Hints")
        for h in hints:
            h = h or {}
            key = h.get("key", "hint")
            val = h.get("value", "")
            path = h.get("path", "")
            at = f" @ `{path}`" if path else ""
            print(f"- {key}: {val}{at}")


if __name__ == "__main__":
    main()





