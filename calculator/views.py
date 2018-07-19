from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.generic import TemplateView, View
from calculator.models import BoltArea, ResShear, ResCrushing, StallMark
from math import ceil, sqrt, tan, cos


class TemplateCalculator(TemplateView):
    template_name = "calc.html"


class BoltsNumber(TemplateView):
    template_name = "bolts_number.html"

    def get_context_data(self, **kwargs):
        context = super(BoltsNumber, self).get_context_data()
        context['stall_list'] = combo_box(StallMark.objects.values_list('stall_mark'))
        context['class_list'] = ['BC', 'A']
        context['bolts_list'] = combo_box(ResShear.objects.values_list('bolt_class'))
        context['diam_list'] = combo_box(BoltArea.objects.values_list('bolt_diam'))
        return context

    def post(self, request):
        if request.method == 'POST':
            responce = self.get_context_data()
            responce['value_force'] = request.POST.get('force')
            responce['value_nmin'] = request.POST.get('nmin')
            responce['value_width'] = request.POST.get('width')
            responce['value_length'] = request.POST.get('length')
            responce['value_stall'] = request.POST.get('stall')
            responce['value_class'] = request.POST.get('class')
            responce['value_bolts'] = request.POST.get('bolts')
            responce['value_diam'] = int(request.POST.get('diam'))
            responce['value_ns'] = request.POST.get('ns')
            responce['value_number'] = request.POST.get('number')
            number = post_number(request)
            responce['result_nb'] = post_strength(request)
            responce['result_number'] = number[2]
            responce['result_nbs'] = number[0]
            responce['result_nbp'] = number[1]
            return render(request, self.template_name, responce)


class WeldingFas(TemplateView):
    template_name = "welding_fas.html"

    def get_context_data(self, **kwargs):
        context = super(WeldingFas, self).get_context_data()
        context['place_list'] = ['Монтажный', 'Заводской']
        context['list_number'] = ['Без ответной планки', 'Ответная планка']
        return context

    def post(self, request):
        if request.method == 'POST':
            responce = self.get_context_data()
            responce['value_force'] = request.POST.get('force')
            responce['value_nforce'] = request.POST.get('nforce')
            responce['value_katet'] = request.POST.get('kw')
            responce['value_length'] = request.POST.get('lw')
            responce['value_width'] = request.POST.get('width')
            responce['value_place'] = request.POST.get('place')
            responce['value_number'] = request.POST.get('plank')
            responce['result'] = post_fas(request)
            place = request.POST.get('place')
            if place == 'Монтажный':
                responce['constant'] = '1660'
            else:
                responce['constant'] = '1980'
            return render(request, self.template_name, responce)


class WeldingTable(TemplateView):
    template_name = "welding_table.html"

    def get_context_data(self, **kwargs):
        context = super(WeldingTable, self).get_context_data()
        return context

    def post(self, request):
        if request.method == 'POST':
            responce = self.get_context_data()
            responce['value_force'] = request.POST.get('force')
            responce['value_hweld'] = request.POST.get('hweld')
            responce['value_length'] = request.POST.get('length')
            result = post_table(request)
            responce['result_length'] = result[0]
            responce['result_hweld'] = result[1]
            return render(request, self.template_name, responce)


class WeldingFrame(TemplateView):
    template_name = "welding_frame.html"

    def get_context_data(self, **kwargs):
        context = super(WeldingFrame, self).get_context_data()
        return context

    def post(self, request):
        if request.method == 'POST':
            responce = self.get_context_data()
            responce['value_force'] = request.POST.get('force')
            responce['value_moment'] = request.POST.get('moment')
            responce['value_katet'] = request.POST.get('katet')
            responce['value_height'] = request.POST.get('height')
            responce['value_thickness'] = request.POST.get('thickness')
            result = post_frame(request)
            responce['result_width'] = result[0]
            responce['result_length'] = result[1]
            return render(request, self.template_name, responce)


class WeldingBead(TemplateView):
    template_name = "welding_bead.html"


