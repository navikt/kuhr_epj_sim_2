# OPPGJOR.EPJ_SIM_PASIENT

class Pasient:

    def __init__(self, input: tuple):
        self.pasient_fnr  = int(input[0])
        self.pasient_navn = str(input[1]).rstrip()

    def __str__(self):
        return (
            f"Pasient(\n"
            f"  pasient_fnr: {self.pasient_fnr},\n"
            f"  pasient_navn: {self.pasient_navn}\n"
            f")"
        )
