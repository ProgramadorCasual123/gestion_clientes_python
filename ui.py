from tkinter import *
from tkinter import ttk
import database as db
from tkinter.messagebox import askokcancel, WARNING
import helpers


class CenterWidgetMixin:

    #Así podemos sacar la resolución necesaria en cada pantalla
    def center(self):
        self.update()
        w = self.winfo_width()
        h = self.winfo_height()
        ws= self.winfo_screenheight()
        hs = self.winfo_screenheight()
        x = int((ws/2) - (w/2))
        y = int((hs/2) - (h/2))
        
        self.geometry(f'{w}x{h}+{x}+{y}')
        #self.geometry('WIDTHxHEIGH+OFFSET_X+OFFSET_Y') Fórmula para sacar la resolución


#Creamos una clase para crear un cliente
class CreateClientWindow(Toplevel, CenterWidgetMixin):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Crear cliente')
        self.build()
        self.center()
        self.transient(parent)
        self.grab_set()
        
    #Definimos una función para la función del botón de crear
    def build(self):
        frame = Frame(self)
        frame.pack(padx=20, pady=10)
        
        #Agregamos los textos divididos en columnas
        Label(frame, text='DNI (2 ints y 1 upper char)').grid(row=0, column=0)
        Label(frame, text='Nombre(de 2 a 30 chars)').grid(row=0, column=1)
        Label(frame, text='Apellido (de 2 a 30 chars)').grid(row=0, column=2)

        #Entradas de texto 
        dni = Entry(frame)
        dni.grid(row=1, column=0)
        dni.bind("<KeyRelease>", lambda event: self.validate(event, 0))
        nombre = Entry(frame)
        nombre.grid(row=1, column=1)
        nombre.bind("<KeyRelease>", lambda event: self.validate(event, 1))
        apellido = Entry(frame)
        apellido.grid(row=1, column=2)
        apellido.bind("<KeyRelease>", lambda event: self.validate(event, 2))
     
        frame = Frame(self)
        frame.pack(pady=10)
        
        #Botón de crear en la pantalla de crear
        crear = Button(frame, text='Crear', command=self.create_client)
        crear.configure(state=DISABLED) #Desactivado hasta que cumpla características
        crear.grid(row=0, column=0)
        Button(frame, text='Cancelar', command=self.close).grid(row=0, column=1)
    
        #Exportamos
        self.validaciones = [0, 0, 0]
        self.crear = crear
        self.dni = dni
        self.nombre = nombre
        self.apellido = apellido

    def create_client(self):
        self.master.treeview.insert(
            parent='', index='end', iid=self.dni.get(),
            values=(self.dni.get(), self.nombre.get(), self.apellido.get()))
        db.Clientes.crear(self.dni.get(), self.nombre.get(), self.apellido.get())
        self.close()

    #Botón de cerrar dentro de la pantalla crear
    def close(self):
        self.destroy()
        self.update()
        
    #Verificar con color rojo o negro si es correcto
    def validate(self, event, index):
        valor = event.widget.get()
        # Validar como dni si es el primer campo o textual para los otros dos
        valido = helpers.dni_valido(valor, db.Clientes.lista) if index == 0 \
            else (valor.isalpha() and len(valor) >= 2 and len(valor) <= 30)
        event.widget.configure({"bg": "Green" if valido else "Red"})

        #Cambiar el estado e validación :)
        self.validaciones[index] = valido
        self.crear.config(state=NORMAL if self.validaciones == [1,1,1] else DISABLED)
        
