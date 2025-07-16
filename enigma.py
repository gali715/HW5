import json



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
            s += self.encryptLetter(ch)
        self.IncreaseWheels()
        self.reset()
        return s


    def encryptLetter(self,letter):
        c3 = letter
        if not letter.isalpha() or not letter.islower():
            return c3
        else:
            self.counter += 1
            i = self.hash_map[letter]
            increase = (((self.wheels[0]*2)*self.wheels[1]+self.wheels[2]) % 26)
            if increase != 0:
                i += increase
            else:
                i += 1
            i %= 26
            c1 =  self.hash_map[i]
            c2 = self.reflector_map[c1]
            i = self.hash_map[c2]
            if increase != 0:
                i -= increase
            else:
                i -= 1
            i %= 26
            c3 = self.hash_map[i]
        return c3


    def IncreaseWheels (self):
        if self.wheels[0] > 8:
            self.wheels[0] = 1
        else :
            self.wheels[0] +=1
        if self.counter % 2 == 0 :
            self.wheels[1] *= 2
        else:
            self.wheels[1] -= 1
        if self.counter % 10 == 0 :
            self.wheels[2] = 10
        elif self.counter % 3 == 0 :
            self.wheels[2] = 5
        else :
            self.wheels[2] = 0

    def reset(self, wheels=None):
        self.counter = 0
        if wheels is None:
            self.wheels = self._start_wheels.copy()
        else:
            self.wheels = list(wheels)


class JsonFileException(Exception):
    pass

def load_enigma_from_path(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
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

