import sys
import json

# --- Constants ---
LETTERS_NUM = 26
USAGE_ERROR = "Usage: python3 enigma.py -c <config_file> -i <input_file> -o <output_file>"
SCRIPT_ERROR = "The enigma script has encountered an error"


# --- Exception Class ---
class JsonFileException(Exception):
    pass


# --- Enigma Machine ---
class Enigma:
    def __init__(self, hash_map, wheels, reflector_map):
        self.hash_map = hash_map
        self.reverse_hash = {v: k for k, v in hash_map.items()}
        self._start_wheels = wheels.copy()
        self.reflector_map = reflector_map

    def encrypt(self, message):
        encrypted = ""
        wheels = self._start_wheels.copy()
        encrypted_count = 0

        for ch in message:
            if ch.islower():
                encrypted += self.encrypt_letter(ch, wheels)
                encrypted_count += 1
            else:
                encrypted += ch
            self.update_wheels(wheels, encrypted_count)

        return encrypted

    def encrypt_letter(self, ch, wheels):
        i = self.hash_map[ch]
        add = ((wheels[0] * 2) - wheels[1] + wheels[2]) % LETTERS_NUM
        i += add if add != 0 else 1
        i %= LETTERS_NUM
        c1 = self.reverse_hash[i]
        c2 = self.reflector_map[c1]
        i = self.hash_map[c2]
        i -= add if add != 0 else 1
        i %= LETTERS_NUM
        return self.reverse_hash[i]

    def update_wheels(self, wheels, count):
        # W1
        wheels[0] = wheels[0] + 1 if wheels[0] < 8 else 1
        # W2
        if count % 2 == 0:
            wheels[1] *= 2
        else:
            wheels[1] -= 1
        # W3
        if count % 10 == 0:
            wheels[2] = 10
        elif count % 3 == 0:
            wheels[2] = 5
        else:
            wheels[2] = 0


# --- Config Loader ---
def load_enigma_from_path(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Enigma(
            hash_map=data["hash_map"],
            wheels=data["wheels"],
            reflector_map=data["reflector_map"]
        )
    except (OSError, json.JSONDecodeError) as e:
        raise JsonFileException(f"Invalid JSON file: {path}") from e


# --- Main Runner ---
def main(argv):
    args = argv[1:]
    config_path = None
    input_path = None
    output_path = None

    # Parse flags manually
    try:
        for i in range(0, len(args), 2):
            if i + 1 >= len(args):
                raise ValueError()
            flag, value = args[i], args[i + 1]
            if flag == "-c":
                config_path = value
            elif flag == "-i":
                input_path = value
            elif flag == "-o":
                output_path = value
            else:
                raise ValueError()
    except ValueError:
        print(USAGE_ERROR, file=sys.stderr)
        sys.exit(1)

    # Required parameters check
    if not config_path or not input_path:
        print(USAGE_ERROR, file=sys.stderr)
        sys.exit(1)

    try:
        enigma = load_enigma_from_path(config_path)

        with open(input_path, "r", encoding="utf-8") as f:
            messages = f.readlines()

        encrypted_lines = [enigma.encrypt(line.rstrip('\n')) + '\n' for line in messages]

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.writelines(encrypted_lines)
        else:
            sys.stdout.writelines(encrypted_lines)

    except Exception:
        print(SCRIPT_ERROR, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
