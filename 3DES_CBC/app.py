from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class _3DES_CBC:
    """
    This is a class to handle 3DES encryption and decryption in CBC mode.
    """

    def __init__(self, key1: bytes, key2: bytes, key3: bytes):
        """
        This initializes the 3DES_CBC cipher with three 8-byte (64-bit) keys.

        Args:
            key1 (bytes): The first 8-byte key.
            key2 (bytes): The second 8-byte key.
            key3 (bytes): The third 8-byte key.

        Raises:
            ValueError: If any key is not 8 bytes long.
        """
        if not (len(key1) == 8 and len(key2) == 8 and len(key3) == 8):
            raise ValueError("All of the 3DES keys must be 8 bytes long (64 bits).")

        self.key = key1 + key2 + key3
        self.block_size = DES3.block_size

    def encrypt(self, plaintext: bytes) -> tuple[bytes, bytes]:
        """
        This encrypts the plaintext using 3DES in CBC mode.

        Args:
            plaintext (bytes): The data to be encrypted.

        Returns:
            tuple[bytes, bytes]: A tuple containing the IV and the ciphertext.
                                 The important part is that the IV is returned, so it can be used for decryption.
        """

        iv = get_random_bytes(self.block_size)

        cipher = DES3.new(self.key, DES3.MODE_CBC, iv=iv)

        padded_plaintext = pad(plaintext, self.block_size)

        ciphertext = cipher.encrypt(padded_plaintext)

        return iv, ciphertext

    def decrypt(self, iv: bytes, ciphertext: bytes) -> bytes:
        """
        This decrypts the ciphertext using 3DES in CBC mode.

        Args:
            iv (bytes): The initialization vector used during encryption.
            ciphertext (bytes): The data to be decrypted.

        Returns:
            bytes: The original decrypted plaintext.

        Raises:
            ValueError: If the IV is not 8 bytes long.
        """
        if len(iv) != self.block_size:
            raise ValueError(f"IV must be {self.block_size} bytes long.")

        cipher = DES3.new(self.key, DES3.MODE_CBC, iv=iv)

        padded_plaintext = cipher.decrypt(ciphertext)

        plaintext = unpad(padded_plaintext, self.block_size)

        return plaintext


if __name__ == "__main__":

    key1 = get_random_bytes(8)
    key2 = get_random_bytes(8)
    key3 = get_random_bytes(8)

    print(f"Generated Key 1: {key1.hex()}")
    print(f"Generated Key 2: {key2.hex()}")
    print(f"Generated Key 3: {key3.hex()}\n")

    try:
        cipher_3des = _3DES_CBC(key1, key2, key3)
    except ValueError as error:
        print(f"Error creating cipher: {error}")
        exit()

    original_plaintext = b"Hi every body , we are going to encrypt this message with 3DES CBC mode :)"

    print(f"Original plaintext: {original_plaintext.decode('utf-8')}\n")

    print("..... Encryption .....")
    iv_encrypted, ciphertext = cipher_3des.encrypt(original_plaintext)
    print(f"Generated IV (for decryption): {iv_encrypted.hex()}")
    print(f"Ciphertext (hex): {ciphertext.hex()}\n")

    print("..... Decryption .....")
    try:
        decrypted_plaintext = cipher_3des.decrypt(iv_encrypted, ciphertext)
        print(f"Decrypted plaintext: {decrypted_plaintext.decode('utf-8')}")
        print(f"Decryption successful: {original_plaintext == decrypted_plaintext}\n")
    except ValueError as error:
        print(f"Error during decryption: {error}")
    except Exception as error:
        print(f"An unexpected error occurred during decryption: {error}")

    print("\n..... Short Message Demonstration .....")
    short_message = b"Short message"
    print(f"Original short message: {short_message.decode('utf-8')}")

    iv_short, ciphertext_short = cipher_3des.encrypt(short_message)
    print(f"Generated IV (short): {iv_short.hex()}")
    print(f"Ciphertext (short, hex): {ciphertext_short.hex()}")
    print(
        f"Ciphertext length (short): {len(ciphertext_short)} bytes \t"
        f"(expected: {cipher_3des.block_size} bytes due to padding)")

    decrypted_short_message = cipher_3des.decrypt(iv_short, ciphertext_short)
    print(f"Decrypted short message: {decrypted_short_message.decode('utf-8')}")
    print(f"Decryption successful (short): {short_message == decrypted_short_message}")
