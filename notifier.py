# notifier.py
import asyncio
import logging
import html
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError, BadRequest, RetryAfter

from config import MAX_MESSAGE_LENGTH

async def prepare_telegram_messages(items_by_site):
    """Prepares messages grouped by site, split to fit Telegram's limits."""
    if not items_by_site:
        logging.info("No new items found across all sites to prepare message.")
        return ["ℹ️ No new content found today."]

    # First, deduplicate items across all sites
    seen_urls = set()
    deduplicated_items_by_site = {}
    
    for site_name, items in items_by_site.items():
        unique_items = []
        for item in items:
            if item['url'] not in seen_urls:
                seen_urls.add(item['url'])
                unique_items.append(item)
            else:
                logging.warning(f"Duplicate URL found and filtered: {item['url']}")
        
        if unique_items:  # Only add site if it has unique items
            deduplicated_items_by_site[site_name] = unique_items
            logging.info(f"Site {site_name}: {len(items)} items reduced to {len(unique_items)} unique items")

    if not deduplicated_items_by_site:
        logging.info("No unique items found after deduplication.")
        return ["ℹ️ No new unique content found today."]

    messages = []
    current_message = ""
    site_needs_continuation_header = {}  # Track if a site got split {site_name: True}

    for site_name, items in deduplicated_items_by_site.items():
        # Determine header: Base or Continuation
        safe_site_name = html.escape(site_name)
        header_base = f"<b>📰 Updates from {safe_site_name}</b>\n\n"
        header_cont = f"<b>📰 Updates from {safe_site_name} (cont.)</b>\n\n"

        # Decide if we need the continuation header for *this* site
        is_continuation = site_needs_continuation_header.get(site_name, False)
        site_header = header_cont if is_continuation else header_base

        # Check if the header *itself* fits in a new message (edge case)
        if len(site_header) > MAX_MESSAGE_LENGTH:
            logging.warning(f"Site header for '{site_name}' is too long ({len(site_header)} chars). Skipping site.")
            continue

        # Check if adding the header to the current message exceeds the limit
        if current_message and len(current_message) + len(site_header) > MAX_MESSAGE_LENGTH:
            messages.append(current_message)  # Finalize previous message
            current_message = site_header  # Start new message with header
            site_needs_continuation_header = {site_name: False}  # Reset continuation flags
        else:
            # Add header (either to empty message or existing one)
            if not current_message:
                current_message = site_header
            else:
                separator = "\n\n"
                if len(current_message) + len(separator) + len(site_header) <= MAX_MESSAGE_LENGTH:
                    current_message += separator + site_header
                else:
                    messages.append(current_message)
                    current_message = site_header
                    site_needs_continuation_header = {site_name: False}

            site_needs_continuation_header[site_name] = False

        # Add items for this site
        for item in items:
            # First check if titles are the same
            if item['english_title'] == item['chinese_title']:
                item_text = (
                    f"• <b>{html.escape(item['english_title'])}</b>\n"
                    f"  <a href='{html.escape(item['url'])}'>Read more</a>\n\n"
                )
            else:
                item_text = (
                    f"• <b>{html.escape(item['english_title'])}</b>\n"
                    f"  ({html.escape(item['chinese_title'])})\n"
                    f"  <a href='{html.escape(item['url'])}'>Read more</a>\n\n"
                )

            # Check if item_text itself is too large
            if len(item_text) > MAX_MESSAGE_LENGTH:
                logging.warning(f"Single item too long ({len(item_text)} chars), skipping: {item['url']}")
                continue

            # Check if adding this item exceeds the limit
            if len(current_message) + len(item_text) > MAX_MESSAGE_LENGTH:
                messages.append(current_message)
                current_message = header_cont + item_text
                site_needs_continuation_header[site_name] = True
                
                for other_site in site_needs_continuation_header:
                    if other_site != site_name:
                        site_needs_continuation_header[other_site] = False

                if len(current_message) > MAX_MESSAGE_LENGTH:
                    logging.warning(f"Item too long even with continuation header ({len(current_message)} chars). Sending header and item separately for {item['url']}")
                    messages.append(header_cont)
                    if len(item_text) <= MAX_MESSAGE_LENGTH:
                        messages.append(item_text)
                    else:
                        logging.error(f"Cannot send item as it exceeds max length: {item['url']}")
                    current_message = ""
            else:
                current_message += item_text

    # Add the last remaining message if it's not empty
    if current_message.strip():
        messages.append(current_message)

    if not messages:
        logging.info("Prepared messages list is empty after processing items.")
        return ["ℹ️ No new content found today that could be formatted."]

    logging.info(f"Prepared {len(messages)} message parts for Telegram.")
    return messages


async def send_telegram_messages(bot: Bot, chat_id: str, messages: list):
    """Sends a list of messages to Telegram, handling potential errors and rate limits."""
    if not messages:
        logging.info("No messages to send.")
        try:
            await bot.send_message(
                chat_id=chat_id,
                text="No new headline",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            logging.debug("Successfully sent 'No new headline' message.")
        except BadRequest as e:
            logging.error(f"Telegram Bad Request error sending 'No new headline': {e}")
        except TelegramError as e:
            logging.error(f"Telegram API error sending 'No new headline': {e}")
        except Exception as e:
            logging.error(f"Unexpected error sending 'No new headline': {e}", exc_info=True)
        return

    base_delay = 2  # Base delay between messages in seconds
    max_retries = 5  # Maximum number of retries per message

    for i, message in enumerate(messages, 1):
        if not message or message.isspace():
            logging.warning(f"Skipping empty message part {i}/{len(messages)}.")
            continue

        retry_count = 0
        while retry_count < max_retries:
            try:
                logging.info(f"Sending message part {i}/{len(messages)} ({len(message)} chars)")
                await bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
                logging.debug(f"Successfully sent message part {i}")
                
                # Add a longer delay between messages to avoid rate limits
                if len(messages) > 1 and i < len(messages):
                    await asyncio.sleep(base_delay)
                break  # Message sent successfully, exit retry loop

            except RetryAfter as e:
                retry_after = int(str(e).split()[-2])  # Extract retry seconds from error
                logging.warning(f"Rate limit hit for part {i}, waiting {retry_after} seconds")
                await asyncio.sleep(retry_after)
                retry_count += 1
                continue

            except BadRequest as e:
                logging.error(f"Telegram Bad Request error sending part {i}: {e}. Message length: {len(message)}")
                logging.debug(f"Failed message content (first 500 chars): {message[:500]}...")
                break  # Don't retry on bad requests

            except TelegramError as e:
                wait_time = base_delay * (2 ** retry_count)  # Exponential backoff
                logging.error(f"Telegram API error sending part {i}: {e}. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                retry_count += 1
                if retry_count >= max_retries:
                    logging.error(f"Failed to send message part {i} after {max_retries} retries")

            except Exception as e:
                logging.error(f"Unexpected error sending Telegram message part {i}: {e}", exc_info=True)
                break  # Don't retry on unexpected errors

        # Add additional delay after retries
        if retry_count > 0 and i < len(messages):
            await asyncio.sleep(base_delay * 2)