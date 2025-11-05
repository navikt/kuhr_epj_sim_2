import oracledb
from domain.pasient import Pasient
from domain.profil import Profil


async def getProfil(conn: oracledb.Connection, antall: int, omraade: str):

    """
        FAGOMRAADE_KODE
        DIAGNOSER
        TAKSTER
    """

    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM (
            SELECT * 
            FROM OPPGJOR.EPJ_SIM_PROFIL_11_12_19
            ORDER BY DBMS_RANDOM.VALUE
        )
        WHERE ROWNUM <= :1
        AND FAGOMRAADE_KODE = :2
    """, [antall, omraade])

    profiler = [Profil(row) for row in cursor.fetchall()]

    return profiler


async def getPasient(conn, antall: int):

    """
        PASIENT_FNR
        PASIENT_NAVN
    """

    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM (
            SELECT * 
            FROM OPPGJOR.EPJ_SIM_PASIENT
            ORDER BY DBMS_RANDOM.VALUE
        )
        WHERE ROWNUM <= :1
    """, [antall])

    pasienter = [Pasient(row) for row in cursor.fetchall()]

    return pasienter
