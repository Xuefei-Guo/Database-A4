import argparse
from datetime import date
import sys


def parse_date(value):
    """Accept valid calendar dates in exactly YYYY-MM-DD format."""
    try:
        result = date.fromisoformat(value)
        if result.isoformat() != value:
            raise ValueError
        return result
    except ValueError:
        raise argparse.ArgumentTypeError("Enter a valid date in YYYY-MM-DD format")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Sakila ORM data synchronization")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="Check connections and prepare analytics tables, dates and sync state")
    commands.add_parser("full-load", help="Load all relevant Sakila data")
    commands.add_parser("incremental", help="Synchronize new or changed rows using last_update")
    validation = commands.add_parser("validate", help="Compare source and analytics data")
    validation.add_argument("--from", dest="date_from", type=parse_date)
    validation.add_argument("--to", dest="date_to", type=parse_date)
    args = parser.parse_args(argv)

    try:
        if args.command == "validate":
            from validate import validate
            validate(args.date_from, args.date_to)
        else:
            from sync.runner import full_load, incremental, init_db
            if args.command == "init":
                init_db()
            elif args.command == "full-load":
                full_load()
            else:
                incremental()
    except Exception as error:
        print(f"{args.command} failed: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
