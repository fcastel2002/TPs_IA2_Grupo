# environment_controller.py
from typing import Dict

class Environment:
    """
    Modelo del entorno: lectura de sensores y cálculo de las variables Z.
    El método read_sensors debe ser implementado por el usuario o subclases.
    """
    def __init__(self,
                 comfort_day: float,
                 comfort_night_cal: float,
                 comfort_night_enf: float):
        self.comfort_day = comfort_day            # v0
        self.comfort_night_cal = comfort_night_cal  # v0CAL
        self.comfort_night_enf = comfort_night_enf  # v0ENF

    def read_sensors(self) -> Dict[str, float]:
        """
        Debe devolver un dict con:
          - 'hora': float en [0,24]
          - 'temp_int': temperatura interior actual (v_t)
          - 'temp_ext': temperatura exterior actual (v_et)
          - 'temp_pred': temperatura exterior pronosticada (TPREDICHA)
             (¡Necesita implementación realista!)
        """
        raise NotImplementedError("Subclase debe implementar read_sensors() con datos reales/simulados")

    def _calculate_z_values(self, v_int: float, v_ext: float) -> Dict[str, float]:
        """
        Calcula los tres valores Z basados en las diferentes temperaturas de referencia.
        """
        driving_diff = (v_ext - v_int)
        z_day = (v_int - self.comfort_day) * driving_diff
        z_cal = (v_int - self.comfort_night_cal) * driving_diff
        z_enf = (v_int - self.comfort_night_enf) * driving_diff
        return {'Z': z_day, 'ZCAL': z_cal, 'ZENF': z_enf}


    def get_crisp_inputs(self) -> Dict[str, float]:
        """
        Lee sensores y calcula todas las entradas nítidas necesarias para el FIS.
        """
        s = self.read_sensors() # Debe devolver 'hora', 'temp_int', 'temp_ext', 'temp_pred'

        # --- VALIDACIÓN CORREGIDA ---
        # Verificar que 'temp_pred' está presente ANTES de usarlo
        if 'temp_pred' not in s:
             raise ValueError("La lectura de sensores (read_sensors) no devolvió la clave 'temp_pred'")
        # -----------------------------

        # Ahora podemos calcular z y construir el diccionario de salida
        z_values = self._calculate_z_values(s['temp_int'], s['temp_ext'])

        crisp_inputs = {
            'Hora': s['hora'],
            'TPREDICHA': s['temp_pred'], # Usar el valor validado
            **z_values # Combina los diccionarios {'Z':..,'ZCAL':..,'ZENF':..}
        }

        return crisp_inputs

class FuzzyController:
    """
    Orquesta el sistema de control difuso:
    - Lee inputs nítidos del Environment
    - Ejecuta inferencia
    - Desborrosifica
    (Esta clase no necesita cambios)
    """
    def __init__(self,
                 fis,
                 defuzzifier,
                 environment: Environment):
        self.fis = fis
        self.defuzzifier = defuzzifier
        self.env = environment

    def step(self) -> float:
        """
        Realiza un ciclo de control:
          1) Obtener entradas nítidas
          2) Inferir salidas difusas
          3) Desborrosificar y devolver acción (apertura ventana)
        """
        crisp_inputs = self.env.get_crisp_inputs()
        fuzzy_outputs = self.fis.infer(crisp_inputs)
        # Opcional: Imprimir para debug
        # print(f"Hora: {crisp_inputs['Hora']:.1f}, TPred: {crisp_inputs['TPREDICHA']:.1f}, Z: {crisp_inputs['Z']:.1f}, ZCAL: {crisp_inputs['ZCAL']:.1f}, ZENF: {crisp_inputs['ZENF']:.1f}")
        # print(f"  Fuzzified: {self.fis.fuzzified_inputs(crisp_inputs)}")
        # print(f"  Outputs: {fuzzy_outputs}")
        action = self.defuzzifier.defuzzify(fuzzy_outputs)
        # print(f"  Action: {action:.2f}")
        return action