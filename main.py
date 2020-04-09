import sys #Para usar exit()
import time #Para usar sleep()
import pygame

ancho = 640
alto = 480
color_azul = (0, 0, 64) #Color azul para el fondo
color_blanco = (255, 255, 255) #Color blanco

class Escena:
    def __init__(self):
        "Inicialización"
        self.proximaEscena = False
        self.jugando = True
    def leer_eventos(self, eventos):
        "Lee la lista de todos los eventos."
        pass
    def actualizar(self):
        "Cálculos y lógica."
        pass
    def dibujar(self, pantalla):
        "Dibuja los objetos en pantalla."
        pass
    def cambiar_escena(self, escena):
        "Selleciona la nueva escena a ser desplegada."
        self.proximaEscena = escena

class Director:
    def __init__(self, titulo = "", res = (ancho, alto)):
        pygame.init()
        #Inicializando la pantalla
        self.pantalla =  pygame.display.set_mode(res)
        #Configurar titulo de la pantalla
        pygame.display.set_caption(titulo)
        #Crear el reloj.
        self.reloj = pygame.time.Clock()
        self.escena = None
        self.escenas = {}

    def ejecutar(self, escena_inicial, fps = 60):
        self.escena = self.escenas[escena_inicial]
        jugando = True
        while jugando:
            self.reloj.tick(fps)
            eventos = pygame.event.get()
            #Revizar todos los eventos
            for evento in eventos:
                if evento.type == pygame.QUIT:
                    # cerrar el videojuego.
                    #jugando = False
                    sys.exit()

            self.escena.leer_eventos(eventos)
            self.escena.actualizar()
            self.escena.dibujar(self.pantalla)
            self.elegirEscena(self.escena.proximaEscena)

            if jugando:
                jugando = self.escena.jugando
            pygame.display.flip()

        time.sleep(2)
    def elegirEscena(self, proximaEscena):
        if proximaEscena:
            if proximaEscena not in self.escenas:
                self.agregarEscena(proximaEscena)
            self.escena = self.escenas[proximaEscena]
    def agregarEscena(self, escena):
        escenaClase = 'Escena'+escena
        escenaObj = globals()[escenaClase]
        self.escenas[escena] = escenaObj()

class EscenaNivel1(Escena):
    def __init__(self):
        Escena.__init__(self)
        self.bolita = Bolita()
        self.jugador = Paleta()
        self.muro = Muro(50)
        self.puntuacion = 0
        self.vidas = 3
        self.esperando_saque = True

        #Ajustar repeticion de evento de tecla presionada.
        pygame.key.set_repeat(30)#Retraso en milisegundos

    def leer_eventos(self, eventos):
        for evento in eventos:
            #Buscar eventos del teclado
            if evento.type == pygame.KEYDOWN:
                self.jugador.update(evento)
                if self.esperando_saque == True and evento.key == pygame.K_SPACE:
                    self.esperando_saque = False
                    if self.bolita.rect.centerx < ancho / 2:
                        self.bolita.speed = [3, -3]
                    else:
                        self.bolita.speed = [-3, -3]
    def actualizar(self):
        #Actualizar posicion de la bolita.
        if self.esperando_saque == False:
            self.bolita.update()
        else:
            self.bolita.rect.midbottom = self.jugador.rect.midtop

        #Colision entre bolita y jugador.
        if pygame.sprite.collide_rect(self.bolita, self.jugador):
            self.bolita.speed[1] = -self.bolita.speed[1]
        #Colision entre bolita y el muro
        lista = pygame.sprite.spritecollide(self.bolita, self.muro, False)
        if lista:
            ladrillo = lista[0]
            cx = self.bolita.rect.centerx
            if cx < ladrillo.rect.left or cx > ladrillo.rect.right:
                self.bolita.speed[0] = -self.bolita.speed[0]
            else:
                self.bolita.speed[1] = -self.bolita.speed[1]
            self.muro.remove(ladrillo)
            self.puntuacion += 10

        #Verificar si la bolita sale
        if self.bolita.rect.top > alto:
            self.vidas -= 1
            self.esperando_saque = True
        if self.vidas <= 0:
            self.cambiar_escena('JuegoTerminado')

    def dibujar(self, pantalla):
        #Poner el fondo de pantalla
        pantalla.fill(color_azul)

        #Mostrar puntuación.
        self.mostrar_puntuacion(pantalla)

        #Mostrar vidas.
        self.mostrar_vidas(pantalla)

        #Dibujar bolita en pantalla
        pantalla.blit(self.bolita.image, self.bolita.rect)

        #Dibujar jugador en pantalla
        pantalla.blit(self.jugador.image, self.jugador.rect)

        #Dibujar los ladrillos.
        self.muro.draw(pantalla)

    #Mostrar la puntuacion en pantalla.
    def mostrar_puntuacion(self, pantalla):
        fuente = pygame.font.SysFont('Consolas', 22)
        texto = fuente.render(str(self.puntuacion).zfill(5), True, (color_blanco))
        texto_rect = texto.get_rect()
        texto_rect.topleft = [0, 0]
        pantalla.blit(texto, texto_rect)

    #Mostrar las vidas en pantalla.
    def mostrar_vidas(self, pantalla):
        fuente = pygame.font.SysFont('Consolas', 22)
        cadena = "Vidas: " + str(self.vidas).zfill(2)
        texto = fuente.render(cadena, True, (color_blanco))
        texto_rect = texto.get_rect()
        texto_rect.topright = [ancho, 0]
        pantalla.blit(texto, texto_rect)

