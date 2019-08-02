import database as db


class Asset(db.BaseModel):
    __tablename__ = 'assets'

    id = db.Column('ticker', db.String, primary_key=True)
    name = db.Column('name', db.String)
    shares = db.Column('shares', db.Integer, default=0, nullable=False)
    is_active = db.Column('is_active', db.Boolean, default=True)

    allocation = db.relationship('Allocation', secondary='assetAllocationRelationship', uselist=False)


class AssetAllocationRelationship(db.BaseModel):
    __tablename__ = 'assetAllocationRelationship'

    id = db.Column('relationship_id', db.Integer, primary_key=True)
    asset_id = db.Column('asset_id', db.String, db.ForeignKey('assets.ticker'), nullable=False)
    allocation_id = db.Column('allocation_id', db.Integer, db.ForeignKey('allocation.allocation_id'), nullable=False)

    allocation = db.relationship('Allocation')


class Allocation(db.BaseModel):
    __tablename__ = 'allocation'

    id = db.Column('allocation_id', db.Integer, primary_key=True)
    name = db.Column('name', db.String)
    target = db.Column('target', db.Float, nullable=False, default=0.0)

    assets = db.relationship('Asset', secondary='assetAllocationRelationship')


db.BaseModel.metadata.create_all(db.engine)
