# Changelog

All notable changes to this project will be documented in this file.

## [0.0.2] - 2026-10-04

### Added
- `send_photo()` method
- `edit_message_text()` and `edit_message_caption()` methods
- `delete_message()` method
- `answer_callback_query()` method
- `callback_query_handler()` decorator
- JSON serialization for `reply_markup` in multipart requests
- `from_user` alias for the reserved `from` field in `Message`,
  `CallbackQuery`, `InlineQuery`

### Fixed
- `Message.from_user` was missing, broke every handler
- `BUTTON_INVALID` when sending photo with reply_markup

## [0.0.1] - 2026-10-03

### Added
- Initial project skeleton