class EscenaJuegoTerminado(Escena):
    def actualizar(self):
        self.jugando = False

    def dibujar(self, pantalla):
        fuente = pygame.font.SysFont('Verdana', 72)
        texto = fuente.render('Game Over', True, (color_blanco))
        texto_rect = texto.get_rect()
        texto_rect.center = [ancho / 2, alto / 2]
        pantalla.blit(texto, texto_rect)

class Bolita(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #cargar Imagen de la bolita
        self.image = pygame.image.load('images/original.png')
        #Obtener rectangulo de la bolita
        self.rect = self.image.get_rect()
        #Posicion inicial de la bolita
        self.rect.centerx = ancho / 2
        self.rect.centery = alto / 2
        #Establecer velocodad inicial
        self.speed = [3, 3]

    def update(self):
        #Evitar que salga por debajo
        if self.rect.top <= 0:
            self.speed[1] = -self.speed[1]#Invertimos la velocidad cuando llegue hasta abajo de la pantalla
        #Evitar que salga por la derecha.
        elif self.rect.right >= ancho or self.rect.left <= 0:
            self.speed[0] = -self.speed[0]#Lo mismo que arriba.
        #Mover en base a su posicion actual y velocidad.
        self.rect.move_ip(self.speed)

class Paleta(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #cargar Imagen de la bolita
        self.image = pygame.image.load('images/paleta.png')
        #Obtener rectangulo de la bolita
        self.rect = self.image.get_rect()
        #Posicion inicial centrada en pantalla en X
        self.rect.midbottom = (ancho / 2, alto - 20)
        #Estblecer velocodad inicial
        self.speed = [0, 0]

    def update(self, evento):
        #Buscar si se presiono la tecla izquierda.
        if evento.key == pygame.K_LEFT and self.rect.left > 0:
            self.speed = [-10, 0]
        #Si se presiona la tecla derecha.
        elif evento.key == pygame.K_RIGHT and self.rect.right < ancho:
            self.speed = [10, 0]
        else:
            self.speed = [0, 0]
        #Mover en base a su posicion actual y velocidad.
        self.rect.move_ip(self.speed)

class Ladrillo(pygame.sprite.Sprite):
    def __init__(self, posicion):
        pygame.sprite.Sprite.__init__(self)
        #cargar Imagen de la bolita
        self.image = pygame.image.load('images/ladrillo.png')
        #Obtener rectangulo del ladrillo
        self.rect = self.image.get_rect()
        #Posicion Inicial, provista externamente.
        self.rect.topleft = posicion

class Muro(pygame.sprite.Group):
    def __init__(self, cantidadLadrillos):
        pygame.sprite.Group.__init__(self)
        pos_x = 0
        pos_y = 20
        for i in range(cantidadLadrillos):
            ladrillo = Ladrillo((pos_x, pos_y))
            self.add(ladrillo)

            #Con esto se acomoda los ladrillos.
            pos_x += ladrillo.rect.width
            if pos_x >= ancho:
                pos_x = 0
                pos_y += ladrillo.rect.height

director = Director('Juego de Ladrillos', (ancho, alto))
director.agregarEscena('Nivel1')
director.ejecutar('Nivel1')