class EditClientWindow(Toplevel, CenterWidgetMixin):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Actualizar cliente')
        self.build()
        self.center()
        # Obliga al usuario a interactuar con la subventana
        self.transient(parent)
        self.grab_set()

    def build(self):
        
        #Pantalla
        frame = Frame(self)
        frame.pack(padx=20, pady=10)

        #Textos de las opciones
        Label(frame, text="DNI (No editable)").grid(row=0, column=0)
        Label(frame, text="Nombre (2 a 30 chars)").grid(row=0, column=1)
        Label(frame, text="Apellido (2 a 30 chars)").grid(row=0, column=2)

        #Entradas de info
        dni = Entry(frame)
        dni.grid(row=1, column=0)
        nombre = Entry(frame)
        nombre.grid(row=1, column=1)
        nombre.bind("<KeyRelease>", lambda event: self.validate(event, 0))
        apellido = Entry(frame)
        apellido.grid(row=1, column=2)
        apellido.bind("<KeyRelease>", lambda event: self.validate(event, 1))

        #Ingresar info a los campos de entrada
        cliente = self.master.treeview.focus()
        campos = self.master.treeview.item(cliente, 'values')
        dni.insert(0, campos[0])
        dni.config(state=DISABLED) #Para que no pueda cambiar
        nombre.insert(0, campos[1])
        apellido.insert(0, campos[2])

        frame = Frame(self)
        frame.pack(pady=10)

        #Botónes
        actualizar = Button(frame, text="Actualizar", command=self.edit_client)
        actualizar.grid(row=0, column=0)
        Button(frame, text="Cancelar", command=self.close).grid(row=0, column=1)

        #Referencia de validación
        self.validaciones = [1, 1]  # True, True

        #Exportar
        self.actualizar = actualizar
        self.dni = dni
        self.nombre = nombre
        self.apellido = apellido

    #Función para validar
    def validate(self, event, index):
        valor = event.widget.get()
        valido = (valor.isalpha() and len(valor) >= 2 and len(valor) <= 30)
        event.widget.configure({"bg": "Green" if valido else "Red"})
        # Cambiar estado del botón en base a las validaciones
        self.validaciones[index] = valido
        self.actualizar.config(state=NORMAL if self.validaciones == [1, 1] else DISABLED)

    def edit_client(self):
        cliente = self.master.treeview.focus() #Seleccionar
        self.master.treeview.item(cliente, values=(self.dni.get(), self.nombre.get(), self.apellido.get()))
        db.Clientes.modificar(self.dni.get(), self.nombre.get(), self.apellido.get())
        
    def close(self):
        self.destroy()
        self.update()


#Creamos una clase para la pantalla
class MainWindow(Tk):
    def __init__(self):
        super().__init__()
        self.title('Gestor de clientes')
        self.build()
        
    def build(self):
        frame = Frame(self)
        frame.pack()

        #Treeview es una librería que funciona para representar en tablas
        treeview = ttk.Treeview(frame)
        treeview['columns'] = ('DNI', 'Nombre', 'Apellido' )
        
        #Establecer valores columnas
        treeview.column('#0', width=0, stretch=NO)
        treeview.column('DNI', anchor=CENTER)
        treeview.column('Nombre', anchor=CENTER)
        treeview.column('Apellido', anchor=CENTER)
        
        #Titulo de las columnas de las tablas
        treeview.heading('DNI', text='DNI', anchor=CENTER)
        treeview.heading('Nombre', text='Nombre', anchor=CENTER)
        treeview.heading('Apellido', text='Apellido', anchor=CENTER)
        
        #Hacemos el scrollbar, la ruedita que sube y baja
        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        treeview['yscrollcommand'] = scrollbar.set
        
        #Agregamos los clientes del archivo csv
        for cliente in db.Clientes.lista:
            treeview.insert(
                parent='', index='end', iid=cliente.dni,
                values=(cliente.dni, cliente.nombre, cliente.apellido))
        
        treeview.pack()
        
        frame = Frame(self)
        frame.pack(pady=20)
        
        #Botónes de para editar usuarios
        Button(frame, text='Crear', command=self.create).grid(row=0, column=0)
        Button(frame, text='Modificar', command=self.edit).grid(row=0, column=1)
        Button(frame, text='Borrar', command=self.delete).grid(row=0, column=2)
        
        self.treeview = treeview
        
    #Hacemos la función del botón de borrar
    def delete(self):
        cliente = self.treeview.focus()
        if cliente:
            campos = self.treeview.item(cliente, 'values')
            confirmar = askokcancel(
                title='Confirmación',
                message=f'¿Borrar a {campos[1]} {campos[2]}?',
                icon=WARNING)
            if confirmar:
                #Eliminamos el usuario
                self.treeview.delete(cliente)
                db.Clientes.borrar(campos[0])
                
            
    def create(self):
        CreateClientWindow(self)

    def edit(self):
        if self.treeview.focus(): #Comprobar selección 
            EditClientWindow(self)
    
#Corremos el programa
if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()