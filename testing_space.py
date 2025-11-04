
def string_to_morse(message):
    morse_dict = {
        'A' : '.-', 'B' : '-...', 'C' : '-.-.', 'D' : '-..', 'E' : '.', 'F' : '..-.', 'G' : '--.', 'H' : '....', 'I' : '..', 'J' : '.---',
        'K' : '-.-', 'L' : '.-..', 'M' : '--', 'N' : '-.', 'O' : '---', 'P' : '.--.', 'Q' : '--.-', 'R' : '.-.', 'S' : '...', 'T' : '-',
        'U' : '..-', 'V' : '...-', 'W' : '.--', 'X' : '-..-', 'Y' : '-.--', 'Z' : '--..', '0' : '-----', '1' : '.----', '2' : '..---',
        '3' : '...--', '4' : '....-', '5' : '.....', '6' : '-....', '7' : '--...', '8' : '---..', '9' : '----.','.' : '.-.-.-', ',' : '--..--',
        '?' : '..--..', '/' : '--..-.', '@' : '.--.-.', '!' : '-.-.--', ' ' : ' '
    }
    morse_code = ' '.join(morse_dict.get(char.upper(), '') for char in message)
    print(morse_code)
    return morse_code

def morse_to_text(morse_code):
    # Morse code dictionary (reversed for decoding)
    morse_dict = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G', '....': 'H',  '..': 'I', '.---': 'J', 
        '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
        '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z', '.----': '1', '..---': '2', '...--': '3', 
        '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9', '-----': '0', '--..--': ',', 
        '.-.-.-': '.', '..--..': '?', '-..-.': '/', '-....-': '-', '-.--.': '(', '-.--.-': ')'
    }

    # Split Morse code into words ("/" separates words)
    words = morse_code.strip().split(' / ')
    decoded_text = []

    for word in words:
        letters = word.split()
        decoded_word = ''.join(morse_dict.get(letter, '') for letter in letters)
        decoded_text.append(decoded_word)

    print(' '.join(decoded_text))
    return ' '.join(decoded_text)



#string_to_morse("sos")
morse_to_text("... --- ...")


