Web VPython 3.2

scene.range = 10
scene.autoscale = False
scene.userspin = False

restart = False
paused = False
angles = 0
freq = 10

dl = 0.01
dt = 0.01

#for modeling purposes and simplicity, these constants will be set to 1
c = 1 #speed of light
m = 1 #electron mass
h = 1 #planks constant
r = 1 # electron radius

#wave packet form
def dsine(x, freq, phase, dis):
    return exp(-(x**2)) * sin(freq * (x - dis + phase))
    
    
def kn_rejacc(Ei): #rejection acceptance method since the pdf is univertible
    g = Ei / (m*c**2) #photon energy per electron rest mass
    def diff_cross(x):
        l_ratio = 1 / (1 + g * (1 - x))#x = cos (theta), change of variables for simplicity, l_ratio is the ration of the incident and outgoing photon wavelengths
        f = (
            0.5 * r**2 * l_ratio**2 * 
            (l_ratio + 1 / l_ratio - (1 - x**2))
            )
        return f 
        
    def get_max(): #finding the maximum value of the distribution for the envelope
        domain = [(i - 50) / 50 for i in range(101)]
        maximum = 0
        for i in domain:
            if diff_cross(i) > maximum:
                maximum = diff_cross(i)
        return maximum
    
    env = get_max() * 1.2 #envelope to bound distribution
    samplex = random() * 2 - 1
    sampley = random()
    while sampley > diff_cross(samplex) / env:
        samplex = random() * 2 - 1
        sampley = random()
#    if random() > 0.5:
#        return acos(samplex)
#    else: 
#        return -acos(samplex)
    return acos(samplex)
    
    

class photon:
    def __init__(self, wlength, ipos, theta):
        self.wlength = wlength
        self.theta = theta
        self.ipos = ipos
        self.localtime = 0 #since photons travel in a straight line from initial position, local time must be reset after every collision
        self.freq = c / wlength
        self.dir = rotate(vec(1,0,0), angle = self.theta, axis = vec(0,0,1))
        self.E_i = h * self.freq
    
    def create_photon(self): #create photons based on initial angle and displacement
        self.curv = curve(color=vec(1-self.freq / 20,0,self.freq / 20))
        for i in range(400):
            dx = (i - 200) * dl
            y = dsine(dx, self.freq, 0, self.ipos.x)
            rotated = rotate(vec(dx, y, 0), angle = diff_angle(self.dir,vec(1,0,0)), axis = vec(0,0,1))
            self.curv.append(pos = rotated + self.ipos)
        self.pos = vec(self.ipos.x, self.ipos.y, 0)

    def photon_step(self):
        for i in range(self.curv.npoints):
            self.curv.color = vec(1-self.freq / 20,0,self.freq / 20)
            dx = (i - 200) * dl
            t = self.localtime * c    
            y = dsine(dx, self.freq, t, 0)
            pos = rotate(vec(dx + t, y, 0), angle = diff_angle(self.dir,vec(1,0,0)), axis = vec(0,0,1)) + self.ipos
            self.curv.modify(i, pos = pos)
        self.localtime += dt
        self.pos += rotate(vec(1,0,0), angle = diff_angle(self.dir,vec(1,0,0)), axis = vec(0,0,1)) * dt
            
    def collision(self):#calculating energy and updating frequency and electron velocity from conservation of energy and momentum
        self.E_f = self.E_i / (1 + (self.E_i / (m * c**2)) * (1-cos(self.theta)))
        self.K = self.E_i - self.E_f
        self.lambda_i = self.wlength
        self.lambda_f = h /(m*c) * (1 - cos(self.theta)) + self.lambda_i #shift in wavelength
        self.freq = c/self.lambda_f
        self.wlength = self.lambda_f
        self.dir = rotate(self.dir, angle = self.theta, axis = vec(0,0,1))
        self.localtime = 0
        
        
class electron:
    def __init__(self, position, vel):
        self.position = position
        self.vel = vel
        self.hit = vec(1,0,0) # direction of collision
        self.p = vec(0,0,0)
        
    def create_electron(self):
        self.sphere = sphere(pos=self.position, radius=1, color=color.cyan)
        return self.sphere
        
    def electron_step(self):
        if mag(self.p) != 0:
            self.sphere.pos += mag(self.p) * c**2 / sqrt((mag(self.p) * c)**2 + (m*c**2)**2) * dt * norm(self.p)
            
    def collision(self, in_dir, out_dir, E_i, E_f): #electron direction from conservation of momentum
        p_i = E_i / c * norm(in_dir)
        p_f = E_f / c * norm(out_dir)
        p_e = p_i - p_f
        #self.hit = norm(p_e)
        self.p += p_e 
 
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
    p = photon(c/freq, vec(-10, 2*(i - 5), 0), 0)
    p.create_photon()
    photons.append(p)
    
#for i in range(1):
#    p = photon(0.08, vec(-10, -10, 0), pi/4)
#    p.create_photon()
#    photons.append(p)

        
# widgets
start = button(bind = run, text = 'run')
reset = button(bind = reset, text = 'reset')
pause = button(bind = pauser, text = 'pause')
#angle = slider(bind = change_angle, min = 0, max = 180, step = 1, value = angles)
#angle_text = wtext(text=f'{angles}\n')
frequency = slider(bind = change_freq, min = 1, max = 20, step = 1, value = freq)
frequency_text = wtext(text = f'{freq}\n')
click_text = wtext(text='Click on the canvas to place electrons, and then run')

def change_angle(evt):
    global angles 
    angles = evt.value
    angle_text.text = f'{angles}\n'
    
def change_freq(evt):
    global freq 
    freq = evt.value
    frequency_text.text = f'{freq}\n'
    
def reset():
    global restart
    global photons
    global electrons
    restart = True
    n = 0
    for phot in photons:
        phot.curv.clear()
        photons[n] = photon(c/freq, vec(-10, 2*(n - 5), 0), 0)
        photons[n].create_photon()
        n+=1
    for elect in electrons:
        elect.sphere.visible = False
        del elect
    electrons = []
        
def pauser():
    global paused
    paused = True

#histogram = 

def run():
    global paused
    paused = False
    while True:
        rate(1000)
        for phot in photons:
            phot.photon_step()
            for elect in electrons:
                distance_front = mag(phot.pos + phot.dir - elect.sphere.pos)  # detect a little in front of photon
                if distance_front < elect.sphere.radius: #detect collision with electron
                    
                    #store incoming direction, change angle based on distribution, 
                    #store outgoing direction and update energy and wavelength
                    in_dir = phot.dir
                    phot.theta = kn_rejacc(phot.E_i)
                    phot.collision()
                    out_dir = phot.dir
                   
                    #calculate electrons momentum from photon's momentum 
                    #then update the photon's internal time and initial position
                    elect.collision(in_dir, out_dir, phot.E_i, phot.E_f)
                    phot.ipos = elect.sphere.pos + phot.dir # so we don't get repeated collisions we start it a little forward
                    phot.pos = vec(phot.ipos.x, phot.ipos.y, 0)
                    phot.freq = c / phot.lambda_f
                    phot.E_i = h * phot.freq
        for elec in electrons:
            elec.electron_step() 
        if restart == True:
            restart = False
            break
        if paused == True:
            break
        

