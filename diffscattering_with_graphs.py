Web VPython 3.2

scene.range = 10
scene.autoscale = False
scene.userspin = False

restart = False
paused = False
freq = 10

dl = 0.01
dt = 0.01

sum_K = 0
sum_Ei_curr = 0
init_Ei = 0

init_iM = 0
sum_M_curr = 0
sum_M = 0

#for modeling purposes and simplicity, these constants will be set to 1
c = 1 #speed of light
m = 1 #electron mass
h = 1 #planks constant
r = 1 # electron radius

energy_graph = graph(
    title = 'Conservation of Energy (E = hf)',
    xtitle = '???',
    ytitle = 'Energy (hf)',
    width = 450,
    height = 300,
    xmin = 0, xmax = 6,
    ymin = 0, ymax = 7,
    align = 'right'
)

bar_Ei   = gvbars(graph=energy_graph, delta=0.5, color=color.magenta,  label='initial energy of photon')
bar_Ef   = gvbars(graph=energy_graph, delta=0.5, color=color.purple,  label='final energy of photon')
bar_Ke   = gvbars(graph=energy_graph, delta=0.5, color=color.cyan,    label='kinetic energy of electron')
bar_Etot = gvbars(graph=energy_graph, delta=0.5, color=color.blue,   label='check')

def update_energy_graph(E_i, E_f, K):
    bar_Ei.plot(1, E_i)
    bar_Ef.plot(2, E_f)
    bar_Ke.plot(3, K)
    bar_Etot.plot(4, E_f + K) # should be equal to E_i ?
    energy_graph.ymax = max(E_i, E_f + K) * 1.5

update_energy_graph(h * (c / (c/freq)), 0, 0)

#===== momentum graph
momenta_graph = graph(
    title = 'Momentum',
    xtitle = '???',
    ytitle = 'momenta',
    width = 450,
    height = 300,
    xmin = 0, xmax = 5,
    ymin = -2, ymax = 2,
    align = 'right'
)

bar_iM   = gvbars(graph=momenta_graph, delta=0.5, color=color.magenta,  label='initial momentum of photon')
bar_fM   = gvbars(graph=momenta_graph, delta=0.5, color=color.purple,  label='final momentum of photon')
bar_eM   = gvbars(graph=momenta_graph, delta=0.5, color=color.cyan,    label='momentum of electron after collision')
bar_Mtot = gvbars(graph=momenta_graph, delta=0.5, color=color.blue,   label='check')

def update_momenta_graph(iM, fM, eM):
    bar_iM.plot(1, iM)
    bar_fM.plot(2, fM)
    bar_eM.plot(3, eM)
    bar_Mtot.plot(4, fM + eM) # should be equal to iM ?
    momenta_graph.ymax = max(iM, fM + eM) * 1.5

update_momenta_graph(h / (c/freq) , 0, 0) ## fix this to be momenta, not energy

## checks for the sum aren't working ?!?!?

# ======end

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
#        return -acos(samplex)
#    else: 
#        return -acos(samplex)
    return acos(samplex)
    
    

class photon:
    def __init__(self, wlength, ipos, theta):
        self.wlength = wlength
        self.theta = theta #initial angle from positive x-axis
        self.ipos = ipos #initial position
        self.localtime = 0 #since photons travel in a straight line from initial position, local time must be reset after every collision
        self.freq = c / wlength
        self.dir = rotate(vec(1,0,0), angle = self.theta, axis = vec(0,0,1))
        self.E_i = h * self.freq
        self.iM = h / self.wlength
    
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
            rotated = rotate(vec(dx + t, y, 0), angle = diff_angle(self.dir,vec(1,0,0)), axis = vec(0,0,1))
            self.curv.modify(i, pos = rotated + self.ipos)
        self.localtime += dt
        self.pos += rotate(vec(1,0,0), angle = diff_angle(self.dir,vec(1,0,0)), axis = vec(0,0,1)) * dt
            
    def collision(self):#calculating energy and updating frequency and electron velocity from conservation of energy and momentum
        self.E_f = self.E_i / (1 + (self.E_i / (m * c**2)) * (1-cos(self.theta)))
        self.K = self.E_i - self.E_f
        self.wlength += h /(m*c) * (1 - cos(self.theta))
        self.freq = c / self.wlength
        self.M = h / (self.wlength)
        self.dir = rotate(self.dir, angle = self.theta, axis = vec(0,0,1))
        self.localtime = 0
        
        
