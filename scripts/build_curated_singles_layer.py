#!/usr/bin/env python3
"""Build the deterministic curated singles point layer."""

from pathlib import Path

from data_layer_lib import build_curated_singles_layer, parser_with_io, write_json


def main() -> None:
    parser = parser_with_io(__doc__ or "")
    args = parser.parse_args()
    out = args.out or args.curated
    metrics = build_curated_singles_layer(args.input, args.cleaned, out, args.quarantine)
    write_json(out / "_curated_metrics.json", metrics)
    print(f"wrote curated singles layer to {out}")


if __name__ == "__main__":
    main()
