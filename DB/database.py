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

        class AnalysesModel(self.db.Model):
            __tablename__ = 'Analyses'
            analysisId =  self.db.Column(self.db.Integer, primary_key=True)
            userId = self.db.Column(self.db.Integer, self.db.ForeignKey('users.userId', ondelete='CASCADE'), nullable=False)
            createdAt = self.db.Column(self.db.DateTime(), nullable=False, default=self.db.func.current_timestamp())

            skinType = self.db.Column(self.db.Integer, nullable=False)

        self.UserModel = UserModel
        self.AnalysesModel = AnalysesModel

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
        result = self.UserModel.query.filter_by(username = username).first()
        if result is not None:
            return True
        return False

    def verify_user(self, username, password):
        user = self.UserModel.query.filter_by(username = username).first()
        if not check_password_hash(user.password, password):
            return False
        return True

    def delete_user(self, username):
        self.UserModel.query.filter_by(username = username).first()


    def create_analysis(self, username, skinType):
        user = self.UserModel.query.filter_by(username = username).first()
        analysis = self.AnalysesModel()

        analysis.userId = user.userId
        analysis.skinType = skinType

        self.db.session.add(analysis)
        self.db.session.commit()

    def get_analyses(self, username):
        user = self.UserModel.query.filter_by(username = username).first()
        analyses = self.AnalysesModel.query.with_entities(self.AnalysesModel.createdAt, self.AnalysesModel.status).filter_by(userId = user.userId).all()
        return [{'timestamp': analysis[0].timestamp(),
                 'skinType': analysis[0]}
                for analysis in analyses]