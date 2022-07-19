import telebot
from PIL import Image, ImageFont, ImageFilter, ImageDraw
import os
import sys
from py_linq import Enumerable

values = []
msgr_to_delete = []

bot = telebot.TeleBot("<TOKEN_TELEGRAM>")

def procesar(id_chat):

    chatValues = {}
    items = Enumerable(values).where(lambda p: p['id'] == id_chat)
    if(items.count() == 6):
        for item in items:
            chatValues[item['type']] = item['value']
        
        imageEdit(chatValues)
        
        img_base = open(chatValues['imagen_base'], 'rb')
        bot.send_photo(id_chat, img_base)
        img_base.close()
        
        img_exif = open(chatValues['imagen_exif'], 'rb')
        bot.send_photo(id_chat, img_exif)
        img_exif.close()
        
        os.remove(chatValues['imagen_base'])
        os.remove(chatValues['imagen_exif'])
        
        insertMsgr(bot.send_message(id_chat,"Si no te gusta con el resultado puedes reemplazar tu respuesta o imagen para seguir probando.\nSi te gusta el resultado usa el comando /confirmar para terminar con esta foto 😍. "))
        
def deleteMsgrs(id_chat):
    for msgr in Enumerable(msgr_to_delete).where(lambda p: p['id_chat'] == id_chat):
        try:
            bot.delete_message(id_chat, msgr['id_message'])
        except Exception as e:
            print(e)

def insertMsgr(msgr):
    msgr_to_delete.append({'id_chat': msgr.chat.id, 'id_message': msgr.id })
    
def insertValue(id_chat, type, value):
    items = Enumerable(values)
    item = items.first_or_default(lambda p: p['id'] == id_chat and p['type'] == type)
    if item == None :
        values.append({
            "id": id_chat, 
            "type": type,
            "value": value,
        })
    else:
        item['value'] = value

def deleteValues(id_chat):
    
    for item in Enumerable(values).where(lambda p: p['id'] == id_chat):
        if item['type'] == 'imagen':
            os.remove(item['value'])
        values.remove(item)
    

def getReplyType(reply_message):
    
    if str(reply_message).startswith("Modelo"):
        return "modelo"
    elif str(reply_message).startswith("Parametros"):
        return "focal"
    elif str(reply_message).startswith("Lugar"):
        return "lugar"
    elif str(reply_message).startswith("Fecha"):
        return "fecha"
    elif str(reply_message).startswith("Autor"):
        return "autor"
    elif str(reply_message).startswith("Adjunta"):
        return "imagen"
    else :
        return None

def imageEdit(values):
    path = values['imagen']
    fn, fext = os.path.splitext(os.path.basename(path))
    resolucion = (1080,1080)
    
    image = Image.open(path).convert("RGBA")
    image.thumbnail(resolucion)
    bg = Image.new('RGBA', (1080,1080), color="white")
    
    if image.size[0] < image.size[1]:
        bg.paste(image, box=(540-(int(image.size[0]/2)),0))
    else:
        bg.paste(image, box=(0, 540-(int(image.size[1]/2))))

    values['imagen_base'] = f'Imagenes/{fn}_base.png'
    bg.save(values['imagen_base'])
   
    bgexif = Image.open(resource_path("bgexif.png")).convert("RGBA")
    resolucion = (700, 700)
    image.thumbnail(resolucion, Image.ANTIALIAS)
    shadowImage = dropShadow(image, background="white", shadow=(0x00,0x00,0x00,0xff), border=30, iterations=70)
    bgexif.paste(shadowImage, box=(400 - int(image.size[0]/2), 120 + 390 - int(image.size[1]/2)))

    draw = ImageDraw.Draw(bgexif)
    font = ImageFont.truetype(resource_path("OpenSans-Regular.ttf"), 21)

    draw.multiline_text((878,280), values['modelo'], fill="black", font = font)
    draw.multiline_text((878,340), values['focal'], fill="black", font = font)
    draw.multiline_text((878,435), values['lugar'], fill="black", font = font)
    draw.multiline_text((878,515), values['fecha'], fill="black", font = font)
    draw.multiline_text((878,595), values['autor'], fill="black", font = font)

    values['imagen_exif'] = f'Imagenes/{fn}_exif.png'
    bgexif.save(values['imagen_exif'])

    image.close()
    bgexif.close()
    bg.close()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def dropShadow(image, offset=(5,5), background=0xffffff, shadow=0x444444, border=8, iterations=3):
    # Create the backdrop image -- a box in the background colour with a 
    # shadow on it.
    totalWidth = image.size[0] + abs(offset[0]) + 2*border
    totalHeight = image.size[1] + abs(offset[1]) + 2*border
    back = Image.new(image.mode, (totalWidth, totalHeight), background)

    # Place the shadow, taking into account the offset from the image
    shadowLeft = border + max(offset[0], 0)
    shadowTop = border + max(offset[1], 0)
    back.paste(shadow, [shadowLeft, shadowTop, shadowLeft + image.size[0], 
    shadowTop + image.size[1]] )

    # Apply the filter to blur the edges of the shadow.  Since a small kernel
    # is used, the filter must be applied repeatedly to get a decent blur.
    n = 0
    while n < iterations:
        back = back.filter(ImageFilter.BLUR)
        n += 1

    # Paste the input image onto the shadow backdrop  
    imageLeft = border - min(offset[0], 0)
    imageTop = border - min(offset[1], 0)
    back.paste(image, (imageLeft, imageTop))

    return back