class SweepPipe(TemplateView):
    template_name = "sweep_pipe.html"

    def get_context_data(self, **kwargs):
        context = super(SweepPipe, self).get_context_data()
        return context



# Функции для расчета болтового соединения
def combo_box(data_list):
    lst = []
    for i in data_list:
        lst.append(*list(i))

    return lst


def post_number(request):
    if request.method == 'POST':
        stallmark = request.POST.get('stall')
        db = request.POST.get('diam')
        if request.POST.get('class') == 'A':
            cls = 'cls_a'
        else:
            cls = 'cls_bc'
        rbs = ResShear.objects.values_list('bolt_rbs').get(bolt_class=request.POST.get('bolts'))
        force = request.POST.get('force')
        nmin = request.POST.get('nmin')
        ns = request.POST.get('ns')
        run = StallMark.objects.values_list('stall_run').get(stall_mark=stallmark)
        rbp = ResCrushing.objects.values_list(cls).get(stall_run=run[0])
        ab = BoltArea.objects.values_list('bolt_ab').get(bolt_diam=db)
        radio = request.POST.get('radio')

        return bolts_number([force, rbs[0], rbp[0], ab[0], db, nmin, ns, radio])

    else:
        result = 'Result'

        return result


def post_strength(request):
    if request.method == 'POST':
        force = request.POST.get('force')
        number = request.POST.get('number')
        width = request.POST.get('width')
        length = request.POST.get('length')
        radio = request.POST.get('radio')

        return bolts_strength([force, length, width, number, radio])

    else:
        result = 'Result'

        return result


def bolts_number(data, jb=0.9, jc=0.9, jn=0.95):
    for i in data:
        if i == '':
            return ['Нет данных', 'Нет данных', 'Нет данных']

    if data[7] == '1':
        n = (float(data[0]) * 1000) / 9.81
    else:
        n = float(data[0])

    rbs = int(data[1]) * 10
    rbp = int(data[2]) * 10
    ab = float(data[3])
    db = (int(data[4]) / 10)
    sumtmin = float(data[5])
    ns = int(data[6])
    force = []

    # Расчет усилий

    shear = rbs * ab * ns * jb * jc * jn
    crushing = rbp * db * sumtmin * jb * jc * jn

    force.append(int(shear))
    force.append(int(crushing))

    # Выбор меньшего значения усилия и округление его до целого значения

    nbt = int(ceil(min(force)))

    # Округление результата в большую сторону

    number = ceil((n * jn) / nbt)

    return [int(ceil(shear)), int(ceil(crushing)), number]


def bolts_strength(data):
    for i in data:
        if i == '':
            return 'Нет данных'

    if data[4] == '1':
        rop = (float(data[0]) * 1000) / 9.81
    else:
        rop = float(data[0])

    l = float(data[1])
    a = float(data[2])
    n = int(data[3])

    Nb = sqrt((rop / n) ** 2 + ((rop * l) / a) ** 2)

    return int(ceil(Nb))


# Функции для расчета сварного узла через фасонку
def post_fas(request):
    if request.method == 'POST':
        reaction = request.POST.get('force')
        force = request.POST.get('nforce')
        welding_katet = request.POST.get('kw')
        welding_length = request.POST.get('lw')
        width = request.POST.get('width')
        radio = request.POST.get('numeric')
        double = request.POST.get('plank')

        if force == '':
            force = '0'

        return welding_fas([reaction, width, welding_length, welding_katet, force, double, radio])

    else:
        result = ''

        return result


def welding_fas(data):
    for i in data:
        if i == '':
            return 'Нет данных'

    if data[5] == 'Ответная планка':
        double = 2
    else:
        double = 1

    if data[6] == '1':
        rop = (float(data[0]) * 1000) / 9.81
        nforce = (float(data[4]) * 1000) / 9.81
    else:
        rop = float(data[0])
        nforce = float(data[4])

    l = float(data[1])
    lw = float(data[2])
    hw = float(data[3])

    tw = sqrt((rop / (0.7 * double * hw * lw)) ** 2 + ((6 * rop * l) / (0.7 *
                                                                        double * hw * (lw) ** 2) + (
                                                           nforce / (0.7 * hw * lw))) ** 2)

    return int(ceil(tw))


