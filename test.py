import microbit as mb

STANNA = 0
FRAMÅT = mb.pin13
BAKÅT = mb.pin14
HÖGER = mb.pin16
VÄNSTER = mb.pin15
IM = mb.Image


class Inst:
    def __init__(self):
        self.sätt(STANNA, STANNA)

    def sätt(self, rik, sväng):
        self.rik = rik
        self.sväng = sväng

    def sätt_från_annan(self, annan):
        self.sätt(annan.rik, annan.sväng)

    def är_samma(self, annan):
        return self.rik == annan.rik and self.sväng == annan.sväng

    def bild(self):
        if self.rik == BAKÅT:
            return IM.NO
        if self.sväng == HÖGER:
            return IM.ARROW_W
        if self.sväng == VÄNSTER:
            return IM.ARROW_E
        return IM.HEART


def sp(val, pin):
    pin.write_digital(1 if val == pin else 0)


def motsatt_sida(sväng):
    return VÄNSTER if sväng == HÖGER else HÖGER


nuvarande = Inst()


def flytta(ins):
    nuvarande.sätt_från_annan(ins)
    sp(ins.rik, FRAMÅT)
    sp(ins.rik, BAKÅT)
    sp(ins.sväng, HÖGER)
    sp(ins.sväng, VÄNSTER)


class Öga:
    def __init__(self, pin, sida):
        self.pin = pin
        self.sida = sida
        self.minst = 1023
        self.up()

    def up(self):
        self.senast = max(self.pin.read_analog(), 1)
        self.minst = min(self.minst, self.senast)
        self.dold_multi = self.senast / self.minst


höger = Öga(mb.pin1, HÖGER)
vänster = Öga(mb.pin2, VÄNSTER)
MIN_DOLD = 0.05
MIN_DOLD_MULTI = 3  # hur mycket mer ett öga måste ha jämfört med min för att börja svänga
MIN_DIFF = 1.2  # minsta skillnad mellan vänster/höger för att börja svänga
KRASCH_TID_MÄTNING = 2000
KRASCH_FAKTOR = 1.8
TID_TILL_ÄNDRING = 300
TID_TILL_SLUTA_RÄDDNING = 500


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
        self.reset()

    def reset(self):
        self.arr.clear()
        self.in_slot = 0
        self.minimum = -1
        self.faktor = 0

    def up(self, tid):
        if nuvarande.rik != FRAMÅT or nuvarande.sväng != STANNA:  # använd bara när vi går rakt framåt
            self.reset()
            return
        val = abs(mb.accelerometer.get_z()) # max(-mb.accelerometer.get_z(), 0)
        if len(self.arr) != 0 and self.arr[-1][1] // 200 == tid // 200:
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
        self.faktor = nu / max(self.minimum, 1)
        return self.faktor > KRASCH_FAKTOR

    def genomsnitt(self):
        totalt = 0
        for _, element in enumerate(self.arr):
            totalt += element[0]
        return totalt / len(self.arr)


def sätt_pixlar(hur_många):
    for n in range(25):
        mb.display.set_pixel(n % 5, n // 5, 9 if n < hur_många else 0)


def hummux():
    är_startat = False
    mb.pin12.write_digital(1)
    inst_tid = 0
    senaste_inst = Inst()
    nya_inst = Inst()
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
            mb.display.show(IM.SAD)
            senaste_inst.sätt(STANNA, STANNA)
            flytta(senaste_inst)
            inst_tid = 0
            till_ändring = TID_TILL_ÄNDRING
            kraschen.reset()
            continue
        tiden = mb.running_time()
        höger.up()
        vänster.up()
        nya_inst.sätt(FRAMÅT, STANNA)
        mest_dolda = hitta_mest_dolda()
        kraschar = kraschen.up(tiden)

        # if mest_dolda is not None:
        #    nya_inst.sväng = motsatt_sida(mest_dolda.sida)
        if kraschar:
            nya_inst.sätt(BAKÅT, räddning_håll)
            senaste_inst.sätt_från_annan(nya_inst)
            inst_tid = 0
            till_ändring = TID_TILL_SLUTA_RÄDDNING
            räddning_håll = motsatt_sida(räddning_håll)  # byt håll nästa gång

        if nya_inst.är_samma(senaste_inst):
            if tiden - inst_tid > till_ändring:
                if not stå_still:
                    flytta(nya_inst)
                mb.display.show(nya_inst.bild())
                if not kraschar:
                    till_ändring = TID_TILL_ÄNDRING
        else:
            inst_tid = tiden
            senaste_inst.sätt_från_annan(nya_inst)
        # sätt_pixlar(kraschen.faktor * 10)
        # sätt_pixlar(-mb.accelerometer.get_y() / 40)


hummux()
