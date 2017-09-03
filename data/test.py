from Crypto.Cipher import AES

# Two-way encryption function using AES <Harry>
def encrypt(string):
    while len(string) % 16 != 0:
        string = string + ' '
    key = b'asdfghjkl1234567'
    mode = AES.MODE_CBC
    IV = b'asdfghjkl1234567'
    encryptor = AES.new(key, mode, IV)
    cipher_text = encryptor.encrypt(string)
    return cipher_text

# Decryption function using AES <Harry>
def decrypt(string):
    key = b'asdfghjkl1234567'
    mode = AES.MODE_CBC
    IV = b'asdfghjkl1234567'
    decryptor = AES.new(key, mode, IV)
    plain_text = decryptor.decrypt(string)
    return plain_text.strip().decode('utf-8')

file = open('testuser', mode='wb')
information = encrypt('adfsagjkdshzvjdhjklsagh4@gmail.com$' + 'female$' + '18$' + 'Medical professional$' + '1234567890987654321$')
file.write(information)
file.close()

file = open('testuser', mode = 'rb')
plain_text = decrypt(file.read())
print(plain_text)
file.close()
index = 0
last = 0
new = plain_text.find('$', last)
information = ['','','','','']
while (new != -1) and (index <= 4):
    information[index] = plain_text[last:new]
    last = new + 1
    index = index + 1
    new = plain_text.find('$', last)
    print(information[index - 1])
