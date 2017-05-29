#!/usr/bin/env python
# -*- coding: utf-8 -*-


import telebot
from telebot import types
import time
import os
import serial
import pygame


TOKEN = "TOKEN"  # Cambiar por el token
ncid = "Nº CID"  # Cambiar por el numero cid

userStep = {}
knownUsers = []

arduino = serial.Serial('/dev/ttyUSB0', 9600)

commands = {'start': 'Arranca el bot',
            'ayuda': 'Comandos disponibles',
            'exec': 'Ejecuta un comando'}

menu = types.ReplyKeyboardMarkup()
menu.add("RPinfo", "Camara")
menu.add("Arduino", "Seguridad")

cam_menu = types.ReplyKeyboardMarkup()
cam_menu.add("Foto", "Timelapse")
cam_menu.add("Atras")

info_menu = types.ReplyKeyboardMarkup()
info_menu.add("TEMP", "HD")
info_menu.add("RAM", "CPU")
info_menu.add("Status", "Logs")
info_menu.add("Atras")

ard_menu = types.ReplyKeyboardMarkup()
ard_menu.add("LED ON", "LED OFF")
ard_menu.add("Efectos Sonido")
ard_menu.add("Mensaje Voz")
ard_menu.add("Atras")

snd_menu = types.ReplyKeyboardMarkup()
snd_menu.add("Sicofonia", "Risa Malvada")
snd_menu.add("Alarma", "Mario")
snd_menu.add("Atras")

sec_menu = types.ReplyKeyboardMarkup()
sec_menu.add("LiveCam ON", "LiveCam OFF")
sec_menu.add("Move ON", "Move OFF")
sec_menu.add("Alarma ON", "Alarma OFF")
sec_menu.add("Descargar", "Atras")


# COLOR TEXTO
class color:
    RED = '\033[91m'
    BLUE = '\033[94m'
    GREEN = '\033[32m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# USER STEP
def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        knownUsers.append(uid)
        userStep[uid] = 0
        print(color.RED + " [¡] ¡¡NUEVO USUARIO!!" + color.ENDC)


# LISTENER
def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            print(time.strftime("%d/%m/%y-%H:%M:%S") + color.GREEN + " [" + str(m.chat.id) + "] " + str(m.chat.first_name) + ": " + color.ENDC + m.text)


# PLAY SOUND
def play(fname, seg):
    pygame.mixer.init()
    pygame.mixer.init(44100)
    pygame.mixer.music.load(fname)
    pygame.mixer.music.play()
    time.sleep(seg)
    pygame.mixer.music.stop()


# INFO HD
def diskSpace():
    p = os.popen("df -h /")
    i = 0
    while 1:
        i += 1
        line = p.readline()
        if i == 2:
            return(line.split()[1:5])


# INFO RAM
def ramInfo():
    p = os.popen('free -o -h')
    i = 0
    while 1:
        i += 1
        line = p.readline()
        if i == 2:
            return(line.split()[1:4])


# TEXTO A VOZ
def txt2snd(m):
    cid = m.chat.id
    tipo = m.text
    with open('/tmp/msg.txt', 'r') as f:
        msg = f.readline()
    if tipo == "Hombre":
        os.system('espeak -ves+m7 -p30 -a150 \"%s\" 2> /dev/null' % msg)
    elif tipo == "Mujer":
        os.system('espeak -ves+f5 -a150 \"%s\" 2> /dev/null' % msg)
    elif tipo == "Fantasma":
        os.system('espeak -ves+whisper -p5 -s140 -a40 \"%s\" 2> /dev/null' % msg)
    bot.send_message(cid, "Mensaje reproducido")
    userStep[cid] = 3
    bot.send_message(cid, "Menu Arduino:", reply_markup=ard_menu)


def mensaje(m):
    msg = m.text
    with open('/tmp/msg.txt', 'w') as f:
        f.write(msg)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Hombre', 'Mujer')
    markup.add('Fantasma')
    tipo = bot.reply_to(m, "Tipo de voz?: ", reply_markup=markup)
    bot.register_next_step_handler(tipo, txt2snd)


