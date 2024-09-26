import json
from microdot import Microdot
from Url_encode import url_encode
from galactic import GalacticUnicorn, Channel
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY
from random import randint, choice
from time import sleep

import mm_wlan as MM_WLAN
from WIFI_CONFIG import SSID, PSK

#Set up global vars
APP      = Microdot()
URL      = url_encode()
GU       = GalacticUnicorn()
CHANNEL  = GU.synth_channel(1)
GRAPHICS = PicoGraphics(DISPLAY)
WIDTH    = GalacticUnicorn.WIDTH
HEIGHT   = GalacticUnicorn.HEIGHT
SCALE    = 1
#Set synth ready to play
GU.play_synth()
CHANNEL.configure(waveforms=Channel.TRIANGLE + Channel.SQUARE + Channel.NOISE,
                                  attack=0.016,
                                  decay=0.168,
                                  sustain=0xafff / 65535,
                                  release=0.168,
                                  volume= 0.5)
#Connect to wifi
MM_WLAN.connect_to_network(SSID, PSK)

def random_note(note_list=[100, 200, 500, 1000,2000, 3000, 4000]):
    #trigger the synth to playing a random note from a list of notes
    note = choice(note_list)
    CHANNEL.frequency(note)
    CHANNEL.trigger_attack()

def stop_synth():
    #stop the synth from playing
    CHANNEL.trigger_release()     


def glitch_screen_write(message,
                 font = "bitmap8",
                 scale = SCALE,
                 bounce_range = (2,3),
                 wait = 0.05, #in s
                 glitch_level = 1,
                 repeat = 1
                        ):
    size = GRAPHICS.measure_text(message, scale)
    GRAPHICS.set_font(font)
    print(f'printing {message}')
    for i in range(repeat):
        offset = int(WIDTH)
        for _ in range(offset + size + 1):
            
            #set the draw HEIGHT (bounce) and pen colour this frame
            random_note()
            bounce = randint(*bounce_range)
            #CHANNEL.trigger_attack()              
            pen = GRAPHICS.create_pen(
                randint(25,50),
                randint(0,200),
                randint(0,100))
            GRAPHICS.set_pen(pen)
            
            #write the message to screen            
            GRAPHICS.text(message, offset, bounce, scale=scale)
            GU.update(GRAPHICS)
                        
            #create random glitch pixels the write them to screen            
            errors = [(randint(0, WIDTH), randint(0, HEIGHT)) for h in range(glitch_level)]
            for e in errors:
                pen = GRAPHICS.create_pen(
                choice([0,250]),
                choice([0,100,250]),
                choice([0,100,250]))
                GRAPHICS.set_pen(pen) 
                GRAPHICS.pixel(*e)
            GU.update(GRAPHICS)
            
            #sleep in s            
            sleep(wait)
            #set pen to blank and draw over everything we drew            
            GRAPHICS.set_pen(0)
            GRAPHICS.text(message, offset, bounce, scale=1)
            for e in errors:
               GRAPHICS.pixel(*e)
            GU.update(GRAPHICS)
            #change the offset to move the position of text drawing            
            offset -= 1
    stop_synth()
    print(f'printing done')


@APP.route('/')
def index(request):
    print('main')
    return glitch_screen_write("you got here")

@APP.route('/message/<message>')
def index(request, message):
    print(f'recieved message {message}')
    glitch_screen_write(URL.decode(message))
    print(message)
    return message


@APP.post('/message_v2')
def index(request):
    data = json.loads(request.body)
    message = data.get('message')
    user   = data.get('user')
    bits   = data.get('bits')
    message_type = data.get('type') or 'bits'
    print(f'recieved message_v2 {json.loads(request.body)}')
    glitch_screen_write(f'{message}')
    return json.loads(request.body)


glitch_screen_write("Ready", repeat=1)
APP.run(port=80)
