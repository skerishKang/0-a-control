from scripts.telegram_helpers import _format_bytes


class AttachmentProgressReporter:
    def __init__(self, total_items: int):
        self.total_items = total_items
        self.started = 0
        self.current_index_by_message_id = {}
        self.last_percent_by_message_id = {}

    def __call__(self, event: dict) -> None:
        stage = event.get("stage")
        message_id = event.get("message_id")
        if message_id is None:
            return

        if stage == "start":
            self.started += 1
            self.current_index_by_message_id[message_id] = self.started
            name = event.get("attachment_name") or f"message-{message_id}"
            size = _format_bytes(event.get("file_size"))
            print(
                f"[{self.started}/{self.total_items}] download start "
                f"msg={message_id} file={name} size={size}",
                flush=True,
            )
            return

        index = self.current_index_by_message_id.get(message_id, self.started or 1)
        if stage == "progress":
            percent = int(event.get("percent") or 0)
            prev_percent = self.last_percent_by_message_id.get(message_id, -1)
            if percent == prev_percent:
                return
            self.last_percent_by_message_id[message_id] = percent
            current_bytes = _format_bytes(event.get("current_bytes"))
            total_bytes = _format_bytes(event.get("total_bytes"))
            name = event.get("attachment_name") or f"message-{message_id}"
            bar_fill = min(10, max(0, percent // 10))
            bar = "#" * bar_fill + "-" * (10 - bar_fill)
            print(
                f"[{index}/{self.total_items}] [{bar}] {percent:>3}% "
                f"{name} {current_bytes}/{total_bytes}",
                flush=True,
            )
            return

        if stage in {"done", "exists"}:
            name = event.get("attachment_name") or f"message-{message_id}"
            suffix = "already-exists" if stage == "exists" else "saved"
            target_path = event.get("target_path") or "-"
            print(
                f"[{index}/{self.total_items}] {suffix} msg={message_id} "
                f"file={name} path={target_path}",
                flush=True,
            )