# TIMELAPSE
def timelapse(m):
    cid = m.chat.id
    start = 0
    end = m.text
    print(color.BLUE + "Nº FOTOS: " + str(end) + color.ENDC)
    if end.isdigit():
        bot.send_message(cid, "Comienza la captura de fotos...")
        print(color.BLUE + "[+] Comienza la captura de fotos..." + color.ENDC)
        while start < int(end):
            print(color.BLUE + " [i] Capturando imagen %i" % start + color.ENDC)
            bot.send_chat_action(cid, 'typing')
            os.system("fswebcam -i 0 -d /dev/video0 -r 640x480 -q --no-banner fotos/%d%m%y_%H%M%S.jpg")
            start = start + 1
            time.sleep(10)
        print(color.BLUE + "[-] Proceso TIMELAPSE finalizado!!" + color.ENDC)
        bot.send_message(cid, "Proceso TIMELAPSE finalizado!!")

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('SI', 'NO')
        msg = bot.reply_to(m, "Enviar fotos? ", reply_markup=markup)
        bot.register_next_step_handler(msg, tarFotos)
    else:
        bot.send_message(cid, "Introduce numero de fotos")
        bot.register_next_step_handler(m, timelapse)
        return


# TAR FOTOS
def tarFotos(m):
    cid = m.chat.id
    msg = m.text
    if msg == "SI":
        bot.send_message(cid, "Comprimiendo fotos...")
        print(color.BLUE + "[+] Comprimiendo fotos..." + color.ENDC)
        bot.send_chat_action(cid, 'typing')
        if userStep[cid] == 2:
            os.system("tar -cvf /tmp/fotos.tar fotos/*.jpg")
            bot.send_message(cid, "Fotos comprimidas. Enviando...")
            bot.send_chat_action(cid, 'upload_document')
            tar = open('/tmp/fotos.tar', 'rb')
            bot.send_document(cid, tar)
        elif userStep[cid] == 4:
            os.system("sudo tar -cvf /tmp/motion.tar motion/*.*")
            bot.send_message(cid, "Fotos comprimidas. Enviando...")
            bot.send_chat_action(cid, 'upload_document')
            tar = open('/tmp/motion.tar', 'rb')
            bot.send_document(cid, tar)
        print(color.BLUE + " [+] Fotos Enviadas!!" + color.ENDC)
        userStep[cid] = 0
        bot.send_message(cid, "Menu Principal:", reply_markup=menu)
    else:
        userStep[cid] = 0
        bot.send_message(cid, "Menu Principal:", reply_markup=menu)


# LOGS
def logs(m):
    cid = m.chat.id
    msg = m.text
    if msg == "Fail2Ban":
        f2blog()
        log = open('/tmp/f2b.log', 'rb')
    elif msg == "OpenVPN":
        os.system('sudo cp /var/log/openvpn.log /tmp/')
        os.system('sudo chmod 777 /tmp/openvpn.log')
        log = open('/tmp/openvpn.log', 'rb')
    elif msg == "Logins":
        authlog()
        log = open('/tmp/login.log', 'rb')
    elif msg == "Atras":
        userStep[cid] = 1
        bot.send_message(cid, "Menu Info:", reply_markup=info_menu)

    if msg == "Fail2Ban" or msg == "OpenVPN" or msg == "Logins":
        bot.send_chat_action(cid, 'upload_document')
        bot.send_document(cid, log)
        print(color.BLUE + " [+] Log Enviado!!" + color.ENDC)
        userStep[cid] = 0
        bot.send_message(cid, "Menu Principal:", reply_markup=menu)


def f2blog():
    bans = {}
    os.system('sudo cp /var/log/fail2ban.log /tmp/')
    os.system('sudo chmod 777 /tmp/fail2ban.log')
    with open('/tmp/fail2ban.log', 'r') as log:
        for line in log.readlines():
            if "[ssh] Ban" in line:
                ip = line.split()[6]
                if ip not in bans:
                    bans[ip] = 1
                else:
                    bans[ip] = bans[ip] + 1

    with open('/tmp/f2b.log', 'w') as f2b:
        f2b.write("\n [i] Número de IPs: %i" % len(bans) + "\n")
        for ip, i in bans.iteritems():
            f2b.write('[-] IP: %s \t : %i\n' % (ip, i))


def authlog():
    os.system('sudo cp /var/log/auth.log /tmp/')
    os.system('sudo chmod 777 /tmp/auth.log')
    with open('/var/log/auth.log', 'r') as log:
        for line in log.readlines():
            if "Failed password" in line:
                array = line.split()
                if len(array) == 16:
                    datetime = time.strftime("%Y") + '-' + '-'.join(array[:3])
                    user = array[10]
                    ip = array[12]
                    port = array[14]
                    service = array[15]
                else:
                    datetime = time.strftime("%Y") + '-' + '-'.join(array[:3])
                    user = array[8]
                    ip = array[10]
                    port = array[12]
                    service = array[13]

                with open('/tmp/login.log', 'a+') as f:
                    f.write(" %s %s @ %s:%s - %s\n" % (datetime, user, ip, port, service))


