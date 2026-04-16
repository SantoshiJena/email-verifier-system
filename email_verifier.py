import argparse
import re
import sys

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
LOCAL_PART_REGEX = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+$")
DOMAIN_LABEL_REGEX = re.compile(r"^[A-Za-z0-9-]{1,63}$")


def validate_email(email: str) -> tuple[bool, str | None]:
    email = email.strip()
    if not email:
        return False, "Email is empty"
    if email.count("@") == 0:
        return False, "Missing '@' symbol"
    if email.count("@") > 1:
        return False, "Multiple '@' symbols"

    local, _, domain = email.partition("@")
    if not local:
        return False, "Missing local part before '@'"
    if len(local) > 64:
        return False, "Local part is too long"
    if local.startswith(".") or local.endswith("."):
        return False, "Local part cannot begin or end with dot"
    if ".." in local:
        return False, "Consecutive dots are not allowed in local part"
    if not LOCAL_PART_REGEX.match(local):
        return False, "Invalid characters in local part"

    if not domain:
        return False, "Missing domain after '@'"
    if len(domain) > 255:
        return False, "Domain is too long"
    if domain.startswith(".") or domain.endswith("."):
        return False, "Domain cannot begin or end with dot"
    if ".." in domain:
        return False, "Consecutive dots are not allowed in domain"

    labels = domain.split('.')
    if len(labels) < 2:
        return False, "Domain must include a top-level domain"

    for label in labels:
        if not label:
            return False, "Invalid domain label"
        if len(label) > 63:
            return False, "Domain label is too long"
        if label.startswith("-") or label.endswith("-"):
            return False, "Domain labels cannot start or end with hyphen"
        if not DOMAIN_LABEL_REGEX.match(label):
            return False, "Invalid domain label characters"

    if not EMAIL_REGEX.match(email):
        return False, "Invalid email format"

    return True, None


def format_result(email: str, valid: bool, reason: str | None) -> str:
    if valid:
        return f"{email} -> Valid Email ✅"
    result = f"{email} -> Invalid Email ❌"
    if reason:
        result += f"\n  Reason: {reason}"
    return result


def load_emails_from_file(path: str) -> list[str]:
    with open(path, encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Email Verifier Automation System")
    parser.add_argument("-e", "--email", help="Verify a single email address")
    parser.add_argument("-f", "--file", help="Verify multiple emails from a file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    emails: list[str] = []

    if args.email:
        emails = [args.email]
    elif args.file:
        try:
            emails = load_emails_from_file(args.file)
        except FileNotFoundError:
            print(f"File not found: {args.file}")
            return 1
        except OSError as exc:
            print(f"Unable to read file: {exc}")
            return 1
        if not emails:
            print("No emails found in file.")
            return 1
    else:
        print("Email Verifier Automation System")
        print("Enter one email per line. Leave blank and press Enter to finish.")
        added_any = False
        while True:
            try:
                email_input = input("Email: ").strip()
            except EOFError:
                break
            if not email_input:
                break
            valid, reason = validate_email(email_input)
            print(format_result(email_input, valid, reason))
            added_any = True
        if not added_any:
            print("No email provided.")
            return 0

    for email in emails:
        valid, reason = validate_email(email)
        print(format_result(email, valid, reason))

    return 0


if __name__ == "__main__":
    sys.exit(main())
