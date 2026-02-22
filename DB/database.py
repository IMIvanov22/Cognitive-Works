import secrets
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
    def __init__(self, app, wipeDB = False, backend = "mysql"):
        self.app = app

        if backend == "mysql":
            self.app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://skincare:skincare@localhost/skincare'
        elif backend == "sqlite":
            self.app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{self.app.root_path}/DB/dev/skincare.sqlite"
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        self.db = SQLAlchemy(self.app)

        class UserModel(self.db.Model):
            __tablename__ = 'users'
            userId = self.db.Column(self.db.Integer, primary_key=True)
            createdAt = self.db.Column(self.db.DateTime(), nullable=False, default=self.db.func.current_timestamp())

            username = self.db.Column(self.db.String(32), unique=True, nullable=False)
            password = self.db.Column(self.db.String(512), nullable=False)

            analyses = self.db.relationship('AnalysesModel', backref='user', cascade='all, delete-orphan')
            tokens = self.db.relationship('TokenModel', backref='user', cascade='all, delete-orphan')

        class AnalysesModel(self.db.Model):
            __tablename__ = 'analyses'
            analysisId =  self.db.Column(self.db.Integer, primary_key=True)
            userId = self.db.Column(self.db.Integer, self.db.ForeignKey('users.userId', ondelete='CASCADE'), nullable=False)
            createdAt = self.db.Column(self.db.DateTime(), nullable=False, default=self.db.func.current_timestamp())

            skinType = self.db.Column(self.db.Integer, nullable=False)

        class TokenModel(self.db.Model):
            __tablename__ = 'tokens'
            tokenId = self.db.Column(self.db.Integer, primary_key=True)
            userId = self.db.Column(self.db.Integer, self.db.ForeignKey('users.userId', ondelete='CASCADE'), nullable=False)
            createdAt = self.db.Column(self.db.DateTime(), nullable=False, default=self.db.func.current_timestamp())

            token = self.db.Column(self.db.String(512), unique=True, nullable=False)

        class RecommendationModel(self.db.Model):
            __tablename__ = 'recommendations'
            recommendationId = self.db.Column(self.db.Integer, primary_key=True)
            analysisId = self.db.Column(self.db.Integer, self.db.ForeignKey('analyses.analysisId', ondelete='CASCADE'), nullable=False)

            productName = self.db.Column(self.db.String(256), nullable=False)
            brand = self.db.Column(self.db.String(256), nullable=False)
            goodForAcne = self.db.Column(self.db.Boolean, nullable=False)

        AnalysesModel.recommendations = self.db.relationship('RecommendationModel', backref='analysis', cascade='all, delete-orphan')

        self.UserModel = UserModel
        self.AnalysesModel = AnalysesModel
        self.TokenModel = TokenModel
        self.RecommendationModel = RecommendationModel

        with self.app.app_context():
            if wipeDB:
                self.db.drop_all()
            self.db.create_all()

    def create_user(self, username, password):
        user = self.UserModel()

        user.username = username
        user.password = generate_password_hash(password)

        self.db.session.add(user)
        self.db.session.commit()

    def user_exists(self, username):
        user = self.UserModel.query.filter_by(username = username).first()

        if user is not None:
            return True
        return False

    def verify_user(self, username, password):
        user = self.UserModel.query.filter_by(username = username).first()

        if not check_password_hash(user.password, password):
            return False
        return True

    def delete_user(self, username):
        user = self.UserModel.query.filter_by(username = username).first().delete()



    def create_token(self, username):
        user = self.UserModel.query.filter_by(username = username).first()
        token = self.TokenModel()
        token.userId = user.userId

        token.token = secrets.token_hex(64)

        self.db.session.add(token)
        self.db.session.commit()
        return token.token

    def token_exists(self, token):
        token = self.TokenModel.query.filter_by(token = token).first()

        if token is not None:
            return True
        return False

    def get_user(self, token):
        token_row = self.TokenModel.query.filter_by(token = token).first()
        if not token_row:
            return None
        user = self.UserModel.query.filter_by(userId = token_row.userId).first()
        return user.username if user else None

    def delete_tokens(self, username):
        user = self.UserModel.query.filter_by(username = username).first()

        self.TokenModel.query.filter_by(userId = user.userId).delete()
        self.db.session.commit()



    def create_analysis(self, username, skinType, recommendations=None):
        user = self.UserModel.query.filter_by(username = username).first()
        analysis = self.AnalysesModel()

        analysis.userId = user.userId
        analysis.skinType = skinType

        self.db.session.add(analysis)
        self.db.session.flush()

        if recommendations:
            for rec in recommendations:
                r = self.RecommendationModel()
                r.analysisId = analysis.analysisId
                r.productName = rec['product_name']
                r.brand = rec['brand']
                r.goodForAcne = rec['good_for_acne']
                self.db.session.add(r)

        self.db.session.commit()

    def get_analyses(self, username):
        user = self.UserModel.query.filter_by(username = username).first()
        analyses = self.AnalysesModel.query.filter_by(userId = user.userId).order_by(self.AnalysesModel.createdAt.desc()).all()
        return [{'timestamp': analysis.createdAt.timestamp(),
                 'skinType': analysis.skinType,
                 'recommendations': [{
                     'product_name': r.productName,
                     'brand': r.brand,
                     'good_for_acne': r.goodForAcne
                 } for r in analysis.recommendations]}
                for analysis in analyses]