# STATUS SERVER
def statusServer(m):
    cid = m.chat.id
    msg = m.text
    if msg == "ON":
        bot.send_message(cid, "[i] Status Server ON")
        print(color.BLUE + "[i] Status Server ON" + color.ENDC)
        os.system('nodejs Raspberry-Pi-Status/server.js &')
    elif msg == "OFF":
        bot.send_message(cid, "[i] Status Server OFF")
        print(color.BLUE + "[i] Status Server OFF" + color.ENDC)
        f = os.popen('ps -e | grep nodejs')
        pid = f.read().split()[0]
        os.system('sudo kill %s' % pid)
    userStep[cid] = 1
    bot.send_message(cid, "Menu Info:", reply_markup=info_menu)


bot = telebot.TeleBot(TOKEN)
bot.set_update_listener(listener)


# START
@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    userStep[cid] = 0
    bot.send_message(cid, "Wake up " + str(m.chat.first_name) + "...")
    time.sleep(1)
    bot.send_message(cid, "Fwhibbit has you...")
    time.sleep(1)
    bot.send_message(cid, "Follow the white rabbit...\n", reply_markup=menu)


# AYUDA
@bot.message_handler(commands=['ayuda'])
def command_help(m):
    cid = m.chat.id
    if cid == ncid:
        help_text = "Comandos disponibles: \n"
        for key in commands:
            help_text += "/" + key + ": "
            help_text += commands[key] + "\n"
        bot.send_message(cid, help_text)
    else:
        bot.send_message(cid, " ¡¡PERMISO DENEGADO!!")
        print(color.RED + " ¡¡PERMISO DENEGADO!! " + color.ENDC)


# EXEC COMANDO
@bot.message_handler(commands=['exec'])
def command_exec(m):
    cid = m.chat.id
    if cid == ncid:
        bot.send_message(cid, "Ejecutando: " + m.text[len("/exec"):])
        bot.send_chat_action(cid, 'typing')
        time.sleep(2)
        f = os.popen(m.text[len("/exec"):])
        result = f.read()
        bot.send_message(cid, "Resultado: " + result)
    else:
        bot.send_message(cid, " ¡¡PERMISO DENEGADO!!")
        print(color.RED + " ¡¡PERMISO DENEGADO!! " + color.ENDC)


# MENU PRINCIPAL
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 0)
def main_menu(m):
    cid = m.chat.id
    text = m.text
    if cid == ncid:
        if text == "RPinfo":  # RPINFO
            bot.send_message(cid, "Informacion disponible:", reply_markup=info_menu)
            userStep[cid] = 1
        elif text == "Camara":  # CAMARA
            bot.send_message(cid, "Opciones de la camara:", reply_markup=cam_menu)
            userStep[cid] = 2
        elif text == "Arduino":  # ARDUINO
            bot.send_message(cid, "Opciones Arduino:", reply_markup=ard_menu)
            userStep[cid] = 3
        elif text == "Seguridad":  # SEGURIDAD
            bot.send_message(cid, "Opciones Seguridad:", reply_markup=sec_menu)
            userStep[cid] = 4
        else:
            command_text(m)
    else:
        bot.send_message(cid, " ¡¡PERMISO DENEGADO!!")
        print(color.RED + " ¡¡PERMISO DENEGADO!! " + color.ENDC)