# Функции для расчета сварного узла через столик
def post_table(request):
    if request.method == 'POST':
        reaction = request.POST.get('force')
        katet = request.POST.get('hweld')
        length = request.POST.get('length')
        radio = request.POST.get('numeric')

        return welding_table([reaction, length, katet, radio])

    else:
        result = ''
        return [result, result]


def welding_table(data):
    for i in data:
        if i == '':
            return ['Нет данных', 'Нет данных']

    # Расчет сварных швов и размеров опорных столиков

    if data[3] == '1':
        rop = (float(data[0]) * 1000) / 9.81
    else:
        rop = float(data[0])

    l1 = float(data[1])
    ryw = 1980
    h2 = float(data[2])

    h1 = rop / (2 * 0.7 * l1 * ryw)
    l2 = rop / (2 * 0.7 * 0.65 * h2 * ryw)

    return {'1': round(l2, 2), '2': round(h1, 1)}


# Функции для расчета рамного узла
def post_frame(request):
    if request.method == 'POST':
        force = request.POST.get('force')
        moment = request.POST.get('moment')
        katet = request.POST.get('katet')
        height = request.POST.get('height')
        thickness = request.POST.get('thickness')
        radio = request.POST.get('numeric')

        return welding_frame([force, moment, height, thickness, katet, radio])
    else:
        result = ['', '']
        return result


def welding_frame(data):
    for i in data:
        if i == '':
            return ['Нет данных', 'Нет данных']

    # Расчет сварных швов и размеров накладки рамного узла

    if data[5] == '1':
        rop = (float(data[0]) * 1000) / 9.81
        mop = (float(data[1]) * 1000) / 9.81
    else:
        rop = float(data[0])
        mop = float(data[1])

    h = float(data[2])
    t = float(data[3])
    hw = float(data[4])
    ryw = 1660

    b = mop / (h * rop * t)
    l = mop / (2 * 0.7 * h * hw * ryw)

    return [round(b, 2), round(l, 2)]


# Функции для расчета сварного двутавра
def post_bead(request):
    if request.method == 'POST':
        height = request.POST.get('height')
        tst = request.POST.get('tst')
        width = request.POST.get('width')
        tp = request.POST.get('tp')

        return welding_bead([height, tst, width, tp])
    else:
        result = ['', '']
        return result


def welding_bead(data):
    for i in data:
        if i == '':
            return ['Нет данных', 'Нет данных']

    # Расчет момента инерции и массы сварной двутавровой балки

    hst = float(data[0])
    tst = float(data[1])
    bpol = float(data[2])
    tpol = float(data[3])

    ix = (tst * (hst ** 3)) / 12 + 2 * bpol * tpol * (((hst + tpol) / 2) ** 2)
    m = (((hst / 100) * (tst / 100)) + ((bpol / 100) * (tpol / 100)) * 2) * 7850

    return [round(m, 1), int(ix)]


