import PySimpleGUI as sg

sg.theme('Dark Green 7')

width=951
height=540
padding=width*0.01
effectiveWidth=width-2*padding
effectiveHeight=height-2*padding
headerHeight=effectiveHeight*0.1
productListHeight=effectiveHeight*0.75
footerHeight=effectiveHeight*0.15

header = [[ sg.Text('Bitte Ausweis scannen', expand_x=True) ]]
productList =   [[ 
                sg.Column( [[sg.Text('Spezi')]], element_justification='l'), 
                sg.Column( [[sg.Text('15€')]], element_justification='r' ), 
                sg.Column( [[sg.Button('X')]], element_justification='r' )  
            ]]
footer = [[ sg.Button('Reset'), sg.Button('Buchen') ]]

layout = [
            [sg.Frame( 'Fachschaftsmitglied', header , size=(effectiveWidth, headerHeight) )],
            [sg.Frame( 'Einkaufsliste', productList, size=(effectiveWidth, productListHeight) )],
            [sg.Frame( '', footer, size=(effectiveWidth, footerHeight) )]
        ]



# Create the Window
window = sg.Window('Window Title', layout, no_titlebar=False, location=(0,0), size=(width,height), keep_on_top=True)


# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    print('You entered ', values[0])

window.close()
