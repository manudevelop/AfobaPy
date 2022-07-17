from fileinput import filename
from logging import exception
import shutil
import PIL
import PySimpleGUI as sg
import PySimpleGUIQt as sgqt
import os
import sys
from PIL import Image, ImageFont, ImageFilter, ImageDraw

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

def begin():
    if not os.path.isdir("Imagenes"):
        os.mkdir("Imagenes")
    
def end():
    pass

def btnAbrir_Click(path):
    # i = Image.open(path)
    # exif = {ExifTags.TAGS[k]: v for k, v in i.getexif().items() if k in ExifTags.TAGS}
    pass

def imageEdit(values):
    previsualizar = values['chkPrevisualizacion']
    path = values['txtImagePath']
    fn, fext = os.path.splitext(os.path.basename(path))
    resolucion = (1080,1080)
    
    image = Image.open(path).convert("RGBA")
    image.thumbnail(resolucion)
    bg = Image.new('RGBA', (1080,1080), color="white")
    
    if image.size[0] < image.size[1]:
        bg.paste(image, box=(540-(int(image.size[0]/2)),0))
    else:
        bg.paste(image, box=(0, 540-(int(image.size[1]/2))))

    bg.save(f'Imagenes/{fn}_base.png')
    if(previsualizar):
        bg.show()

    bgexif = Image.open(resource_path("bgexif.png")).convert("RGBA")
    resolucion = (700, 700)
    image.thumbnail(resolucion, Image.ANTIALIAS)
    shadowImage = dropShadow(image, background="white", shadow=(0x00,0x00,0x00,0xff), border=30, iterations=70)
    bgexif.paste(shadowImage, box=(400 - int(image.size[0]/2), 120 + 390 - int(image.size[1]/2)))

    draw = ImageDraw.Draw(bgexif)
    # font = ImageFont.truetype(resource_path("Roboto-Regular.ttf"), 20)
    font = ImageFont.truetype(resource_path("OpenSans-Regular.ttf"), 21)

    camara = values['txtModeloCamara']
    focal = values['txtFocal']
    lugar = values['txtLugar']
    fecha = values['txtFecha']
    autor = values['txtAutor']

    draw.multiline_text((878,280), camara, fill="black", font = font)
    draw.multiline_text((878,340), focal, fill="black", font = font)
    draw.multiline_text((878,435), lugar, fill="black", font = font)
    draw.multiline_text((878,515), fecha, fill="black", font = font)
    draw.multiline_text((878,595), autor, fill="black", font = font)

    bgexif.save(f'Imagenes/{fn}_exif.png')

    if previsualizar:
        bgexif.show()
    
def runWindow():
    begin()
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "btnConvertir":
            imageEdit(values)
        elif event == "btnAbrir":
            btnAbrir_Click(values)
        if event is None:
            break
        print (event, values)
    end()


layout = [
        [
            [sg.Text('Selecciona una imagen')],
            [
                # sg.Text('Single File Playback', justification='right'), 
                sg.InputText(size=(70, 1), key="txtImagePath"), 
                sg.FileBrowse('Buscar', key="fbImages", file_types=(("Imagen File", "*.png, *.jpg, *.jpeg")))
            ],
            # [
            #     sg.Button('Abrir', key='btnAbrir')
            # ],
            [
                sg.Text('Modelo:', size=(10, 0)),
                sg.Multiline(key="txtModeloCamara", size=(65, 2), default_text='Canon EOS\n77D')
            ],
            [
                sg.Text('Focal:', size=(10, 0)),
                sg.Multiline(key="txtFocal", size=(65, 3), default_text='f/1,8 1/900\n35 mm\nISO 160')
            ],
            [
                sg.Text('Lugar:', size=(10, 0)),
                sg.Multiline(key="txtLugar", size=(65, 2), default_text="La Herradura\n(Granada)")
            ],
            [
                sg.Text('Fecha:', size=(10, 0)),
                sg.Multiline(key="txtFecha", size=(65, 2), default_text="12 octubre\n2019")
            ],
            [
                sg.Text('Autor:', size=(10, 0)),
                sg.Multiline(key="txtAutor", size=(65, 2), default_text="Manolo Ruiz\n(@manruirub)")
            ],
            [
                sg.Checkbox('Mostrar previsualizacion', key='chkPrevisualizacion')
            ],
            [
                sg.Button('Convertir', key='btnConvertir')
                # sgqt.Image(key="ivImagen")
            ],
        ],
    ]

window = sg.Window("AFOBA Instragram Py by Manolo Ruiz", layout, default_element_size=(640,420), resizable=True, finalize=True)
runWindow()
window.close()