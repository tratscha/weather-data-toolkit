from __future__ import annotations

import socket
from datetime import datetime

HOST = "127.0.0.1"
PORT = 5026


def get_valid_date() -> str:
    while True:
        requested_day = input("Welche Wetterdaten von welchem Tag soll ich suchen? (Format: DD.MM.YYYY) ").strip()
        try:
            datetime.strptime(requested_day, "%d.%m.%Y")
            return requested_day
        except ValueError:
            print("Ungültiges Datum. Bitte im Format DD.MM.YYYY eingeben.")


def run_client() -> None:
    requested_day = get_valid_date()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(requested_day.encode("utf-8"))

        chunks = []
        while True:
            data = s.recv(4096)
            if not data:
                break
            chunks.append(data)

    response = b"".join(chunks).decode("utf-8")
    print("\n" + response)


if __name__ == "__main__":
    run_client()