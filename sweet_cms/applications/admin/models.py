import os

from flask import url_for

from sweet_cms.database import PkModel, Column, reference_col, relationship
from sweet_cms.extensions import db, ma








class Seo(PkModel):
    __tablename__ = "seo"
    meta_tag = Column(db.String(80), nullable=False)
    title = Column(db.String(80), nullable=False)
    content = Column(db.String(256), nullable=False)


class Setting(PkModel):
    __tablename__ = "settings"
    name = Column(db.String(80), nullable=False)
    display_name = Column(db.String(80), nullable=False)
    value = Column(db.String(512), nullable=True)


# Schemas

