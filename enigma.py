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
        self._start_wheels = wheels.copy()
        self.reflector_map = reflector_map
        self.counter = 0
        self.reverse_hash = {v: k for k, v in hash_map.items()}


    def encrypt(self, message):
        if not message:
            return ""

        s = ""
        temp_wheels = self._start_wheels.copy()
        got_encrypted = 0

        for ch in message:
            if ch.islower():
                s += self.encrypt_letter(ch, temp_wheels)
                got_encrypted += 1
            else:
                s+= ch
            self.increase_wheels(temp_wheels,got_encrypted)
        return s


    def encrypt_letter(self,letter,wheels):
        if not letter.isalpha() or not letter.islower():
            return letter
        else:
            self.counter += 1
            i = self.hash_map[letter]
            increase = (((wheels[0]*2)*wheels[1]+wheels[2]) % LETTERS_NUM)
            if increase != 0:
                i += increase
            else:
                i += 1
            i %= LETTERS_NUM
            c1 =  self.reverse_hash[i]
            c2 = self.reflector_map[c1]
            i = self.hash_map[c2]
            if increase != 0:
                i -= increase
            else:
                i -= 1
            i %= LETTERS_NUM
            c3 = self.reverse_hash[i]
        return c3


    def increase_wheels (self, wheels, got_encrypted):
        if wheels[0] > 8:
            wheels[0] = 1
        else :
            wheels[0] +=1
        if got_encrypted % TWO == 0 :
            wheels[1] *= TWO
        else:
            wheels[1] -= 1
        if got_encrypted % 10 == 0 :
            wheels[TWO] = 10
        elif got_encrypted % 3 == 0 :
            wheels[TWO] = 5
        else :
            wheels[TWO] = 0




def load_enigma_from_path(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return Enigma(
            hash_map=data['hash_map'],
            wheels=data['wheels'],
            reflector_map=data['reflector_map']
        )
    except (OSError, json.JSONDecodeError) as e:
        raise JsonFileException(f"Invalid JSON file: {path}") from e

    except (json.JSONDecodeError, FileNotFoundError):
        raise Exception("Error reading JSON file")
    except (TypeError, ValueError) as e:
        raise Exception("Invalid configuration")

   

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

