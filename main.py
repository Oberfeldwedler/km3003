import PySimpleGUI as sg

sg.theme('BluePurple')
font = ("Arial", 15)
initialWidth=951
initialHeight=540


header = [[ 
    sg.Text('Bitte Ausweis scannen') 
]]

product0 = [[
    sg.Column( [[ sg.Text('Getränk') ]] ), 
    sg.Push(),
    sg.Column( [[ sg.Text('15€') ]] ), 
    sg.Column( [[ sg.Button('X', size=5) ]] )
]] 

sum = [[ 
    sg.Column( [[sg.Text('Summe')]] ), 
    sg.Push(), 
    sg.Column( [[sg.Text('80€')]] )
]]

productList = [
    [ product0 ],
    [ sg.VPush() ], 
    [ sg.HorizontalSeparator() ],
    [ sum ]
]

footer = [[ 
    # sg.Button('Reset'), sg.Push() ,sg.Button('Buchen')
    sg.Button( 'Reset', size=20 ), sg.Button('Buchen', expand_x=True ) 
]]

layout = [
    [ sg.Frame( 'Fachschaftsmitglied', header , expand_x=True, element_justification='center' ) ],
    [ sg.Frame( 'Einkaufsliste', productList , expand_x=True, expand_y=True ) ],
    [ sg.Frame( '', footer, expand_x=True ) ]
]

# class Product:
#     barcode=""
#     price




# Create the Window
window = sg.Window (
    'Window Title', 
    layout, 
    no_titlebar=False,  
    size=(initialWidth,initialHeight), 
    location=(0,0), 
    keep_on_top=True,
    font=font
)
window.Resizable=True


# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()



    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    print('You entered ', values[0])

window.close()
