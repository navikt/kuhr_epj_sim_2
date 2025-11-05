from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Identifikasjon:
    id: Optional[str] = None
    type: Optional[str] = None


@dataclass
class Eea:
    Dok: Optional[str] = None
    CardId: Optional[str] = None
    Id: Optional[str] = None
    TrygdekontorNavn: Optional[str] = None
    TrygdekontorNr: Optional[str] = None
    eeaGyldighetFra: Optional[str] = None
    eeaGyldighet: Optional[str] = None


@dataclass
class Pasient:
    etternavn: Optional[str] = None
    fornavn: Optional[str] = None
    kjonn: Optional[str] = None
    trygdenasjon: Optional[str] = None
    identifikasjon: Optional[Identifikasjon] = None
    fodselsdato: Optional[str] = None
    eea: Optional[Eea] = None


@dataclass
class Diagnose:
    kodeverk: Optional[str] = None
    kode: Optional[str] = None


@dataclass
class HenvisningFra:
    id: Optional[str] = None
    type: Optional[str] = None


@dataclass
class Henvisning:
    dato: Optional[str] = None
    id: Optional[str] = None
    diagnoser: Optional[List[Diagnose]] = field(default_factory=list)
    henvistFra: Optional[HenvisningFra] = None


@dataclass
class Behandler:
    id: Optional[str] = None
    type: Optional[str] = None


@dataclass
class Prosedyrekode:
    kodeverk: Optional[str] = None
    kode: Optional[str] = None


@dataclass
class Tannkode:
    tannkode: Optional[str] = None


@dataclass
class Takst:
    belop: Optional[float] = None
    kode: Optional[str] = None
    antall: Optional[int] = None
    tenner: Optional[List[Tannkode]] = field(default_factory=list)


@dataclass
class Regning:
    guid: Optional[str] = None
    korrigeringBetaltEgenandel: Optional[bool] = None
    betaltEgenandel: Optional[bool] = None
    kreditering: Optional[bool] = None
    regningsnummer: Optional[str] = None
    tidspunkt: Optional[str] = None
    merknad: Optional[str] = None
    pasient: Optional[Pasient] = None
    arsakFriEgenandel: Optional[str] = None
    diagnoser: Optional[List[Diagnose]] = field(default_factory=list)
    sjeldenMedisinskTilstand: Optional[str] = None
    henvisning: Optional[Henvisning] = None
    utforendeBehandler: Optional[Behandler] = None
    relatertBehandler: Optional[Behandler] = None
    moderasjonskode: Optional[str] = None
    stonadspunkt: Optional[str] = None
    prosedyrekoder: Optional[List[Prosedyrekode]] = field(default_factory=list)
    takster: Optional[List[Takst]] = field(default_factory=list)
    belop: Optional[float] = None


@dataclass
class Behandlerkrav:
    avdeling: Optional[str] = None
    navnEPJ: Optional[str] = None
    reshId: Optional[str] = None
    regninger: Optional[List[Regning]] = field(default_factory=list)
    antallRegninger: Optional[int] = None
    belop: Optional[float] = None


@dataclass
class Behandlerkravmelding:
    praksisId: Optional[str] = None
    behandlerkrav: Optional[Behandlerkrav] = None
