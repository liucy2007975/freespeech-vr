#!/usr/bin/env python

# pykey -- a Python version of crikey,
# http://shallowsky.com/software/crikey
# Simulate keypresses under X11.
#
# This software is copyright 2008 by Akkana Peck.
# Please share and re-use this under the terms of the GPLv2
# or, at your option, any later GPL version.

import Xlib.display
import Xlib.X
import Xlib.XK
import Xlib.protocol.event

UseXTest = True

try :
    import Xlib.ext.xtest
except ImportError:
    UseXTest = False
    print "no XTest extension; using XSendEvent"

import sys, time

display = Xlib.display.Display()
window = display.get_input_focus()._data["focus"];

if UseXTest and not display.query_extension("XTEST") :
    UseXTest = False

special_X_keysyms = {
    '\b' : "BackSpace",
    ' ' : "space",
    '\t' : "Tab",
    '\n' : "Return",  # for some reason this needs to be cr, not lf
    '\r' : "Return",
    '\e' : "Escape",
    '!' : "exclam",
    '#' : "numbersign",
    '%' : "percent",
    '$' : "dollar",
    '&' : "ampersand",
    '"' : "quotedbl",
    '\'' : "apostrophe",
    '(' : "parenleft",
    ')' : "parenright",
    '*' : "asterisk",
    '=' : "equal",
    '+' : "plus",
    ',' : "comma",
    '-' : "minus",
    '.' : "period",
    '/' : "slash",
    ':' : "colon",
    ';' : "semicolon",
    '<' : "less",
    '>' : "greater",
    '?' : "question",
    '@' : "at",
    '[' : "bracketleft",
    ']' : "bracketright",
    '\\' : "backslash",
    '^' : "asciicircum",
    '_' : "underscore",
    '`' : "grave",
    '{' : "braceleft",
    '|' : "bar",
    '}' : "braceright",
    '~' : "asciitilde"
    }


def get_keysym(ch) :
    keysym = Xlib.XK.string_to_keysym(ch)
    if keysym == 0 :
        # Unfortunately, although this works to get the correct keysym
        # i.e. keysym for '#' is returned as "numbersign"
        # the subsequent display.keysym_to_keycode("numbersign") is 0.
        keysym = Xlib.XK.string_to_keysym(special_X_keysyms[ch])
    return keysym

def is_shifted(ch) :
    if ch.isupper() :
        return True
    if "~!@#$%^&*()_+{}|:\"<>?".find(ch) >= 0 :
        return True
    return False

def char_to_keycode(ch) :
    keysym = get_keysym(ch)
    keycode = display.keysym_to_keycode(keysym)
    if keycode == 0 :
        print "Sorry, can't map", ch

    if (is_shifted(ch)) :
        shift_mask = Xlib.X.ShiftMask
    else :
        shift_mask = 0

    return keycode, shift_mask

def send_string(str) :
    for ch in str :
        #print "sending", ch, "=", display.keysym_to_keycode(Xlib.XK.string_to_keysym(ch))
        keycode, shift_mask = char_to_keycode(ch)
        if (UseXTest) :
            #print "Trying fake_input of", ch, ", shift_mask is", shift_mask
            if shift_mask != 0 :
                Xlib.ext.xtest.fake_input(display, Xlib.X.KeyPress, 50)
            Xlib.ext.xtest.fake_input(display, Xlib.X.KeyPress, keycode)
            Xlib.ext.xtest.fake_input(display, Xlib.X.KeyRelease, keycode)
            if shift_mask != 0 :
                Xlib.ext.xtest.fake_input(display, Xlib.X.KeyRelease, 50)
        else :
            event = Xlib.protocol.event.KeyPress(
                time = int(time.time()),
                root = display.screen().root,
                window = window,
                same_screen = 0, child = Xlib.X.NONE,
                root_x = 0, root_y = 0, event_x = 0, event_y = 0,
                state = shift_mask,
                detail = keycode
                )
            window.send_event(event, propagate = True)
            event = Xlib.protocol.event.KeyRelease(
                time = int(time.time()),
                root = display.screen().root,
                window = window,
                same_screen = 0, child = Xlib.X.NONE,
                root_x = 0, root_y = 0, event_x = 0, event_y = 0,
                state = shift_mask,
                detail = keycode
                )
            window.send_event(event, propagate = True)

for argp in range(1, len(sys.argv)) :
    send_string(sys.argv[argp])
    display.sync()