@bot.message_handler(commands=["empezar", "start", "confirmar", "ayuda", "help", "reset"])
def sendMessage(message):
    print(message.text)
    if message.text in ["/empezar", "/start"]:
        insertMsgr(bot.reply_to(message, "Bienvenido al bot de AFOBA para preparar las fotos para instagram.\n*Responde a cada mensaje* para preparar tu imagen.\nUsa el comando /ayuda si lo necesitas😉", parse_mode= 'Markdown'))
        insertMsgr(bot.send_message(message.chat.id,"Modelo de cámara usado"))#Ejemplo:\nCanon\nEOS 77D
        insertMsgr(bot.send_message(message.chat.id,"Parametros usados"))#Ejemplo:\nf/1,8 1/900\n35 mm\nISO 160
        insertMsgr(bot.send_message(message.chat.id,"Lugar de la foto"))#Ejemplo:\nLa Herradura\n(Granada)
        insertMsgr(bot.send_message(message.chat.id,"Fecha de la foto"))#Ejemplo:\n12 octubre\n2019
        insertMsgr(bot.send_message(message.chat.id,"Autor"))#Ejemplo:\nManolo Ruiz\n(@manruirub)
        insertMsgr(bot.send_message(message.chat.id,"Adjunta la foto que quieres preparar"))
    elif message.text in ["/confirmar"]:
        insertMsgr(message)
        deleteMsgrs(message.chat.id)
        deleteValues(message.chat.id)
        bot.send_message(message.chat.id, "Buen trabajo!!🎉🎉\nNo olvides mandarle las dos imagenes a Manolo para que las publique en el instagram 😊.")
    elif message.text in ["/help", "/ayuda"]:
        insertMsgr(bot.send_message(message.chat.id,"Estás teniendo problemas? No te preocupes que seguro que con estos consejos lo haces fenomenal😊\n\nPara que la información salga bien es importante seguir el siguiente estilo:"))
        insertMsgr(bot.send_message(message.chat.id,"*Modelo de cámara usado*\n_Usa dos lineas. Ejemplo:_\n\nCanon\nEOS 77D", parse_mode= 'Markdown'))
        insertMsgr(bot.send_message(message.chat.id,"*Parametros usados*\n_Usa tres lineas para indicar apertura, velocidad, distancia e ISO. Ejemplo:_\n\nf/1,8 1/900\n35 mm\nISO 160", parse_mode= 'Markdown'))
        insertMsgr(bot.send_message(message.chat.id,"*Lugar de la foto*\n_Usa dos lineas. Ejemplo:_\n\nLa Herradura\n(Granada)", parse_mode= 'Markdown'))#Ejemplo:
        insertMsgr(bot.send_message(message.chat.id,"*Fecha de la foto*\n_Usa dos lineas. Con mes y año es suficiente. Ejemplo:_\n\n12 octubre\n2019", parse_mode= 'Markdown'))#Ejemplo:
        insertMsgr(bot.send_message(message.chat.id,"*Autor*\n_Usa dos lineas. Puedes agrega tu alias de instagram. Ejemplo:_\n\nManolo Ruiz\n(@manruirub)", parse_mode= 'Markdown'))#Ejemplo:\nManolo Ruiz\n(@manruirub)
        insertMsgr(bot.send_message(message.chat.id,"Ahora si que puedes /empezar 😉", parse_mode= 'Markdown'))
    elif message.text in ["/reset"]:
        insertMsgr(message)
        deleteMsgrs(message.chat.id)
        deleteValues(message.chat.id)
@bot.message_handler()
def sendMessage(message):
    print(message.text)
    insertMsgr(message)
    if message.reply_to_message == None:
        return
    
    type = getReplyType(message.reply_to_message.text)

    if type == None:
        return

    insertValue(message.chat.id, type, message.text)
    insertMsgr(bot.reply_to(message, "👌👌"))
    procesar(message.chat.id)

@bot.message_handler(content_types=['photo'])
def photo(message):
    print('Image receive')
    insertMsgr(message)
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    path = f'Imagenes/{message.chat.id}image.jpg'
    with open(path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    insertValue(message.chat.id, "imagen", path)
    procesar(message.chat.id)


if(not os.path.isdir("./Imagenes")):
    os.mkdir("./Imagenes")

bot.polling()