# Функции для расчета разверток труб
def pipe_cylinder(data):
    for i in data:
        if i == '':
            return ['Нет данных']

    t = float(data[1])
    beta = float(data[2]) * 0.0174533

    if beta <= 45:
        d = float(data[0]) - t
    else:
        d = float(data[0])

    h = (d / tan(beta)) / 2

    # Разбивка на количество промежутков в зависимости от диаметра трубы

    if d < 250:
        n = 8
    elif 250 <= d < 350:
        n = 12
    elif 350 <= d < 500:
        n = 16
    elif 500 <= d < 750:
        n = 24
    elif 750 <= d < 1000:
        n = 32
    elif 1000 <= d < 1500:
        n = 48
    elif 1500 <= d < 2000:
        n = 64
    elif d > 2000:
        n = 96

    # Список коэфициентов для умножения

    list_koef1 = [0, 0.004815, 0.019215, 0.043060, 0.076120, 0.118079, 0.168530, 0.226990, 0.292893, 0.365607,
                  0.444430, 0.528603, 0.617317, 0.709715, 0.804910, 0.901983, 1, 1.098017, 1.195090, 1.290285,
                  1.382683, 1.471397, 1.555570, 1.634393, 1.707107, 1.773010, 1.831470, 1.881921, 1.923880,
                  1.956940, 1.980785, 1.995185, 2]

    list_koef2 = [0, 0.002141, 0.008555, 0.019215, 0.034074, 0.053070, 0.076120, 0.103127, 0.133975, 0.168530,
                  0.206647, 0.248160, 0.292893, 0.340654, 0.391239, 0.444430, 0.5, 0.557711, 0.617317, 0.678561,
                  0.741181, 0.804910, 0.869474, 0.934597, 1, 1.065403, 1.130526, 1.195090, 1.258819, 1.321439,
                  1.382683, 1.442289, 1.5, 1.555570, 1.608761, 1.659346, 1.707107, 1.751840, 1.793353, 1.831470,
                  1.866025, 1.896873, 1.923880, 1.946930, 1.965926, 1.980785, 1.991445, 1.997859, 2]
    # Список в который будут записаны координаты для построения развертки трубы

    list_cylinder = []

    # Список индексов, которые зависят от того на сколько частей разбивается труба

    if n == 8:
        list_index = [0, 8, 16, 24, 32, 24, 16, 8, 0]

    elif n == 16:
        list_index = [0, 4, 8, 12, 16, 20, 24, 28, 32, 28, 24, 20, 16, 12, 8, 4, 0]

    elif n == 32:
        list_index = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 30, 28, 26, 24, 22, 20, 18,
                      16, 14, 12, 10, 8, 6, 4, 2, 0]

    elif n == 64:
        list_index = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                      26, 27, 28, 29, 30, 31, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16,
                      15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

    elif n == 12:
        list_index = [0, 8, 16, 24, 32, 40, 48, 40, 32, 24, 16, 8, 0]

    elif n == 24:
        list_index = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 44, 40, 36, 32, 28, 24, 20, 16, 12, 8, 4, 0]

    elif n == 48:
        list_index = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48,
                      46, 44, 42, 40, 38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0]

    else:
        list_index = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                      26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
                      47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25,
                      24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

    # Заполнение списка координат

    for i in list_index:
        if n == 8 or n == 16 or n == 32 or n == 64:
            x = round(list_koef1[i] * h, 4)
            list_cylinder.append(x)
        else:
            x = round(list_koef2[i] * h, 4)
            list_cylinder.append(x)

    # Создание списка с индексом и значением

    dict_result = {}

    for index, value in enumerate(list_cylinder):
        dict_result[index] = value

    return dict_result


