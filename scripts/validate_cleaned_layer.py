#!/usr/bin/env python3
"""Validate Milestone 1B cleaned and curated outputs."""

from data_layer_lib import parser_with_io, validate_layer


def main() -> None:
    parser = parser_with_io(__doc__ or "")
    args = parser.parse_args()
    result = validate_layer(args.cleaned, args.curated, args.contracts)
    print(f"Milestone 1B {result['status']}: curated rows={result['curated_singles_point_rows']}")


if __name__ == "__main__":
    main()