# MENU INFO
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 1)
def info_opt(m):
        cid = m.chat.id
        txt = m.text
        if txt == "TEMP":  # TEMP
            bot.send_message(cid, "[+] TEMPERATURAS")
            print(color.BLUE + "[+] TEMPERATURAS" + color.ENDC)
            # cpu temp
            tempFile = open("/sys/class/thermal/thermal_zone0/temp")
            cpu_temp = tempFile.read()
            tempFile.close()
            cpu_temp = round(float(cpu_temp) / 1000)
            bot.send_message(cid, "  [i]   CPU: %s" % cpu_temp)
            print(color.GREEN + " [i] CPU: %s" % cpu_temp + color.ENDC)
            # gpu temp
            gpu_temp = os.popen('/opt/vc/bin/vcgencmd measure_temp').read().split("=")[1][:-3]
            bot.send_message(cid, "  [i]   GPU: %s" % gpu_temp)
            print(color.GREEN + " [i] GPU: %s" % gpu_temp + color.ENDC)
        elif txt == "HD":  # HD
            bot.send_message(cid, "[+] DISCO DURO")
            print(color.BLUE + "[+] DISCO DURO" + color.ENDC)
            bot.send_message(cid, "  [i]   Total: %s" % diskSpace()[0])
            print(color.GREEN + " [i] Total: %s" % diskSpace()[0] + color.ENDC)
            bot.send_message(cid, "  [i]   Usado: %s" % diskSpace()[1])
            print(color.GREEN + " [i] Usado: %s" % diskSpace()[1] + color.ENDC)
            bot.send_message(cid, "  [i]   Disponible: %s" % diskSpace()[2])
            print(color.GREEN + " [i] Disponible: %s" % diskSpace()[2] + color.ENDC)
        elif txt == "RAM":  # RAM
            bot.send_message(cid, "[+] MEMORIA RAM")
            print(color.BLUE + "[+] MEMORIA RAM" + color.ENDC)
            bot.send_message(cid, "  [i]   Total: %s" % ramInfo()[0])
            print(color.GREEN + " [i] Total: %s" % ramInfo()[0] + color.ENDC)
            bot.send_message(cid, "  [i]   Usado: %s" % ramInfo()[1])
            print(color.GREEN + " [i] Usado: %s" % ramInfo()[1] + color.ENDC)
            bot.send_message(cid, "  [i]   Disponible: %s" % ramInfo()[2])
            print(color.GREEN + " [i] Disponible: %s" % ramInfo()[2] + color.ENDC)
        elif txt == "CPU":  # CPU
            bot.send_message(cid, "[+] CPU")
            print(color.BLUE + "[+] CPU" + color.ENDC)
            cpu = os.popen('mpstat | grep -A 5 "%idle" | tail -n 1 | awk -F " " \'{print 100 - $ 12}\'a').read()
            bot.send_message(cid, "  [i]   Usado: %s" % cpu)
            print(color.GREEN + " [i] Usado: %s" % cpu + color.ENDC)
        elif txt == "Status":  # STATUS SERVER
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add("ON", "OFF")
            msg = bot.reply_to(m, "Accion: ", reply_markup=markup)
            bot.register_next_step_handler(msg, statusServer)
        elif txt == "Logs":  # LOGS
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add("Fail2Ban", "Logins")
            markup.add("OpenVPN", "Atras")
            msg = bot.reply_to(m, "Elegir Log: ", reply_markup=markup)
            bot.register_next_step_handler(msg, logs)
        elif txt == "Atras":  # ATRAS
            userStep[cid] = 0
            bot.send_message(cid, "Menu Principal:", reply_markup=menu)
        else:
            command_text(m)


# MENU CAMARA
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 2)
def cam_opt(m):
    cid = m.chat.id
    text = m.text
    if text == "Foto":  # FOTO
        bot.send_message(cid, "Tomando foto ...")
        bot.send_chat_action(cid, 'upload_photo')
        foto = "fotos/" + (time.strftime("%H%M%S-%d%m%y")) + ".jpg"
        os.system('fswebcam -d /dev/video0 -r 640x480 --no-banner %s' % foto)
        bot.send_photo(cid, open(foto, 'rb'))
        print(color.BLUE + " [i] Foto enviada!!" + color.ENDC)
    elif text == "Timelapse":  # TIMELAPSE
        bot.send_message(cid, "Nº Fotos?: ")
        bot.register_next_step_handler(m, timelapse)
    elif text == "Atras":  # ATRAS
        userStep[cid] = 0
        bot.send_message(cid, "Menu Principal:", reply_markup=menu)
    else:
        command_text(m)


# MENU ARDUINO
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 3)
def ard_opt(m):
    cid = m.chat.id
    text = m.text
    if text == "LED ON":  # LED ON
        print(color.BLUE + " [i] LED ON" + color.ENDC)
        arduino.write('1')
    elif text == "LED OFF":  # LED OFF
        print(color.BLUE + " [i] LED OFF" + color.ENDC)
        arduino.write('0')
    elif text == "Efectos Sonido":  # EFECTOS SONIDO
        bot.send_message(cid, "Efectos de sonido:", reply_markup=snd_menu)
        userStep[cid] = 5
    elif text == "Mensaje Voz":  # MENSAJE VOZ
        bot.send_message(cid, "Escribir mensaje: ")
        bot.register_next_step_handler(m, mensaje)
    elif text == "Atras":  # ATRAS
        userStep[cid] = 0
        bot.send_message(cid, "Menu Principal:", reply_markup=menu)
    else:
        command_text(m)