class electron:
    def __init__(self, position):
        self.position = position
        self.p = vec(0,0,0) #initial momentum
        
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
        self.p += p_e 
        
    def elec_collision(self, other):
        global attached_vec
        if attached_vec:
            print(self.sphere.momentum)
        n = norm(self.sphere.pos - other.sphere.pos) #normal vector
        p_self_n = dot(self.p, n)
        p_other_n = dot(other.p, n)
        J = 0.5 * 2 * (m * p_self_n - m * p_other_n) / (m + m) * n #impulse along normal vector, divided by two since double counted (SHOULD FIX)
        self.p -= J
        other.p += J
 
#making electrons
electrons = []

scene.bind('click', click_electron)

def click_electron(evt):
    e = electron(vec(evt.pos.x, evt.pos.y, 0))
    e.create_electron()
    electrons.append(e)


#making test photons
photons = []
for i in range(10):
    p = photon(c/freq, vec(-10, 2*(i - 5), 0), 0)
    p.create_photon()
    photons.append(p)
        
# widgets
start = button(bind = run, text = 'run')
reset = button(bind = reset, text = 'reset')
pause = button(bind = pauser, text = 'pause')
frequency = slider(bind = change_freq, min = 1, max = 20, step = 1, value = freq)
frequency_text = wtext(text = f'{freq}\n')
click_text = wtext(text='Click on the canvas to place electrons, and then run')

# checkbox, set mode
    
def change_freq(evt):
    global freq 
    freq = evt.value
    frequency_text.text = f'{freq}\n'
    
def reset():
    global restart
    global photons
    global electrons
    global sum_K
    global sum_Ei_curr
    global init_Ei 
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
    
    sum_K = 0
    sum_Ei_curr = 0
    init_Ei = 0
    
    init_iM = 0
    sum_M_curr = 0
    sum_M = 0
    
    bar_Ei.data   = []
    bar_Ef.data   = []
    bar_Ke.data   = []
    bar_Etot.data = []
    update_energy_graph(h * (c / (c/freq)), 0, 0)
    
    bar_iM.data   = []
    bar_fM.data   = []
    bar_eM.data   = []
    bar_Mtot.data = []
    update_momenta_graph(h / wlength, 0, 0) # fix this too
        
def pauser():
    global paused
    paused = True

def run():
    global paused
    global sum_K
    global sum_Ei_curr
    global init_Ei
    global init_iM
    global sum_M_curr
    global sum_M
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
                    
                    if init_Ei == 0:    # keep track of initial photon Ei if its first
                        init_Ei = phot.E_i
                        
                    if init_iM = 0:
                        init_iM = phot.iM
                    
                    phot.theta = kn_rejacc(phot.E_i)
                    phot.collision()
                    out_dir = phot.dir
                    
                    sum_K += phot.K
                    sum_Ei_curr = phot.E_f # keep track of all affected electrons
                    
                    ### momenta update
                    
                    sum_M += phot.M
                    sum_M_curr = phot.M
                    
                    
                    update_energy_graph(init_Ei, sum_Ei_curr, sum_K)
                    update_momenta_graph(init_iM, sum_M_curr, sum_M)
                   
                    #calculate electrons momentum from photon's momentum 
                    #then update the photon's internal time and initial position
                    elect.collision(in_dir, out_dir, phot.E_i, phot.E_f)
                    phot.ipos = elect.sphere.pos + phot.dir # so we don't get repeated collisions we start it a little forward
                    phot.pos = vec(phot.ipos.x, phot.ipos.y, 0)
                    phot.E_i = h * phot.freq
        for self in electrons:
            for other in electrons:
                if other is not self:
                    if mag(other.sphere.pos - self.sphere.pos) < 2 * self.sphere.radius:
                        self.elec_collision(other)
            self.electron_step()  
        if restart == True:
            restart = False
            break
        if paused == True:
            break