def pipe_90(data):
    for i in data:
        if i == '':
            return ['Нет данных']

    diam = float(data[0])
    D = float(data[2])
    t = float(data[1])

    # Разбивка на количество промежутков в зависимости от диаметра трубы

    if diam < 500:
        n = 16
    elif 500 <= diam < 750:
        n = 24
    elif 750 <= diam < 1000:
        n = 32
    elif 1000 < diam < 1500:
        n = 48
    elif 1500 <= diam < 2000:
        n = 64
    else:
        n = 96

    d = diam - 2 * t

    # Список коэфициентов для умножения

    list_koef1 = [0, 0.009607, 0.038060, 0.084265, 0.146446, 0.222215, 0.308658, 0.402454, 0.5, 0.597544, 0.691342,
                  0.777785, 0.853554, 0.915734, 0.961939, 0.990393, 1, 0.990393, 0.961939, 0.915734, 0.853554,
                  0.777785, 0.691342, 0.597544, 0.5, 0.402454, 0.308658, 0.222215, 0.146446, 0.084265, 0.038060,
                  0.009607, 0]

    list_koef2 = [0, 0.004278, 0.017037, 0.038060, 0.066987, 0.103323, 0.146446, 0.195620, 0.25, 0.308658,
                  0.370590, 0.434737, 0.5, 0.565263, 0.629405, 0.691342, 0.749999, 0.804381, 0.853554, 0.896676,
                  0.933013, 0.961939, 0.982963, 0.995723, 1, 0.995723, 0.982963, 0.961939, 0.933013, 0.896676,
                  0.853554, 0.804381, 0.749999, 0.691342, 0.629405, 0.565263, 0.5, 0.434737, 0.370590,
                  0.308658, 0.25, 0.195620, 0.146446, 0.103323, 0.066987, 0.038060, 0.017037, 0.004278, 0]

    # Список в который будут записаны координаты для построения развертки трубы

    list_pipe90 = []

    # Список индексов, которые зависят от того на сколько частей разбивается труба

    if n == 8:
        list_index = [0, 8, 16, 24, 32, 24, 16, 8, 0]

    elif n == 16:
        list_index = [0, 4, 8, 12, 16, 20, 24, 28, 32, 28, 24, 20, 16, 12, 8, 4, 0]

    elif n == 32:
        list_index = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 30, 28, 26, 24, 22, 20, 18,
                      16, 14, 12, 10, 8, 6, 4, 2, 0]

    elif n == 64:
        list_index = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                      26, 27, 28, 29, 30, 31, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16,
                      15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

    elif n == 12:
        list_index = [0, 8, 16, 24, 32, 40, 48, 40, 32, 24, 16, 8, 0]

    elif n == 24:
        list_index = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 44, 40, 36, 32, 28, 24, 20, 16, 12, 8, 4, 0]

    elif n == 48:
        list_index = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48,
                      46, 44, 42, 40, 38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0]

    else:
        list_index = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                      26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
                      47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25,
                      24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

    # Заполнение списка координат

    for i in list_index:
        if n == 8 or n == 16 or n == 32 or n == 64:
            x = round((d / 2) * (D / d - sqrt((D / d) ** 2 - list_koef1[i])), 4)
            list_pipe90.append(x)
        else:
            x = round((d / 2) * (D / d - sqrt((D / d) ** 2 - list_koef2[i])), 4)
            list_pipe90.append(x)

    # Создание списка с индексом и значением

    dict_result = {}

    for index, value in enumerate(list_pipe90):
        dict_result[index] = value

    return dict_result


