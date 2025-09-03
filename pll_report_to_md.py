#!/usr/bin/env python3
import json
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: pll_report_to_md.py <pll_report.json>")
        sys.exit(1)

    data = json.load(open(sys.argv[1]))

    print("## PLL/QPLL Report")
    print(f"Found {data.get('summary',{}).get('num_items',0)} PLL/QPLL/GT items\n")

    for i, it in enumerate(data.get("items", []), 1):
        typ = it.get("type", "")
        prim = it.get("primitive", "")
        path = it.get("path", "")
        inst = it.get("inst")
        line = f"- [{i}] {typ} {prim} in `{path}`"
        if inst:
            line += f" inst `{inst}`"
        print(line)
        params = it.get("params", {})
        if params:
            keep = [
                "CLKFBOUT_MULT", "DIVCLK_DIVIDE", "CLKOUT0_DIVIDE", "CLKIN1_PERIOD",
                "QPLL_REFCLK_DIV", "QPLL_FBDIV", "QPLL_FBDIV_RATIO",
            ]
            show = {k: v for k, v in params.items() if k in keep}
            if show:
                print(f"  - params: {show}")

    hints = data.get("hints", [])
    if hints:
        print("\n## Hints")
        for h in hints:
            print(f"- {h.get('key')}: {h.get('value')} @ `{h.get('path')}`")


if __name__ == "__main__":
    main()





