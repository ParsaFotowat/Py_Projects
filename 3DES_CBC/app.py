import streamlit as st
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64

# Function to generate a valid 3DES key with correct parity
def generate_key():
    while True:
        key = get_random_bytes(24)  # 24 bytes for 3DES key
        try:
            key = DES3.adjust_key_parity(key)
            return key
        except ValueError:
            continue  # Retry if key parity adjustment fails

def encrypt_cbc(plaintext, key):
    cipher = DES3.new(key, DES3.MODE_CBC)
    iv = cipher.iv
    padded_plaintext = pad(plaintext.encode('utf-8'), DES3.block_size)
    ciphertext = cipher.encrypt(padded_plaintext)
    return base64.b64encode(iv + ciphertext).decode('utf-8')

def decrypt_cbc(ciphertext, key):
    try:
        raw = base64.b64decode(ciphertext)
        iv = raw[:DES3.block_size]
        cipher = DES3.new(key, DES3.MODE_CBC, iv)
        padded_plaintext = cipher.decrypt(raw[DES3.block_size:])
        return unpad(padded_plaintext, DES3.block_size).decode('utf-8')
    except (ValueError, KeyError, base64.binascii.Error) as e:
        return f"Decryption failed: {str(e)}"

st.title("3DES CBC Encryption/Decryption Demo")

# Key management
if "key" not in st.session_state:
    st.session_state["key"] = generate_key()

if st.button("Generate New Key"):
    st.session_state["key"] = generate_key()
st.write("**Current Key (Base64):**")
st.code(base64.b64encode(st.session_state["key"]).decode('utf-8'))

tab1, tab2 = st.tabs(["Encrypt", "Decrypt"])

with tab1:
    plaintext = st.text_area("Enter plaintext to encrypt:")
    if st.button("Encrypt"):
        if plaintext:
            ciphertext = encrypt_cbc(plaintext, st.session_state["key"])
            st.success("Ciphertext (Base64):")
            st.code(ciphertext)
        else:
            st.warning("Please enter plaintext.")

with tab2:
    ciphertext_input = st.text_area("Enter ciphertext (Base64) to decrypt:")
    if st.button("Decrypt"):
        if ciphertext_input:
            decrypted = decrypt_cbc(ciphertext_input, st.session_state["key"])
            st.success("Decrypted Text:")
            st.code(decrypted)
        else:
            st.warning("Please enter ciphertext.")