# MENU SEGURIDAD
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 4)
def sec_opt(m):
    cid = m.chat.id
    text = m.text
    if text == "Alarma ON":  # ALARMA
        print(color.BLUE + " [i] ALARMA ON" + color.ENDC)
        bot.send_message(cid, "[i] Alarma ON")
        with open('alarm.txt', 'w') as f:
            f.write("1")
    elif text == "Alarma OFF":
        print(color.BLUE + " [i] ALARMA OFF" + color.ENDC)
        bot.send_message(cid, "[i] Alarma OFF")
        with open('alarm.txt', 'w') as f:
            f.write("0")
    elif text == "LiveCam ON":  # LIVECAM
        print(color.BLUE + " [i] Live Cam ON" + color.ENDC)
        bot.send_message(cid, "[i] Live Cam ON")
        os.system('sudo motion -m -n 2> /dev/null')
    elif text == "LiveCam OFF":
        f = os.popen('ps -e | grep motion')
        pid = f.read().split()[0]
        os.system('sudo kill %s' % pid)
        os.system('sudo service motion stop')
        print(color.BLUE + " [i] Live Cam OFF" + color.ENDC)
        bot.send_message(cid, "[i] Live Cam OFF")
    elif text == "Move ON":  # MOVIMIENTO
        print(color.BLUE + " [i] Detector Movimiento ON" + color.ENDC)
        bot.send_message(cid, "[i] Detector Movimiento ON")
        os.system('sudo motion -n 2> /dev/null')
    elif text == "Move OFF":
        f = os.popen('ps -e | grep motion')
        pid = f.read().split()[0]
        os.system('sudo kill %s' % pid)
        os.system('sudo service motion stop')
        print(color.BLUE + " [i] Detector Movimiento OFF" + color.ENDC)
        bot.send_message(cid, "[i] Detector Movimiento OFF")
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('SI', 'NO')
        msg = bot.reply_to(m, "Enviar fotos?: ", reply_markup=markup)
        bot.register_next_step_handler(msg, tarFotos)
    elif text == "Descargar":  # DESCARGAR FOTOS
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('SI', 'NO')
        msg = bot.reply_to(m, "Descargar fotos?: ", reply_markup=markup)
        bot.register_next_step_handler(msg, tarFotos)
    elif text == "Atras":  # ATRAS
        userStep[cid] = 0
        bot.send_message(cid, "Menu Principal:", reply_markup=menu)
    else:
        command_text(m)


# MENU SONIDOS
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 5)
def snd_opt(m):
    cid = m.chat.id
    text = m.text
    if text == "Sicofonia":  # SICOF
        print(color.BLUE + " [i] Sicofonia" + color.ENDC)
        bot.send_message(cid, "[i] Sicofonia")
        play('Sonidos/sicofonia.mp3', 3)
    elif text == "Risa Malvada":  # RISA
        print(color.BLUE + " [i] Risa Malvada" + color.ENDC)
        bot.send_message(cid, "[i] Risa Malvada")
        play('Sonidos/risa-malvada.mp3', 4)
    elif text == "Alarma":  # ALARMA
        print(color.BLUE + " [i] Alarma" + color.ENDC)
        bot.send_message(cid, "[i] Alarma")
        play('Sonidos/alarma.mp3', 15)
    elif text == "Mario":
        print(color.BLUE + " [i] Super Mario" + color.ENDC)
        bot.send_message(cid, "[i] Mario")
        arduino.write('2')
    elif text == "Atras":  # ATRAS
        userStep[cid] = 3
        bot.send_message(cid, "Menu Arduino:", reply_markup=ard_menu)
    else:
        command_text(m)


# FILTRAR MENSAJES
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_text(m):
    cid = m.chat.id
    if (m.text.lower() in ['hola', 'hi', 'buenas', 'buenos dias']):
        bot.send_message(cid, 'Muy buenas, ' + str(m.from_user.first_name) + '. Me alegra verte de nuevo.', parse_mode="Markdown")
    elif (m.text.lower() in ['adios', 'aios', 'adeu', 'ciao']):
        bot.send_message(cid, 'Hasta luego, ' + str(m.from_user.first_name) + '. Te echaré de menos.', parse_mode="Markdown")


print 'Corriendo...'
bot.polling(none_stop=True)