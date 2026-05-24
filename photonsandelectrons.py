Web VPython 3.2

scene.range = 10
scene.autoscale = False
scene.userrotate = False

dl = 0.01
dt = 0.01
c = 1

def cot(n):
    return 1 / tan(n)
    
m = 1
h = 1

class photon:
    def __init__(self, wlength, init_d, theta):
        self.wlength = wlength
        self.init_d = init_d
        self.theta = theta
    
    def create_photon(self):
        self.curv = curve(color=vec(1,0,0))
        self.freq = c / self.wlength
        for i in range(400):
            dx = (i - 200) * dl
            self.curv.append(pos=vector(dx-10,exp(-((dx)**2)) * sin(self.freq * dx) + self.init_d, 0))
        return self.curv
    
    def photon_step(self, n):
        for i in range(self.curv.npoints):
            dx = (i - 200) * dl
            self.curv.modify(i, pos = vec(dx - 10 + n * c * dt, exp(-((dx)**2)) * sin(self.freq * (dx - self.init_d + n * c * dt)) + self.init_d,0))
            self.center = self.curv.point(self.curv.npoints-1).pos.x
            self.y = self.curv.point(0).pos.y
            
class electron:
    def __init__(self, position, vel, phi):
        self.position = position
        self.vel = vel
        self.phi = phi
        
    def create_electron(self):
        self.sphere = sphere(pos=self.position, radius=0.5, color=color.cyan)
        return self.sphere
        
    def electron_step(self):
        electron.pos += vec(abs(cos(phi)), - abs(sin(phi)),0) * self.vel * dt 
        
electrons = []
for i in range(5):
    e = electron(vec(i - 5, 2*(i - 5), 0), 0, 0)
    e.create_electron()
    electrons.append(e)
    
for i in range(5):
    e = electron(vec(i + 5, 2*(i)+0.4, 0), 0, 0)
    e.create_electron()
    electrons.append(e)
            
photons = []
for i in range(10):
    p = photon(0.04 * i, 2*(i - 5))
    p.create_photon()
    photons.append(p)   
    
n = 0
while True:
    rate(1000)
    for phot in photons:
        phot.photon_step(n)
        for elect in electrons:
            distance = ((phot.center - elect.sphere.pos.x)**2 + (phot.y - elect.sphere.pos.y)**2)**0.5
            if distance < elect.sphere.radius :
                phot.curv.clear()
      
    n+=1
    