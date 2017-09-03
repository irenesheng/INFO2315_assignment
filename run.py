from bottle import route, get, run, post, request, redirect, static_file
from Crypto.Hash import MD5
from Crypto.Cipher import AES
from Crypto import Random
import re
import numpy as np
import os

#-----------------------------------------------------------------------------
# This class loads html files from the "template" directory and formats them using Python.
class FrameEngine:
    def __init__(this,
        template_path="templates/",
        template_extension=".html",
        **kwargs):
        this.template_path = template_path
        this.template_extension = template_extension
        this.global_renders = kwargs

    def load_template(this, filename):
        path = this.template_path + filename + this.template_extension
        file = open(path, 'r')
        text = ""
        for line in file:
            text+= line
        file.close()
        return text

    def simple_render(this, template, **kwargs):
        template = template.format(**kwargs)
        return  template

    def render(this, template, **kwargs):
        keys = this.global_renders.copy() #Not the best way to do this, but backwards compatible from PEP448, in Python 3.5+ use keys = {**this.global_renters, **kwargs}
        keys.update(kwargs)
        template = this.simple_render(template, **keys)
        return template

    def load_and_render(this, filename, header="header", tailer="tailer", **kwargs):
        template = this.load_template(filename)
        rendered_template = this.render(template, **kwargs)
        rendered_template = this.load_template(header) + rendered_template
        rendered_template = rendered_template + this.load_template(tailer)
        return rendered_template

#-----------------------------------------------------------------------------

# Allow image loading
@route('/img/<picture>')
def serve_pictures(picture):
    return static_file(picture, root='img/')

# Allow CSS
@route('/css/<css>')
def serve_css(css):
    return static_file(css, root='css/')

# Allow javascript
@route('/js/<js>')
def serve_js(js):
    return static_file(js, root='js/')
#-----------------------------------------------------------------------------

# Hash function (with salt) <Harry>
def hash(string):
    salt = "!#sa!#lt!#"
    salted_string = string + salt
    hashed_string = MD5.new(salted_string.encode()).hexdigest()
    return hashed_string

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

#-----------------------------------------------------------------------------

# Check the login credentials
def check_login(username, password):
    login = False
    if username != "admin": # Wrong Username
        err_str = "Incorrect Username"
        return err_str, login

    if password != "password":
        err_str = "Incorrect Password"
        return err_str, login

    login_string = "Logged in!"
    login = True
    return login_string, login

#-----------------------------------------------------------------------------

# Read account information from database <Harry>
# information -> [0]email_address [1]gender [2]age [3]account_type [4]medicare_number
# format of data file | encrypt(email_address) + '$' + encrypt(gender) + '$' + ... +encrypt(medicare_number) + '$'
def get_account_details(username):
    script_dir = os.path.dirname(__file__)
    rel_path = "data/testuser" #TODO replace 'testuser' with hash function
    abs_file_path = os.path.join(script_dir, rel_path)
    file = open(abs_file_path, mode = 'rb')
    plain_text = decrypt(file.read())
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
    return information

# Write account information from database <Harry>
# information -> [0]email_address [1]gender [2]age [3]account_type [4]medicare_number
def write_account_details(username, information):
    script_dir = os.path.dirname(__file__)
    rel_path = "data/testuser" #TODO replace 'testuser' with hash function
    abs_file_path = os.path.join(script_dir, rel_path)
    file = open(abs_file_path, mode = 'wb')
    file.write(encrypt(information[0] + '$' + information[1] + '$' + information[2] + '$' + information[3] + '$' + information[4] + '$'))
    file.close()

#-----------------------------------------------------------------------------

# Check edit information <Harry>
def check_edit(username, email_address, gender, age):
    valid = False
    if not ('@' in email_address):
        err_str = "Invalid email address!"
        return err_str, valid
    if not (age.isdigit()):
        err_str = "Invalid age!"
        return err_str, valid
    if (int(age) > 150):
        err_str = "hmmm, maybe you are too old to be our user."
        return err_str, valid
    valid = True
    information = get_account_details(username)
    information[0] = email_address
    information[1] = gender
    information[2] = age
    write_account_details(username, information)
    err_str = ''
    return err_str, valid

#-----------------------------------------------------------------------------
# Redirect to login
@route('/')
@route('/home')
def index():
    return fEngine.load_and_render("index")

# Display the login page
@get('/login')
def login():
    return fEngine.load_and_render("login")

# Attempt the login
@post('/login')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')
    err_str, login = check_login(username, password)
    if login:
        return fEngine.load_and_render("valid", flag=err_str)
    else:
        return fEngine.load_and_render("invalid", reason=err_str)

# Display the register page
@get('/register')
def register():
    return fEngine.load_and_render("register")

# Register a new account
@post('/register')
def do_register():
    return FrameEngine.load_and_render("register")

# Display the account profile <Harry>
@get('/account')
def account():
    information = get_account_details("testuser") #TODO replace this with variable
    return fEngine.load_and_render("account", username = 'username', email_address = information[0], gender = information[1], age = information[2], account_type = information[3], medicare_number = information[4])
    #TODO replace this with variable

# Display edit page for account information <Harry>
@get('/edit')
def edit():
    information = get_account_details("testuser") #TODO replace this with variable
    return fEngine.load_and_render("edit", username = 'username', email_address = information[0], gender = information[1], age = information[2], account_type = information[3], medicare_number = information[4])

# Attempt to edit account informaiton <Harry>
@post('/edit')
def do_edit():
    email_address = request.forms.get('email_address')
    gender = request.forms.get('gender')
    age = request.forms.get('age')
    err_str, valid = check_edit('username', email_address, gender, age) #TODO replace with variable
    if valid:
        return fEngine.load_and_render('edit_success')
    else:
        return fEngine.load_and_render('edit_failed', reason = err_str)

@get('/about')
def about():
    garble = ["leverage agile frameworks to provide a robust synopsis for high level overviews.",
    "iterate approaches to corporate strategy and foster collaborative thinking to further the overall value proposition.",
    "organically grow the holistic world view of disruptive innovation via workplace diversity and empowerment.",
    "bring to the table win-win survival strategies to ensure proactive domination.",
    "ensure the end of the day advancement, a new normal that has evolved from generation X and is on the runway heading towards a streamlined cloud solution.",
    "provide user generated content in real-time will have multiple touchpoints for offshoring."]
    return fEngine.load_and_render("about", garble=np.random.choice(garble))

#-----------------------------------------------------------------------------

fEngine = FrameEngine()
run(host='localhost', port=8080, debug=True)
