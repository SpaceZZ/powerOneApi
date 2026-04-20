"""
Main application entry point.
All code for the inverter API is located in the aurora_vision_api module.

Usage:
    python main.py            # full run: fetch, email, archive to SQL
    python main.py --dry-run  # fetch only — no email, no SQL (useful for testing)
"""
import argparse
import json
import logging
import sys

import aurora_vision_api
import configurator
import email_sender
import html_render
import image_charts
import pv_calculator
from sql_insert import sql_handling

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Aurora Vision PV daily reporter")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch API data and print results, but skip email and SQL archiving",
    )
    parser.add_argument(
        "--test-email",
        action="store_true",
        help="Fetch data, render and send the email, but skip SQL archiving",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.dry_run:
        logger.info("=== DRY RUN MODE: no email, no SQL ===")
    if args.test_email:
        logger.info("=== TEST EMAIL MODE: email will be sent, SQL skipped ===")

    # Read configuration
    config = configurator.Configurator()

    # Fetch data from Aurora Vision
    session = aurora_vision_api.Session(
        user=config.user,
        password=config.password,
        api_key=config.api_key,
        installationID=config.installationID,
        timezone=config.timezone,
    )

    logger.info("Fetching summary data...")
    result = session.get_data()

    logger.info("Fetching extended (15-min bins) data...")
    result_extended = session.get_data(extended=True)

    if not result:
        logger.error("No summary data returned from API — aborting")
        sys.exit(1)

    if args.dry_run:
        logger.info("--- Summary result ---")
        logger.info(json.dumps(result, indent=2, default=str))
        if result_extended:
            logger.info("--- Extended result (first 5 bins) ---")
            sample = dict(list(result_extended.items())[:5])
            logger.info(json.dumps(sample, indent=2, default=str))
            logger.info(f"  ... ({len(result_extended)} total bins)")
        return  # stop here in dry-run

    # --- Full run ---
    chart_link = ""
    max_time = ""
    max_power = 0.0

    if result_extended:
        # Extended data contains 15-min bins; strip out the "today" summary key
        bin_data = {k: v for k, v in result_extended.items() if k != "today"}

        max_time, max_power = pv_calculator.calculate_max_power(bin_data)

        non_zero_data, start_time, end_time, mid_time = pv_calculator.get_only_valid_data(bin_data)
        if non_zero_data:
            chart_link = image_charts.create_link(
                non_zero_data.values(), start_time, end_time, mid_time
            )
    else:
        logger.warning("Extended data unavailable — chart and peak power will be omitted")

    html = html_render.render(result, max_time, max_power, chart_link)

    sender = email_sender.EmailSender(
        email=config.email,
        password=config.email_password,
        recipients=config.recipients,
    )
    sender.send(html)

    if not args.test_email:
        sql_handling.handle_sql_archiving(result, config)


if __name__ == "__main__":
    main()
