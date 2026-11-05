import argparse
from src.pipeline import run
from src.reporting.reports import generate_monthly_report

def main() -> None:
    parser = argparse.ArgumentParser(description="CommerceLens command line")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate"); all_cmd = sub.add_parser("run-all"); all_cmd.add_argument("--database", action="store_true")
    report = sub.add_parser("report"); report.add_argument("--period", choices=["monthly"], default="monthly")
    args = parser.parse_args()
    if args.command == "validate":
        result = run(validate_only=True); print(result["quality"].to_string(index=False))
    elif args.command == "run-all":
        result = run(database=args.database); print(f"Pipeline complete: {len(result['mart']):,} orders exported.")
    else:
        csv_path, pdf_path = generate_monthly_report(); print(f"Created {csv_path} and {pdf_path}")
if __name__ == "__main__": main()
