# notifier.py
import asyncio
import logging
import html # <--- Add this import statement
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError, BadRequest

from config import MAX_MESSAGE_LENGTH

async def prepare_telegram_messages(items_by_site):
    """Prepares messages grouped by site, split to fit Telegram's limits."""
    if not items_by_site:
        logging.info("No new items found across all sites to prepare message.")
        return ["ℹ️ No new content found today."]

    messages = []
    current_message = ""
    site_needs_continuation_header = {} # Track if a site got split {site_name: True}

    for site_name, items in items_by_site.items():
        if not items: # Skip sites with no new items
            continue

        # Determine header: Base or Continuation
        # Escape site_name just in case it contains HTML chars, although unlikely here
        safe_site_name = html.escape(site_name) # Now 'html' is defined
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
            messages.append(current_message) # Finalize previous message
            current_message = site_header # Start new message with header
            # Reset continuation flags for other sites if we start a new message
            site_needs_continuation_header = {site_name: False} # This site starts fresh in new msg
        else:
            # Add header (either to empty message or existing one)
            if not current_message:
                current_message = site_header
            else:
                # Add double newline for separation, check length again
                separator = "\n\n"
                if len(current_message) + len(separator) + len(site_header) <= MAX_MESSAGE_LENGTH:
                     current_message += separator + site_header
                else: # Cannot even fit separator + header, start new message
                     messages.append(current_message)
                     current_message = site_header
                     site_needs_continuation_header = {site_name: False}

            # Ensure flag is correctly set after adding header
            site_needs_continuation_header[site_name] = False # Added header normally

        # Add items for this site
        for item in items:
            # Construct the message with proper formatting
            title_part = f"• <b>{item['english_title']}</b>\n"
            chinese_part = f"  ({item['chinese_title']})\n" if item['english_title'] != item['chinese_title'] else ""
            link_part = f"  <a href='{html.escape(item['url'])}'>Read more</a>\n\n"
            
            item_text = title_part + chinese_part + link_part

            # Check if item_text itself is too large (should be rare)
            if len(item_text) > MAX_MESSAGE_LENGTH:
                logging.warning(f"Single item too long ({len(item_text)} chars), skipping: {item['url']}")
                continue  # Skip this item

            # Check if adding this item exceeds the limit
            if len(current_message) + len(item_text) > MAX_MESSAGE_LENGTH:
                # Finish the current message
                messages.append(current_message)
                # Start a new message with a continuation header for *this site*
                current_message = header_cont + item_text
                # Mark that *this site* needs continuation header if more items follow
                site_needs_continuation_header[site_name] = True
                 # Reset continuation flags for other sites
                for other_site in site_needs_continuation_header:
                     if other_site != site_name:
                         site_needs_continuation_header[other_site] = False

                # Check edge case: continuation header + item is still too long
                if len(current_message) > MAX_MESSAGE_LENGTH:
                    logging.warning(f"Item too long even with continuation header ({len(current_message)} chars). Sending header and item separately for {item['url']}")
                    messages.append(header_cont) # Send just the header
                    # Attempt to send item alone (might still fail if item_text > limit)
                    if len(item_text) <= MAX_MESSAGE_LENGTH:
                         messages.append(item_text)
                    else:
                         logging.error(f"Cannot send item as it exceeds max length: {item['url']}")
                    current_message = "" # Reset message buffer
                    # Keep site_needs_continuation_header[site_name] = True

            else:
                # It fits, add it
                current_message += item_text

    # Add the last remaining message if it's not empty
    if current_message.strip():
        messages.append(current_message)

    if not messages: # If all items were skipped or sites empty
         logging.info("Prepared messages list is empty after processing items.")
         return ["ℹ️ No new content found today that could be formatted."]

    logging.info(f"Prepared {len(messages)} message parts for Telegram.")
    return messages


async def send_telegram_messages(bot: Bot, chat_id: str, messages: list):
    """Sends a list of messages to Telegram, handling potential errors."""
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

    for i, message in enumerate(messages, 1):
        if not message or message.isspace():
            logging.warning(f"Skipping empty message part {i}/{len(messages)}.")
            continue
        try:
            logging.info(f"Sending message part {i}/{len(messages)} ({len(message)} chars)")
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            logging.debug(f"Successfully sent message part {i}")
            # Add a small delay between messages if sending many parts
            if len(messages) > 1 and i < len(messages): # Avoid sleep after last message
                await asyncio.sleep(0.5) # 0.5 second delay

        except BadRequest as e:
             # Often due to malformed HTML or message length issues
             logging.error(f"Telegram Bad Request error sending part {i}: {e}. Message length: {len(message)}")
             logging.debug(f"Failed message content (first 500 chars): {message[:500]}...") # Log snippet
        except TelegramError as e:
            # More general Telegram API errors (network, rate limits, etc.)
            logging.error(f"Telegram API error sending part {i}: {e}")
            # Consider implementing retry logic here for specific errors (e.g., rate limits)
            await asyncio.sleep(2) # Wait before potentially trying next part or giving up
        except Exception as e:
            logging.error(f"Unexpected error sending Telegram message part {i}: {e}", exc_info=True)