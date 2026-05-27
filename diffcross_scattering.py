Web VPython 3.2

restart = False
paused = False
scene.range = 10
scene.autoscale = False
scene.userrotate = False
angles = 67

dl = 0.01
dt = 0.01

#for modeling purposes and simplicity, these constants will be set to 1
c = 1
m = 1 
h = 1
r = 1 # electron radius


def cot(n):
    return 1 / tan(n)
 
#wave packet form
def dsine(x, freq, phase, dis):
    return exp(-(x**2)) * sin(freq * (x - dis + phase))
    
#probability of scattering from Klein Nishina Differential Cross Section
def kn_pdf(Ei):
    s_t = 8 * pi * (r**2)/ 3 
    g = Ei / (m*c**2)
    def diff_cross(x):
        l_ratio = 1 / (1 + g * (1 - x))#x = cos (theta), change of variables for simplicity, l_ratio is the ration of the incident and outgoing photon wavelengths
        f = (
            0.5 * r**2 * l_ratio**2 * 
            (l_ratio + 1 / l_ratio - (1 - x**2))
            )
        return f 
    print(diff_cross(0))
    total_cross = (
        0.75 * s_t
        * (
            (1/g)
             * (1 - ((2 * g + 1) / g**2))
             * log(1 + 2 * g)
             + 0.5 + (4 / g)
             - (1 / (2 * (1 + 2 * g)**2))
             )
        )
    def pdf(x):
        return 2 * pi * diff_cross(x) / total_cross 
    print(pdf(0))
    #newton's method on CDF + Prob = 0, this isn't right actually because I used pdf not cdf
    prob = random()
    x = (1 + 1 / (1 + 2 * g))/2
    h = 0.001
    for i in range(20):
        f = pdf(x) - prob
        df = (pdf(x + h) - pdf(x - h)) / (2 * h)
        x -= f / df
        x = max(-1, min(1, x))
    print(acos(x))
    return acos(x)
    
    
def kn_rejacc(Ei):
    s_t = 8 * pi * (r**2)/ 3 
    g = Ei / (m*c**2)
    def diff_cross(x):
        l_ratio = 1 / (1 + g * (1 - x))#x = cos (theta), change of variables for simplicity, l_ratio is the ration of the incident and outgoing photon wavelengths
        f = (
            0.5 * r**2 * l_ratio**2 * 
            (l_ratio + 1 / l_ratio - (1 - x**2))
            )
        return f 
    total_cross = (
        0.75 * s_t
        * (
            (1/g)
             * (1 - ((2 * g + 1) / g**2))
             * log(1 + 2 * g)
             + 0.5 + (4 / g)
             - (1 / (2 * (1 + 2 * g)**2))
             )
        )
    def pdf(x):
        return 2 * pi * diff_cross(x) / total_cross 
        
    g = pdf(1)
    samplex = random() * 2 - 1
    sampley = random()
    while sampley > pdf(samplex) / g:
        samplex = random() * 2 - 1
        sample = samplex * g
        sampley = random()
    #if random() > 0.5:
        #return acos(samplex)
    #else: 
        #return -acos(samplex)
    return acos(samplex)
    
    


class photon:
    def __init__(self, wlength, ipos, theta):
        self.wlength = wlength
        self.theta = theta
        self.ipos = ipos
        self.localtime = 0
        self.freq = c / wlength
        self.dir = rotate(vec(1,0,0), angle = self.theta, axis = vec(0,0,1))
        self.E_i = h * self.freq
    
    def create_photon(self): #create photons based on initial angle and displacement
        self.curv = curve(color=vec(1,1,0))
        for i in range(400):
            dx = (i - 200) * dl
            y = dsine(dx, self.freq, 0, self.ipos.x)
            pos = rotate(vec(dx, y, 0), angle = diff_angle(self.dir,vec(1,0,0)), axis = vec(0,0,1)) + self.ipos
            self.curv.append(pos = pos)
        self.pos = vec(self.ipos.x, self.ipos.y, 0)
        return self.curv
    
    def photon_step(self):
        for i in range(self.curv.npoints):
            dx = (i - 200) * dl
            t = self.localtime * c    
            y = dsine(dx, self.freq, t, 0)
            pos = rotate(vec(dx + t, y, 0), angle = diff_angle(self.dir,vec(1,0,0)), axis = vec(0,0,1)) + self.ipos
            self.curv.modify(i, pos = pos)
        self.localtime += dt
        self.pos += rotate(vec(1,0,0), angle = diff_angle(self.dir,vec(1,0,0)), axis = vec(0,0,1)) * dt
        #spheree = sphere(pos = self.pos, radius = 0.1)
            
    def collision(self):#calculating energy and updating frequency and electron velocity from conservation of energy and momentum
        self.E_f = self.E_i / (1 + (self.E_i / (m * c**2)) * (1-cos(self.theta)))
        self.K = self.E_i - self.E_f
        self.v_e = c * sqrt(1 - 1/(1 + self.K/(m*c**2))**2) #electron deflected velocity
        self.lambda_i = self.wlength
        self.lambda_f = h /(m*c) * (1 - cos(self.theta)) + self.lambda_i
        self.freq = c/self.lambda_f
        self.wlength = self.lambda_f
        self.dir = rotate(self.dir, angle = self.theta, axis = vec(0,0,1))
        
        
class electron:
    def __init__(self, position, vel):
        self.position = position
        self.vel = vel
        self.hit = vec(1,0,0) # direction of collision
        
    def create_electron(self):
        self.sphere = sphere(pos=self.position, radius=1, color=color.cyan)
        return self.sphere
        
    def electron_step(self):
        if self.vel != 0:
            self.sphere.pos += self.hit * self.vel * dt
            
    def collision(self, in_dir, out_dir, E_i, E_f): #electron direction from conservation of momentum
        p_i = E_i / c * norm(in_dir)
        p_f = E_f / c * norm(out_dir)
        p_e = p_i - p_f
        self.hit = norm(p_e)
 
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
    p = photon(0.04, vec(-10, 2*(i - 5), 0), 0)
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
angle = slider(bind = change_angle, min = 0, max = 180, step = 1, value = angles)
angle_text = wtext(text=f'{angles}\n')
click_text = wtext(text='Click on the canvas to place electrons, and then run')

def change_angle(evt):
    global angles 
    angles = evt.value
    angle_text.text = f'{angles}\n'
    
def reset():
    global restart
    global photons
    global electrons
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
    electrons = []
        
def pauser():
    global paused
    paused = True

def run():
    global paused
    paused = False
    while True:
        rate(1000)
        for phot in photons:
            phot.photon_step()
            for elect in electrons:
                distance_front = mag(phot.pos + phot.dir - elect.sphere.pos)  # detect a little in front for symmetry when it leaves
                if distance_front < elect.sphere.radius: #detect collision with electron
                    in_dir = phot.dir
                    #phot.theta = angles * pi / 180
                    phot.theta = kn_rejacc(phot.E_i)
                    phot.collision()
                    out_dir = phot.dir
                    elect.collision(in_dir, out_dir, phot.E_i, phot.E_f)
                    phot.localtime = 0
                    phot.ipos = elect.sphere.pos + phot.dir # so we don't get repeated collisions we start it a little forward
                    phot.pos = vec(phot.ipos.x, phot.ipos.y, 0)
                    elect.vel = phot.v_e
                    phot.freq = c / phot.lambda_f
        for elec in electrons:
            elec.electron_step() 
        if restart == True:
            restart = False
            break
        if paused == True:
            break
