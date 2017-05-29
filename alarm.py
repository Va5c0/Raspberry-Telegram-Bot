#!/usr/bin/env python
# -*- coding: utf-8 -*-


import telebot
import sys
import pygame
import time
import os


TOKEN = "TOKEN"  # Cambiar por  el token
cid = "Nº CID"  # Cambiar por el numero cid
bot = telebot.TeleBot(TOKEN)


def play(fname, seg):
    pygame.mixer.init()
    pygame.mixer.init(44100)
    pygame.mixer.music.load(fname)
    pygame.mixer.music.play()
    time.sleep(seg)
    pygame.mixer.music.stop()


if len(sys.argv) < 2:
    print("Uso: %s [cam/move]" % sys.argv[0])
elif sys.argv[1] == "cam":
    bot.send_message(cid, "¡¡Camara no disponible!!")
elif sys.argv[1] == "move":
    bot.send_message(cid, "¡¡Movimiento Detectado!!")
    with open('alarm.txt', 'r') as f:
        state = f.readline().strip('\n')
    if state == "1":
        play('Sonidos/alarma.mp3', 15)
        os.system('espeak -ves+m7 -s165 -p30 \"Intruso detectado\"')
else:
    print(" ¡¡ERROR!!")