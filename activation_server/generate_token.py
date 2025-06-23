import json, random, string, os

TOKENS_FILE = "tokens.json"

def generate_token():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=4)) + "-" + \
           "".join(random.choices(string.ascii_uppercase + string.digits, k=4))

def add_token(email):
    if not os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'w') as f:
            json.dump({}, f)

    with open(TOKENS_FILE, 'r') as f:
        tokens = json.load(f)

    new_token = generate_token()
    tokens[new_token] = {"used": False, "email": email}

    with open(TOKENS_FILE, 'w') as f:
        json.dump(tokens, f, indent=2)

    print(f"Token for {email}: {new_token}")

if __name__ == '__main__':
    email = input("Enter recipient email: ")
    add_token(email)