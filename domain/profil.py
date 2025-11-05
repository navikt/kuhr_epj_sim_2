from typing import Optional

# OPPGJOR.EPJ_SIM_PROFIL_11_12_19

class Profil:

    def __init__(self, input: tuple):

        self.fagomraade_kode: str = input[0]
        self.enkeltregning_status_k: str = input[1]
        self.diagnoser:     list[str] = input[2].split(",")
        self.takster:       list[str] = input[3].split(",")
        self.henvisning_id: Optional[int] = input[4]
        self.antall:        Optional[int] = input[5]
        self.rnd_offset: int = input[6]
        self.samhandler_praksis_type_kode: Optional[int] = input[7]

    def __repr__(self):
        return (
            f"Profil(\n"
            f"  fagomraade_kode: {self.fagomraade_kode}\n"
            f"  enkeltregning_status_k: {self.enkeltregning_status_k}\n"
            f"  diagnoser: {self.diagnoser}\n"
            f"  takster: {self.takster}\n"
            f"  henvisning_id: {self.henvisning_id}\n"
            f"  antall: {self.antall}\n"
            f"  rnd_offset: {self.rnd_offset}\n"
            f"  samhandler_praksis_type_kode: {self.samhandler_praksis_type_kode}\n"
            f")"
        )
