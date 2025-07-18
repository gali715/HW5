import json
import sys

class JsonFileException(Exception):
    pass
LETTERS_NUM = 26
TWO = 2
USAGE_ERROR = "Usage: python3 enigma.py -c <config_file> -i <input_file> -o <output_file>"
SCRIPT_ERROR = "The enigma script has encountered an error"


class Enigma:

    def __init__(self, hash_map, wheels, reflector_map):
        self.hash_map = hash_map
        self.wheels = list(wheels)
        self._start_wheels = list(wheels)
        self.reflector_map = reflector_map
        self.counter = 0

    def encrypt(self, message):
        s = ""
        for ch in message:
            s += self.encrypt_letter(ch)
        self.increase_wheels()
        self.reset()
        return s


    def encrypt_letter(self,letter):
        c3 = letter
        if not letter.isalpha() or not letter.islower():
            return c3
        else:
            self.counter += 1
            i = self.hash_map[letter]
            increase = (((self.wheels[0]*2)*self.wheels[1]+self.wheels[2]) % LETTERS_NUM)
            if increase != 0:
                i += increase
            else:
                i += 1
            i %= LETTERS_NUM
            c1 =  self.hash_map[i]
            c2 = self.reflector_map[c1]
            i = self.hash_map[c2]
            if increase != 0:
                i -= increase
            else:
                i -= 1
            i %= LETTERS_NUM
            c3 = self.hash_map[i]
        return c3


    def increase_wheels (self):
        if self.wheels[0] > 8:
            self.wheels[0] = 1
        else :
            self.wheels[0] +=1
        if self.counter % TWO == 0 :
            self.wheels[1] *= TWO
        else:
            self.wheels[1] -= 1
        if self.counter % 10 == 0 :
            self.wheels[TWO] = 10
        elif self.counter % 3 == 0 :
            self.wheels[TWO] = 5
        else :
            self.wheels[TWO] = 0

    def reset(self, wheels=None):
        self.counter = 0
        if wheels is None:
            self.wheels = self._start_wheels.copy()
        else:
            self.wheels = list(wheels)



def load_enigma_from_path(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise JsonFileException(f"Invalid JSON file: {path}") from e

    # Validate keys
    for key in ("hash_map", "wheels", "reflector_map"):
        if key not in data:
            raise JsonFileException(f"Missing key '{key}' in {path}")

    # Create and return Enigma
    return Enigma(
        data["hash_map"],
        data["wheels"],
        data["reflector_map"]
    )


def main(arguments):

    if len(sys.argv) != TWO:
        print('usage: script.py <path_to_dir>')
    config_path, input_path,output_path = None,None,None
    for index in range(0, len(arguments),TWO):
        if arguments[index] == "-c" and arguments[index] is None:
            config_path = arguments[index+1]

        elif arguments[index] == "-i" and arguments[index] is None:
            input_path = arguments[index+1]
        elif arguments[index] == "-o" and arguments[index] is None:
            output_path = arguments[index+1]
        else:
            print(USAGE_ERROR)
            exit(1)
    if config_path is None or input_path is None:
        print(USAGE_ERROR)
        exit(1)
    try:
        enigma = load_enigma_from_path(config_path)
        encrypted = enigma.encrypt(input_path)
        if output_path:
            with open(output_path, 'w') as f:
                for msg in encrypted:
                    f.write(f"{msg}\n")
        else:
            for msg in encrypted:
                print(msg)


    except Exception:
        # give a short, user-friendly message but keep the exit status ≠ 0
        print("SCRIPT_ERROR")

if __name__ == "__main__":
    main(sys.argv)

