import microbit as mb

STANNA = 0
FRAMMÅT = 1
BAKÅT = 2
HÖGER = 1
VÄNSTER = 2


def set_pin(pin, val):
    if pin.read_digital() != val:
        pin.write_digital(val)


def flytta(riktning, sväng):
    if riktning == FRAMMÅT or riktning == BAKÅT:
        if mb.pin8.read_digital():
            if riktning == FRAMMÅT:
                set_pin(mb.pin13, 1)
                set_pin(mb.pin14, 0)
            else:
                set_pin(mb.pin13, 0)
                set_pin(mb.pin14, 1)
    else:
        set_pin(mb.pin13, 0)
        set_pin(mb.pin14, 0)
    if sväng == HÖGER:
        set_pin(mb.pin15, 0)
        set_pin(mb.pin16, 1)
    elif sväng == VÄNSTER:
        set_pin(mb.pin15, 1)
        set_pin(mb.pin16, 0)
    else:
        set_pin(mb.pin15, 0)
        set_pin(mb.pin16, 0)


ögon = []


class Öga:
    def __init__(self, pin, sida):
        self.pin = pin
        self.sida = sida
        self.mest = 0
        self.minst = 1023
        self.senast = 0
        self.förändring = 0
        self.boost = 0
        self.dold_ökning = 0
        self.dold_multi = 1
        if sida == HÖGER:
            self.andra_sidan = VÄNSTER
        else:
            self.andra_sidan = HÖGER
        self.uppdatera_värde()

    def andra_ögat(self):
        return ögon[1] if self.sida == HÖGER else ögon[0]

    def uppdatera_värde(self):
        self.senast = max(self.pin.read_analog(), 1)
        self.mest = max(self.mest, self.senast)
        self.minst = min(self.minst, self.senast)
        self.boost = self.senast - self.minst
        self.dold_multi = self.senast / self.minst

    def uppdatera(self):
        innan = self.senast
        self.uppdatera_värde()
        self.förändring = self.senast - innan
        if self.förändring > 0:
            self.dold_ökning = self.förändring / innan
        else:
            self.dold_ökning = 0


höger = Öga(mb.pin1, HÖGER)
vänster = Öga(mb.pin2, VÄNSTER)
ögon = [höger, vänster]
MIN_DOLD = 0.05
MIN_DOLD_MULTI = 3  # hur mycket mer ett öga måste ha jämfört med min för att börja svänga
MIN_DIFF = 1.2  # minsta skillnad mellan vänster/höger för att börja svänga
KRASCH_TID_MÄTNING = 1000


def hitta_mest_dolda():
    # if höger.senast == vänster.senast:
    #    return None
    # return höger if höger.senast > vänster.senast else vänster

    dold_max = max(höger.dold_multi, vänster.dold_multi)
    mest = max(höger.senast, vänster.senast)
    minst = min(höger.senast, vänster.senast)
    if max(mest, 1) / max(minst, 1) < MIN_DIFF and dold_max < MIN_DOLD_MULTI:
        #    if höger.dold_ökning >= MIN_DOLD or vänster.dold_ökning >= MIN_DOLD:
        #        return höger if höger.dold_ökning > vänster.dold_ökning else vänster
        return None
    return höger if höger.senast > vänster.senast else vänster


class Inställningar:
    def __init__(self):
        self.riktning = STANNA
        self.sväng = STANNA

    def sätt(self, riktning, sväng):
        self.riktning = riktning
        self.sväng = sväng

    def sätt_från_annan(self, annan):
        self.sätt(annan.riktning, annan.sväng)

    def är_samma(self, annan):
        return self.riktning == annan.riktning and self.sväng == annan.sväng

    def bild(self):
        if self.sväng == HÖGER:
            return mb.Image.ARROW_W
        if self.sväng == VÄNSTER:
            return mb.Image.ARROW_E
        return mb.Image.HEART


class KraschHanterare:
    def __init__(self):
        self.arr = []
        self.in_slot = 0;

    def uppdatera(self, tid):
        val = mb.accelerometer.get_y()
        if len(self.arr) != 0 and self.arr[-1][1] // 100 == tid // 100:
            self.arr[-1] = ((self.arr[-1][0] * self.in_slot + val) / (self.in_slot + 1), tid)
            return
        self.arr.append((val, tid))
        while tid - self.arr[0][1] > KRASCH_TID_MÄTNING:
            self.arr.pop(0)

    def genomsnitt(self):
        totalt = 0
        for _, element in enumerate(self.arr):
            totalt += element[0]
        return totalt / len(self.arr)

    def krashar(self):
        return False


def sätt_pixlar(hur_många):
    for n in range(25):
        mb.display.set_pixel(n % 5, n // 5, 9 if n < hur_många else 0)


def hummux():
    är_startat = False
    mb.pin12.write_digital(1)
    # pin12.write_analog(1023)
    inställning_tid = 0
    senaste_inställningarna = Inställningar()
    nya_inställningar = Inställningar()
    stå_still = False
    krashen = KraschHanterare()
    while True:
        if mb.button_a.was_pressed():
            är_startat = not är_startat
            stå_still = False
        if mb.button_b.was_pressed():
            är_startat = not är_startat
            stå_still = True
        if not är_startat:
            mb.display.show(mb.Image.SAD)
            flytta(STANNA, STANNA)
            inställning_tid = 0
            continue
        tiden = mb.running_time()
        höger.uppdatera()
        vänster.uppdatera()
        sväng = STANNA
        riktning = FRAMMÅT
        mest_dolda = hitta_mest_dolda()
        krashen.uppdatera(tiden)
        # sätt_pixlar(krashen.genomsnitt() // 10)
        if mest_dolda is not None:
            sväng = mest_dolda.andra_sidan
        nya_inställningar.sätt(riktning, sväng)
        # sätt_pixlar((tiden // 100) % 26)
        if nya_inställningar.är_samma(senaste_inställningarna):
            if tiden - inställning_tid > 300:
                if not stå_still:
                    flytta(nya_inställningar.riktning, nya_inställningar.sväng)
                # mb.display.show(nya_inställningar.bild())
        else:
            inställning_tid = tiden
            senaste_inställningarna.sätt_från_annan(nya_inställningar)


hummux()
# test()
