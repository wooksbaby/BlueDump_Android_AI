from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from database import Base


class Member(Base):
    __tablename__ = "TB_MEMBER"

    MEMBER_NUM = Column(Integer, primary_key=True, autoincrement=True)
    MEMBER_ID = Column(String(20), nullable=False)
    MEMBER_PW = Column(String(200), nullable=False)
    MEMBER_NICKNAME = Column(String(50))
    JOIN_DATE = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    PROFILE_PATH = Column(String(450))

    group_rooms = relationship(
        "GroupRoom", order_by="GroupRoom.GROUP_ROOM_NUM", back_populates="member"
    )
    group_details = relationship(
        "GroupDetail", order_by="GroupDetail.GROUP_SERIAL_NUM", back_populates="member"
    )


class GroupRoom(Base):
    __tablename__ = "TB_GROUPROOM"

    GROUP_ROOM_NUM = Column(Integer, primary_key=True, autoincrement=True)
    GROUP_ROOM_NAME = Column(String(45), nullable=False)
    GROUP_ROOM_OPTION = Column(Boolean, default=True)
    CREATE_DATE = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    GROUP_ROOM_URL = Column(String(450))
    MEMBER_NUM = Column(Integer, ForeignKey("TB_MEMBER.MEMBER_NUM"), nullable=False)
    CLASSIFIED_FINISH_FLAG = Column(
        Enum("INACTIVE", "ACTIVE", "COMPLETED"), default="INACTIVE", nullable=False
    )

    member = relationship("Member", back_populates="group_rooms")
    group_details = relationship(
        "GroupDetail",
        order_by="GroupDetail.GROUP_SERIAL_NUM",
        back_populates="group_room",
    )


class GroupDetail(Base):
    __tablename__ = "TB_GROUP_DETAIL"

    GROUP_SERIAL_NUM = Column(Integer, primary_key=True, autoincrement=True)
    MEMBER_NUM = Column(Integer, ForeignKey("TB_MEMBER.MEMBER_NUM"), nullable=False)
    GROUP_ROOM_NUM = Column(
        Integer, ForeignKey("TB_GROUPROOM.GROUP_ROOM_NUM"), nullable=False
    )

    member = relationship("Member", back_populates="group_details")
    group_room = relationship("GroupRoom", back_populates="group_details")
