import microbit as mb

STANNA = 0
FRAMÅT = 1
BAKÅT = 2
HÖGER = 1
VÄNSTER = 2


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


def sp(pin, val):
    if pin.read_digital() != val:
        pin.write_digital(val)


def motsatt_sida(sväng):
    return VÄNSTER if sväng == HÖGER else VÄNSTER


nuvarande = Inställningar()


def flytta(ins):
    nuvarande.sätt_från_annan(ins)
    if ins.riktning == FRAMÅT:
        sp(mb.pin13, 1)
        sp(mb.pin14, 0)
    elif ins.riktning == BAKÅT:
        sp(mb.pin13, 0)
        sp(mb.pin14, 1)
    else:
        sp(mb.pin13, 0)
        sp(mb.pin14, 0)
    if ins.sväng == HÖGER:
        sp(mb.pin15, 0)
        sp(mb.pin16, 1)
    elif ins.sväng == VÄNSTER:
        sp(mb.pin15, 1)
        sp(mb.pin16, 0)
    else:
        sp(mb.pin15, 0)
        sp(mb.pin16, 0)


class Öga:
    def __init__(self, pin, sida):
        self.pin = pin
        self.sida = sida
        self.minst = 1023
        self.senast = 0
        self.dold_multi = 1
        self.uppdatera()

    def uppdatera(self):
        self.senast = max(self.pin.read_analog(), 1)
        self.minst = min(self.minst, self.senast)
        self.dold_multi = self.senast / self.minst


höger = Öga(mb.pin1, HÖGER)
vänster = Öga(mb.pin2, VÄNSTER)
MIN_DOLD = 0.05
MIN_DOLD_MULTI = 3  # hur mycket mer ett öga måste ha jämfört med min för att börja svänga
MIN_DIFF = 1.2  # minsta skillnad mellan vänster/höger för att börja svänga
KRASCH_TID_MÄTNING = 1000
KRASCH_FAKTOR = 1.2
TID_TILL_ÄNDRING = 300
TID_TILL_SLUTA_RÄDDNING = 2000


def hitta_mest_dolda():
    dold_max = max(höger.dold_multi, vänster.dold_multi)
    mest = max(höger.senast, vänster.senast)
    minst = min(höger.senast, vänster.senast)
    if max(mest, 1) / max(minst, 1) < MIN_DIFF and dold_max < MIN_DOLD_MULTI:
        return None
    return höger if höger.senast > vänster.senast else vänster


class KraschHanterare:
    def __init__(self):
        self.arr = []
        #self.in_slot = 0
        self.minimum = -1
        self.kraschar = False

    def reset(self):
        self.arr.clear()
        self.in_slot = 0
        self.minimum = -1
        self.kraschar = False

    def uppdatera(self, tid):
        if nuvarande.riktning != FRAMÅT or nuvarande.sväng != STANNA:  # använd bara när vi går rakt framåt
            self.reset()
            return
        val = abs(mb.accelerometer.get_z())
        if len(self.arr) != 0 and self.arr[-1][1] // 100 == tid // 100:
            self.arr[-1] = ((self.arr[-1][0] * self.in_slot + val) / (self.in_slot + 1), tid)
            return
        self.arr.append((val, tid))
        self.in_slot = 1
        fullt = False
        while tid - self.arr[0][1] > KRASCH_TID_MÄTNING:
            self.arr.pop(0)
            fullt = True
        if not fullt:
            return
        nu = self.genomsnitt()
        self.minimum = nu if self.minimum == -1 else min(nu, self.minimum)
        if nu / max(self.minimum, 1) > KRASCH_FAKTOR:
            self.kraschar = True

    def genomsnitt(self):
        totalt = 0
        for _, element in enumerate(self.arr):
            totalt += element[0]
        return totalt / len(self.arr)


def hummux():
    är_startat = False
    mb.pin12.write_digital(1)
    inställning_tid = 0
    senaste_inställningarna = Inställningar()
    nya_inställningar = Inställningar()
    stå_still = False
    till_ändring = TID_TILL_ÄNDRING
    räddning_håll = VÄNSTER
    kraschen = KraschHanterare()
    while True:
        if mb.button_a.was_pressed():
            är_startat = not är_startat
            stå_still = False
        if mb.button_b.was_pressed():
            är_startat = not är_startat
            stå_still = True
        if not är_startat:
            mb.display.show(mb.Image.SAD)
            senaste_inställningarna.sätt(STANNA, STANNA)
            flytta(senaste_inställningarna)
            inställning_tid = 0
            till_ändring = TID_TILL_ÄNDRING
            kraschen.reset()
            continue
        tiden = mb.running_time()
        höger.uppdatera()
        vänster.uppdatera()
        nya_inställningar.sätt(FRAMÅT, STANNA)
        mest_dolda = hitta_mest_dolda()
        kraschen.uppdatera(tiden)

        if mest_dolda is not None:
            nya_inställningar.sväng = motsatt_sida(mest_dolda.sida)
        if kraschen.kraschar:
            nya_inställningar.sätt(BAKÅT, räddning_håll)
            senaste_inställningarna.sätt_från_annan(nya_inställningar)
            inställning_tid = 0
            till_ändring = TID_TILL_SLUTA_RÄDDNING
            räddning_håll = motsatt_sida(räddning_håll)  # byt håll nästa gång

        if nya_inställningar.är_samma(senaste_inställningarna):
            if tiden - inställning_tid > till_ändring:
                if not stå_still:
                    flytta(nya_inställningar)
                mb.display.show(nya_inställningar.bild())
        else:
            inställning_tid = tiden
            senaste_inställningarna.sätt_från_annan(nya_inställningar)


hummux()
