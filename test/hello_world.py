from nicegui import ui

# Lila Farbschema definieren
ui.colors(primary='#9c27b0')

# Styles für den Scrollbar definieren
custom_thumb_style = {'width': '25px', 'border-radius': '12px', 'backgroundColor': '#9c27b0', 'opacity': 0.5}
custom_bar_style = {'width': '25px', 'backgroundColor': '#f1f1f1', 'opacity': 0.2}

# Globales Padding der Seite entfernen
ui.query('.nicegui-content').classes('p-0')

with ui.column().classes('w-full h-screen p-4 gap-4 no-wrap'):

    # Kopfbereich (Fachschaft)
    with ui.card().classes('w-full shadow-md'):
        ui.label("Fachschaftsmitglied").classes('text-bold text-2xl text-primary')
        ui.label("Bitte Ausweis scannen").classes('text-grey-7 pt-0')

    # Warenkorb Bereich
    with ui.card().classes('w-full grow overflow-hidden no-wrap shadow-lg'):
        ui.label("Warenkorb").classes('text-bold text-xl mb-2')

        with ui.scroll_area() \
            .classes('w-full grow') \
            .props(f':thumb-style="{custom_thumb_style}" :bar-style="{custom_bar_style}" visible'):
            with ui.column().classes('w-full gap-2 p-1 pr-10'): # pr-4 schafft Platz für den breiten Scrollbar
                for i in range(15): 
                    with ui.row().classes('w-full items-center bg-slate-50 px-4 py-3 rounded-lg border border-slate-100'):
                        ui.label(f'Getränk {i+1}').classes('grow font-medium')
                        ui.label(f'{i+1},50 €').classes('px-4 font-bold')
                        ui.button(icon='delete').props('flat round').classes('text-gray-400 hover:text-red-500')
        
        ui.separator().classes('my-2')
        
        with ui.row().classes('w-full items-center px-2 py-2'):
            ui.label("Gesamt:").classes('text-xl font-medium')
            ui.space()
            ui.label("24,50 €").classes('text-4xl font-black text-primary')

    # Buttons
    with ui.row().classes('w-full gap-4 items-end'):
        ui.button("ZURÜCKSETZEN", color='red', icon='refresh') \
            .classes('flex-[1] h-20 text-base font-bold rounded-xl opacity-80')
        ui.button("JETZT BUCHEN", color='primary', icon='check_circle') \
            .classes('flex-[4] h-20 text-2xl font-bold rounded-xl shadow-lg')

ui.run()