"""
Author: Enrico Schmitz
API
Script: Pydantic models to load in the json
"""
from math import isnan
from typing import Union, Optional

from pydantic import BaseModel as PydanticBaseModel, validator


class BaseModel(PydanticBaseModel):
    @validator('*')
    def change_nan_to_none(cls, v, field):
        if field.outer_type_ is float and isnan(v):
            return None
        return v


class LegendItem(BaseModel):
    Label: str
    Data: str


class MappingItem(BaseModel):
    Key: str
    Desc: str
    Mapping: str


class ProtocolLegendData(BaseModel):
    Description: str
    ProtocolMapping: list[MappingItem]


class CustomProtocolLegend(BaseModel):
    Label: str
    Data: ProtocolLegendData


class Description(BaseModel):
    Description: str
    Legend: list[LegendItem]
    CustomProtocolLegend: list[CustomProtocolLegend]


class RgsVersion(BaseModel):
    RgsVersion: str
    RgsMode: str
    IrcVersion: str
    LogFileSpecificationVersion: str
    TimeZone: str


class ProtocolInfo(BaseModel):
    ProtocolVersion: str
    ProtocolName: str
    ProtocolID: int
    TrackingDevice: str
    ProtocolMode: str
    Condition: str


class SessionInfo(BaseModel):
    SessionID: int
    PatientID: int
    IsPrescribedAsRoutine: Union[str, bool]
    SessionDate: str
    LocalSessionTime: str


class UserModel(BaseModel):
    PredictedPerformance: str
    DifficultyParameters: list[str]
    UserWeights: list
    DefaultWeights: list


class Header(BaseModel):
    RgsInfo: RgsVersion
    ProtocolInfo: ProtocolInfo
    SessionInfo: SessionInfo
    IRC: dict[str, list[UserModel]]
    CommonEvents: list[str]
    ProtocolEvents: list[str]
    ObjectEvents: list[str]


class Timestamp(BaseModel):
    t: int


class Score(BaseModel):
    t: int
    value: int


class AlgorithmDescription(BaseModel):
    Method: str
    PredictionTarget: float
    MinPredictionAcceptanceThreshold: Optional[float] = None
    MaxPredictionAcceptanceThreshold: Optional[float] = None
    Predicted: float
    Obtained: int


class DifficultyParameters(BaseModel):
    Key: str
    Value: float
    Mapping: float


class SuccessRate(BaseModel):
    AlgorithmDescription: AlgorithmDescription
    DifficultyParameters: list[DifficultyParameters]


class IrcComputeDifficulty(BaseModel):
    t: int
    Performances: dict[str, SuccessRate]


class CommonEvents(BaseModel):
    ProtocolStart: Timestamp
    ProtocolPaused: list
    ProtocolAborted: dict
    ProtocolFinished: Timestamp
    RegisterScore: list[Score]
    IrcComputeDifficulty: list[IrcComputeDifficulty]


class ProtocolEvents(BaseModel):
    StartNewSeries: list[Score]
    StartNewLevel: list[Score]


class ObjectEvent(BaseModel):
    t: int
    id: int
    value: Optional[str] = None
    X: float
    Y: float
    Z: float


class Position(BaseModel):
    t: int
    X: float
    Y: float
    Z: float


class Positions(BaseModel):
    Position: list[Position]


class Data(BaseModel):
    CommonEvents: CommonEvents
    ProtocolEvents: ProtocolEvents
    ObjectEvents: dict[str, list[ObjectEvent]]
    TrackingRaw: dict[str, Positions]
    Kinematics: dict[str, Positions]


class RawLogFile(BaseModel):
    LogFileDescription: Description
    Header: Header
    Data: Data


def parse_Json(dictionary: dict) -> RawLogFile:
    return RawLogFile.parse_obj(dictionary)
