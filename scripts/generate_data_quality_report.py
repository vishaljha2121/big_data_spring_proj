#!/usr/bin/env python3
"""Generate JSON and Markdown data-quality evidence for Milestone 1B."""

from data_layer_lib import generate_reports, parser_with_io


def main() -> None:
    parser = parser_with_io(__doc__ or "")
    args = parser.parse_args()
    report = generate_reports(args.input, args.cleaned, args.curated, args.quarantine, root=args.contracts.parent)
    print(f"wrote reports; curated singles rows={report['curated_singles_point_rows']}")


if __name__ == "__main__":
    main()
