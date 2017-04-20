from __future__ import absolute_import

from Crypto.Hash import SHA
from Crypto.Cipher import AES
import base64
import os
import logging

_logger = logging.getLogger(__name__)

"""pos_checksum
Point of Sale Checksum.

An helper library that of provided by the TGN.CheckSumString
"""


class Salt(object):
    """Salt
    An abstraction to handle simple operations on the salt bytes iterable
    """

    #Salt bytes to use for salting the string 
    _DEFAULT_SALT_BYTES = [1, 240, 239, 34, 69, 171]

    def __init__(self, salt_bytes=None):
        """Constructor

        @param: salt_bytes - iterable of byte value to use for the Salt
        """
        salt_bytes = salt_bytes or self._DEFAULT_SALT_BYTES
        self.bytes_ = bytearray(salt_bytes)
        self.length = len(salt_bytes)

    def byte(self, index):
        """byte

        Obtain the byte value stored at the provided index. 
        @param: index (int)
        @return: byte value (int)
        """
        return self.bytes_[index % self.length]


class SimpleHash(object):
    """SimpleHash - Salted hashing"""

    #Mask Bytes. Used for mask values to be used when salting a plain string
    _DEFAULT_MASK_BYTE = 15

    """
    The following two magic values are obtained from the C# `PasswordDeriveByte.GetBytes` operation. 
    Ancestry implementation uses the `_DEFAULT_SALT_BYTES` value to generate a new byte sequence for 
    encrypting the obtained hash. The generated sequence is the same everytime!. We were unable 
    to locate a parallel implementation in Python.
    """
    ENC_KEY = [159, 193, 42, 107, 146, 228, 223, 233, 200, 70, 8, 167, 21, 116, 145, 118,
                174, 217, 202, 171, 75, 74, 231, 92, 85, 23, 124, 31, 179, 68, 12, 185]
    ENC_IV = [200, 70, 8, 167, 21, 116, 145, 118, 114, 1, 123, 112, 220, 220, 171, 164]


    def __init__(self, salt=None, mask=None):
        """Constructor"""
        self.salt = salt or Salt()
        self.mask = mask or self._DEFAULT_MASK_BYTE

        self.enc_key = bytes(bytearray(self.ENC_KEY))
        self.enc_iv = bytes(bytearray(self.ENC_IV))

    def _merge_bytes(self, left, right):
        """Applies `mask` to the provided values and returns a new tuple"""
        first = (left & ~self.mask) | (right & self.mask)
        first = first & 255
        second = (left & self.mask) | (right & ~self.mask)
        second = second & 255
        return (first, second)

    def _salt_string(self, plain_string):
        """Constructs the salted string"""
        bytes_ = bytearray(plain_string)
        salted_value = bytearray(len(bytes_) * 2)

        i = 0
        for b in bytes_:
            salt_byte = self.salt.byte(i)
            masked_values = self._merge_bytes(b, salt_byte)
            salted_value[i * 2] = masked_values[0]
            salted_value[i * 2 + 1] = masked_values[1]
            i += 1
        return bytes(salted_value)

    def compute_hash(self, plain_string):
        """Compute a salted hash"""
        salted_buffer = self._salt_string(plain_string)
        sha_hash = SHA.new(salted_buffer)
        return sha_hash.digest()

    def protect_hash(self, hash_digest):
        """Protect the provided hash digest using AES (CBC mode, PCKS7 padding)"""

        rand_eight_bytes = bytes(os.urandom(8))
        hash_bytes = bytes(hash_digest)

        # Calculate the padding value/length as required by PCKS7 padding
        # CBC mode requires that the input buffer length is a multiple of AES block size
        new_buffer_len = len(hash_bytes) + len(rand_eight_bytes)
        padding = AES.block_size - (new_buffer_len % AES.block_size)

        # New buffer. hash + ticks + padding
        new_buffer = bytearray()
        new_buffer.extend(hash_bytes)
        new_buffer.extend(rand_eight_bytes)
        new_buffer.extend([padding for i in range(padding)])
        immutable_buffer = bytes(new_buffer)

        # AES in CBC mode. RijndaelManaged in C#
        aes_enc = AES.new(self.enc_key, AES.MODE_CBC, self.enc_iv)
        enc_message = aes_enc.encrypt(immutable_buffer)
        return enc_message

    def unprotect_hash(self, encrypted_hash):
        """Remove encryption and return the hash component

        Assumes that the underlying hash value is a SHA1 hash.
        """
        aes_enc = AES.new(self.enc_key, AES.MODE_CBC, self.enc_iv)
        decrypted_value = aes_enc.decrypt(encrypted_hash)
        return decrypted_value[:SHA.digest_size]


class CheckSumString(object):
    """CheckSumString"""

    def __init__(self, hash_alg=None):
        """Constructor
        Uses an instance of the default SimpleHash implementation
        """
        self.hash_alg = hash_alg or SimpleHash()

    def get(self, plain_text):
        """Obtain an checksum (entryped hash value) for the provided plain text value"""
        hash_digest = self.hash_alg.compute_hash(plain_text)
        enc_message = self.hash_alg.protect_hash(hash_digest)
        checksum = base64.b64encode(enc_message)
        _logger.debug("Checksum: {0}\nText: {1}".format(checksum, plain_text))
        return checksum

    def verify(self, plain_text, checksum):
        """verify the provided plain text generates the provided hash"""
        enc_hash = base64.b64decode(checksum)
        plain_hash = self.hash_alg.unprotect_hash(enc_hash)

        hash_digest = self.hash_alg.compute_hash(plain_text)
        return base64.b64encode(plain_hash) == base64.b64encode(hash_digest)
