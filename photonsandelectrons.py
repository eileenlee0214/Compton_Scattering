Web VPython 3.2

restart = False
scene.range = 10
scene.autoscale = False
scene.userrotate = False
angles = 67

dl = 0.01
dt = 0.01
c = 1

def cot(n):
    return 1 / tan(n)
 
#wave packet form
def dsine(x, freq, phase, dis):
    return exp(-(x**2)) * sin(freq * (x - dis + phase))
    
m = 1
h = 1

class photon:
    def __init__(self, wlength, ipos, theta):
        self.wlength = wlength
        self.theta = theta
        self.ipos = ipos
        self.localtime = 0
        self.freq = c / wlength
    
    def create_photon(self):
        self.curv = curve(color=vec(1,0,0))
        for i in range(400):
            dx = (i - 200) * dl
            y = dsine(dx, self.freq, 0, self.ipos.x)
            pos = rotate(vec(dx, y, 0), angle = self.theta, axis = vec(0,0,1)) + self.ipos
            self.curv.append(pos = pos)
        self.pos = vec(self.ipos.x, self.ipos.y, 0)
        return self.curv
    
    def photon_step(self):
        for i in range(self.curv.npoints):
            dx = (i - 200) * dl
            t = self.localtime * c    
            y = dsine(dx, self.freq, t, 0)
            pos = rotate(vec(dx + t, y, 0), angle = self.theta, axis = vec(0,0,1)) + self.ipos
            self.curv.modify(i, pos = pos)
        self.localtime += dt
        self.pos += rotate(vec(1,0,0), angle = self.theta, axis = vec(0,0,1)) * dt
            
    def collision(self):#calculating energy and updating frequency and electron velocity
        self.E_i = h * self.freq
        self.E_f = self.E_i / (1 + (self.E_i / (m * c**2)) * (1-cos(self.theta)))
        self.K = self.E_i - self.E_f
        self.v_e = c * sqrt(1 - 1/(1 + self.K/(m*c**2)**2)) #electron deflected velocity
        self.lambda_i = self.wlength
        self.lambda_f = h /(m*c) * (1 - cos(self.theta)) + self.lambda_i
        self.freq = c/self.lambda_f
        self.wlength = self.lambda_f
        
class electron:
    def __init__(self, position, vel, phi):
        self.position = position
        self.vel = vel
        self.phi = phi
        
    def create_electron(self):
        self.sphere = sphere(pos=self.position, radius=0.5, color=color.cyan)
        return self.sphere
        
    def electron_step(self):
        if self.vel != 0:
            self.sphere.pos += vec(abs(cos(self.phi)), - abs(sin(self.phi)),0) * self.vel * dt 
        
    def find_phi(self, theta, E_i):
        if theta == 0 or theta == pi:
            return 0
        else:
            def f(phi):
                return cot(phi) - (1 + E_i / (m*c**2)) * (sin(theta) / (1 + cos(theta)))
            phi = 1.0
            
            #newtons method
            for i in range(20):
                h = 0.0001
                df = (f(phi + h) - f(phi - h)) / (2*h)
                phi -= f(phi)/df
            self.phi = phi
 
#making electrons
electrons = []

scene.bind('click', click_electron)

def click_electron(evt):
    e = electron(vec(evt.pos.x, evt.pos.y, 0), 0, 0)
    e.create_electron()
    electrons.append(e)


#making test photons
photons = []
for i in range(10):
    p = photon(0.08, vec(-10, 2*(i - 5), 0), 0)
    p.create_photon()
    photons.append(p)

        
# widgets
start = button(bind = run, text = 'run')
reset = button(bind = reset, text = 'reset')
angle = slider(bind = change_angle, min = 0, max = 180, step = 1, value = angles)
angle_text = wtext(text=f'{angles}\n')

def change_angle(evt):
    global angles 
    angles = evt.value
    angle_text.text = f'{angles}\n'
    
def reset():
    global restart
    global photons
    restart = True
    n = 0
    for phot in photons:
        phot.curv.clear()
        photons[n] = photon(0.08, vec(-10, 2*(n - 5), 0), 0)
        photons[n].create_photon()
        n+=1
    for elect in electrons:
        elect.sphere.visible = False
        del elect
        

def run():
    while True:
        rate(1000)
        for phot in photons:
            phot.photon_step()
            for elect in electrons:
                distance = mag(phot.pos + vec(100 * dl, 0, 0) - elect.sphere.pos)  
                if distance < elect.sphere.radius: #detect collision with electron
                    phot.theta += angles * pi / 180
                    phot.collision()
                    phot.localtime = 0
                    phot.ipos = elect.sphere.pos 
                    elect.vel = phot.v_e
                    elect.find_phi(phot.theta, phot.E_i)
                    phot.freq = c / phot.lambda_f
        for elec in electrons:
            elec.electron_step() 
        if restart == True:
            restart = False
            break
