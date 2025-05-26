import streamlit as st
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64

class _3DES_CBC:
    def __init__(self, key1: bytes, key2: bytes, key3: bytes):
        if not (len(key1) == 8 and len(key2) == 8 and len(key3) == 8):
            raise ValueError("All of the 3DES keys must be 8 bytes long (64 bits).")
        self.key = key1 + key2 + key3
        self.block_size = DES3.block_size

    def encrypt(self, plaintext: bytes) -> tuple[bytes, bytes]:
        iv = get_random_bytes(self.block_size)
        cipher = DES3.new(self.key, DES3.MODE_CBC, iv=iv)
        padded_plaintext = pad(plaintext, self.block_size)
        ciphertext = cipher.encrypt(padded_plaintext)
        return iv, ciphertext

    def decrypt(self, iv: bytes, ciphertext: bytes) -> bytes:
        if len(iv) != self.block_size:
            raise ValueError(f"IV must be {self.block_size} bytes long.")
        cipher = DES3.new(self.key, DES3.MODE_CBC, iv=iv)
        padded_plaintext = cipher.decrypt(ciphertext)
        plaintext = unpad(padded_plaintext, self.block_size)
        return plaintext

st.title("3DES CBC Encryption/Decryption Demo")

st.sidebar.header("Key Management")
if "key1" not in st.session_state:
    st.session_state["key1"] = get_random_bytes(8)
    st.session_state["key2"] = get_random_bytes(8)
    st.session_state["key3"] = get_random_bytes(8)

if st.sidebar.button("Generate New Keys"):
    st.session_state["key1"] = get_random_bytes(8)
    st.session_state["key2"] = get_random_bytes(8)
    st.session_state["key3"] = get_random_bytes(8)

key1 = st.sidebar.text_input("Key 1 (hex)", st.session_state["key1"].hex())
key2 = st.sidebar.text_input("Key 2 (hex)", st.session_state["key2"].hex())
key3 = st.sidebar.text_input("Key 3 (hex)", st.session_state["key3"].hex())

try:
    cipher_3des = _3DES_CBC(bytes.fromhex(key1), bytes.fromhex(key2), bytes.fromhex(key3))
except Exception as e:
    st.error(f"Key error: {e}")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Encrypt a Message")
    plaintext = st.text_area("Plaintext", "Hello, this is a 3DES CBC demo!", key="plaintext")
    if st.button("Encrypt"):
        iv, ciphertext = cipher_3des.encrypt(plaintext.encode("utf-8"))
        st.session_state["iv_b64"] = base64.b64encode(iv).decode()
        st.session_state["ciphertext_b64"] = base64.b64encode(ciphertext).decode()
        st.success("Encryption successful!")
    if "iv_b64" in st.session_state and "ciphertext_b64" in st.session_state:
        st.markdown("**IV (base64):**")
        st.code(st.session_state["iv_b64"], language="text")
        st.markdown("**Ciphertext (base64):**")
        st.code(st.session_state["ciphertext_b64"], language="text")

with col2:
    st.subheader("Decrypt a Message")
    iv_b64 = st.text_input("IV (base64)", st.session_state.get("iv_b64", ""), key="iv_input")
    ciphertext_b64 = st.text_area("Ciphertext (base64)", st.session_state.get("ciphertext_b64", ""), key="ciphertext_input")
    if st.button("Decrypt"):
        try:
            iv = base64.b64decode(iv_b64)
            ciphertext = base64.b64decode(ciphertext_b64)
            plaintext = cipher_3des.decrypt(iv, ciphertext)
            st.success("Decryption successful!")
            st.markdown("**Decrypted Plaintext:**")
            st.code(plaintext.decode("utf-8"), language="text")
        except Exception as e:
            st.error(f"Decryption failed: {e}")