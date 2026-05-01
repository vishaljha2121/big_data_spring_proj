#!/usr/bin/env python3
"""Build project-compliant cleaned Parquet outputs from staging CSV.GZ inputs."""

from pathlib import Path

from data_layer_lib import build_cleaned_layer, parser_with_io


def main() -> None:
    parser = parser_with_io(__doc__ or "")
    args = parser.parse_args()
    out = args.out or Path("data/cleaned")
    build_cleaned_layer(args.input, out, Path("."))
    print(f"wrote cleaned layer to {out}")


if __name__ == "__main__":
    main()