def pipe_pipe(data):
    for i in data:
        if i == '':
            return ['Нет данных']

    diam = float(data[0])
    D = float(data[2])
    t = float(data[1])
    beta = float(data[3]) * 0.0174533

    # Разбивка на количество промежутков в зависимости от диаметра трубы

    if diam < 500:
        n = 16
    elif 500 <= diam < 750:
        n = 24
    elif 750 <= diam < 1000:
        n = 32
    elif 1000 <= diam < 1500:
        n = 48
    elif 1500 <= diam < 2000:
        n = 64
    else:
        n = 96

    d = diam - t

    # Список коэфициентов для умножения

    list_koef1 = [0, 0.009607, 0.038060, 0.084265, 0.146446, 0.222215, 0.308658, 0.402454, 0.5, 0.597544, 0.691342,
                  0.777785, 0.853554, 0.915734, 0.961939, 0.990393, 1, 0.990393, 0.961939, 0.915734, 0.853554,
                  0.777785, 0.691342, 0.597544, 0.5, 0.402454, 0.308658, 0.222215, 0.146446, 0.084265, 0.038060,
                  0.009607, 0]

    list_koef2 = [0, 0.004278, 0.017037, 0.038060, 0.066987, 0.103323, 0.146446, 0.195620, 0.25, 0.308658,
                  0.370590, 0.434737, 0.5, 0.565263, 0.629405, 0.691342, 0.749999, 0.804381, 0.853554, 0.896676,
                  0.933013, 0.961939, 0.982963, 0.995723, 1, 0.995723, 0.982963, 0.961939, 0.933013, 0.896676,
                  0.853554, 0.804381, 0.749999, 0.691342, 0.629405, 0.565263, 0.5, 0.434737, 0.370590,
                  0.308658, 0.25, 0.195620, 0.146446, 0.103323, 0.066987, 0.038060, 0.017037, 0.004278, 0]

    # Список в который будут записаны координаты для построения развертки трубы

    list_pipe = []

    # Список индексов, которые зависят от того на сколько частей разбивается труба

    if n == 8:
        list_index = [0, 8, 16, 24, 32, 24, 16, 8, 0]

    elif n == 16:
        list_index = [0, 4, 8, 12, 16, 20, 24, 28, 32, 28, 24, 20, 16, 12, 8, 4, 0]

    elif n == 32:
        list_index = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 30, 28, 26, 24, 22, 20, 18,
                      16, 14, 12, 10, 8, 6, 4, 2, 0]

    elif n == 64:
        list_index = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                      26, 27, 28, 29, 30, 31, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16,
                      15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

    elif n == 12:
        list_index = [0, 8, 16, 24, 32, 40, 48, 40, 32, 24, 16, 8, 0]

    elif n == 24:
        list_index = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 44, 40, 36, 32, 28, 24, 20, 16, 12, 8, 4, 0]

    elif n == 48:
        list_index = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48,
                      46, 44, 42, 40, 38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0]

    else:
        list_index = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                      26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
                      47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25,
                      24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

    # Заполнение списка координат

    for i in list_index:
        if n == 8 or n == 16 or n == 32 or n == 64:
            if i < 16:
                x = round((1 / cos(beta)) * (d / 2) * (D / d - sqrt((D / d) ** 2 - list_koef1[i])) + (d / 2) * tan(
                    beta) * (1 - sqrt(1 - list_koef1[i])), 4)
                list_pipe.append(x)
            else:
                x = round((1 / cos(beta)) * (d / 2) * (D / d - sqrt((D / d) ** 2 - list_koef1[i])) + (d / 2) * tan(
                    beta) * (1 + sqrt(1 - list_koef1[i])), 4)
                list_pipe.append(x)
        else:
            if i < 24:
                x = round((1 / cos(beta)) * (d / 2) * (D / d - sqrt((D / d) ** 2 - list_koef2[i])) + (d / 2) * tan(
                    beta) * (1 - sqrt(1 - list_koef2[i])), 4)
                list_pipe.append(x)
            else:
                x = round((1 / cos(beta)) * (d / 2) * (D / d - sqrt((D / d) ** 2 - list_koef2[i])) + (d / 2) * tan(
                    beta) * (1 + sqrt(1 - list_koef2[i])), 4)
                list_pipe.append(x)

    # Создание списка с индексом и значением

    dict_result = {}

    for index, value in enumerate(list_pipe):
        dict_result[index] = value

    return dict_result


def pipe_list(request):
    value_diameter_list = request.GET.get('diameter_list')
    value_thickness_list = request.GET.get('thickness_list')
    value_angle_list = request.GET.get('angle_list')
    result = pipe_cylinder([value_diameter_list, value_thickness_list, value_angle_list])
    return JsonResponse(result)


def pipe90(request):
    value_diameter_pipe90 = request.GET.get('diameter_pipe90')
    value_thickness_pipe90 = request.GET.get('thickness_pipe90')
    value_diameter_to_pipe90 = request.GET.get('diameter_to_pipe90')
    result = pipe_90([value_diameter_pipe90, value_thickness_pipe90, value_diameter_to_pipe90])
    return JsonResponse(result)


def pipe(request):
    value_diameter_pipe = request.GET.get('diameter_pipe')
    value_thickness_pipe = request.GET.get('thickness_pipe')
    value_angle_pipe = request.GET.get('angle_pipe')
    value_diameter_to_pipe = request.GET.get('diameter_to_pipe')
    result = pipe_pipe([value_diameter_pipe, value_thickness_pipe, value_diameter_to_pipe, value_angle_pipe])
    return JsonResponse(result)


def table(request):
    value_radio1 = request.GET.get('radio1')
    value_force = request.GET.get('force')
    value_hweld = request.GET.get('hweld')
    value_length = request.GET.get('length')
    result = welding_table([value_force, value_length, value_hweld, value_radio1])
    return JsonResponse(result)
