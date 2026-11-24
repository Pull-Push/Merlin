from flask_app import app
from flask import request, jsonify
import string
import random


@app.route('/encrypt', methods=['POST'])
def encrypt():
    data = request.get_json()
    key = data['key']
    seckey = build_key(key['shift'], key['seed1'], key['seed2'], key['seed3'])
    encrypted = encode_message(key['message'], seckey)
    return jsonify(encrypted)


@app.route('/decrypt', methods=['POST'])
def decrypt():
    data = request.get_json()
    key = data['key']
    seckey = build_key(key['shift'], key['seed1'], key['seed2'], key['seed3'])
    decrypted = decode_message(key['message'], seckey)
    return jsonify(decrypted)


def build_key(shift, seed1, seed2, seed3):
    """
    Build a multi-layer substitution cipher key from 4 inputs.

    Each seed deterministically shuffles the printable character set into a
    unique ordering, producing 4 substitution maps layered on top of each other.
    Same seeds always produce the same key — that's what makes it decryptable.
    """
    seeds = [shift, seed1, seed2, seed3]
    charset = " " + string.digits + string.ascii_letters + string.punctuation
    layers = []

    for seed in seeds:
        rng = random.Random(seed)
        # Assign a random float to each character, then sort to get a shuffled charset
        scored = sorted(charset, key=lambda _: rng.random())
        # Map each original character -> its shuffled counterpart
        substitution = dict(zip(charset, scored))
        layers.append(substitution)

    return layers


def encode_message(message, key):
    """Pass the message through each substitution layer in order."""
    output = message
    for layer in key:
        output = "".join(layer.get(ch, ch) for ch in output)
    return output


def decode_message(encoded, key):
    """Reverse each substitution layer in reverse order."""
    output = encoded
    for layer in reversed(key):
        reverse_layer = {v: k for k, v in layer.items()}
        output = "".join(reverse_layer.get(ch, ch) for ch in output)
    return output
