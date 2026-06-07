class Comision_Actividad:
    def __init__(self, id_comision, id_actividad, ponderacion_porcentaje, id_comision_actividad=None):
        self.id_comision_actividad = id_comision_actividad
        self.id_comision = id_comision
        self.id_actividad = id_actividad
        self.ponderacion_porcentaje = ponderacion_porcentaje